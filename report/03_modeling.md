## Modeling

### Model Choice

Given the tabular nature of the dataset and the presence of complex nonlinear interactions between features (e.g., time, promotion, product category, and store effects), a tree-based gradient boosting model is adopted.

Specifically, **LightGBM** is used due to its:

- Strong performance on structured/tabular data
- Ability to handle heterogeneous features (numerical + categorical)
- Robustness to feature scaling and missing values
- Efficiency in training on large datasets

LightGBM is particularly suitable for this problem, as it can naturally capture:

- Nonlinear relationships
- Feature interactions (e.g., promotion × family, time × store)
- Piecewise patterns in demand dynamics

This makes it well aligned with the structural patterns identified during EDA and feature engineering.