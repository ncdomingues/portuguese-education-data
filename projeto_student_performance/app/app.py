"""Student performance dashboard.

Run from the project folder:
    streamlit run app/app.py
"""
from pathlib import Path

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score, recall_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"
GRADES = ["G1", "G2", "G3"]
TARGET_RECALL = 0.80

st.set_page_config(page_title="Student Performance", page_icon="🎓", layout="wide")


@st.cache_data
def load():
    por = pd.read_csv(RAW / "student-por.csv", sep=";").assign(subject="Portuguese")
    mat = pd.read_csv(RAW / "student-mat.csv", sep=";").assign(subject="Maths")
    return pd.concat([por, mat], ignore_index=True)


@st.cache_resource
def train(subject):
    df = load().query("subject == @subject").drop(columns="subject")
    X, y = df.drop(columns=GRADES), (df["G3"] < 10).astype(int)
    pipe = Pipeline([
        ("prep", ColumnTransformer([
            ("cat", OneHotEncoder(handle_unknown="ignore"), X.select_dtypes("object").columns),
        ], remainder="passthrough")),
        ("model", RandomForestClassifier(n_estimators=500, min_samples_leaf=3,
                                         class_weight="balanced", random_state=42, n_jobs=-1)),
    ])
    # Choose the alert threshold on cross-validated predictions to reach the target recall
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    p = cross_val_predict(pipe, X, y, cv=cv, method="predict_proba")[:, 1]
    thresholds = np.sort(np.unique(p))[::-1]
    threshold = next(t for t in thresholds if recall_score(y, p >= t) >= TARGET_RECALL)
    stats = {"recall": recall_score(y, p >= threshold), "precision": precision_score(y, p >= threshold)}
    return pipe.fit(X, y), X, threshold, stats


data = load()

st.title("🎓 Student Performance in Portuguese Secondary Schools")
st.caption("UCI Student Performance dataset (Cortez & Silva, 2008) · two schools, 2005/06")

subject = st.sidebar.radio("Subject", ["Portuguese", "Maths"])
df = data[data["subject"] == subject]

tab_overview, tab_factors, tab_risk = st.tabs(["Overview", "What matters", "Early-warning calculator"])

# --- Overview ---------------------------------------------------------------
with tab_overview:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Students", len(df))
    c2.metric("Mean final grade", f"{df['G3'].mean():.1f} / 20")
    c3.metric("Fail rate (G3 < 10)", f"{(df['G3'] < 10).mean():.0%}")
    c4.metric("Likely dropouts (G3 = 0)", int((df["G3"] == 0).sum()))

    hist = alt.Chart(df).mark_bar().encode(
        x=alt.X("G3:O", title="Final grade (0–20)"),
        y=alt.Y("count():Q", title="Students"),
        color=alt.condition(alt.datum.G3 >= 10, alt.value("#4c72b0"), alt.value("#c44e52")),
        tooltip=["G3", "count()"],
    ).properties(height=320)
    st.altair_chart(hist, use_container_width=True)
    st.caption("Red bars are failing grades. The spike at 0 is students who most likely dropped out mid-year: "
               "every one of them has zero recorded absences.")

# --- Factors ----------------------------------------------------------------
with tab_factors:
    labels = {
        "failures": "Past class failures", "higher": "Wants higher education", "studytime": "Weekly study time",
        "Medu": "Mother's education", "Fedu": "Father's education", "Dalc": "Weekday alcohol use",
        "Walc": "Weekend alcohol use", "goout": "Going out with friends", "school": "School",
        "sex": "Sex", "address": "Urban / rural", "schoolsup": "Extra school support", "internet": "Internet at home",
    }
    factor = st.selectbox("Factor", list(labels), format_func=labels.get)
    g = df.groupby(factor)["G3"].agg(mean="mean", students="size",
                                      fail_rate=lambda s: (s < 10).mean()).reset_index()
    left, right = st.columns(2)
    left.altair_chart(alt.Chart(g).mark_bar().encode(
        x=alt.X(f"{factor}:O", title=labels[factor]), y=alt.Y("mean:Q", title="Mean final grade"),
        tooltip=[factor, alt.Tooltip("mean:Q", format=".2f"), "students"],
    ).properties(height=300, title="Mean final grade"), use_container_width=True)
    right.altair_chart(alt.Chart(g).mark_bar(color="#c44e52").encode(
        x=alt.X(f"{factor}:O", title=labels[factor]),
        y=alt.Y("fail_rate:Q", title="Fail rate", axis=alt.Axis(format="%")),
        tooltip=[factor, alt.Tooltip("fail_rate:Q", format=".0%"), "students"],
    ).properties(height=300, title="Share of students failing"), use_container_width=True)
    st.caption("Associations, not causes. For example, students with extra school support have lower grades "
               "because support is given to those already struggling.")

# --- Risk calculator --------------------------------------------------------
with tab_risk:
    model, X, threshold, stats = train(subject)
    st.write(
        f"A random forest trained on **background information only** (no term grades), as if used at the start "
        f"of the school year. The alert threshold is set to catch {stats['recall']:.0%} of failing students; "
        f"about {stats['precision']:.0%} of flagged students actually fail."
    )

    # Start from a "typical" student (most common / median values) and let the user change key features
    student = {c: (X[c].mode()[0] if X[c].dtype == object else int(X[c].median())) for c in X.columns}
    a, b, c = st.columns(3)
    student["school"] = a.selectbox("School", ["GP", "MS"])
    student["sex"] = a.selectbox("Sex", ["F", "M"])
    student["age"] = a.slider("Age", 15, 22, 16)
    student["failures"] = b.slider("Past class failures", 0, 3, 0)
    student["higher"] = b.selectbox("Wants higher education", ["yes", "no"])
    student["studytime"] = b.slider("Weekly study time (1: <2h … 4: >10h)", 1, 4, 2)
    student["Medu"] = c.slider("Mother's education (0 none … 4 higher)", 0, 4, int(student["Medu"]))
    student["Dalc"] = c.slider("Weekday alcohol use (1–5)", 1, 5, 1)
    student["absences"] = c.slider("Absences", 0, 30, int(student["absences"]))

    risk = model.predict_proba(pd.DataFrame([student])[X.columns])[0, 1]
    m1, m2 = st.columns([1, 2])
    m1.metric("Model risk score", f"{risk:.0%}")
    if risk >= threshold:
        m2.error(f"⚠️ Flagged for early support (score ≥ {threshold:.0%})")
    else:
        m2.success(f"Not flagged (score < {threshold:.0%})")
    st.caption("The score comes from a model trained with balanced class weights, so it ranks students by risk "
               "rather than giving a calibrated probability. Other features are set to typical values. "
               "Educational demo, not a decision tool.")
