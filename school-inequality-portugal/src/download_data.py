"""Download the raw data into data/raw/.

Sources
- ENES 2024: national secondary exam results, one row per exam taken
  (Júri Nacional de Exames / DGE). https://www.dge.mec.pt/relatoriosestatisticas-0
- Infoescolas (Feb 2025 release, school year 2022/23): school and municipality
  indicators for Científico-Humanísticos courses (DGEEC). https://infoescolas.medu.pt/bds.asp
"""
import zipfile
from pathlib import Path

import requests

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"

FILES = {
    "enes2024.zip": "https://www.dge.mec.pt/sites/default/files/JNE/enes2024_imprensa.zip",
    "InfoEscolas2024_Secundario_CH_DadosPorEscola.xlsx":
        "https://infoescolas.medu.pt/docs/2024/InfoEscolas2024_Secundario_CH_DadosPorEscola.xlsx",
    "InfoEscolas2024_Secundario_CH_DadosPorRegiao.xlsx":
        "https://infoescolas.medu.pt/docs/2024/InfoEscolas2024_Secundario_CH_DadosPorRegiao.xlsx",
}


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for name, url in FILES.items():
        target = RAW_DIR / name
        if target.exists():
            print(f"  already there: {name}")
            continue
        print(f"Downloading {name} ...")
        resp = requests.get(url, timeout=120)
        resp.raise_for_status()
        target.write_bytes(resp.content)

    # The ENES zip contains a single Access database (.mdb)
    with zipfile.ZipFile(RAW_DIR / "enes2024.zip") as z:
        z.extractall(RAW_DIR)
        print("  extracted:", ", ".join(z.namelist()))
    print("Done.")


if __name__ == "__main__":
    main()
