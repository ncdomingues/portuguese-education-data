"""Turn the raw files into tidy tables in data/processed/.

Outputs
- exams_2024.parquet          one row per exam taken in 2024, with labels
- schools_infoescolas.parquet school context indicators (Infoescolas, CH courses)
- municipalities.parquet      municipality context indicators (Infoescolas, CH courses)

The ENES database is a Microsoft Access file. It is read with `access-parser`
(pure Python, works on any OS); this takes about a minute.
"""
from pathlib import Path

import numpy as np
import pandas as pd
from access_parser import AccessParser

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"

INFO_SCHOOLS = RAW / "InfoEscolas2024_Secundario_CH_DadosPorEscola.xlsx"
INFO_REGIONS = RAW / "InfoEscolas2024_Secundario_CH_DadosPorRegiao.xlsx"
YEARS = ["2019/20", "2020/21", "2021/22", "2022/23"]


# ---------------------------------------------------------------------------
# ENES 2024 (exam results)
# ---------------------------------------------------------------------------
def build_exams():
    mdb = next(RAW.glob("enes2024*.mdb"))
    db = AccessParser(str(mdb))
    table = lambda name: pd.DataFrame(db.parse_table(name))

    exams = table("tblHomologa_2024")
    subjects = table("tblExames")[["Exame", "Descr"]].rename(columns={"Descr": "subject"})
    courses = table("tblCursos")[["Curso", "Descr"]].rename(columns={"Descr": "course"})
    schools = table("tblEscolas").rename(columns={"Descr": "school_name"})
    districts = table("tblCodsDistrito").rename(columns={"Descr": "district"})
    municipalities = table("tblCodsConcelho").rename(columns={"Descr": "municipality"})

    schools = (schools
               .merge(districts, on="Distrito", how="left")
               .merge(municipalities, on=["Distrito", "Concelho"], how="left"))
    schools["municipality_code"] = schools["Distrito"] + schools["Concelho"]
    schools = schools[["Escola", "school_name", "district", "municipality", "municipality_code",
                       "Nuts3", "PubPriv", "CodDGEEC"]]

    df = (exams
          .merge(subjects, on="Exame", how="left")
          .merge(courses, on="Curso", how="left")
          .merge(schools, on="Escola", how="left"))

    df = df.rename(columns={
        "Escola": "school_code", "Fase": "phase", "Exame": "exam_code", "Sexo": "sex", "Idade": "age",
        "Curso": "course_code", "CIF": "internal_grade", "Class_Exam": "exam_score", "CFD": "final_grade",
        "ParaAprov": "for_approval", "ParaMelhoria": "for_improvement", "ParaIngresso": "for_admission",
        "Interno": "internal", "SitFreq": "enrolment_status", "PubPriv": "sector", "CodDGEEC": "school_dgeec",
        "Nuts3": "nuts3",
    })
    df["sex"] = df["sex"].str.upper()
    df["sector"] = df["sector"].map({"PUB": "Public", "PRI": "Private"})
    df["phase"] = df["phase"].astype(int)
    for col in ["for_approval", "for_improvement", "for_admission", "internal"]:
        df[col] = df[col].eq("S")
    df["exam_score_20"] = df["exam_score"] / 10  # exams are scored 0–200, internal grades 0–20

    cols = ["school_code", "school_dgeec", "school_name", "sector", "district", "municipality",
            "municipality_code", "nuts3", "phase", "exam_code", "subject", "course_code", "course",
            "sex", "age", "internal_grade", "exam_score", "exam_score_20", "final_grade",
            "for_approval", "for_improvement", "for_admission", "internal", "enrolment_status"]
    return df[cols]


# ---------------------------------------------------------------------------
# Infoescolas (school and municipality context)
# ---------------------------------------------------------------------------
def read_block(path, sheet, first_row, n_fixed, groups, fields):
    """Read an Infoescolas sheet whose columns repeat `fields` once per group (e.g. per school year)."""
    raw = pd.read_excel(path, sheet_name=sheet, header=None)
    body = raw.iloc[first_row:].copy()
    body = body[body[0].notna() & ~body[0].astype(str).str.startswith(("#", "Dados", "TOTAL"))]
    out = body.iloc[:, :n_fixed].copy()
    col = n_fixed
    for g in groups:
        for f in fields:
            out[f"{f}_{g}"] = pd.to_numeric(body.iloc[:, col], errors="coerce")  # '-' and '*' become NaN
            col += 1
    return out


def build_schools():
    cte = read_block(INFO_SCHOOLS, "ConclusãoTempoEsperado", 7, 3, YEARS, ["n", "completion", "expected"])
    cte.columns = ["school_dgeec", "school_name", "municipality"] + list(cte.columns[3:])

    ret = read_block(INFO_SCHOOLS, "Retencao", 7, 3, YEARS, ["ret10", "ret11", "ret12"])
    ret.columns = ["school_dgeec", "school_name", "municipality"] + list(ret.columns[3:])

    size = pd.read_excel(INFO_SCHOOLS, sheet_name="Cursos", header=None).iloc[6:, [0, 8]]
    size.columns = ["school_dgeec", "students_ch"]
    size["students_ch"] = pd.to_numeric(size["students_ch"], errors="coerce")

    df = (cte
          .merge(ret.drop(columns=["school_name", "municipality"]), on="school_dgeec", how="outer")
          .merge(size, on="school_dgeec", how="left"))
    df["school_dgeec"] = df["school_dgeec"].astype(str).str.strip()

    # Pool the last three cohorts (weighted by cohort size) for more stable school-level estimates
    recent = YEARS[1:]
    n = df[[f"n_{y}" for y in recent]]
    for f in ["completion", "expected"]:
        v = df[[f"{f}_{y}" for y in recent]].to_numpy()
        w = np.where(np.isnan(v), 0, n.fillna(0).to_numpy())
        df[f"{f}_pooled"] = np.where(w.sum(1) > 0, np.nansum(v * w, 1) / np.maximum(w.sum(1), 1), np.nan)
    df["n_pooled"] = n.sum(axis=1, min_count=1)
    df["value_added_completion"] = df["completion_pooled"] - df["expected_pooled"]
    return df


def build_municipalities():
    cte = read_block(INFO_REGIONS, "ConclusãoTempoEsperado(CTE)", 7, 3, YEARS[1:], ["n", "completion", "expected"])
    ase = read_block(INFO_REGIONS, "CTEcomASEeEquidade", 7, 3, YEARS[1:],
                     ["n_ase", "completion_ase", "expected_ase", "equity"])
    df = cte.merge(ase.iloc[:, [0] + list(range(3, ase.shape[1]))], on=0)
    df = df.rename(columns={0: "region_code", 1: "region_name", 2: "region_type"})
    df = df[df["region_type"] == "Município"].copy()
    df["municipality_code"] = df["region_code"].str.replace("MUN", "", regex=False)

    # Share of students with School Social Action support (ASE): a socio-economic indicator
    recent = YEARS[1:]
    df["n_total"] = df[[f"n_{y}" for y in recent]].sum(axis=1, min_count=1)
    df["n_ase_total"] = df[[f"n_ase_{y}" for y in recent]].sum(axis=1, min_count=1)
    df["pct_ase"] = df["n_ase_total"] / df["n_total"]
    return df


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    print("Reading ENES 2024 (about a minute) ...")
    exams = build_exams()
    exams.to_parquet(OUT / "exams_2024.parquet", index=False)
    print(f"  exams_2024.parquet: {len(exams):,} rows")

    schools = build_schools()
    schools.to_parquet(OUT / "schools_infoescolas.parquet", index=False)
    print(f"  schools_infoescolas.parquet: {len(schools):,} schools")

    mun = build_municipalities()
    mun.to_parquet(OUT / "municipalities.parquet", index=False)
    print(f"  municipalities.parquet: {len(mun):,} municipalities")


if __name__ == "__main__":
    main()
