[English](README.md) | **Português**

# Dados da Educação em Portugal

Projetos de ciência de dados sobre o desempenho dos alunos e a desigualdade entre escolas secundárias portuguesas.

| Projeto | Pergunta | Dados |
|---|---|---|
| [Desempenho dos alunos](projeto_student_performance/README.pt.md) | O que prevê a nota final de um aluno, e conseguimos identificar alunos em risco no início do ano? | UCI Student Performance: 649 alunos, duas escolas, 2005/06 |
| [Desigualdade entre escolas](school-inequality-portugal/README.pt.md) | Quanto do resultado de uma escola nos exames vem do contexto dos seus alunos? As conclusões de 2005/06 ainda se verificam? | ENES 2024 (311 909 exames nacionais) + contexto das escolas do Infoescolas |

**Resumo em linguagem simples:** o [results-at-a-glance.html](results-at-a-glance.html) é um dashboard de uma página com as principais conclusões, para quem não é técnico, em inglês e português.

## Destaques
- Ter reprovado é o sinal de alerta mais claro, em 2005/06 e em 2024.
- Um modelo de alerta precoce, só com a informação do início do ano, apanha 8 em cada 10 alunos que vêm a reprovar.
- O contexto dos alunos explica cerca de 58% das diferenças entre escolas nos exames. A vantagem em bruto dos colégios diminui cerca de 90% quando se tem em conta o perfil dos alunos.
- Ter bons exames e levar os alunos a terminar a tempo não estão relacionados: a "melhor escola" depende da medida.

## Ferramentas
Python, pandas, scikit-learn, SHAP, matplotlib/seaborn, Streamlit, Jupyter.

Cada projeto tem o seu README com os passos para o correr. Os dados originais não estão no repositório; cada projeto tem um script que os descarrega da fonte oficial.
