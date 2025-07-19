import matplotlib.dates as mdates
import osmnx as ox
import pandas as pd
import pyvista as pv
from matplotlib import pyplot as plt

from astroufcg.astronomy import get_noon_times, obseve_shadow, setup

path = "../../../"
setup(path)


def set_experiment(site_01, site_02, year=2023, object_height=10):
    """Configura o experimento de Eratóstenes para dois locais."""
    location_01 = pd.DataFrame(
        [list(ox.geocode(site_01))], columns=["lat", "lon"]
    ).iloc[0]
    location_02 = pd.DataFrame(
        [list(ox.geocode(site_02))], columns=["lat", "lon"]
    ).iloc[0]

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
    formato_hora = mdates.DateFormatter("%H:%M")

    fig, ax = plt.subplots(figsize=(10, 6))
    for prefix in ["01", "02"]:
        idx = int(prefix) - 1
        min_shadow = df[f"shadow_length_{prefix}"].min()
        t_min_shadow = df["time_02"].iloc[
            df.reset_index()[f"shadow_length_{prefix}"].idxmin()
        ]  # .strftime("%H:%M")
        ax.axhline(
            y=min_shadow,
            color=colors[idx],
            linestyle=":",
            label=f"Sombra {prefix}: {min_shadow:.2f} m (min) at {t_min_shadow.strftime('%H:%M')}",
        )
        ax.axvline(
            x=t_min_shadow,
            color=colors[idx],
            linestyle="--",
            label=f"Meio-dia site_{prefix}: {t_min_shadow.strftime('%H:%M')}",
        )
        ax.plot(
            df["time_02"],
            df[f"shadow_length_{prefix}"].values,
            label=f"site_{prefix}",
            color=colors[idx],
        )

        if prefix == "02":
            shadow_01 = df[
                df.time_02.dt.strftime("%H:%M") == t_min_shadow.strftime("%H:%M")
            ]["shadow_length_01"].values

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
    # ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=20, prune="both"))
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


def animate_shadow_3D(
    site,
    df,
    prefix="01",
    year=-200,
    object_height=10,
    filename="../../../content/00_images/cap_01/shadow.gif",
):
    sun_color = "lightyellow"
    alt = df[f"alt_{prefix}"].values
    az = df[f"az_{prefix}"].values
    _times = df[f"time_{prefix}"].dt.strftime("%H:%M")

    center = [0, 0, 0]
    radius = 1
    radius_floor = 5
    height = object_height
    direction = [0, 0, 1]
    direction_floor = [0, 0, -1]

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

    pv.global_theme.anti_aliasing = "ssaa"
    pv.global_theme.multi_samples = 16
    pv.global_theme.smooth_shading = True

    plotter = pv.Plotter(off_screen=True, lighting=None, window_size=(1280, 720))
    plotter.renderer.shadow_map_resolution = 2048
    plotter.renderer.use_shadows = True
    plotter.renderer.use_ssao = True
    plotter.renderer.ssao_radius = 0.5
    plotter.renderer.ssao_bias = 0.01
    plotter.set_background("sienna", top="skyblue")

    camera = pv.Camera()
    plotter.camera = camera
    plotter.camera_position = "xz"
    plotter.camera.elevation = 30
    plotter.camera.azimuth = 90

    _make_scene(plotter, actors, site, alt[0], az[0], "lower_left")

    plotter.open_movie(filename, framerate=10)

    for i in range(len(_times)):
        _make_scene(plotter, actors, site, alt[i], az[i], "lower_left")
        plotter.write_frame()

    plotter.close()

    print(f"Animação salva em: {filename}")
