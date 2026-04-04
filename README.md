# Store Sales Forecasting — Time Series Modeling with LightGBM

## Executive Summary

This project builds a time series forecasting model for multi-store retail sales using LightGBM.

The model captures sales dynamics primarily through temporal dependencies (lag features) and demand signals (transactions), while incorporating store-level and product-level structural information.

Results show strong performance in normal sales ranges, but systematic underestimation in extreme high-demand scenarios due to long-tail effects and missing demand-triggering features.

Error analysis reveals that prediction limitations stem more from feature representation than model capacity.

---

## Problem Description

The goal is to predict daily sales for multiple stores and product families.

The main challenges include:

- Strong temporal dependency
- Heterogeneity across stores
- Different behavior across product categories
- Long-tail distribution with extreme sales spikes

---

## Data & EDA Highlights

Exploratory analysis reveals a structured system:

- Sales follow strong **weekly patterns**
- Product categories define **composition of demand**
- Stores determine **baseline scale**
- Promotion has **heterogeneous effects**
- Transactions act as a proxy for **customer traffic**

This leads to a conceptual decomposition:

> sales ≈ transactions × basket_size

---

## Feature Engineering

Feature design is guided by system structure rather than brute-force generation.

### Time Features
- dayofweek, month, cyclical encoding (sin/cos)
- captures seasonality and periodic patterns

### Store Features
- store_nbr (categorical)
- store_baseline (expanding mean)
- captures scale differences

### Product Family Features
- family (categorical)
- family_ratio_hist (composition)
- family_baseline / store_baseline
- captures demand structure

### Sales Features (Core)
- lag1, lag7
- rolling mean (7 days)
- diff features

### Promotion Features
- lag, rolling, diff
- captures behavioral effects

### Transactions Features
- lag, rolling, diff
- captures demand (traffic signal)

### Leakage Control
- all features use past information only (shift)
- no current-day aggregation features
- time-based split for validation

---

## Modeling Approach

### Model Choice

LightGBM is selected due to its ability to:

- handle nonlinear relationships
- model feature interactions
- perform well on tabular data

---

### Validation Strategy

A time-based cross-validation strategy is used:

- Expanding training window
- Forward validation splits
- No random shuffling

This simulates real-world forecasting conditions.

---

### Training Setup

- Model: LightGBM
- Learning rate: 0.05
- Estimators: 500
- Leaves: 31
- Early stopping applied

---

### Evaluation Metrics

- RMSE (Root Mean Squared Error)

Evaluation includes:

- Fold-level RMSE
- Out-of-Fold (OOF) RMSE

---

## Results

- Mean CV RMSE: 363.574
- OOF RMSE: 377.4702

The model shows stable performance across time splits.

---

## Feature Importance

Key drivers:

1. **Primary Drivers**
   - sales_lag features
   - transactions features
   - store_nbr

2. **Structural Factors**
   - time features
   - family

3. **Secondary Signals**
   - promotion
   - baseline features

👉 Model structure:

> Sales ≈ temporal dynamics + demand signal + store effect

---

## Residual Analysis

- Model performs well in normal sales range
- Systematic underestimation in high-sales scenarios
- Long-tail distribution leads to large errors

Key observations:

- Errors concentrated in food categories (e.g., GROCERY I)
- Extreme values are not well captured
- Variance increases with sales level (heteroscedasticity)

---

## Error Analysis

Errors can be decomposed into:

### 1. Long-tail Errors
- rare but high impact
- demand spikes

### 2. Systematic Errors
- category-level bias
- persistent underperformance

Certain stores also show consistently higher error.

---

## Modeling Perspective

The model behaves as an implicit hierarchical system:

Store-level  
↓  
Category structure  
↓  
Temporal dynamics (dominant)

---

## Limitations & Future Work

### Limitations

- Cannot capture demand spikes
- Missing promotion intensity features
- Long-tail underestimation

### Future Work

- Add event / holiday-driven features
- Model demand triggers
- Consider segmented models (normal vs high demand)

---

## Project Structure

- notebook: full analysis and modeling
- report:
  1. reports for each section
  2. assets：plots used in the report
- output：notebooks exported as html，easy to read

📌 Full workflow is available in the notebook.
