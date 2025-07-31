import sys

import requests
from tqdm import tqdm

sys.path.append("../")

from pathlib import Path

import astropy.constants as const
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import specutils
import stsynphot as stsyn
import synphot
from astropy import units as u
from astropy.io import fits
from astropy.modeling import custom_model, fitting
from astropy.visualization import quantity_support
from IPython.display import Markdown, display
from scipy.interpolate import interp1d
from specutils import Spectrum1D
from specutils.manipulation import extract_region
from synphot import Observation, SourceSpectrum
from synphot.models import BlackBodyNorm1D

quantity_support()

spectral_units = {"Wavelength": u.nm, "Flux": u.Unit("W.m^(-2).nm^(-1)")}

scale = u.kpc.to(u.au) ** 2  # Normalizando espectro de corpo negro para 1 R_sun - 1 AU

# Propriedades do Sol
m_sun = const.M_sun
r_sun = const.R_sun
l_sun = const.L_sun

visible_range = [380, 780] * u.nm

Filters = {
    "U": {
        "name": "johnson,u",
        "color": "#8000FF",
    },
    "B": {
        "name": "johnson,b",
        "color": "#0000FF",
    },
    "V": {
        "name": "johnson,v",
        "color": "#A0FF00",
    },
    "R": {
        "name": "cousins,r",
        "color": "#FF0000",
    },
    "I": {
        "name": "cousins,i",
        "color": "#800000",
    },
}


def download_file(url, path):
    # Verifica se o arquivo já existe
    if Path(path).is_file():
        print(f"O arquivo {Path(path).name} já existe em {Path(path).parent}.")
        return

    # Faz a requisição para a URL
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get("content-length", 0))

    # Verifica se a requisição foi bem sucedida
    if response.status_code != 200:
        print(f"Erro ao acessar a URL: {response.status_code}")
        return

    # Cria a barra de progresso
    progress_bar = tqdm(
        total=total_size, unit="B", unit_scale=True, desc=Path(path).name
    )

    # Faz o download e salva o arquivo
    with Path.open(path, "xb") as file:
        for data in response.iter_content(chunk_size=1024):
            progress_bar.update(len(data))
            file.write(data)

    progress_bar.close()

    if total_size != 0 and progress_bar.n != total_size:
        print("Erro: O download não foi completado.")
    else:
        print(f"Download concluído: {path}")


def load_lines(file_path, n_lines=100, wv_range=(0, 2000), min_width=0.5):
    lines = pd.read_csv(
        file_path,
        header=None,
        compression="gzip",
        encoding="latin1",
        sep=r"\s+",
        on_bad_lines="skip",
    )
    # Seleciona nassa molecular, lambda, intensidade e largura
    lines = lines.iloc[:, [0, 1, 2, 4]]
    lines.columns = ["MMol", "Lambda", "Strength", "width"]

    lines.Lambda = 1e7 / lines.Lambda  # conterve cm^-1 para nm
    lines.width = 1e7 / lines.Lambda  # conterve cm^-1 para nm
    lines = (
        lines[
            (lines.Lambda > wv_range[0])
            & (lines.Lambda <= wv_range[0])
            & (lines.width >= min_width)
        ]
        .sort_values(by="Strength", ascending=False)
        .iloc[:n_lines, :]
    )
    return lines


def _load_spectra(filenames):
    # Carregando dados
    # Carrega espectro solar de referência
    with fits.open(filenames[0]) as hdul:
        data_HST = hdul[1].data  # Extract spectrum data
    wave = data_HST["Wavelength"].byteswap()
    wave = wave.view(wave.dtype.newbyteorder("<"))  # Convert to little-endian
    flux = data_HST["Flux"].byteswap()
    flux = flux.view(flux.dtype.newbyteorder("<"))  # Convert to little-endian
    spec_HST_df = pd.DataFrame({"Wavelength": wave, "Flux": flux})
    HST_units = [u.AA, u.Unit("erg cm-2 s-1 AA-1")]
    # Carrega espectro solar de alta resolução
    spec_HR_df = pd.read_table(
        filenames[2], header=None, comment=";", sep=r"\s+", encoding="latin1"
    )
    spec_HR_df.columns = ["Wavelength", "Flux"]
    HR_units = list(spectral_units.values())
    result = {"HST": (spec_HST_df, HST_units), "HR": (spec_HR_df, HR_units)}
    print("=========================================")
    print("Datasets carregados em pandas dataframes.")
    print("=========================================")
    return result


def show_spectra_units(specs):
    table_md = "### Espectros Gerados\n\n"
    table_md += '<table style="border-collapse: collapse; width: 100%;">\n'
    table_md += "  <tr style='background-color: #222222; color: white;'>\n"
    table_md += "    <th>Dataset</th><th>specutils Units</th><th>synphot Units</th>\n"
    table_md += "  </tr>\n"

    colors = ["#f0f0f0", "#d9edf7"]  # Alternância de cores (cinza claro e azul claro)
    colors = ["goldenrod", "slateblue"]
    for i, (key, values) in enumerate(specs.items()):
        row_color = colors[i % 2]  # Alterna entre as cores

        try:
            specutils_units = (
                f"{values['specutils'].spectral_axis.unit}"
                r"   X   "
                f"{values['specutils'].flux.unit}"
            )
        except AttributeError:
            specutils_units = "$$\\text{Unknown}$$"

        try:
            synphot_units = (
                f"{values['synphot'].waveset.unit}"
                r"   X   "
                f"{synphot.units.PHOTLAM.decompose()}"
            )
        except AttributeError:
            synphot_units = "$$\\text{Unknown}$$"

        table_md += f"  <tr style='color: {row_color};'>\n"
        table_md += (
            f"    <td>{key}</td><td>{specutils_units}</td><td>{synphot_units}</td>\n"
        )
        table_md += "  </tr>\n"

    table_md += "</table>\n"
    display(Markdown(table_md))


def generate_spectra(filenames):
    spec_data = _load_spectra(filenames)
    specs = {}
    for key, (data, units) in spec_data.items():
        spec = Spectrum1D(
            spectral_axis=data["Wavelength"].values * units[0],
            flux=data["Flux"].values * units[1],
        )
        if units != spectral_units.values():
            spec = spec.with_spectral_axis_and_flux_units(
                spectral_units["Wavelength"], spectral_units["Flux"]
            )
        spec_syn = SourceSpectrum.from_spectrum1d(spec)
        specs[key] = {"specutils": spec, "synphot": spec_syn}
    print
    return specs


def extract_spectra(specs, wv_range):
    l_min, l_max = wv_range
    region = specutils.SpectralRegion(l_min, l_max)
    result = {}
    for key, data in specs.items():
        spec = data["specutils"]
        spec = extract_region(spec, region)
        spec_syn = SourceSpectrum.from_spectrum1d(spec)
        result[key] = {"specutils": spec, "synphot": spec_syn}
    return result


@custom_model
def bb_scaled(wave, Temperature=5700, scale=1.0):
    bb_model = BlackBodyNorm1D(temperature=Temperature)(wave)
    return scale * bb_model


def fit_blackbody(spec, T0, scale=1.0):
    if isinstance(spec, specutils.spectra.Spectrum):
        spec = SourceSpectrum.from_spectrum1d(spec)

    wave = spec.waveset
    flux = spec(wave)
    result = {}

    # Set temperature as a free parameter
    bb_scaled.Temperature.fixed = False  # Allow temperature to vary
    bb_scaled.scale.fixed = True  # Fix the scale parameter

    bb_model = bb_scaled(Temperature=T0, scale=scale)

    # Define the fitter
    fitter = fitting.TRFLSQFitter()

    # Fit the model
    model_fit = fitter(bb_model, wave.value, flux.value)

    T_bb = int(model_fit.Temperature.value)

    spec_bb = Spectrum1D(
        spectral_axis=wave, flux=model_fit(wave.value) * synphot.units.PHOTLAM
    ).with_spectral_axis_and_flux_units(*spectral_units.values())
    spec_bb_syn = SourceSpectrum.from_spectrum1d(spec_bb)
    scale_SUN = pow(r_sun / u.au, 2).decompose()

    T_eff = int(
        (
            (
                spec.integrate(flux_unit=synphot.units.FLAM).si
                / const.sigma_sb
                / scale_SUN
            )
            ** (1 / 4)
        ).value
    )

    spec_bb_eff = Spectrum1D(
        spectral_axis=wave,
        flux=bb_scaled(Temperature=T_eff, scale=scale)(wave.value)
        * synphot.units.PHOTLAM,
    ).with_spectral_axis_and_flux_units(*spectral_units.values())
    spec_bb_eff_syn = SourceSpectrum.from_spectrum1d(spec_bb_eff)
    result["Temperatures"] = {"Ajuste": T_bb, "Efetiva": T_eff}
    result["Spectra"] = {
        "Ajuste": {"specutils": spec_bb, "synphot": spec_bb_syn},
        "Efetiva": {"specutils": spec_bb_eff, "synphot": spec_bb_eff_syn},
    }
    return result


def blackbody(T, wave):
    if not hasattr(wave, "unit"):
        wave = wave * spectral_units["Wavelength"]
    elif wave.unit != spectral_units["Wavelength"]:
        wave = wave.to(spectral_units["Wavelength"])
    if hasattr(T, "unit"):
        if T.unit != u.K:
            T = T.to(u.K)
        T = T.value
    wave2bb = wave.to(u.AA)
    spec = Spectrum1D(
        spectral_axis=wave2bb,
        flux=bb_scaled(Temperature=T, Scale=scale)(wave2bb) * synphot.units.PHOTLAM,
    ).with_spectral_axis_and_flux_units(*spectral_units.values())
    return spec


def make_observations(specs, filters=None):
    if filters is None:
        filters = get_filters()
    result = {}
    for key, data in specs.items():
        spec_syn = data["synphot"]
        obs = {}
        for filter_name, filter_data in filters.items():
            obs[filter_name] = Observation(
                spec_syn, filter_data["response"], binset=filter_data["wavelength"]
            )
        result[key] = obs
    return result


def get_filters(filters=None):
    if filters is None:
        filters = Filters
    result = {}
    for filter_name, filter_data in filters.items():
        filter = stsyn.band(filter_data["name"])
        wavelength = filter.waveset
        result[filter_name] = {
            "wavelength": wavelength,
            "response": filter,
            "color": filter_data["color"],
        }
    return result


def plot_filters(filters=None, ax=None):
    if filters is None:
        filters = Filters
    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=(12, 6))
    for filter_name, filter_data in filters.items():
        if filter_data["wavelength"].unit != spectral_units["Wavelength"]:
            filter_data["wavelength"] = filter_data["wavelength"].to(
                spectral_units["Wavelength"]
            )
        ax.plot(
            filter_data["wavelength"],
            filter_data["response"](filter_data["wavelength"]),
            label=filter_name,
            color=filter_data["color"],
            drawstyle="steps-mid",
        )
        ax.fill_between(
            filter_data["wavelength"],
            filter_data["response"](filter_data["wavelength"]),
            color=filter_data["color"],
            alpha=0.3,
        )
    ax.axvline(visible_range[0], color="violet", linestyle="--")
    ax.axvline(visible_range[1], color="red", linestyle="--")
    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel("Transmission")
    ax.legend()
    return ax


def plot_spectra(specs, range=None, ax=None):
    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=(12, 6))
    for key, spec in specs.items():
        if isinstance(spec, dict):
            spec = spec["specutils"]
            ax.plot(spec.spectral_axis, spec.flux, label=key, alpha=0.5, linewidth=4)
    ax.axvline(visible_range[0], color="violet", linestyle="--")
    ax.axvline(visible_range[1], color="red", linestyle="--")
    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel(f"Flux {spec.flux.unit}")
    if range is not None:
        ax.set_xlim(range)
    ax.legend()
    return ax


def plot_observations(observations, range=None, ax=None):
    total_wavelength = None
    total_flux = None
    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=(12, 6))

    waves = []
    fluxes = []
    keys = list(observations.keys())
    for key, obs in observations.items():
        if obs.binset.unit != spectral_units["Wavelength"]:
            binset = obs.binset.to(spectral_units["Wavelength"])
        else:
            binset = obs.binset
        waves.append(binset.value)
        fluxes.append(obs.binflux.value)

    lambda_min = min(np.hstack(waves))
    lambda_max = max(np.hstack(waves))
    delta = np.diff(np.hstack(waves)).max()
    total_wavelength = np.arange(lambda_min, lambda_max, delta)
    total_flux = np.zeros_like(total_wavelength)

    for key, wave, flux in zip(keys, waves, fluxes):
        # Interpolar para somar corretamente os fluxos em uma grade comum
        interp_flux = interp1d(wave, flux, bounds_error=False, fill_value=0)
        common_flux = interp_flux(total_wavelength)

        total_flux += common_flux  # Somar fluxos interpolados
        # Plotar cada resposta espectral
        ax.plot(
            wave,
            flux,
            label=key,
            alpha=0.5,
            linewidth=1,
            drawstyle="steps-mid",
            color=Filters[key]["color"],
        )
        ax.fill_between(wave, flux, color=Filters[key]["color"], alpha=0.3)

    # Plotar a soma total com destaque (preto e linha grossa)
    ax.plot(
        total_wavelength,
        total_flux,
        label="Total",
        color="black",
        linestyle="dotted",
        linewidth=2,
    )

    ax.axvline(visible_range[0], color="violet", linestyle="--")
    ax.axvline(visible_range[1], color="red", linestyle="--")
    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel("Flux")
    if range is not None:
        ax.set_xlim(range)
    ax.legend()
    return ax
