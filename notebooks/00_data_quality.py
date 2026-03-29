# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.18.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Data Quality Assessment
#
# ## Objective
# This notebook focuses on assessing data quality before further analysis and modeling.
#
# The workflow follows a structured approach:
# 1. Inspect data quality for each feature
# 2. Identify missing values, anomalies, and inconsistencies
# 3. Apply necessary cleaning strategies
# 4. Prepare reliable data for downstream EDA and modeling
#
# Note:
# - Cleaning is performed incrementally, prioritizing critical features
# - Additional cleaning may be applied during later analysis stages if needed

# %% [markdown]
# ## Data Loading
#
# Load raw datasets and define project directory structure.

# %%
import pandas as pd
import os
import numpy as np
from pathlib import Path
try:
    ROOT = Path(__file__).resolve().parent
except NameError:
    ROOT = Path(os.getcwd()).resolve().parent
Data=ROOT/"data"
Raw=Data/"raw"
Processed=Data/"processed"
External=Data/"external"
Feature=Data/"feature"

df_holidays_events=pd.read_csv(Raw/"holidays_events.csv")
df_oil=pd.read_csv(Raw/"oil.csv")
df_stores=pd.read_csv(Raw/"stores.csv")
df_test=pd.read_csv(Raw/"test.csv")
df_train=pd.read_csv(Raw/"train.csv")
df_transactions=pd.read_csv(Raw/"transactions.csv")

# %%
###train.csv
df_train.describe(include='all')

# %% [markdown]
# ## ID Column Validation
#
# Check whether the ID column is consistent and usable.

# %%
is_incremental = (df_train["id"].diff().dropna() == 1).all()
print('id column is incremental:',is_incremental)

# %% [markdown]
# ### Interpretation
#
# The `id` column is a strictly increasing sequence from 0 to 3000887, with no missing values or irregular jumps.
#
# This indicates:
# - It is a system-generated index
# - It does not carry business meaning
# - It should not be used as a predictive feature
#
# Conclusion:
# The `id` column is valid but excluded from modeling.

# %% [markdown]
# ## Date Column Validation
#
# Evaluate completeness and validity of the time dimension.

# %%
is_null=df_train["date"].isnull().sum()
print(is_null)

df_train["date"] = pd.to_datetime(df_train["date"], errors="coerce")
invalid_count = df_train["date"].isna().sum()

print(df_train["date"].min(),"→",df_train["date"].max())

full_range = pd.date_range(df_train["date"].min(), df_train["date"].max())


missing_dates = set(full_range.date) - set(df_train["date"].dt.date)
print("The lost dates are",missing_dates)
print("The number of lost dates is", len(missing_dates))


# %% [markdown]
# ### Interpretation
#
# The `date` column contains no missing values and can be successfully parsed into datetime format.
#
# The dataset spans from [min_date] to [max_date].
#
# A completeness check reveals that December 25th is consistently missing.
#
# This is likely a business-driven absence (e.g., stores closed on holidays), rather than a data quality issue.
#
# Conclusion:
# - No cleaning required
# - Missing dates are treated as valid business gaps


# %% [markdown]
# ### Store_nbr Column Validation
#
# Check the validation and the completeness of the number of stores

# %%
print("missing number",df_train["store_nbr"].isnull().sum())
print("type of data",df_train["store_nbr"].dtype)
print(df_train["store_nbr"].unique())
print("range of data",df_train["store_nbr"].min(),"→",df_train["store_nbr"].max())
full_nbr=df_stores["store_nbr"]
missing_nbr=set(full_nbr)-set(df_train["store_nbr"].unique())
print("missing data",missing_nbr)

# %% [markdown]
# ## Feature: store_nbr
#
# ### Checks
# - Missing values: None
# - Data type: Integer
# - Value range: 1 to 54
# - Unique values: Complete set of store IDs
#
# ### Interpretation
#
# The `store_nbr` column represents store identifiers.
#
# Key observations:
# - No missing values
# - Integer type, suitable for categorical representation
# - Value range matches the full list of stores (1–54)
# - No missing or unexpected store IDs compared to `stores.csv`
#
# This indicates that the store dimension is complete and consistent across datasets.
#
# ### Conclusion
#
# - No cleaning required
# - Can be safely used as a categorical feature in modeling

# %% [markdown]
# ### Family Column Validation
#
# Check the validation and the completeness of the family range

# %%
df_train["family"] = df_train["family"].str.strip()
print("missing number",df_train["family"].isnull().sum())
print(df_train["family"].unique())

# %% [markdown]
# ## Feature: family
#
# ### Checks
# - Missing values: None
# - Data type: String (categorical)
# - Data cleaning applied: Leading/trailing whitespace removed using `.str.strip()`
# - Unique values: Fixed and finite set of product categories
#
# ### Interpretation
#
# The `family` column represents product categories.
#
# Key observations:
# - No missing values after cleaning
# - Values form a well-defined and finite category set
# - No abnormal or unexpected categories detected
# - No duplicate categories caused by formatting issues (e.g., extra spaces)
#
# This indicates that the category dimension is clean, consistent, and reliable.
#
# ### Conclusion
#
# - No further cleaning required
# - Can be safely used as a categorical feature in analysis and modeling

# %% [markdown]
# ### Sales Column Validation
# Assess the numerical feature of sales

# %%
###sales
print("missing number",df_train["sales"].isnull().sum())
print("the number of data<0",(df_train["sales"]<0).sum())
print("type of data",df_train["sales"].dtype)

# %% [markdown]
# ## Feature: sales
#
# ### Checks
# - Missing values: None
# - Negative values: None
# - Data type: Float
#
# ### Interpretation
#
# The `sales` column represents the target variable, indicating daily sales volume.
#
# Key observations:
# - No missing values detected
# - No negative values, which aligns with expected business logic
# - Stored as a continuous numerical variable (`float64`)
#
# Although the data exhibits noticeable fluctuations, this behavior is expected in retail datasets due to:
# - Promotions and discounts
# - Holiday effects
# - Store-specific demand variation
#
# ### Conclusion
#
# - No cleaning required
# - No outlier removal applied at this stage
# - The feature is retained in its original form to preserve underlying patterns for modeling


# %% [markdown]
# ### Onpromotion Column Validation
# Assess the numerical feature of onpromotion

# %%
###onpromotion
print("missing number",df_train["onpromotion"].isnull().sum())
print("the number of data<0",(df_train["onpromotion"]<0).sum())
print("the number of data not integer",(df_train["onpromotion"]%1!=0).sum())
print("the type of number",df_train["onpromotion"].dtype)


# %% [markdown]
# ## Feature: onpromotion
#
# ### Data Integrity Checks
# - Missing values: None
# - Negative values: None
# - Non-integer values: None
# - Data type: Integer
#
# ### Interpretation
#
# The `onpromotion` column represents the number of items (SKUs) on promotion for a given store and product family.
#
# Key observations:
# - No missing values detected
# - No negative values, which aligns with business expectations
# - All values are integers, confirming it is a count-based feature
# - The feature reflects varying levels of promotional intensity across time and stores
#
# ### Conclusion
#
# - No cleaning required
# - No transformation applied at this stage
# - Retained in original form as a meaningful explanatory variable for modeling

# %% [markdown]
# ### Store the clean data to files

# %%
df_train.to_csv(Processed/"train.csv", index=False, encoding="utf-8-sig")


# %% [markdown]
# # Overall Data Usability Assessment
#
# Based on the initial data quality checks, the dataset meets the fundamental requirements for further analysis and modeling in terms of:
# - Structural completeness
# - Feature consistency
# - Value validity
#
# No critical data quality issues requiring immediate cleaning or correction were identified.
#
# Therefore, the dataset is considered **usable** at this stage.
#
# Note:
# This stage focuses on validating the structural and semantic usability of the data rather than exploring trends, distributions, or relationships.
#
# Exploratory Data Analysis (EDA) will be conducted in subsequent steps.

# %% [markdown]
# # Feature Roles and Modeling Context

# %% [markdown]
# ## ID Column
#
# The `id` column is a system-generated unique identifier used for sample tracking.
#
# - It does not contain business-relevant information
# - It is not used as a predictive feature in modeling
#
# Conclusion:
# The `id` column is excluded from modeling.

# %% [markdown]
# ## Core Business Dimensions (4 Features)

# %% [markdown]
# ### 1. Date (`date`)
#
# Represents the temporal dimension of sales activity.
#
# - Captures when each transaction occurs
# - Enables time-based analysis such as seasonality and trends

# %% [markdown]
# ### 2. Product Category (`family`)
#
# Represents the product category to which each item belongs.
#
# - Used to analyze differences in sales patterns across categories
# - Helps capture category-level demand structure

# %% [markdown]
# ### 3. Store Identifier (`store_nbr`)
#
# Represents individual stores.
#
# - Enables store-level analysis
# - Captures spatial and operational differences between stores

# %% [markdown]
# ### 4. Promotion Intensity (`onpromotion`)
#
# Represents the number of items under promotion on a given day.
#
# - Reflects promotional intensity
# - Serves as a key driver of demand variation

# %% [markdown]
# ## Target Variable

# %% [markdown]
# ### Sales (`sales`)
#
# Represents the target variable to be predicted.
#
# - Indicates daily sales volume
# - Serves as the primary output for modeling

# %% [markdown]
# # Initial Structural Hypotheses (To Be Validated in EDA)
#
# Before conducting Exploratory Data Analysis (EDA), we formulate a set of structural hypotheses based on domain understanding and feature semantics.
#
# These hypotheses serve as analytical guidance rather than conclusions, and will be validated in subsequent analysis.

# %% [markdown]
# ## Time Dimension Hypotheses
#
# 1. Sales behavior is likely influenced by temporal factors such as:
#    - Holidays
#    - Day-of-week effects (weekday vs weekend)
#    - Seasonal patterns
#
# 2. Different time periods may correspond to different consumption patterns:
#    - Routine daily consumption vs holiday-driven consumption
#
# These patterns will be explored and validated in EDA.

# %% [markdown]
# ## Product Category Hypotheses
#
# 1. Different product categories may exhibit relatively stable sales patterns aligned with daily consumer needs.
#
# 2. Sales behavior across categories may differ between holiday and non-holiday periods.

# %% [markdown]
# ## Store-Level Variation Hypotheses
#
# 1. Stores may show significant differences in overall sales due to:
#    - Location
#    - Customer base
#    - Operational strategies
#
# 2. Some stores may consistently perform above or below the average level.

# %% [markdown]
# ## Promotion Effect Hypotheses
#
# 1. The number of promoted items may have a positive or nonlinear impact on total sales.
#
# 2. Promotion effects may vary across:
#    - Stores
#    - Product categories
#
# Potential diminishing returns or heterogeneous effects will be examined in later analysis.

# %% [markdown]
# # Scope of Current Stage
#
# This stage focuses on validating whether the dataset is suitable for further analysis and modeling.
#
# Exploration of:
# - Trends
# - Seasonality
# - Feature relationships
# - Hypothesis validation
#
# will be conducted in the subsequent EDA stage.
