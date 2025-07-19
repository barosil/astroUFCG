import holoviews as hv
import numpy as np
import pandas as pd
import panel as pn
from bokeh.models import HoverTool
from holoviews.plotting.util import hex2rgb, process_cmap
from PIL import Image

hv.extension("bokeh")
pn.extension()


# Utility functions for color manipulation
def get_luminance(color):
    R, G, B = hex2rgb(color)
    r, g, b = [c / 255 for c in (R, G, B)]
    r_lin = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
    g_lin = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
    b_lin = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
    return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin


def get_contrasting_color(color):
    return "#000000" if get_luminance(color) > 0.5 else "#FFFFFF"


# Function to adjust font size based on text length and available width
def ajustar_tamanho_fonte(largura, texto, max_font="8pt", min_font="4pt"):
    fator = largura / (len(texto) * 0.6) if texto else 1
    _min, _max = int(min_font.replace("pt", "")), int(max_font.replace("pt", ""))
    tamanho = max(min(fator * 6, _max), _min)
    return f"{int(tamanho)}pt"


def build_timeline(
    df: pd.DataFrame,
    image_size: int = 60,
    width: int = 1000,
    entry_height: int = 30,
    max_rows: int = 5,
    max_ticks: int = 12,
    aspect_ratio: float = 9 / 16,
    pad=0.5,
    bgcolor="aliceblue",
):
    # 📊 Configurações iniciais
    df = df.copy()
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

    # 🗓️ Configurações de tempo e posicionamento
    start = df["START"].min()
    end = df["END"].max()
    _span_x = end - start
    tick_interval = max(10, (_span_x // max_ticks // 10) * 10)
    ticks = list(
        range((start // 10) * 10, int(end + tick_interval), int(tick_interval))
    )

    # 🔲 Escalas e tamanhos
    slot_width = tick_interval / 2
    h_offset = tick_interval / 2
    span_x = ticks[-1] - ticks[0] + slot_width + h_offset
    scale_x = width / span_x
    height = width * aspect_ratio
    image_x_scale = aspect_ratio * image_size / scale_x
    v_offset = entry_height + 2 * pad
    pad = entry_height * pad
    image_pad = pad
    scale_y = height / (v_offset + 2 * pad + max_rows * (entry_height + pad))
    span_y = height / scale_y
    image_y_scale = image_size  # / scale_y

    # -------------------------------

    df["END"] = df["END"].fillna(df["START"] + tick_interval / 4)

    df["alpha"] = df["END"].apply(lambda x: 0.2 if pd.isna(x) else 1)

    categorias = sorted(df["CATEGORIA"].unique())
    df["direction"] = df["CATEGORIA"].apply(lambda x: 1 if x == "SOCIEDADE" else -1)

    # 🎨 Cores
    cat_color_dict = dict(zip(categorias, process_cmap("YlOrRd", len(categorias))))
    bar_cmap_list = ["YlOrRd", "YlGnBu", "Purples"]
    entry_cmap_dict = {
        cat: process_cmap(bar_cmap_list[i % len(bar_cmap_list)], max_rows)
        for i, cat in enumerate(categorias)
    }

    def aplicar_cores(grupo):
        cat = grupo.name
        grupo = grupo.reset_index(drop=True)
        grupo["entry_color"] = grupo.index.map(
            lambda i: entry_cmap_dict[cat][i % max_rows]
        )
        grupo["text_color"] = grupo["entry_color"].apply(get_contrasting_color)
        grupo["categoria_color"] = cat_color_dict[cat]
        return grupo

    df = (
        df.groupby("CATEGORIA", group_keys=True)
        .apply(aplicar_cores, include_groups=False)
        .reset_index()
    )

    # Tratando dos dados das categorias
    meta_df = (
        df.groupby(["CATEGORIA", "direction"])
        .agg(size=("NOME", "size"), start_min=("START", "min"))
        .reset_index()
    )
    meta_df["n_rows"] = meta_df["size"].clip(upper=max_rows)
    meta_df["offset_index"] = meta_df.groupby("direction").cumcount() + 1

    meta_df["start_x"] = start - slot_width - h_offset
    meta_df["end_x"] = start - h_offset
    meta_df["start_y"] = +meta_df["direction"] * v_offset + meta_df["direction"] * (
        entry_height + pad
    ) * max_rows * (meta_df["offset_index"] - 1)
    meta_df["end_y"] = (
        meta_df["start_y"] + max_rows * (entry_height + pad) * meta_df["direction"]
    )
    meta_df["categoria_color"] = meta_df["CATEGORIA"].map(cat_color_dict)
    meta_df["text_color"] = meta_df["categoria_color"].apply(get_contrasting_color)

    meta_df["START"] = df["START"]
    meta_df["END"] = df["END"]

    # Definindo as limites do Gráfico
    top = meta_df[meta_df["direction"] == 1]["end_y"].max()
    bottom = meta_df[meta_df["direction"] == -1]["end_y"].min()

    # -------------------------------

    # 🎯 Posicionamento das entradas. Coordenada y é atualizada até max_rows
    def posicionar(grupo):
        cat = grupo.name
        meta = meta_df[meta_df["CATEGORIA"] == cat].iloc[0]
        direction = meta["direction"]
        entry_pad = entry_height + pad
        outputs = []

        # Cada slot armazenará as faixas [x_start, x_end] já ocupadas
        slots = {i: [] for i in range(max_rows)}
        flip = False

        for _, item in grupo.iterrows():
            x_start = item["START"]
            x_end = item["END"]
            allocated = False

            # Tenta dois ciclos de direção (flip=False e flip=True)
            for _ in range(2):
                for slot in range(max_rows):
                    has_overlap = any(
                        not (x_end <= existing[0] or x_start >= existing[1])
                        for existing in slots[slot]
                    )
                    if not has_overlap:
                        mult = -1 if flip else 1
                        y_start = meta["start_y"] + direction * entry_pad * slot * mult
                        y_end = y_start + direction * entry_height

                        outputs.append(
                            {
                                **item.to_dict(),
                                "entry_x_start": x_start,
                                "entry_x_end": x_end,
                                "entry_y_start": y_start,
                                "entry_y_end": y_end,
                            }
                        )

                        # Registra faixa ocupada no slot
                        slots[slot].append([x_start, x_end])
                        allocated = True
                        break
                if allocated:
                    break
                else:
                    flip = not flip  # Tenta com direção invertida

            if not allocated:
                print(f"⚠️ Não foi possível posicionar item: {item['LABEL']}")

        return pd.DataFrame(outputs)

    # Agrupando e posicionando as entradas
    pos_df = (
        df.groupby("CATEGORIA", group_keys=True)
        .apply(posicionar, include_groups=False)
        .reset_index(drop=True)
    )

    pos_df["x_center"] = (
        pos_df["entry_x_start"] + (pos_df["entry_x_end"] - pos_df["entry_x_start"]) / 2
    )
    pos_df["y_image"] = pos_df["direction"].map({1: top, -1: bottom})

    # 🖼️ Construindo os elementos do gráfico
    # Definindo os slots para as categorias
    slots = hv.Rectangles(
        meta_df[["start_x", "start_y", "end_x", "end_y", "categoria_color"]],
        vdims=["categoria_color"],
    ).opts(color="categoria_color", line_color="categoria_color")

    # 🏷️ Adicionando rótulos das categorias
    labels = hv.Overlay(
        [
            hv.Text(
                row.end_x - slot_width / 2,
                row.start_y + row.direction * np.abs(row.end_y - row.start_y) / 2,
                row.CATEGORIA,
            ).opts(
                text_color=row.text_color,
                text_font_size=ajustar_tamanho_fonte(
                    np.abs(row.start_y - row.end_y), row.CATEGORIA
                ),
                angle=90,
                text_align="center",
                text_baseline="middle",
            )
            for _, row in meta_df.iterrows()
        ]
    )

    # 🏷️ Adicionando entradas
    entries = hv.Rectangles(
        pos_df[
            [
                "entry_x_start",
                "entry_y_start",
                "entry_x_end",
                "entry_y_end",
                "DESCRICAO",
                "entry_color",
                "alpha",
            ]
        ],
        vdims=["DESCRICAO", "entry_color", "alpha"],
    ).opts(
        color="entry_color",
        alpha="alpha",
        line_color="entry_color",
        tools=[HoverTool(tooltips=[("Desc:", "@DESCRICAO")])],
    )

    # 🏷️ Adicionando rótulos das entradas
    entries_labels = hv.Overlay(
        [
            hv.Text(
                row.entry_x_start,
                row.entry_y_end + pad if row.direction == 1 else row.entry_y_end - pad,
                row.NOME,
            ).opts(
                text_color="black",
                text_font_size="7pt",
                text_align="left",
                text_baseline="middle",
            )
            for _, row in pos_df.iterrows()
        ]
    )

    pad_image_panel = 0
    # 🖼️ Linhas e marcadores para imagens
    image_lines = hv.Segments(
        [
            (
                row.x_center,
                row.entry_y_end + pad if row.direction == 1 else row.entry_y_end - pad,
                row.x_center,
                top + pad_image_panel
                if row.direction == 1
                else bottom - pad_image_panel,
            )
            for _, row in pos_df.iterrows()
            if pd.notnull(row.get("IMAGEM"))
        ]
    ).opts(color="gray", line_width=1, alpha=0.5)

    # Marcadores para imagens
    image_markers_top = hv.Points(
        [
            (
                row.x_center,
                top if row.direction == 1 else bottom,
            )
            for _, row in pos_df[pos_df.direction == 1].iterrows()
            if pd.notnull(row.get("IMAGEM"))
        ]
    ).opts(marker="v", size=6, color="gray", alpha=0.7)

    image_markers_bottom = hv.Points(
        [
            (
                row.x_center,
                top if row.direction == 1 else bottom,
            )
            for _, row in pos_df[pos_df.direction == -1].iterrows()
            if pd.notnull(row.get("IMAGEM"))
        ]
    ).opts(marker="^", size=6, color="gray", alpha=0.7)

    image_markers = hv.Overlay([image_markers_top, image_markers_bottom])

    # Linhas para entradas sem imagens
    no_image_entries = pos_df[pos_df.IMAGEM.isnull()]
    no_image_lines = hv.Segments(
        [
            (row.entry_x_start, row.entry_y_start, row.entry_x_start, 0)
            for _, row in no_image_entries.iterrows()
        ]
    ).opts(color="gray", line_width=1, alpha=0.5)

    top_line = hv.HLine(top).opts(color="steelblue", line_width=2)
    bottom_line = hv.HLine(bottom).opts(color="steelblue", line_width=2)
    axis_line = hv.HLine(0).opts(color="indigo", line_width=3)

    cat_lines = hv.Overlay(
        [
            hv.HLine(row.start_y).opts(color="steelblue", line_width=1, alpha=0.5)
            for _, row in meta_df.iterrows()
        ]
    )

    tick_lines = hv.Segments([(t, 0, t, v_offset / 3) for t in ticks]).opts(
        color="goldenrod", line_width=1, alpha=0.5
    )

    tick_labels = hv.Overlay(
        [
            hv.Text(t, v_offset * 0.4, str(t)).opts(
                text_align="center",
                text_font_size="7pt",
                text_baseline="bottom",
                text_color="black",
            )
            for t in ticks
        ]
    )

    # 🖼️ Posicionar imagens com margin
    image_panes = []

    for direction in [-1, 1]:
        sub = pos_df[
            (pos_df["direction"] == direction) & (pos_df["IMAGEM"].notnull())
        ].copy()
        sub = sub.sort_values("x_center").reset_index(drop=True)

        placed_points = []

        for i, row in sub.iterrows():
            # Ponto inicial
            point = np.array(
                [
                    row.x_center,
                    row.y_image + direction * (image_y_scale / 2 + image_pad),
                ]
            )

            # Tentativas de reposicionar até não sobrepor
            max_attempts = 4
            attempts = 0
            while attempts < max_attempts:
                too_close = False
                for px, py in placed_points:
                    dx = np.abs(point[0] - px)
                    dy = np.abs(point[1] - py)
                    if dx < 1.1 * image_x_scale and dy < image_x_scale:
                        too_close = True
                        break
                if not too_close:
                    break
                # Deslocar verticalmente
                point[1] += direction * (image_y_scale + image_pad)
                attempts += 1

            if attempts >= max_attempts:
                print(
                    f"⚠️ Imagem {row.IMAGEM} não pôde ser posicionada (linha {direction}) após {max_attempts} tentativas."
                )
                continue

            placed_points.append(point.tolist())
            y_limits = (
                min(placed_points, key=lambda p: p[1])[1] - image_y_scale / 2,
                max(placed_points, key=lambda p: p[1])[1] + image_y_scale / 2,
            )
            image_array = np.array(Image.open(row.IMAGEM))
            x0 = point[0] - image_x_scale / 2
            y0 = min(
                point[1] - direction * image_y_scale / 2,
                point[1] + direction * image_y_scale / 2,
            )
            x1 = point[0] + image_x_scale / 2
            y1 = max(
                point[1] - direction * image_y_scale / 2,
                point[1] + direction * image_y_scale / 2,
            )
            image_panes.append(
                hv.RGB(
                    image_array,
                    bounds=(
                        point[0] - image_x_scale / 2,
                        point[1] - direction * image_y_scale / 2,
                        point[0] + image_x_scale / 2,
                        point[1] + direction * image_y_scale / 2,
                    ),
                )
            )

    plot = hv.Overlay(
        [
            top_line,
            bottom_line,
            cat_lines,
            slots,
            labels,
            entries,
            entries_labels,
            no_image_lines,
            axis_line,
            tick_lines,
            tick_labels,
            image_lines,
            image_markers,
            *image_panes,
        ]
    ).opts(
        width=width,
        height=int(height),
        xaxis=None,
        yaxis=None,
        show_grid=False,
        toolbar=None,
        xlim=(
            start - slot_width - h_offset - tick_interval,
            end + slot_width + h_offset,
        ),
        bgcolor=bgcolor,
    )

    # return pn.Column(pn.pane.HoloViews(plot))
    return plot
