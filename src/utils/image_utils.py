import os
from io import BytesIO
from pathlib import Path

import pandas as pd
import requests
from PIL import Image
from rapidfuzz import fuzz, process, utils

# Configuração de diretórios
local_path = Path(__file__).parent
IMG_DIR = local_path / "../../content/00_images/processed"
TMP_DIR = local_path / "../../content/00_images/downloads"
CSV_FILE = local_path / "../../data/misc/imagens.csv"
Path.mkdir(IMG_DIR, exist_ok=True)
Path.mkdir(TMP_DIR, exist_ok=True)

# Formatos e tamanhos disponíveis
FORMATS = {
    "paisagem": (16, 9),
    "retrato": (9, 16),
    "quadrado": (1, 1),
}
SIZES = {
    "grande": 720,
    "medio": 360,
    "thumbnail": 150,
}


def salva_df(df: pd.DataFrame, nome_arquivo: str):
    """
    Salva o DataFrame em um arquivo CSV (append ou cria novo).
    """
    caminho = local_path / "../../data/misc" / nome_arquivo
    if not caminho.is_file():
        df.to_csv(caminho, index=False, encoding="utf-8")
    else:
        df.to_csv(caminho, index=False, mode="a", header=False, encoding="utf-8")
    print(f"[OK] DataFrame salvo em {caminho}")


def contar_imagens_salvas():
    return len([f for f in os.listdir(IMG_DIR) if f.endswith(".jpg")])


def baixar_imagem(url: str) -> Image.Image:
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    return Image.open(BytesIO(response.content)).convert("RGB")


def salvar_original(img: Image.Image, indice: int) -> str:
    nome = f"{indice:04d}.jpg"
    caminho = IMG_DIR / nome
    img.save(caminho)
    return nome


def redimensionar_centralizado(
    img: Image.Image, formato: str, tamanho: str
) -> Image.Image:
    ratio_w, ratio_h = FORMATS[formato]
    altura_final = SIZES[tamanho]
    largura_final = int((ratio_w / ratio_h) * altura_final)

    img_ratio = img.width / img.height
    target_ratio = largura_final / altura_final

    escala = (
        altura_final / img.height
        if img_ratio > target_ratio
        else largura_final / img.width
    )
    novo_tamanho = (int(img.width * escala), int(img.height * escala))
    img = img.resize(novo_tamanho, Image.LANCZOS)

    left = (img.width - largura_final) // 2
    upper = (img.height - altura_final) // 2
    right = left + largura_final
    lower = upper + altura_final

    return img.crop((left, upper, right, lower))


def salvar_versao(img: Image.Image, indice: int, formato: str, tamanho: str) -> str:
    nome_base = f"{indice:04d}_{formato}_{tamanho}.png"
    caminho = IMG_DIR / nome_base
    img.save(caminho, format="PNG")
    return nome_base


def processar_formato(img, contador, formato, tamanho):
    if formato not in FORMATS:
        print(f"[AVISO] Formato inválido: {formato}")
        return None
    if tamanho not in SIZES:
        print(f"[AVISO] Tamanho inválido: {tamanho}")
        return None
    try:
        versao = redimensionar_centralizado(img, formato, tamanho)
        nome_versao = salvar_versao(versao, contador, formato, tamanho)
        return nome_versao
    except Exception as e:
        print(
            f"[ERRO] Falha ao gerar versão {formato}-{tamanho} para imagem {contador}: {e}"
        )
        return None


def processar_imagem(img, id, formatos):
    nomes_versao = []
    for formato in formatos:
        f, t = formato
        nome_versao = processar_formato(img, id, f, t)
        nomes_versao.append(nome_versao or "FALHA")
    return nomes_versao


def processar_csv(entrada_csv: str, data: pd.DataFrame = None):
    # df = pd.read_csv(entrada_csv, dtype="str")

    # Carrega CSV já salvo
    caminho_csv = local_path / "../../data/misc" / CSV_FILE
    if caminho_csv.exists():
        df_existente = pd.read_csv(caminho_csv, dtype="str")
        df_existente["id"] = df_existente["id"].astype("Int64")
        id_atual = df_existente["id"].max()
        # Remove registros já existentes
        combinacoes_existentes = set(
            zip(df_existente["url"], df_existente["formato"], df_existente["tamanho"])
        )
        df = df_existente[
            ~df_existente[["url", "formato", "tamanho"]]
            .apply(tuple, axis=1)
            .isin(combinacoes_existentes)
        ].reset_index(drop=True)
    else:
        df = pd.DataFrame()
        id_atual = 0

    # Adiciona dados extras se houver
    if data is not None:
        df = pd.concat([df, data], ignore_index=True)

    df = df.drop_duplicates(
        subset=["url", "formato", "tamanho"], keep="last"
    ).reset_index(drop=True)

    # Garante campos obrigatórios
    if "id" not in df.columns or df["id"].isnull().all():
        novos_ids = range(id_atual + 1, id_atual + 1 + len(df))
        df["id"] = pd.Series(novos_ids, dtype="Int64")
    else:
        for i in df.index:
            if pd.isna(df.loc[i, "id"]):
                id_atual += 1
                df.loc[i, "id"] = id_atual
        df["id"] = df["id"].astype("Int64")

    if "processado" not in df.columns:
        df["processado"] = "NÃO"

    columns = [
        "id",
        "label",
        "nome_original",
        "url",
        "timestamp",
        "descricao",
        "nome_versao",
        "formato",
        "tamanho",
        "processado",
    ]

    registros = []
    for _, row in df.iterrows():
        if row["processado"] == "SIM":
            print(f"[AVISO] Imagem {row['id']} já processada, pulando...")
            continue

        try:
            img = baixar_imagem(row["url"])
        except Exception as e:
            print(f"[ERRO] Falha ao baixar imagem {row['url']}: {e}")
            continue

        row["nome_original"] = salvar_original(img, int(row["id"]))
        row["timestamp"] = pd.Timestamp.now().strftime("%Y-%m-%d")
        formatos = row.get("formato", "paisagem").split("|")
        tamanhos = row.get("tamanho", "grande").split("|")
        combinacoes = [[f, t] for f in formatos for t in tamanhos]
        nomes_versao = processar_imagem(img, int(row["id"]), combinacoes)

        for i, nome_versao in enumerate(nomes_versao):
            nova = row.copy()
            nova["nome_versao"] = nome_versao
            nova["formato"] = combinacoes[i][0]
            nova["tamanho"] = combinacoes[i][1]
            nova["processado"] = "SIM" if nome_versao != "FALHA" else "NÃO"
            registros.append(nova)

    if registros:
        _tmp = pd.DataFrame(registros, columns=columns)
        salva_df(_tmp, CSV_FILE)
        print(f"[OK] {len(registros)} registros adicionados ao {CSV_FILE}")
    else:
        print("[INFO] Nenhuma nova imagem processada.")


def get_image(
    file=CSV_FILE, query=None, formato=None, tamanho=None, inplace=False, threshold=90
):
    """
    Função para obter uma imagem a partir de um arquivo CSV.

    Args:
        file (str): Caminho do arquivo CSV contendo as informações das imagens.

    Returns:
        pd.DataFrame: DataFrame contendo as informações das imagens processadas.
    """
    df = pd.read_csv(file)
    if formato is not None:
        df = df[df["formato"] == formato]
    if tamanho is not None:
        df = df[df["tamanho"] == tamanho]
    df = df[df.processado == "SIM"]
    df.label.str.normalize("NFKD").str.encode("ascii", errors="ignore").str.decode(
        "utf-8"
    )
    df.descricao.str.normalize("NFKD").str.encode("ascii", errors="ignore").str.decode(
        "utf-8"
    )
    LABELS = df.label.unique().tolist()
    DESCRICOES = df.descricao.unique().tolist()

    matches_label = (
        process.extract(
            query,
            LABELS,
            scorer=fuzz.WRatio,
            limit=2,
            processor=utils.default_process,
        )
        if query
        else []
    )
    matches_descricao = (
        process.extract(
            query,
            DESCRICOES,
            scorer=fuzz.WRatio,
            limit=2,
            processor=utils.default_process,
        )
        if query
        else []
    )
    matches_label_idx = [match[2] for match in matches_label if match[1] >= threshold]
    matches_descricao_idx = [
        match[2] for match in matches_descricao if match[1] >= threshold
    ]
    matches = list(set(matches_label_idx + matches_descricao_idx))
    result = df.iloc[matches] if matches else pd.DataFrame()
    if not matches:
        # print(f"[AVISO] Nenhuma correspondência encontrada para a consulta: {query}")
        return None

    if inplace:
        return result.label.iloc[0], result.nome_versao.tolist()[
            0
        ] if not result.empty else None
    else:
        return result


# Execução principal
if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Uso: python processador_imagens.py entrada.csv")
        sys.exit(1)

    entrada = sys.argv[1]
    if not os.path.exists(entrada):
        print(f"Arquivo não encontrado: {entrada}")
        sys.exit(1)

    processar_csv(entrada)
