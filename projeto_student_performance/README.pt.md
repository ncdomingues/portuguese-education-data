[English](README.md) | **Português**

# Desempenho de Alunos do Secundário

Análise exploratória e modelo preditivo da nota final de alunos de duas escolas secundárias portuguesas.

**Dados:** [UCI Student Performance](https://archive.ics.uci.edu/dataset/320), de Cortez & Silva (2008). São 649 alunos (Português) e 395 alunos (Matemática).

> O notebook e o código estão em inglês, para chegar a um público mais alargado.

## Pergunta
Que fatores estão associados à nota final (`G3`, 0–20)? E conseguimos identificar alunos em risco **no início do ano**, antes de haver notas?

## Principais resultados (Português)
- As **reprovações anteriores** são o fator de contexto mais forte (r ≈ −0,39). A nota média passa de 12,5 (sem reprovações) para cerca de 8,5.
- Há **15 alunos com nota final 0**. O padrão sugere abandono a meio do ano: tiveram nota no 1.º período, mas zero faltas registadas.
- O **apoio educativo** aparece associado a notas *mais baixas*. É um caso claro de causalidade inversa: o apoio é dado a quem já tem dificuldades.
- Validação cruzada com 5 folds:

| Cenário | Modelo | MAE | R² |
|---|---|---|---|
| Alerta precoce (sem G1/G2) | Baseline (média) | 2,41 | 0,00 |
| | Ridge | 1,98 | 0,26 |
| | Random Forest | 1,99 | 0,29 |
| Meio do ano (com G1/G2) | Random Forest | 0,80 | 0,85 |

![Importância das variáveis](figures/05_feature_importance.png)

## Análise aprofundada (notebook 02)
- **Classificador de alerta precoce:** para apanhar 80% dos alunos que reprovam é preciso sinalizar cerca de um terço da turma, e cerca de 1 em cada 3 sinalizados reprova de facto. O limiar de alerta importa mais do que o algoritmo.
- **As notas 0 são abandonos:** nas duas disciplinas, todos os alunos com G3 = 0 têm zero faltas registadas. Retirá-los reduz para metade o erro a meio do ano em Matemática.
- **Matemática vs Português:** a taxa de reprovação duplica em Matemática (33% contra 15%). Nos 382 alunos presentes nos dois ficheiros, as notas têm uma correlação apenas moderada (r ≈ 0,48) e **a diferença entre sexos inverte-se**: as raparigas saem-se melhor a Português e os rapazes a Matemática.
- **Gradient boosting + SHAP:** não há ganho face ao random forest com 649 alunos. O SHAP mostra que as previsões dependem sobretudo da escola, das reprovações anteriores e da intenção de ir para o superior.

![SHAP](figures/11_shap_beeswarm.png)

## Dashboard interativo
```bash
streamlit run app/app.py
```
Visão geral, explorador de fatores e uma calculadora de risco para as duas disciplinas.

## Estrutura
```
data/raw/        dados originais (gerados pelo script de download)
notebooks/       01_eda_and_baseline.ipynb, 02_deeper_analysis.ipynb
app/             app.py (dashboard Streamlit)
src/             download_data.py
figures/         gráficos exportados pelo notebook
```

## Como correr
```bash
pip install -r requirements.txt
python src/download_data.py
jupyter notebook notebooks/01_eda_and_baseline.ipynb
```

## Referência
Cortez, P. & Silva, A. (2008). *Using Data Mining to Predict Secondary School Student Performance.* Proceedings of the 5th FUture BUsiness TEChnology Conference (FUBUTEC 2008), pp. 5–12.
