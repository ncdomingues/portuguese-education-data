**English** | [Português](README.pt.md)

# Portuguese Education Data

Data science projects on student performance and school inequality in Portuguese secondary schools.

| Project | Question | Data |
|---|---|---|
| [Student performance](projeto_student_performance/README.md) | What predicts a student's final grade, and can we flag students at risk at the start of the year? | UCI Student Performance: 649 students, two schools, 2005/06 |
| [School inequality](school-inequality-portugal/README.md) | How much of a school's exam result comes from its students' background? Do the 2005/06 findings still hold? | ENES 2024 (311,909 national exams) + Infoescolas school context |

**Plain-language summary:** [open the live dashboard](https://ncdomingues.github.io/portuguese-education-data/results-at-a-glance.html) ([source](results-at-a-glance.html)). It is a one-page dashboard of the main findings for non-technical readers, in English and Portuguese.

## Highlights
- Repeating a year is the clearest warning sign, in 2005/06 and in 2024.
- An early-warning model built only on start-of-year information catches 8 in 10 students who go on to fail.
- Student background explains about 58% of the differences in exam results between schools. Private schools' raw lead shrinks by about 90% once intake is accounted for.
- Doing well in exams and getting students to finish on time are unrelated, so "best school" depends on the measure.

## Tools
Python, pandas, scikit-learn, SHAP, matplotlib/seaborn, Streamlit, Jupyter.

Each project has its own README with setup steps. Raw data is not stored in the repository; each project includes a script that downloads it from the official source.
