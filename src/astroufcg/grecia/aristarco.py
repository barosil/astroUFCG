from datetime import datetime
from zoneinfo import ZoneInfo

import astropy.units as u
import exifread
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle
from matplotlib_scalebar.scalebar import ScaleBar
from scipy import optimize
from skimage import exposure, img_as_float
from skimage.draw import polygon_perimeter
from skimage.filters import gaussian, threshold_otsu
from skimage.measure import find_contours, perimeter
from timezonefinder import TimezoneFinder

from src.astroufcg.astronomy import setup

path = "../../../"
setup(path)


#### Processamento de imagem
def read_exif(filename):
    """Lê os metadados EXIF de uma imagem."""
    tags = exifread.process_file(open(filename, "rb"))

    # the following functions will help us get GPS data from the EXIF data if it exists
    def _convert_to_degress(value):
        """
        Helper function to convert the GPS coordinates stored in the EXIF to degress in float format
        :param value:
        :type value: exifread.utils.Ratio
        :rtype: float
        """
        d = float(value.values[0].num) / float(value.values[0].den)
        m = float(value.values[1].num) / float(value.values[1].den)
        s = float(value.values[2].num) / float(value.values[2].den)

        return d + (m / 60.0) + (s / 3600.0)

    def get_exif_location(exif_data):
        """
        Returns the latitude and longitude, if available, from the provided exif_data (obtained through get_exif_data above)
        """
        lat = None
        lon = None

        gps_latitude = exif_data.get("GPS GPSLatitude", None)
        gps_latitude_ref = exif_data.get("GPS GPSLatitudeRef", None)
        gps_longitude = exif_data.get("GPS GPSLongitude", None)
        gps_longitude_ref = exif_data.get("GPS GPSLongitudeRef", None)

        if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
            lat = _convert_to_degress(gps_latitude)
            if gps_latitude_ref.values[0] != "N":
                lat = 0 - lat

            lon = _convert_to_degress(gps_longitude)
            if gps_longitude_ref.values[0] != "E":
                lon = 0 - lon

        return lat, lon

    if "EXIF ExposureTime" in tags:
        exposure_tag = tags["EXIF ExposureTime"]
        exposure_time = exposure_tag.values[0].num / exposure_tag.values[0].den * u.s
    if "Image Artist" in tags:
        author_str = tags["Image Artist"].values

    lat, lon = get_exif_location(tags)
    if (lat is not None) and (lon is not None):
        gps = [lat, lon] * u.deg

    tf = TimezoneFinder()
    tzone = ZoneInfo(tf.timezone_at(lat=lat, lng=lon))

    if "EXIF DateTimeOriginal" in tags:
        datetime_str = tags["EXIF DateTimeOriginal"].values.replace(" ", ":").split(":")
        time = datetime(
            int(datetime_str[0]),
            int(datetime_str[1]),
            int(datetime_str[2]),
            int(datetime_str[3]),
            int(datetime_str[4]),
            int(datetime_str[5]),
            tzinfo=tzone,
        ).astimezone(ZoneInfo("UTC"))
    if "Image Model" in tags:
        camera_model_str = tags["Image Model"].values

    return {
        "exposure_time": exposure_time,
        "author": author_str,
        "lat": lat,
        "lon": lon,
        "time": time,
        "camera_model": camera_model_str,
    }


def get_disk(data, sigma=11, plot=False, ax=None, figsize=(16, 10)):
    """
    Obtém o disco solar a partir dos dados de uma imagem.

    :param data: Dados da imagem.
    :param sigma: Desvio padrão para o filtro gaussiano.
    :param plot: Se True, plota o disco solar.
    :return: Disco solar.
    """
    image = img_as_float(data)

    if image.ndim == 3:
        # Convert to grayscale if the image is RGB
        image = np.mean(image, axis=-1)
    # Histogram Equalize
    img_equalized = exposure.equalize_hist(image)
    # Gaussian Blur
    blurred = gaussian(img_equalized, sigma=sigma)
    # Otsu Thresholding
    mask = threshold_otsu(blurred)
    binary = blurred > mask
    contours = find_contours(binary, 0.5)

    results = []
    for i, contour in enumerate(contours):
        contour_img = np.zeros_like(binary, dtype=bool)
        rr, cc = polygon_perimeter(contour[:, 0], contour[:, 1])
        contour_img[rr, cc] = True

        _center = contour.mean(axis=0)
        _radius = perimeter(contour_img) / (2 * np.pi)
        YY, XX = contour[:, 1], contour[:, 0]
        params, _ = fit_leastsq(
            XX,
            YY,
            circle_model,
            circle_jacobian,
            circle_norm,
            guess=[_radius, _center[1], _center[0]],
        )
        results.append(params)

    if plot:
        circles_patches = [
            Circle((param[1], param[2]), radius=param[0], color="red", fill=False)
            for param in results
        ]
        patches = [
            None,
            circles_patches,
            None,
            None,
            None,
        ]

        ax, fig = plot_images(
            [image, img_equalized, blurred, binary],
            titles=[
                "Original Image",
                "Histogram Equalized",
                "Gaussian Blurred",
                "Binary Mask",
            ],
            patches=patches,
            figsize=figsize,
        )

    return results, ax, fig


def fit_leastsq(x, y, model, jac, norm, guess):
    """
    Ajusta um círculo aos dados usando o método dos mínimos quadrados.

    :param x: Coordenadas x dos pontos.
    :param y: Coordenadas y dos pontos.
    :param guess: Chute inicial para os parâmetros do círculo.
    :return: Parâmetros do círculo ajustado.
    """
    dim = len(guess)
    params = guess
    fit, cov = optimize.leastsq(
        lambda p, x, y, model: norm(p, x, y, model),
        guess,
        Dfun=jac,
        args=(x, y, model),
        col_deriv=True,
    )

    params = fit
    residuals = norm(fit, x, y, model)

    return params, residuals


def circle_model(params, x, y):
    """
    Modelo de círculo para ajuste.

    :param params: Parâmetros do círculo (raio, centro_x, centro_y).
    :param x: Coordenadas x dos pontos.
    :param y: Coordenadas y dos pontos.
    :return: Distância dos pontos ao círculo.
    """
    r, cx, cy = params
    return np.sqrt((x - cx) ** 2 + (y - cy) ** 2)


def circle_jacobian(params, x, y, model):
    """
    Jacobiano do modelo de círculo.

    :param params: Parâmetros do círculo (raio, centro_x, centro_y).
    :param x: Coordenadas x dos pontos.
    :param y: Coordenadas y dos pontos.
    :return: Jacobiano do modelo de círculo.
    """
    r, cx, cy = params
    df = np.empty((len(params), x.size))
    R = model(params, x, y)
    df[0] = (cx - x) / R  # dR/dxc
    df[1] = (cy - y) / R  # dR/dyc
    df[2] = -1 * np.ones_like(R)  # dR/dr
    df = df - df.mean(axis=1)[:, np.newaxis]

    return df


def circle_norm(p, x, y, model):
    """
    Normaliza os resíduos do ajuste.

    :param p: Parâmetros do modelo.
    :param x: Coordenadas x dos pontos.
    :param y: Coordenadas y dos pontos.
    :return: Resíduos normalizados.
    """
    R_1 = model(p, x, y)
    R_2 = R_1 - R_1.mean()
    return R_2


def plot_images(images, titles=None, patches=None, figsize=(16, 10), ax=None):
    """
    Plota uma lista de imagens.

    :param images: Lista de imagens a serem plotadas.
    :param titles: Lista de títulos para as imagens.
    :param figsize: Tamanho da figura.
    """
    n = len(images)
    if ax is None:
        fig, axes = plt.subplots(1, n, figsize=figsize)

    if n == 1:
        axes = [axes]

    for ax, img, title, patch in zip(axes, images, titles, patches):
        if not title:
            title = ""
        ax.imshow(img, cmap="gray")
        scalebar = ScaleBar(
            1,
            units="px",
            dimension="pixel-length",
            length_fraction=0.25,
            location="lower right",
            frameon=False,
        )
        ax.add_artist(scalebar)
        if isinstance(patch, list):
            for p in patch:
                ax.add_patch(p)
        ax.set_title(title)
        ax.axis("off")

    return ax, fig
