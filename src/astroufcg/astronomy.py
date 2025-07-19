import os
from pathlib import Path

import numpy as np
import pandas as pd
from jplephem.daf import DAF
from jplephem.excerpter import write_excerpt
from jplephem.spk import SPK
from skyfield import almanac
from skyfield.api import load, wgs84


def setup(path, ephem_file="data/skyfield/de431_excerpt.bsp"):
    """
    Configura o ambiente para o experimento de Eratóstenes.

    :param path: Caminho ou URL do arquivo de efeméride.
    :return: Efeméride carregada.
    """

    # ephem_file = "data/skyfield/de431_excerpt.bsp"
    file = Path(path) / ephem_file if not path.startswith("http") else ephem_file
    if not os.path.exists(file):
        raise FileNotFoundError(f"Arquivo de efeméride não encontrado: {file}")
    eph = load(file.as_posix())
    if eph is None:
        raise ValueError("Não foi possível carregar a efeméride.")
    ts = load.timescale()
    terra = eph["earth"]
    sol = eph["sun"]
    lua = eph["moon"]
    globals()["eph"] = eph
    globals()["ts"] = ts
    globals()["terra"] = terra
    globals()["sol"] = sol
    globals()["lua"] = lua


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
