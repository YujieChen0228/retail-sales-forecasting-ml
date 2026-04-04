# store_sales_analysis

## Executive Summary

This project builds a time series forecasting model for multi-store retail sales using LightGBM.

The model captures sales dynamics primarily through temporal dependencies (lag features) and demand signals (transactions), while incorporating store-level and product-level structural information.

Results show strong performance in normal sales ranges, but systematic underestimation in extreme high-demand scenarios due to long-tail effects and missing demand-triggering features.

Error analysis reveals that prediction limitations stem more from feature representation than model capacity.

Future improvements should focus on capturing demand triggers (e.g., promotions, events) rather than increasing model complexity.
