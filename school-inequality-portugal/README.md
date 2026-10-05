**English** | [Português](README.pt.md)

# School Inequality in Portugal's National Exams (2024)

How much of a school's exam result is explained by its students' background? Which schools do better than expected? And do the findings of a well-known 2005/06 study of two Portuguese schools still hold nationally today?

This project follows up on [student-performance](../projeto_student_performance), which analysed 649 students from two schools in 2005/06.

## Data
| Source | What | Level |
|---|---|---|
| [ENES 2024](https://www.dge.mec.pt/relatoriosestatisticas-0) (Júri Nacional de Exames / DGE) | All 311,909 national secondary exams sat in 2024 | One row per exam |
| [Infoescolas](https://infoescolas.medu.pt/bds.asp) (DGEEC, Feb 2025 release) | Completion rates, retention, and *expected* completion given students' socio-economic profile | School and municipality, 2022/23 |

The two sources are linked through each school's DGEEC code (93% of exam records match).

## Key findings
1. **A school's intake explains ~58% of the variation in its exam results.** Raw school rankings mostly measure who a school enrols.

   ![Context vs results](figures/06_context_vs_results.png)

2. **Private schools' raw advantage (0.45 SD) shrinks to 0.05 SD** once intake is accounted for.
3. **"Good school" depends on the metric.** Value added on exams and value added on on-time completion are unrelated (r = −0.09).

   ![Two value-added measures](figures/08_two_value_added_measures.png)

4. **Inequality is mostly local.** Municipality-level social support (ASE) correlates only weakly with results (r = −0.23). Differences between nearby schools matter more than regional ones.
5. **Then vs now (2005/06 → 2024):**
   - Students who fell behind still do much worse (up to −5 points in Maths A for 19-year-olds).
   - Girls still lead in Portuguese (+0.8).
   - Boys' lead in Maths is gone among exam takers, possibly because of who chooses to sit the exam.
   - Gabriel Pereira is still ahead of Mouzinho da Silveira on exams, but Mouzinho does better on completion relative to its intake.

⚠️ **Main caveat:** in 2024, 98% of exams were taken for university admission, so the exam data describes **applicants**, not all students.

## Project structure
```
src/download_data.py     downloads ENES 2024 and Infoescolas files into data/raw/
src/build_dataset.py     reads the Access database and Excel files, writes tidy parquet files to data/processed/
src/style.py             shared chart style
notebooks/01_exam_results_2024.ipynb    student level: subjects, gender, age, internal vs exam grades, then vs now
notebooks/02_schools_and_context.ipynb  school level: context, value added, municipalities, the two UCI schools
figures/                 exported charts
```

## How to run
```bash
pip install -r requirements.txt
python src/download_data.py
python src/build_dataset.py
jupyter notebook notebooks/
```
`build_dataset.py` reads the Access (.mdb) file with the pure-Python `access-parser`, so it works on Windows, macOS and Linux (about one minute).

## Limitations
- Exam takers in 2024 are self-selected university applicants.
- Infoescolas context refers to 2022/23 cohorts; exams are from 2024.
- The context index is DGEEC's model-based expectation from a few variables (age, ASE support, mother's education, sector), not a full socio-economic measure.
- One year of exam data. School-level value added should be averaged over several years before judging any individual school.
