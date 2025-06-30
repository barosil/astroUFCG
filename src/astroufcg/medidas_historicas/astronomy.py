import numpy as np
from skyfield import almanac
from skyfield.api import Loader, wgs84
from jplephem.spk import SPK
from jplephem.daf import DAF
from jplephem.excerpter import write_excerpt

load = Loader('../data/skyfield/')
#eph = load("de431_part-1.bsp")
eph = load("de431_excerpt.bsp")
terra = eph['earth']
sol = eph['sun']
ts = load.timescale()

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
    start_date = ts.utc(start_date).tt
    end_date = ts.utc(end_date).tt
    with open(path, "rb") as file:
    spk = SPK(DAF(file))
    summaries = spk.daf.summaries()
    with open(output_path, 'w+b') as output_file:
            write_excerpt(spk, output_file, start_date,
                        end_date, summaries)
    return

# --- Configurações Skyfield ---
def make_observer(location):    
    
    lat = location["lat"]
    lon = location["lon"]
    local = terra + wgs84.latlon(latitude_degrees=lat, longitude_degrees=lon)
    return local

def find_summer_noon_time(location, year):
    """Encontra o meio-dia solar no solstício de verão para um local e ano."""
    t0 = ts.utc(year, 1, 1)  
    t1 = ts.utc(year, 12, 31)  
    t, y = almanac.find_discrete(t0, t1, almanac.seasons(eph))
    _ss = t[almanac.SEASON_EVENTS.index("Summer Solstice")]
    summer_solstice = _ss.utc[:3]
    observer = make_observer(location)
    
    t0 =   ts.utc(*summer_solstice, 0, 0)  # Meio-dia do solstício de verão
    t1 =   ts.utc(*summer_solstice, 24, 0)  # Meio-dia do solstício de verão
    f_01 = almanac.meridian_transits(eph, sol, observer - terra)
    times, events = almanac.find_discrete(t0, t1, f_01)
    noon = times[events == 1][0]
    return noon

def make_time_vector(center, amplitude, num_points=100, unit="minutes"):
    """Cria um vetor de tempo centrado em 'center' com amplitude 'amplitude'."""
    scales = {
        "minutes": 1 / 1440.0,  # 1 minuto em dias
        "hours": 1 / 24.0,      # 1 hora em dias
        "days": 1.0,             # 1 dia em dias
        "seconds": 1 / 86400.0   # 1 segundo em dias
    }
    range = np.linspace(- amplitude, amplitude, num_points)
    
    time_vector = ts.utc(center.utc.year, center.utc.month, center.utc.day, center.utc.hour, center.utc.minute) + range * scales[unit]
    return time_vector


def solar_alt_az(location, time):
    """Calcula a altitude e o azimute do Sol para um local e instante."""
    sol = eph['sun']
    astrometric = location.at(time).observe(sol).apparent()
    alt, az, _ = astrometric.altaz()
    return alt.degrees, az.degrees


def shadow_length(height, altitude_deg):
    """Calcula o comprimento da sombra projetada de um objeto."""
    return height / np.tan(np.radians(altitude_deg))


def solar_vector(altitude_deg, azimuth_deg):
    """Retorna vetor unitário na direção do Sol."""
    alt_rad = np.radians(altitude_deg)
    az_rad = np.radians(azimuth_deg)
    x = np.cos(alt_rad) * np.sin(az_rad)
    y = np.cos(alt_rad) * np.cos(az_rad)
    z = np.sin(alt_rad)
    return np.array([x, y, z])
