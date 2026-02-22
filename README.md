# 🎓 Data Engineering Labs

Welcome to the repository for the Data Engineering II course. This repository contains two progressive labs focusing on building data pipelines for Market Analysis.

## 📂 Project Structure

### [TP1: Python ETL Pipeline](./TP1)
- **Documentation**: [📄 Read the full TP1 Guide](./TP1/README.md)
- **Objective**: Build a bespoke ETL pipeline using Python (Pandas) and Streamlit.
- **Tech Stack**: Python, Pandas, Streamlit, Plotly.
- **Key Concepts**: Web Scraping, Data Cleaning, Basic Visualization, Pipeline Stress Testing.

### [TP2: Modern Stack with dbt & DuckDB](./TP2)
- **Documentation**: [📄 Read the full TP2 Guide](./TP2/README.md)
- **Objective**: Refactor the pipeline using industry-standard Data Engineering tools.
- **Tech Stack**: dbt (data build tool), DuckDB, SQL, Kimball Modeling.
- **Key Concepts**: ELT, Dimensional Modeling (Snowflake Schema), SCD2, Incremental Loading, Data Testing.

### 📑 Full Report
- **[Rapport_ECC.pdf](./Rapport_ECC.pdf)** — Complete lab report covering both TP1 and TP2 architectures, implementation details, and critical reflections.

## 🚀 Getting Started

1.  **Install Dependencies**:
    The project uses `poetry` for dependency management at the root level.
    ```bash
    poetry install
    ```

2.  **Navigate to a Lab**:
    - For the Python extraction script, go to `TP1/`.
    - For the dbt pipeline and analytical warehouse, go to `TP2/`.

3.  **Activate Environment**:
    ```bash
    poetry shell
    ```

---
## 👥 Authors
*   **BELEMCOABGA Rosteim Falleiz**
*   **MENDY Vincent**
