import csv
from datetime import date, datetime, timedelta
from functools import partial
from pathlib import Path
from warnings import warn

import numpy as np
import pandas as pd
import pytz
from astropy import constants as const
from astropy import units as u
from astropy.coordinates import (
    GCRS,
    TEME,
    CartesianDifferential,
    CartesianRepresentation,
)
from astropy.time import Time
from astropy.visualization import quantity_support
from geopy.geocoders import Nominatim
from matplotlib import pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from poliastro.bodies import Earth, Moon
from poliastro.constants import GM_earth
from poliastro.core.perturbations import third_body
from poliastro.core.propagation import func_twobody
from poliastro.ephem import Ephem, build_ephem_interpolant
from poliastro.frames import Planes
from poliastro.twobody import Orbit
from poliastro.twobody.propagation import CowellPropagator
from poliastro.twobody.sampling import EpochsArray
from poliastro.util import time_range
from skyfield.api import EarthSatellite, Loader, load, wgs84
from timezonefinder import TimezoneFinder

quantity_support()

spectral_units = {"Wavelength": u.nm, "Flux": u.Unit("W.m^(-2).nm^(-1)")}

scale = u.kpc.to(u.au) ** 2  # Normalizando espectro de corpo negro para 1 R_sun - 1 AU

# Propriedades do Sol
m_sun = const.M_sun
r_sun = const.R_sun
l_sun = const.L_sun

visible_range = [380, 780] * u.nm


# Configurar Loader para carregar TLEs
load = Loader("../../data/TLEs")
eph = load("de421.bsp")


## Seção de Coordenadas Celestes - Skyfield
#------------------------------------------------
def make_analemma(
    start_date=None, end_date=None, hour=None, location="Campina Grande, PB"
):
    # determina coordenadas da localização com geopy
    geolocator = Nominatim(user_agent="Aulas")
    location = geolocator.geocode(location)
    lat, lon = location.latitude, location.longitude
    # determina timezone com timezonefinder e pytz
    tf = TimezoneFinder()
    tz = pytz.timezone(tf.timezone_at(lng=lon, lat=lat))
    # Observador
    earth = eph["earth"]
    observer = earth + wgs84.latlon(lat, lon)
    # Time range
    if hour is None:
        hour = 12
    hour = timedelta(hours=hour)
    if start_date is None:
        start_date = tz.localize(datetime.combine(date.today(), datetime.min.time()))
    else:
        start_date = tz.localize(date.fromisoformat(start_date))
    start_date = (start_date + hour).astimezone(pytz.UTC)
    if end_date is None:
        n_days = 365
    else:
        n_days = (end_date - start_date).days
    ts = load.timescale()
    _times = [start_date + timedelta(days=i) for i in range(n_days)]
    times = ts.from_datetimes(_times)

    sun = eph["sun"]
    observations = observer.at(times).observe(sun).apparent()
    return observations


def plot_analemma(observations, coordinates="horizontal", ax=None):
    geolocator = Nominatim(user_agent="Aulas")
    geocode = partial(geolocator.geocode, language="es")
    location = geolocator.reverse((observations.center.latitude.degrees, observations.center.longitude.degrees), exactly_one=True, language="pt")
    local = location.raw["address"].get("city")
    MONTH_NAMES = "0 Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()

    if coordinates == "horizontal":
        yy, xx, _ = observations.altaz()
        y_label, x_label = "Altitude (degrees)", "Azimuth (degrees)"
    else:
        yy, xx = observations.radec()
        y_label, x_label = "Declination (degrees)", "Right Ascension (degrees)"
    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=(12, 6))
    times = observations.t
    idxs_1 = np.where(times.utc[2].astype(int) == 1)[0]
    ax.plot(xx.degrees, yy.degrees, label=local)
    ax.scatter(xx.degrees[idxs_1], yy.degrees[idxs_1], color="yellow", s=10, zorder=2)

    offset_x, offset_y = 10, 8
    for idx in idxs_1:
        day_i = f"{times.utc.day[idx].astype(int)} - {MONTH_NAMES[times.utc.month[idx].astype(int)]}"
        xi, yi = xx.degrees[idx], yy.degrees[idx]
        xytext = (offset_x, offset_y)
        ax.annotate(
            day_i,
            (xi, yi),
            c="yellow",
            ha="center",
            va="center",
            textcoords="offset points",
            xytext=xytext,
            size=8,
        )

    # Melhorando visualização
    ax.set_xlabel(f"{x_label} (°)")
    ax.set_ylabel(f"{y_label} (°)")
    ax.set_title("Analema do Sol")
    ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.5)
    ax.set_aspect("equal")  # Mantém a proporção correta
    ax.legend()
    sky = LinearSegmentedColormap.from_list("sky", ["black", "blue"])
    extent = ax.get_xlim() + ax.get_ylim()
    ax.imshow([[0, 0], [1, 1]], cmap=sky, interpolation="bicubic", extent=extent)
    return ax


## Seção de Órbitas - Skyfield/Poliastro
#------------------------------------------------
def get_timestamp_idx(times, target_timestamp, tol=1 * u.min):
    time_diffs = np.abs(times - target_timestamp)
    idx = np.argmin(time_diffs)
    if time_diffs[idx] > tol:
        return None
    return idx

def make_time_range(object=None, n_days=365, steps_per_day=96):
    ts = load.timescale()
    if object is None:
        start_date = Time(Time.now().jd, format="jd", scale="tdb")
    else:
        object = EarthSatellite.from_omm(ts, object)
        start_date = Time(object.epoch.to_astropy().jd, format="jd", scale="tdb")
    times = start_date + np.linspace(0, n_days, n_days * steps_per_day) * u.day
    return times

def get_orbital_elements(satellite):
    # Extrair valores do dicionário
    mean_motion = float(satellite["MEAN_MOTION"])  # Revoluções por dia
    eccentricity = float(satellite["ECCENTRICITY"]) * u.one
    inclination = float(satellite["INCLINATION"]) * u.deg
    raan = float(satellite["RA_OF_ASC_NODE"]) * u.deg
    arg_periapsis = float(satellite["ARG_OF_PERICENTER"]) * u.deg
    mean_anomaly = float(satellite["MEAN_ANOMALY"]) * u.deg
    epoch = satellite["EPOCH"]
    # Calcular o semi-eixo maior (a) usando a Terceira Lei de Kepler
    mean_motion_rad_s = mean_motion * (2 * np.pi * u.rad) / (86400 * u.s)  # Converter para rad/s
    semi_major_axis = (GM_earth / (mean_motion_rad_s**2)) ** (1 / 3)  # Semi-eixo maior em metros
    semi_major_axis = ((GM_earth / (mean_motion_rad_s**2)) ** (1 / 3)).to(
        u.km, equivalencies=u.dimensionless_angles()
    )
    return (
        semi_major_axis, eccentricity, inclination, raan, arg_periapsis, mean_anomaly
    )


def get_sat(object="ISS"):
    # Baixar TLEs mais recentes para a ISS
    if not Path("../../data/TLEs/stations.csv").exists():
        url = "https://celestrak.org/NORAD/elements/gp.php?GROUP=stations&FORMAT=csv"
        load.download(url, filename="../../data/TLEs/stations.csv")

    with load.open("stations.csv", mode="r") as f:
        TLEdata = list(csv.DictReader(f))
    ts = load.timescale()
    TLEs = pd.DataFrame.from_dict(TLEdata)
    satellite = TLEs[TLEs.OBJECT_NAME == "ISS (ZARYA)"].iloc[0, :].to_dict()
    #satellite = EarthSatellite.from_omm(ts, ISS_elems)
    return satellite
    


def ephem_from_skyfield(sat, times):
    errors, rs, vs = sat.model.sgp4_array(times.jd1, times.jd2)
    if not (errors == 0).all():
        warn(
            "Some objects could not be propagated, proceeding with the rest",
            stacklevel=2,
        )
        rs = rs[errors == 0]
        vs = vs[errors == 0]
        times = times[errors == 0]

    cart_teme = CartesianRepresentation(
        rs << u.km,
        xyz_axis=-1,
        differentials=CartesianDifferential(
            vs << (u.km / u.s),
            xyz_axis=-1,
        ),
    )
    cart_gcrs = TEME(cart_teme, obstime=times).transform_to(GCRS(obstime=times)).cartesian

    return Ephem(cart_gcrs, times, plane=Planes.EARTH_EQUATOR)    

def get_ephem_kepler(object, times):
    elements = get_orbital_elements(object)
    orbit = Orbit.from_classical(Earth, *elements, epoch=times[0])
    epochs = time_range(start=times[0], end=times[-1], periods=1000)
    ephem = orbit.to_ephem(strategy=EpochsArray(epochs=epochs.tdb))
    return ephem


       

def get_ephem_sgp4(object, times):
    ts = load.timescale()
    _times = ts.from_astropy(times)
    satellite = EarthSatellite.from_omm(ts, object)
    epochs = time_range(start=times[0], end=times[-1], periods=1000)
    ephem = ephem_from_skyfield(satellite, epochs)
    return ephem 




def get_ephem_cowell(object, times):
    tofs = times - times[0]
    elements = get_orbital_elements(object)
    orbit = Orbit.from_classical(Earth, *elements, epoch=times[0])
    body_r = build_ephem_interpolant(
    Moon,
    28 * u.day,
    (times[0] - 2 * u.day, times[-1] + 30 * u.day),
    rtol=1e-2,
    )
    def _f(t0, state, k):
        du_kep = func_twobody(t0, state, k)
        ax, ay, az = third_body(
            t0,
            state,
            k,
            Moon.k.to(u.km**3 / u.s**2).value,
            perturbation_body=body_r,
        )
        du_ad = np.array([0, 0, 0, ax, ay, az])

        return du_kep + du_ad

    ephem = orbit.to_ephem(
    EpochsArray(times[0] + tofs, method=CowellPropagator(rtol=1e-5, f=_f)),
    )
    return ephem

def get_moon(times):
    epochs = time_range(start=times[0], end=times[-1], periods=1000)
    ephem = Ephem.from_body(Moon, epochs, attractor=Earth)   
    return ephem

