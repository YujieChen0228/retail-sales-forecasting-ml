# Feature Engineering

We now translate insights from the EDA into model-ready features.

Rather than generating features blindly, the focus is on encoding key structural components of sales:

- Time patterns (trend and seasonality)
- Store-level baseline differences
- Product category structure
- Promotion effects

Conceptually, sales can be viewed as:

    sales ≈ transactions × basket_size

Since transactions are not available for prediction, we aim to capture these effects indirectly through engineered features.

The following sections outline how each component is constructed.

### Time Features

Time is one of the primary drivers of sales, as identified in the EDA.  
In particular, strong weekly and monthly patterns are observed, indicating the presence of both short-term cycles and longer seasonal effects.

To capture these temporal dynamics, the following features are constructed:

- **dayofweek**: captures intra-week patterns (e.g., weekday vs weekend effects)
- **month**: captures broader seasonal trends
- **is_weekend**: explicitly models behavioral shifts on weekends

In addition, cyclical encoding is applied to avoid artificial discontinuities in time representation:

- **sin/cos transformations of dayofweek**
- **sin/cos transformations of month**

This ensures that the model correctly understands the periodic nature of time (e.g., Sunday is close to Monday, December is close to January).

Although holiday effects are not strongly visible at the aggregate level, they may still interact with other factors (such as promotion or product category).  
Therefore, holiday-related features are retained for potential interaction effects.

### Store Features

Stores primarily determine the baseline sales level (scale effect), as observed in the EDA.

To capture this, we construct a **store-level baseline feature** using historical sales:

- **store_baseline**: expanding mean of past sales for each store (with shift to avoid leakage)

This feature represents the expected sales level of a store based on its historical performance, 
while ensuring that only past information is used at each time step.

In addition:

- **store_nbr** is retained as a categorical feature

This allows the model to learn store-specific patterns that are not fully captured by the baseline alone.

Overall, store-related features aim to separate:

- **scale effects** (store baseline)
- **residual patterns** (captured by other features such as time and promotion)

### Product Family Features

Product family represents the **composition of sales**, rather than the overall scale.

As observed in the EDA, different product categories contribute unevenly to total sales, 
and this composition remains relatively stable over time while still exhibiting meaningful variation.

To capture this, we construct the following features:

- **family (categorical)**  
  Allows the model to learn category-specific patterns

- **family_ratio**  
  Share of each product family within a store on a given day

- **family_ratio_hist**  
  Historical (expanding) mean of family_ratio with shift applied  
  → captures stable consumption structure while avoiding leakage

- **family_baseline**  
  Expanding mean of past sales for each (store, family) pair  
  → represents expected sales level for a category within a store

- **family_v_store**  
  Ratio between family_baseline and store_baseline  
  → captures how each category performs relative to the store’s overall level

These features allow the model to separate:

- **what people buy** (category composition)
- **how much they buy** (captured by store baseline and time features)

By combining both absolute (baseline) and relative (ratio) representations, 
we provide a richer description of consumption behavior across stores and categories.

### Lag-Based Sales Features

Sales exhibit strong temporal dependency, making historical values one of the most important predictors.

To capture short-term dynamics and local trends, we construct lag-based features at the (store, family) level:

- **sales_lag1**  
  Previous day's sales  
  → captures immediate temporal dependency

- **sales_lag7**  
  Sales from the same day in the previous week  
  → captures weekly seasonality

- **sales_rolling_mean7**  
  Rolling mean of past 7 days (with shift applied)  
  → provides a smoothed estimate of recent baseline

- **sales_diff_1**  
  First-order difference (with shift applied)  
  → captures short-term trend and change direction

All features are computed using only past information (via shift), ensuring no leakage.

These features allow the model to capture:

- Local continuity (lag features)
- Short-term baseline (rolling statistics)
- Trend dynamics (differences)

### Promotion Features

Promotion is not a static signal, but a dynamic driver of sales behavior.

As observed in the EDA, promotion does not significantly increase transactions (traffic), 
but instead affects purchasing behavior (e.g., basket size), with heterogeneous effects across product families.

To capture its temporal dynamics, we construct lag-based promotion features at the (store, family) level:

- **onpromotion_lag1**  
  Promotion status from the previous day  
  → captures short-term carryover effects

- **onpromotion_lag7**  
  Promotion status from the same day in the previous week  
  → captures recurring promotion patterns

- **onpromotion_rolling_mean7**  
  Rolling mean of promotion intensity over the past 7 days (with shift)  
  → represents recent promotion exposure level

- **onpromotion_diff_1**  
  First-order difference (with shift)  
  → captures changes in promotion intensity

All features are computed using only past information to avoid leakage.

These features allow the model to learn:

- Short-term promotion persistence
- Weekly promotion cycles
- Accumulated promotion exposure
- Changes in promotion intensity

Importantly, promotion effects are expected to interact with product categories, 
which is implicitly handled through the (store, family) grouping.



### Transactions Features

Transactions represent customer traffic and serve as a proxy for external demand.

As identified in the EDA, sales can be interpreted as:

    sales ≈ transactions × basket_size

This makes transactions a key upstream driver of sales, capturing variation in customer volume rather than purchasing behavior.

To model its temporal dynamics, we construct lag-based features at the store level:

- **transactions_lag1**  
  Previous day's transaction count  
  → captures short-term traffic dependency

- **transactions_lag7**  
  Transactions from the same day in the previous week  
  → captures weekly traffic patterns

- **transactions_rolling_mean7**  
  Rolling mean of past 7 days (with shift)  
  → provides a smoothed estimate of recent traffic level

- **transactions_diff_1**  
  First-order difference (with shift)  
  → captures short-term changes in traffic

All features are computed using only past information to avoid leakage.

These features allow the model to capture:

- Traffic persistence (lag features)
- Weekly seasonality (lag7)
- Local baseline of demand (rolling mean)
- Changes in customer flow (difference)

Transactions features complement sales-based features by providing information about demand volume, 
while sales features capture the realized outcome influenced by both traffic and purchasing behavior.

In practical deployment scenarios, transactions may not be directly available at prediction time.  
In this analysis, they are used as auxiliary signals to better understand demand dynamics.

### Final Feature Processing

Before modeling, we perform a final cleanup of the feature set to ensure consistency and avoid data leakage.

- **Missing values** are filled with 0 for simplicity and compatibility with tree-based models

- **Sorting by (date, store, family)** ensures correct temporal order before modeling

- **date** is retained for time-based splitting (train/validation), but is not used directly as a model input

The following variables are removed to prevent leakage or redundancy:

- **onpromotion, transactions**  
  Raw variables are replaced by their lag-based features

- **total_sales, family_ratio**  
  These are constructed using same-day information and would introduce leakage

- **id**  
  Identifier without predictive value

After preprocessing, the dataset contains only model-ready features derived from historical information.

The final feature set is then exported for downstream modeling.