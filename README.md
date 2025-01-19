# Polars E-commerce Analysis

An efficient e-commerce data analysis toolkit built with Polars, focusing on performance and scalability.

## 🚀 Features

- Fast data processing with Polars
- Comprehensive KPI calculations including:
  - Revenue analysis
  - Product performance metrics
  - Customer segmentation (RFM analysis)
  - Temporal patterns
- Interactive visualizations using Plotly
- Export to Quarto reports
- CLI interface for easy automation

## 📋 Requirements

- Python ≥ 3.12
- Dependencies:
  - polars ≥ 1.20.0
  - plotly ≥ 5.24.1
  - pandas ≥ 2.2.3
  - duckdb ≥ 1.1.3
  - shiny ≥ 1.2.1
  - click ≥ 8.1.8
  - pyarrow ≥ 19.0.0

## 🛠 Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/polars-ecommerce-analysis.git
cd polars-ecommerce-analysis
```

2. Install dependencies:
```bash
pip install -e .
```

## 📊 Usage

### Command Line Interface

Run a complete analysis with the CLI:

```bash
python -m ecommerce_analysis.cli analyze /path/to/data.csv /path/to/output --template-dir /path/to/templates
```

### Python API

```python
from ecommerce_analysis import (
    load_retail_data,
    clean_retail_data,
    generate_kpi_report
)

# Load and clean data
df = load_retail_data("data/raw/online_retail.csv")
df_clean = clean_retail_data(df)

# Generate complete analysis
report = generate_kpi_report(df_clean)
```

## 📁 Project Structure

```
polars-ecommerce-analysis/
├── src/
│   └── ecommerce_analysis/
│       ├── __init__.py
│       ├── cli.py
│       ├── data_loader.py
│       ├── data_cleaner.py
│       ├── kpi_calculator.py
│       ├── visualizer.py
│       └── quarto_exporter.py
├── templates/
│   └── quarto/
│       └── template.qmd
├── tests/
├── main.py
└── pyproject.toml
```

## 📈 Key Features Explained

### Data Processing

- Efficient data loading with predefined schemas
- Robust date parsing with multiple format support
- Advanced data cleaning with validation checks

### KPI Calculations

- Global business metrics
- Product performance analysis
- RFM customer segmentation
- Temporal pattern analysis

### Visualization

- Interactive dashboards with Plotly
- Three main analysis perspectives:
  - Temporal analysis
  - Product analysis
  - Customer segmentation

### Reporting

- Automated report generation with Quarto
- Customizable templates
- Export in multiple formats (HTML, PDF)

## 🔍 Code Quality

The project uses:
- Ruff for linting
- pytest for testing
- Type hints throughout the codebase

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ✍️ Author

Gaël Penessot
- LinkedIn: [Gaël Penessot](https://www.linkedin.com/in/gael-penessot)
- Author of [**Business Intelligence with Python**](https://amzn.to/42jjs1o)