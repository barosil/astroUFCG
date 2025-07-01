import matplotlib.dates as mdates
import numpy as np
import osmnx as ox
import pandas as pd
import pyvista as pv
from jplephem.daf import DAF
from jplephem.excerpter import write_excerpt
from jplephem.spk import SPK
from matplotlib import pyplot as plt
from skyfield import almanac
from skyfield.api import load, wgs84

#load = Loader("../../../data/skyfield")
eph = load("../../data/skyfield/de431_excerpt.bsp")
terra = eph["earth"]
sol = eph["sun"]
lua = eph["moon"]
ts = load.timescale()

# --- Configurações Skyfield ---


def get_ephemeris(path, start_date, end_date, targets=None, output_path=None):
    """
    Carrega a efeméride de um arquivo ou URL.

    :param url: Caminho ou URL do arquivo de efeméride.
    :param start_date: Data de início no formato 'YYYY-MM-DD'.
    :param end_date: Data de término no formato 'YYYY-MM-DD'.
    :param targets: Lista de corpos celestes para carregar (opcional).
    :param output_path: Caminho para salvar a efeméride (opcional).
    :return: Efeméride carregada.
    """
    start_date = ts.ut1(start_date).tt
    end_date = ts.ut1(end_date).tt
    with open(path, "rb") as file:
        spk = SPK(DAF(file))
        summaries = spk.daf.summaries()
        with open(output_path, "w+b") as output_file:
            write_excerpt(spk, output_file, start_date, end_date, summaries)
    return


def make_observer(location):
    lat = float(location["lat"])
    lon = float(location["lon"])
    local = terra + wgs84.latlon(latitude_degrees=lat, longitude_degrees=lon)
    return local


def find_summer_noon_time(location, year):
    """Encontra o meio-dia solar no solstício de verão para um local e ano."""
    t0 = ts.ut1(year, 1, 1)
    t1 = ts.ut1(year, 12, 31)
    t, y = almanac.find_discrete(t0, t1, almanac.seasons(eph))
    _ss = t[almanac.SEASON_EVENTS.index("Summer Solstice")]
    summer_solstice = _ss.ut1_calendar()[:3]
    observer = make_observer(location)

    t0 = ts.ut1(*summer_solstice, 0, 0)  # Meio-dia do solstício de verão
    t1 = ts.ut1(*summer_solstice, 24, 0)  # Meio-dia do solstício de verão
    f_01 = almanac.meridian_transits(eph, sol, observer - terra)
    times, events = almanac.find_discrete(t0, t1, f_01)
    noon = times[events == 1][0]
    return noon


def make_time_vector(center, amplitude, num_points=100, unit="minutes"):
    """Cria um vetor de tempo centrado em 'center' com amplitude 'amplitude'."""
    scales = {
        "minutes": 1 / 1440.0,  # 1 minuto em dias
        "hours": 1 / 24.0,  # 1 hora em dias
        "days": 1.0,  # 1 dia em dias
        "seconds": 1 / 86400.0,  # 1 segundo em dias
    }
    range = np.linspace(-amplitude, amplitude, num_points)
    center_tuples = center.ut1_calendar()
    time_vector = (
        ts.ut1(
            center_tuples[0],
            center_tuples[1],
            center_tuples[2],
            center_tuples[3],
            center_tuples[4],
        )
        + range * scales[unit]
    )
    return time_vector


def solar_alt_az(location, time):
    """Calcula a altitude e o azimute do Sol para um local e instante."""
    sol = eph["sun"]
    astrometric = location.at(time).observe(sol).apparent()
    alt, az, _ = astrometric.altaz()
    return alt.degrees, az.degrees


def shadow_length(height, altitude_deg):
    """Calcula o comprimento da sombra projetada de um objeto."""
    return height / np.tan(np.radians(altitude_deg))


def obseve_shadow(location, times, object_height=10):
    """Observa a sombra projetada de um objeto em um determinado local."""
    obs = make_observer(location)
    astrometric = obs.at(times).observe(sol).apparent()
    alt, az, _ = astrometric.altaz()
    shadow_length_ = shadow_length(object_height, alt.degrees)
    df = pd.DataFrame(
        {"alt": alt.degrees, "az": az.degrees, "shadow_length": shadow_length_},
        index=times.ut1,
    )
    return df


def get_noon_times(location, year=2023):
    """Obtém o meio-dia solar para um local e ano específicos."""
    noon = find_summer_noon_time(location, year)
    times = make_time_vector(noon, 60, 61, "minutes")
    return noon, times


def set_experiment(site_01, site_02, year=2023, object_height=10):
    """Configura o experimento de Eratóstenes para dois locais."""
    location_01 = pd.DataFrame([list(ox.geocode(site_01))], columns=["lat", "lon"]).iloc[0]
    location_02 = pd.DataFrame([list(ox.geocode(site_02))], columns=["lat", "lon"]).iloc[0]

    noon_01, times_01 = get_noon_times(location_01, year)
    noon_02, times_02 = get_noon_times(location_02, year)

    df_01 = obseve_shadow(location_01, times_02, object_height)
    df_02 = obseve_shadow(location_02, times_02, object_height)

    df = pd.DataFrame(
        {
            "alt_01": df_01["alt"].values,
            "az_01": df_01["az"].values,
            "shadow_length_01": df_01["shadow_length"].values,
            "alt_02": df_02["alt"].values,
            "az_02": df_02["az"].values,
            "shadow_length_02": df_02["shadow_length"].values,
            "time_01": pd.to_datetime(times_01.ut1_strftime("%H:%M"), format="%H:%M"),
            "time_02": pd.to_datetime(times_02.ut1_strftime("%H:%M"), format="%H:%M"),
        },
        index=times_02.ut1,
    )
    
    return df


def view_shadow_length(df):
    """Visualiza as sombras projetadas em um gráfico."""
    colors = ["orange", "slateblue"]
    formato_hora = mdates.DateFormatter('%H:%M')

    fig, ax = plt.subplots(figsize=(10, 6))
    for prefix in ["01", "02"]:
        idx = int(prefix) - 1
        min_shadow = df[f"shadow_length_{prefix}"].min()
        t_min_shadow = df["time_02"].iloc[df.reset_index()[f"shadow_length_{prefix}"].idxmin()]#.strftime("%H:%M")
        ax.axhline(
            y=min_shadow,
            color=colors[idx],
            linestyle=":",
            label=f"Sombra {prefix}: {min_shadow:.2f} m (min) at {t_min_shadow.strftime("%H:%M")}",
        )
        ax.axvline(
            x=t_min_shadow,
            color=colors[idx],
            linestyle="--",
            label=f"Meio-dia site_{prefix}: {t_min_shadow.strftime("%H:%M")}",
        )
        ax.plot(
        df["time_02"], df[f"shadow_length_{prefix}"].values, label=f"site_{prefix}", color=colors[idx])
        
        if prefix == "02":
            shadow_01 = df[df.time_02.dt.strftime("%H:%M")==t_min_shadow.strftime("%H:%M")]["shadow_length_01"].values
    
    if "shadow_01" in locals():
        ax.axhline(
            y=shadow_01[0],
            color="green",
            linestyle=":",
            label=f"Sombra 1: {shadow_01[0]:.2f} m",
        )
        
    ax.set_xlabel("Time (UT1)")
    ax.set_ylabel("Comprimento da Sombra de um objeto de 10m (m)")
    ax.xaxis.set_major_formatter(formato_hora)
    ax.legend(ncols=2)
    #ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=20, prune="both"))
    plt.xticks(rotation=45)
    plt.show()
    return


def _make_scene(plotter, actors, title, alt, az, position):
    """Create a scene with a light source and a title."""
    sun_color = "lightyellow"  # Using a named color for simplicity
    plotter.add_text(title, position=position, font_size=16, color="maroon")
    sun_color = "lightyellow"  # Using a named color for simplicity
    Sol = pv.Light(
        color=sun_color,
        intensity=0.8,
        # shadow_attenuation=0.5,
        light_type="scenelight",
    )
    plotter.add_mesh(
        actors["object"],
        color="maroon",  # Cor dos edifícios
        smooth_shading=True,  # Suaviza a aparência
        split_sharp_edges=True,  # Melhora bordas afiadas
        ambient=0.2,
        diffuse=0.5,
        specular=0.8,
        specular_power=30,
    )

    plotter.add_mesh(
        actors["floor"],
        ambient=0.2,
        diffuse=0.5,
        specular=0.2,
        color="sienna",
        smooth_shading=True,
    )
    plotter.add_light(Sol)
    Sol.set_direction_angle(alt, az)
    
    # plotter.update()
    return Sol


def view_shadow_3D(site, df, prefix="01", year=-200, object_height=10, p=None):
    sun_color = "lightyellow"  # Using a named color for simplicity
    alt = df[f"alt_{prefix}"].values
    az = df[f"az_{prefix}"].values
    _times = df[f"time_{prefix}"].dt.strftime("%H:%M")

    # Objects
    center = [0, 0, 0]  # Center of the cylinder
    height = 10  # Height of the cylinder
    radius = 1  # Radius of the cylinder
    radius_floor = 5
    direction = [0, 0, 1]  # Direction of the cylinder
    direction_floor = [0, 0, -1]
    height = 10

    object = pv.Polygon(
        center=center, radius=radius, normal=direction, n_sides=6
    ).extrude((0, 0, height), capping=True)
    floor = pv.Cylinder(
        center=center,
        direction=direction_floor,
        radius=radius_floor,
        height=height / 10,
        resolution=100,
    )
    actors = {"object": object, "floor": floor}
    camera = pv.Camera()

    # Antes de criar o plotter, você pode definir:
    pv.global_theme.anti_aliasing = "ssaa"
    pv.global_theme.multi_samples = 16
    pv.global_theme.smooth_shading = True

    if p is None:
        p = pv.Plotter(notebook=True, lighting=None)
    p.renderer.shadow_map_resolution = 2048  #

    # Configurações avançadas de renderização
    p.renderer.use_shadows = True
    p.renderer.use_ssao = True  # Ambient Occlusion
    p.renderer.ssao_radius = 0.5  # Raio do SSAO
    p.renderer.ssao_bias = 0.01  # Viés do SSAO
    p.set_background("sienna", top="skyblue")
    Sol = _make_scene(p, actors, site, alt[0], az[0], "lower_left")
    p.camera = camera
    p.camera_position = "xz"
    p.camera.elevation = 30
    p.camera.azimuth = 90

    def sun(value):
        """Update the light direction based on the slider value."""
        Sol = _make_scene(
            p, actors, site, alt[int(value)], az[int(value)], "lower_left"
        )
        p.enable_shadows()

    slider = p.add_slider_widget(
        sun,
        [0, len(_times) - 1],
        0,
        title="Sol",
        title_opacity=0.8,
        title_color="yellow",
        fmt="%0.f",
        title_height=0.08,
    )
    p.enable_shadows()
    return p
