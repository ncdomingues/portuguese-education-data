"""Download the UCI Student Performance dataset into data/raw/.

Source: Cortez, P. & Silva, A. (2008). Using Data Mining to Predict Secondary
School Student Performance. https://archive.ics.uci.edu/dataset/320
"""
import io
import zipfile
from pathlib import Path

import requests

URL = "https://archive.ics.uci.edu/static/public/320/student+performance.zip"
RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {URL} ...")
    resp = requests.get(URL, timeout=60)
    resp.raise_for_status()

    # The outer zip contains another zip (student.zip) with the CSV files
    with zipfile.ZipFile(io.BytesIO(resp.content)) as outer:
        inner_bytes = outer.read("student.zip")
    with zipfile.ZipFile(io.BytesIO(inner_bytes)) as inner:
        for name in inner.namelist():
            if name.endswith((".csv", ".txt")):
                (RAW_DIR / Path(name).name).write_bytes(inner.read(name))
                print(f"  saved: {Path(name).name}")

    print("Done.")


if __name__ == "__main__":
    main()
