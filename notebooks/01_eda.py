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
#     display_name: project (original)
#     language: python
#     name: original
# ---

# %% [markdown]
# # Exploratory Data Analysis (EDA)
#
# ## 1. Objective
#
# The goal of this stage is to explore the dataset to uncover meaningful patterns, relationships, and potential drivers of sales behavior.
#
# Building on the previous data quality assessment, this phase focuses on understanding:
#
# - How sales vary over time
# - Differences across product categories
# - Store-level variations
# - The impact of promotions on sales
#
# The insights derived from this stage will guide feature engineering and modeling decisions.
#
# ---
#
# ## 2. Scope
#
# This analysis focuses on:
#
# - Temporal patterns (daily, weekly, seasonal effects)
# - Category-level behavior (`family`)
# - Store-level differences (`store_nbr`)
# - Promotion effects (`onpromotion`)
#
# The objective is not to build models yet, but to identify structure and signals within the data.
#
# ---
#
# ## 3. Analytical Approach
#
# The EDA will be conducted through:
#
# - Aggregation and grouping analysis
# - Time-series visualization
# - Distribution analysis
# - Comparative analysis across key dimensions
#
# Special attention will be given to identifying:
#
# - Stable patterns vs irregular fluctuations
# - Systematic differences across groups
# - Potential interactions between features
#
# ---
#
# ## 4. Link to Previous Stage
#
# The dataset has been validated as clean and usable during the data quality assessment stage.
#
# Therefore, no additional preprocessing is performed here, and the analysis is conducted directly on the original dataset.
#
# ---
#
# ## 5. Key Hypotheses
#
# Based on prior structural understanding, we aim to validate the following:
#
# - Sales exhibit strong weekly patterns
# - Product categories have distinct consumption structures
# - Stores differ mainly in scale rather than composition
# - Promotions have heterogeneous effects across categories
#
# These hypotheses will be tested and refined throughout the analysis.

# %%
#read the data
import pandas as pd
import os
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
try:
    ROOT = Path(__file__).resolve().parent
except NameError:
    ROOT = Path(os.getcwd()).resolve().parent 
Data=ROOT/"data"
Raw=Data/"raw"
Processed=Data/"processed"
External=Data/"external"
Feature=Data/"feature"

df_train_1=pd.read_csv(Processed/"train.csv")
df_holidays_events_0=pd.read_csv(Raw/"holidays_events.csv")
df_oil_0=pd.read_csv(Raw/"oil.csv")
df_stores_0=pd.read_csv(Raw/"stores.csv")
df_test_0=pd.read_csv(Raw/"test.csv")
df_transactions_0=pd.read_csv(Raw/"transactions.csv")

df_train_1["date"]= pd.to_datetime(df_train_1["date"], errors="coerce")

# %% [markdown]
# ## Time Dimension Hypotheses
#
# 1. Sales behavior may be strongly associated with temporal factors such as holidays, weekday/weekend effects, and seasonality.
#
# 2. Different time periods may reflect different consumption states, such as routine daily demand versus holiday-driven demand.

# %% [markdown]
# ### 1. Aggregate Sales Trend Over Time
#
# To obtain an initial view of the temporal structure, sales are aggregated across all stores and product categories and analyzed over time.
#
# This step is intended to identify whether the time dimension exhibits broad trend or cyclical behavior before moving to finer-grained temporal breakdowns.

# %%
df_dates_v_sales_2=df_train_1.groupby("date",as_index=False)["sales"].sum().sort_values("date")
fig,ax=plt.subplots(1,1,figsize=(14, 4))
ax.plot(df_dates_v_sales_2["date"],df_dates_v_sales_2["sales"])
plt.show()

# %% [markdown]
# #### Initial Observation
#
# The aggregated sales series suggests that time is a major structural dimension in this dataset.
#
# At the overall level, sales exhibit both a noticeable long-term trend and recurring cyclical fluctuations, indicating that further temporal decomposition is necessary in subsequent analysis.

# %% [markdown]
# #### Transfer the bins of date to month 

# %%
df_dates_v_sales_2["date"] = pd.to_datetime(df_dates_v_sales_2["date"], errors="coerce")
df_monthly = (
    df_dates_v_sales_2
    .set_index("date")
    .resample("ME")["sales"]
    .sum()
)

fig, ax = plt.subplots(1, 1, figsize=(14, 4))
ax.plot(df_monthly.index, df_monthly.values)
ax.set_xlabel("date")
ax.set_ylabel("sales")
plt.show()


# %% [markdown]
# ### Summary of trend over time
#
# Based on aggregated sales across all stores and product categories in the training set, several structural observations can be made. These findings are intended to guide subsequent analysis and modeling rather than serve as final conclusions.
#
# #### Long-term Trend
# From 2013 to 2017, total sales show a clear upward trend. This suggests that the time dimension is a major source of structure in the dataset, with the baseline sales level increasing over time. As a result, the series does not satisfy a simple stationarity assumption.
#
# #### Seasonal Pattern
# The monthly aggregated series shows recurring annual fluctuations. Peaks and troughs tend to appear in similar periods across different years, indicating the presence of meaningful yearly seasonality in sales behavior.
#
# #### Volatility Pattern
# Sales variability changes over time. Earlier periods exhibit relatively sharper fluctuations, while later periods fluctuate around a higher baseline level. This suggests potential heteroscedasticity in the sales series.
#
# #### Boundary Note
# The sharp decline at the end of the time series is inconsistent with the overall structure and is more likely caused by incomplete time coverage rather than a genuine business shock. This boundary effect should be treated with caution in later analysis and modeling.
#
# #### Conclusion
# Overall, the time dimension appears to be a strong structural factor in total sales, combining both long-term trend and stable seasonal patterns. Time-related features should therefore be retained in subsequent modeling, and further decomposition with other dimensions such as product category, store, and promotion is necessary.

# %% [markdown]
# <!-- #时间维度 EDA 小结（按月聚合）
#
# #基于对训练集中所有门店、所有商品类别销售额的按月聚合分析，可得到以下结构性观察结果（仅作为后续分析与建模的方向指引，而非结论）：
#
# ##1.整体趋势
# ###在 2013–2017 年期间，整体销售额呈现出明显的长期上升趋势，表明时间维度在该数据集中是一个重要的主导结构。销售水平的基准值随时间逐步抬升，数据整体不满足平稳性假设。
#
# ##2.季节性结构
# ###按月聚合结果显示出稳定且重复出现的年度周期性波动，不同年份的高峰与低谷大致出现在相似时间区间，说明销售行为存在显著的年内季节性结构。
#
# ##3.波动特征
# ###销售波动幅度随时间变化，早期阶段波动相对更为剧烈，后期阶段围绕更高的基准水平波动，提示销售数据可能存在异方差特性。
#
# ##4.数据边界说明
# ###时间序列末端出现的明显下降与整体结构不连续，判断为数据时间覆盖不完整导致的技术性截断，而非真实业务层面的异常变化。在后续分析与建模中需对该区间加以注意。
#
# #结论性说明
# ##时间维度在整体销售数据中表现为强结构因素，且同时包含长期趋势与稳定季节性特征。在后续分析中，时间相关特征不宜被忽略，并有必要结合其他维度（如商品类别、门店或促销信息）进行进一步拆分与交叉探索。 -->
#

# %% [markdown]
# ### 2. Monthly Aggregation
# To explore details of sales change with dates, it's necessary to alter the range of date.This step is intended to find patterns between month and sales.

# %% [markdown]
# #### 2.1 Absolute Monthly Sales Comparison
#
# To compare monthly sales patterns across years, total sales are aggregated by month within each year.

# %%
df_m=df_dates_v_sales_2.copy()
df_m["year"]=df_m["date"].dt.year
df_m["month"]=df_m["date"].dt.month
df_m=df_m.groupby(["year","month"],as_index=False)["sales"].sum()

fig, ax = plt.subplots(figsize=(10, 4))

for y in sorted(df_m["year"].unique()):
    tmp = df_m[df_m["year"] == y]
    ax.plot(tmp["month"], tmp["sales"], marker="o", label=str(y))

ax.set_xticks(range(1, 13))
ax.set_xlabel("Month")
ax.set_ylabel("Total Sales")
ax.legend(title="Year")

plt.show()

# %% [markdown]
# **Observation**
#
# The comparison reveals significant differences in overall sales scale across years, reflecting the strong upward trend identified earlier. This scale difference dominates the visualization.
#
# Although the general shape of monthly curves appears similar across years, the absolute values make it difficult to directly compare the relative importance of each month within a given year.
#
# Therefore, absolute monthly comparisons are more suitable for observing growth patterns over time, but not ideal for analyzing intra-year sales structure.

# %% [markdown]
# #### 2.2 Monthly Sales Share (Within-Year Normalization)
#
# To better compare intra-year structure, monthly sales are normalized by total annual sales for each year.
#

# %%
df_y=df_dates_v_sales_2.copy()
df_y["year"]=df_y["date"].dt.year
df_y=df_y.groupby(["year"],as_index=False)["sales"].sum()

fig, ax = plt.subplots(figsize=(10, 4))
df_m_valid=df_m[df_m["year"]<2017]
for y in sorted(df_m_valid["year"].unique()):
    tmp = df_m[df_m["year"] == y]
    total_sales = df_y.loc[df_y["year"] == y, "sales"].iloc[0]
    ax.plot(tmp["month"], tmp["sales"]/total_sales, marker="o", label=str(y))

ax.set_xticks(range(1, 13))
ax.set_xlabel("Month")
ax.set_ylabel("Sales rate")
ax.legend(title="Year")

plt.show()

# %% [markdown]
# **Observation**
#
# After excluding the incomplete year (2017), the normalized monthly sales patterns show strong consistency across years.
#
# Most years exhibit a similar distribution:
# - Early months (especially February) tend to have relatively lower contributions
# - Late months (November–December) account for a higher proportion of annual sales
#
# This indicates that month acts as a stable relative-position feature within a year, rather than being driven by random fluctuations in any single year.

# %% [markdown]
# #### Monthly Summary
#
# The monthly analysis reveals two key structural properties:
#
# 1. Absolute sales are dominated by long-term growth, making cross-year comparisons difficult without normalization.
# 2. After normalization, a stable intra-year pattern emerges, suggesting that month captures consistent seasonal structure.
#
# This implies that:
# - Time-related features should be modeled at both absolute (trend) and relative (seasonality) levels
# - Month is a strong candidate feature for capturing recurring seasonal effects in sales

# %% [markdown]
# ### Weekly Pattern (Day-of-Week Effect)
# To examine intra-week seasonality, sales are aggregated by day of the week and normalized by total weekly sales to obtain relative sales contribution (sales_rate) for each day.

# %%
df_week=df_train_1.copy()
df_week["dow"]=df_week["date"].dt.dayofweek
df_week=df_week.groupby(["dow"],as_index=False)["sales"].sum()
df_week["sales_rate"]=df_week["sales"]/df_week["sales"].sum()
fig,ax=plt.subplots(1,1,figsize=(5,3))
ax.plot(df_week["dow"],df_week["sales_rate"])
ax.set_xlabel("day of week")
ax.set_ylabel("sales rate")
plt.show()
print(df_week)

# %% [markdown]
# **Observation**
#
# A clear intra-week pattern is observed:
#
# - Sales are significantly higher on weekends (day 5–6)
#   - Saturday accounts for approximately 17.3%
#   - Sunday accounts for approximately 18.4%
#
# - Wednesday (day 3) shows the lowest sales contribution at around 11.3%
#
# - Monday to Thursday remain relatively stable, with sales contributions ranging between 12% and 14%

# %% [markdown]
# Overall, the sales distribution exhibits a strong "weekend peak" pattern.
#
# This aligns with typical retail behavior, where customers tend to concentrate their purchases during weekends, leading to higher aggregated sales.
#
# This result suggests that weekday is an important temporal feature influencing sales.
#
# Therefore, in subsequent analysis (e.g., when evaluating the effect of promotion), it is necessary to control for weekly seasonality to avoid mistakenly attributing regular temporal fluctuations to other factors.

# %%
###sales与holiday关系探索
###holiday表格数据清洗
df_holidays_events_0["date"]= pd.to_datetime(df_holidays_events_0["date"], errors="coerce")
print(df_holidays_events_0["date"].isnull().sum())

###在本阶段分析中，节假日信息仅被用于构建“是否处于节假日状态”的布尔标记，未进一步区分节假日类型或作用范围，以避免在早期探索阶段引入不必要的制度复杂性。
# holiday_dates=set(df_holidays_events_0["date"].drop_duplicates())
# holiday_dates = {d.date() for d in holiday_dates}
# df_h=df_dates_v_sales_2.copy()
# df_h["is_holiday"] = df_h["date"].isin(holiday_dates)
hol=df_holidays_events_0.copy()
hol["date"]=pd.to_datetime(hol["date"]).dt.normalize()
hol_day=hol[["date"]].drop_duplicates().assign(is_holiday=True)
df_holiday_train=df_dates_v_sales_2.copy()
df_holiday_train["date"] = pd.to_datetime(df_holiday_train["date"]).dt.normalize()
df_holiday_train = df_holiday_train.merge(hol_day, on="date", how="left")
df_holiday_train["is_holiday"] = df_holiday_train["is_holiday"].fillna(False)

fig, ax = plt.subplots(figsize=(3, 4))

# 非节假日
ax.scatter(
    [0] * (~df_holiday_train["is_holiday"]).sum(),
    df_holiday_train.loc[~df_holiday_train["is_holiday"], "sales"],
    alpha=0.4,
    label="Non-holiday"
)

# 节假日
ax.scatter(
    [1] * (df_holiday_train["is_holiday"]).sum(),
    df_holiday_train.loc[df_holiday_train["is_holiday"], "sales"],
    alpha=0.8,
    label="Holiday"
)

ax.set_xticks([0, 1])
ax.set_xticklabels(["Non-holiday", "Holiday"])
ax.set_ylabel("Daily Total Sales")
ax.legend()

plt.show()


# %% [markdown]
# 将节假日作为二元状态变量，与非节假日对应的日销售额分布进行对比后发现，
# 两类样本在整体分布上高度重叠，未呈现出明显可分的销售区间差异。
# 该结果表明，在当前聚合层级下，节假日并未表现为强主效应，
# 其影响更可能依赖于商品类别、门店特征或促销状态等条件因素。

# %% [markdown]
# ### Family-Level Weekly Consumption Structure

# %% [markdown]
# ### Methodology
#
# Instead of analyzing absolute sales volume, this section focuses on the relative share of each product family in daily total sales.
#
# To construct a stable representation of weekly consumption patterns, the following approach is used:
#
# - Each day is treated as an independent observation of consumption structure  
# - For each day, the share of each product family is calculated relative to total daily sales  
# - These daily shares are then averaged across the same day of the week (Day of Week)
#
# This approach ensures that:
#
# - High-volume days (e.g., promotions or holidays) do not dominate the structure  
# - The analysis reflects typical consumption allocation patterns rather than scale effects  

# %%
## Family × Day-of-Week：周内消费结构探索

# 本节通过分析不同商品大类在每日总销量中的占比，
# 考察其是否呈现出稳定的周内消费节律。
df_f=df_train_1.copy()

df_f["dow"]=df_f["date"].dt.dayofweek
daily_total=df_f.groupby("date")["sales"].sum().rename("total_sales")
# df_f=df_f.groupby(["date","family","dow"],as_index=False)["sales"].sum()###此处若对所有店铺的family情况进行汇总，数据可视化后结果几乎完全没有差异。
# print(df_f)
df_f=df_f.merge(daily_total,on="date")

df_f["family_share"]=df_f["sales"]/df_f["total_sales"]

df_heat=(df_f.groupby(["family","dow"],as_index=False)["family_share"].mean())

heat_df = df_heat.pivot(
    index="family",
    columns="dow",
    values="family_share"
)
plt.figure(figsize=(10, 8))
sns.heatmap(
    heat_df,
    cmap="cubehelix"
)
plt.xlabel("Day of Week")
plt.ylabel("Family")
plt.title("Average Family Share by Day of Week")
plt.show()




# %% [markdown]
# 在对比是否对门店维度进行汇总后，可以观察到：
# 无论在 store×family 粒度还是在全市场 family 粒度下，
# 商品大类的周内消费结构表现高度一致。
#
# 这表明门店差异主要体现在销售规模上，
# 而商品类别在时间维度上的相对结构具有较强的稳定性与一致性。
# 因此，在后续分析中，可以将 family 视为主要的结构维度，
# 而将 store 作为尺度或次级修正因素处理。
#

# %% [markdown]
# ### 关于周内结构的统计方式说明
#
# 在分析商品大类的周内消费结构时，本节采用**“先计算每日占比，再对同类日期取平均”**的方式进行统计。
#
# 具体而言，每一天被视为一个独立的消费结构样本，  
# 商品大类在该日总销量中的占比（share）用于刻画消费者在该日对不同商品类别的相对分配关系。
#
# 随后，对同一星期几（Day of Week）下的占比进行简单平均，以获得典型的周内消费结构轮廓。
#
# 该做法的目的在于：
# - 避免高销量日（如促销日或异常峰值）对结构判断产生过度影响；
# - 关注“在任意一个给定的星期几，消费结构通常呈现为何种形态”，
#   而非被整体销售规模加权后的结果。
#
# 因此，本节结果反映的是**消费结构的稳定性与形态差异**，而非销量规模本身。
#

# %% [markdown]
# ### 周内消费结构的观察结果
#
# 基于商品大类在每日总销量中的占比（share），对不同星期几的平均结构进行对比后，可以得到以下观察结果：
#
# - 从整体结构上看，**GROCERY I、BEVERAGES、CLEANING 以及 PRODUCE** 在各个星期几中始终占据较高的消费比例，构成日常消费结构的核心部分；
# - 对大多数商品大类而言，其在总消费结构中的占比在周内变化幅度较小，整体呈现出较强的稳定性；
# - 少数商品类别表现出轻微但可辨识的周内差异：
#   - **MEATS** 与 **POULTRY** 在周五附近占比略有抬升，可能与家庭聚餐或周末备餐行为相关；
#   - **BEVERAGES** 在周末的占比相较于工作日略高，符合休闲或社交场景消费增加的直觉；
#   - **PRODUCE** 在周中（如周三）出现轻微抬升，该现象在当前 EDA 阶段尚无法给出明确解释，暂作为经验性观察保留。
#
# 总体而言，除少数情境相关商品类别外，  
# **商品大类层面的周内消费结构整体较为平稳**，  
# 星期几并未对大多数商品类别产生显著的结构性影响。
#
# 基于上述结果，可以认为：  
# 周内节律并非普适的主导结构轴，而更可能作为对特定商品类别具有解释力的次级维度。
#
# 后续分析将引入节假日等条件变量，以检验是否存在能够放大或改变上述消费结构的状态切换情形。
#

# %% [markdown]
# ## 节假日条件下的消费结构分析（Methodology）
#
# 在本节中，我们关注的并非节假日是否带来销量的整体提升，  
# 而是**节假日是否改变了不同商品大类在消费结构中的相对位置**。
#
# 为避免将结构变化与规模变化混淆，本节分析延续前文做法，  
# 以商品大类在每日总销量中的占比（share）作为核心分析对象。
#
# ### 节假日定义
#
# 在 EDA 阶段，为保持分析的简洁性与稳健性，  
# 节假日被粗粒度地定义为：
#
# - `is_holiday = True`：该日期存在节假日标记；
# - `is_holiday = False`：该日期不存在节假日标记。
#
# 不进一步区分节假日的类型（如 national / local / regional）或转移假期等情形，  
# 以避免在探索阶段引入过多条件与噪声。
#
# ### 分析方法
#
# 具体分析步骤如下：
#
# 1. 将数据按是否为节假日划分为两组；
# 2. 在每一组中，计算各商品大类在每日总销量中的占比（share）；
# 3. 对节假日与非节假日条件下的占比进行平均，并进行对比分析。
#
# 通过该方法，可以直接观察：
#
# - 节假日是否导致消费结构发生系统性偏移；
# - 哪些商品大类在节假日条件下表现出与日常消费结构不同的行为。
#
# ### 方法论说明
#
# 需要强调的是，本节关注的是**结构变化（structure shift）**，  
# 而非由节假日带来的销量规模变化。
#
# 若某一商品大类在节假日下的占比结构与非节假日基本一致，  
# 则可认为节假日对其主要起到规模放大作用；
#
# 若其占比在节假日下发生明显偏移，  
# 则节假日可能对应一种消费行为的状态切换（regime change）。
#
# 本节分析的目标在于识别上述差异，而非对节假日效应进行精细建模。
#
#

# %%
###Family—holiday-sales pattern
df_fh=df_train_1.copy()
daily_sales=df_fh.groupby("date")["sales"].sum().rename("total_sales")
df_fh=df_fh.groupby(["date","family"],as_index=False)["sales"].sum()
df_fh=df_fh.merge(daily_sales,on="date")
df_fh["family_share"]=df_fh["sales"]/df_fh["total_sales"]

df_fh=df_fh.merge(hol_day, on="date", how="left")
df_fh["is_holiday"]=df_fh["is_holiday"].fillna(False)
df_fh=df_fh.groupby(["family","is_holiday"],as_index=False)["family_share"].mean()


fh_df = df_fh.pivot(
    index="family",
    columns="is_holiday",
    values="family_share"
)
plt.figure(figsize=(10, 8))
sns.heatmap(
    fh_df,
    cmap="cubehelix"
)
plt.xlabel("is_holiday")
plt.ylabel("Family")
plt.title("Average Family Share by holiday")
plt.show()


# %% [markdown]
# ## 节假日对商品结构与整体销售的影响总结
#
# 结合前文对节假日与非节假日条件下销售分布的对比，以及本节对商品大类消费结构（family share）的分析，可以得到以下结论。
#
# ### 商品大类的重要性结构
#
# 从整体消费结构来看，销售占比长期由少数核心商品大类主导：
#
# - **GROCERY I** 始终占据最主要的消费份额，是整体消费结构的绝对核心；
# - **PRODUCE、BEVERAGES、CLEANING** 等品类构成第二梯队，在不同时间条件下保持稳定存在；
# - 其余商品大类整体占比较低，且在时间维度上的波动有限。
#
# 这一结构在不同条件下表现出较强的稳定性。
#
# ### 节假日对商品结构的影响
#
# 在将销量汇总至全市场层面，并对节假日与非节假日条件下的商品大类占比进行对比后，可以观察到：
#
# - 不同商品大类在节假日与非节假日下的 **相对占比结构高度一致**；
# - 未出现节假日条件下系统性放大或压缩某一类商品占比的现象；
# - 节假日并未显著改变整体消费结构的组成方式。
#
# 这表明，在商品大类层面，节假日并不构成明显的结构性切换（regime change），而更像是对既有消费结构的重复与延展。
#
# ### 节假日对整体销售规模的影响
#
# 结合此前对节假日与非节假日 **sales 分布** 的探索结果，可以进一步发现：
#
# - 节假日与非节假日的整体销售分布差异有限；
# - 并未观察到节假日显著抬升整体销售水平或明显改变分布形态的现象。
#
# 因此，在当前数据集中，节假日对整体销售规模的促进作用也相对有限。
#
# ### 综合判断
#
# 综合结构与规模两个层面的分析结果，可以认为：
#
# - **holiday 在本数据集中并非关键的主导变量**；
# - 其既未显著重塑商品大类的消费结构，
#   也未对整体销售规模产生强烈而稳定的提升作用；
# - 相较之下，商品大类本身（family）构成了更为核心且稳定的结构维度。
#
# 基于上述结果，在后续建模中，节假日更适合作为次级或辅助特征，
# 而非作为主要的结构切换信号进行重点建模。
#

# %% [markdown]
# ## EDA 小结与后续分析方向
#
# 在前述分析中，我们从商品大类（family）的角度出发，
# 系统性地考察了时间因素（weekday、holiday）与门店维度（store）
# 对消费结构的影响。
#
# 主要结论包括：
#
# - 商品大类（family）构成了最核心且稳定的消费结构维度；
# - 门店差异主要体现在销售规模上，而对商品结构的影响有限；
# - 节假日既未显著改变商品大类的相对结构，
#   对整体销售规模的提升作用也相对有限。
#
# 上述结果表明，部分外生时间变量（如 holiday）
# 在当前数据集中并非主导性的结构因素。
#
# 基于此，后续 EDA 将重点转向 **promotion 与 store 维度**：
#
# - 对 promotion，关注其是否对整体销售规模以及商品结构产生显著干预；
# - 对 store，重点分析不同门店在销售规模与稳定性上的差异，
#   而非其对商品类别结构的影响。
#
# 该分析路径有助于区分“结构性变量”与“尺度性变量”，
# 并为后续建模阶段的特征选择与简化提供依据。
#

# %%
##对onpromotion进行数据概览
print(df_train_1["onpromotion"].describe())
print(df_train_1["onpromotion"].value_counts().head())
fig, ax = plt.subplots(1, 1, figsize=(14, 4))
ax.hist(df_train_1["onpromotion"].values,bins=20)
ax.set_xlabel("on promotion")
ax.set_ylabel("count")
plt.show()
# 因为 onpromotion 存在极端值，图中绝大多数数据集中在接近 0 的区域。

# %% [markdown]
# ### onpromotion 数据特征概览
#
# 为了理解促销变量 `onpromotion` 的基本性质，我们首先对其分布进行了统计描述和可视化分析。
#
# #### 基本统计特征
#
# 从描述性统计结果可以观察到：
#
# - 数据总量约为 **300 万条记录**；
# - `onpromotion` 的 **均值约为 2.6**，但 **标准差达到 12.2**，说明该变量分布较为离散；
# - **中位数为 0**，且 **75% 分位数仍然为 0**；
# - 最大值达到 **741**，远高于平均水平。
#
# 这些结果表明：大部分时间和商品类别组合下并不存在促销活动，但在少数情况下会出现大量商品同时参与促销。
#
# #### 频数分布特征
#
# 从 `value_counts` 结果可以看到：
#
# - `onpromotion = 0` 占据绝对多数（约 238 万条记录）；
# - 当存在促销时，数量通常较小，例如 1、2、3、4 等；
# - 高值促销数量虽然存在，但频率极低。
#
# 直方图进一步表明：
#
# - `onpromotion` 的分布 **高度右偏（right-skewed）**；
# - 数据呈现 **零膨胀（zero-inflated）+ 长尾（long-tail）** 的典型形态；
# - 少量极端值拉长了右侧尾部。
#
# #### 初步结论
#
# 综合以上观察，可以认为：
#
# - 在大多数 **store–family–date** 组合下并不存在促销活动；
# - 促销行为是一种 **稀疏但强干预的商业策略**；
# - 当促销发生时，可能涉及多个商品同时参与，因此会产生较大的 `onpromotion` 数值。
#
# 因此，在后续分析中，`onpromotion` 更适合被视为一种 **具有强不均衡分布的干预变量**。后续 EDA 将进一步探索：
#
# - 促销数量是否对整体销售规模产生显著影响；
# - 促销强度（promotion intensity）是否与销售额呈现某种趋势关系；
# - 促销是否会改变不同商品大类（family）的消费结构。

# %%
###对时间做归一化
df_promotion_sale=df_train_1.copy()
df_promotion_sale=df_promotion_sale.groupby(["date"],as_index=False).agg({"sales":"sum","onpromotion":"sum"})
df_promotion_sale["baseline"]=df_promotion_sale["sales"].rolling(7).mean().shift(1)
df_promotion_sale["normalised_sales"]=df_promotion_sale["sales"]/df_promotion_sale["baseline"]
df_promotion_sale = df_promotion_sale.dropna()

df_promotion_sale["promo_bucket"] = pd.qcut(
    df_promotion_sale["onpromotion"],
    q=5,
    duplicates="drop"
)
df_promotion_sale["promo_bucket"] = df_promotion_sale["promo_bucket"].astype(str)
print(df_promotion_sale["promo_bucket"].value_counts())
print(df_promotion_sale)
sns.lineplot(x="promo_bucket",y="normalised_sales",data=df_promotion_sale,estimator="mean")


# %% [markdown]
# ### 促销强度与归一化销售额的关系
#
# 为了更好地分析促销活动（promotion）对销售额的影响，我们首先对每日销售额进行时间归一化处理。
#
# 具体来说，我们使用 **过去 7 天的滚动平均销售额（rolling mean）** 作为一个短期基准水平（baseline），用来表示在没有异常波动情况下的正常销售水平。随后将当天销售额除以该基准值：
#
# normalised_sales = sales / baseline
#
# 这种处理可以在一定程度上消除时间序列中的短期波动，例如周内周期性变化或整体需求缓慢变化，使我们能够更关注 **促销活动本身是否会导致销售额偏离正常水平**。
#
# 接下来，我们使用 `onpromotion` 变量衡量当天的促销强度。该变量表示当天处于促销状态的商品数量。为了避免不同促销水平下样本数量差异过大，我们使用 `qcut` 按 **分位数（quantile）** 将促销强度划分为若干区间，使每个区间中的样本量大致相同。
#
# 下图展示了不同促销强度区间下的 **平均归一化销售额**。
#
# #### 观察结果
#
# 从图中可以看到几个较为明显的特征：
#
# - 在 **促销商品数量较少** 的情况下，归一化销售额略高于基准水平。
# - 随着促销商品数量增加到中等水平，销售额相对基准值 **略有下降**。
# - 当促销强度进一步增加时，销售额有所回升，但整体仍然接近基准水平附近。
#
# 总体来看，在控制了短期时间趋势之后，**促销强度与整体销售额之间的关系并不十分显著**。
#
# 一种可能的解释是，促销活动往往并不是随机发生的。零售商可能会在预期需求较低的时期增加促销力度，以刺激消费，因此在聚合到整体销售额层面时，促销的效果可能被这种策略性行为部分抵消。
#
# 此外，`onpromotion` 变量仅表示 **参与促销的商品数量**，并不能反映 **具体折扣力度或促销类型**，因此其对销售额的解释能力可能有限。
#
# 这表明，促销活动可能对 **具体商品或品类层面的销售行为** 产生影响，但在 **整体每日销售额层面**，其影响相对较弱。

# %%
###promotion与family之间的关系
###探索不同family中promotion可能的影响
df_pro_fa=df_train_1.copy()
df_pro_fa["is_promotion"]=df_pro_fa["onpromotion"]>0
effect=df_pro_fa.groupby(["family","is_promotion"])["sales"].mean().unstack()
effect["promo_ratio"]=effect[True]/effect[False]
effect = effect.sort_values("promo_ratio", ascending=False)

print(effect)
fig, ax = plt.subplots(figsize=(12,8))

ax.barh(effect.index, effect["promo_ratio"])

ax.axvline(1, color="red", linestyle="--", linewidth=2)

ax.set_xlabel("promotion / non-promotion mean sales ratio")
ax.set_ylabel("family")
ax.set_title("Promotion Effect by Family")

plt.show()



# %% [markdown]
# #### Promotion 对不同商品类别的影响差异
#
# 在整体层面的分析中，我们发现 promotion 与每日总销售额之间的关系并不明显。然而，这种聚合分析可能掩盖一个重要事实：**促销活动对不同商品类别的影响存在明显差异**。
#
# 因此，我们进一步分析 promotion 在不同商品类别（family）中的效果。
#
# ##### 方法
#
# 我们首先根据 `onpromotion` 是否大于 0，将样本划分为：
#
# - **promotion 状态**：`onpromotion > 0`
# - **非 promotion 状态**：`onpromotion = 0`
#
# 对于每一个商品类别（family），分别计算：
#
# - promotion 状态下的平均销售额
# - 非 promotion 状态下的平均销售额
#
# 并计算两者的比值：
#
# promotion effect ratio = 平均促销销售额 / 平均非促销销售额
#
# 该比值可以理解为：
#
# - **>1**：促销会提升该商品类别的销量  
# - **≈1**：促销影响较小  
# - **<1**：促销可能主要出现在需求较低的时期  
#
# 为了便于观察，我们在图中绘制了一条 **ratio = 1 的参考线**，表示促销对销量没有影响的基准水平。
#
# ##### 结果
#
# 从图中可以看到，不同商品类别对促销的响应差异非常明显。
#
# 促销效果最明显的类别包括：
#
# - **SCHOOL AND OFFICE SUPPLIES（文具类）**
# - **BABY CARE（婴幼儿用品）**
# - **PET SUPPLIES（宠物用品）**
#
# 这些类别在促销期间的平均销售额明显高于非促销时期。
#
# 相比之下，一些食品类商品的促销效果则相对较弱，例如：
#
# - **DAIRY**
# - **MEATS**
# - **BREAD/BAKERY**
# - **GROCERY**
#
# 这些类别即使在促销期间，销量提升幅度也相对有限。
#
# ##### 可能的原因
#
# 这种差异其实符合消费者行为的一些常见规律。
#
# 首先，一些商品类别具有 **较强的囤货属性**，例如：
#
# - 文具用品
# - 婴幼儿用品
# - 宠物用品
#
# 这些商品通常具有以下特点：
#
# - 单价较高
# - 保质期较长或不易过期
# - 消费频率相对较低
#
# 因此，当出现促销时，消费者往往更倾向于 **提前购买或增加购买数量**。
#
# 相比之下，食品类商品通常具有 **保质期较短** 的特点，例如牛奶、生鲜或面包。即使出现促销，消费者的购买量也受到储存条件和消费速度的限制，因此促销对销量的提升效果相对有限。
#
# 此外，食品类商品本身属于 **高频刚需消费品**，即使没有促销也会持续产生需求，因此促销对其销量的边际影响相对较小。
#
# ##### 为什么整体销售额中看不出明显促销效果
#
# 这一结果也解释了为什么在前面的分析中，**整体销售额与 promotion 之间的关系并不明显**。
#
# 原因在于：
#
# - 对促销最敏感的商品类别（如文具、宠物用品、婴幼儿用品）在整体销售额中的占比相对较小
# - 占据销售额主要部分的食品类商品对促销的响应却较弱
#
# 因此，当我们将所有商品类别聚合在一起时，不同类别之间的促销效果会相互抵消，从而导致整体层面的 promotion effect 看起来并不明显。
#
# 此外，在零售实践中，促销活动往往并不是随机发生的。商家可能会在 **预期需求较低的时期增加促销活动，以刺激消费**。在这种情况下，promotion 的出现本身就可能与销售低谷同时发生，这也会进一步削弱在整体数据中观察到的促销效果。
#
# ##### 小结
#
# 总体来看，promotion 对销售的影响具有明显的 **商品类别异质性（heterogeneity）**：
#
# - 一些可囤货、非刚需商品对促销非常敏感  
# - 刚需且保质期较短的食品类商品则相对不敏感  
#
# 这也表明，在后续建模过程中，**promotion 与商品类别（family）的交互关系可能是一个重要特征**，而不是简单地将 promotion 作为一个统一的影响因素。

# %%
##store*sales数据关系探索
df_store=df_train_1.copy()
###总店铺销售额排序
df_store_total=df_store.groupby(["store_nbr"])["sales"].sum().sort_values(ascending=False)
fig,ax=plt.subplots(1,1,figsize=(12,6))
df_store_total.plot(kind="bar",ax=ax)
ax.set_title("Total Sales by Store")
ax.set_xlabel("Store")
ax.set_ylabel("Total Sales")

plt.show()



# %%
###每日销售额分布
daily_store=df_store.groupby(["store_nbr","date"])["sales"].sum().reset_index()
fig,ax=plt.subplots(1,1,figsize=(14,6))
sns.boxplot(x="store_nbr",y="sales",data=daily_store)
ax.set_title("Daily Sales Distribution by Store")
plt.show()

# %% [markdown]
# ### Store 与销售额的关系（Store × Sales）
#
# 在完成时间、商品类别以及促销的分析之后，我们进一步从空间维度出发，研究不同门店（store）对销售额的影响。
#
# ---
#
# #### 方法
#
# 本部分分析主要分为两个层面：
#
# 1. **门店总销售额对比（规模分析）**
#    - 按 `store_nbr` 分组
#    - 对 `sales` 进行求和
#    - 绘制柱状图观察不同门店的整体销售规模差异
#
# 2. **门店每日销售分布（稳定性分析）**
#    - 按 `date + store_nbr` 聚合每日销售额
#    - 使用箱线图（boxplot）分析不同门店的销售分布
#    - 观察中位数、波动范围以及异常值情况
#
# ---
#
# #### 结果
#
# 从图中可以观察到以下关键现象：
#
# ##### 1. 门店之间存在显著的销售规模差异
#
# - 不同 store 的总销售额差异非常明显  
# - 存在明显的“头部店铺”（高销售门店）  
# - 同时也存在销售较低的门店，呈现出一定的长尾分布  
#
# 👉 说明：**store 是一个强影响因子**
#
# ---
#
# ##### 2. 每个门店都有自己的“销售基线”（baseline）
#
# 从箱线图可以看到：
#
# - 不同门店的销售中位数差异明显  
# - 某些门店整体分布显著高于其他门店  
# - 即使在不同日期下，这种差异依然稳定存在  
#
# 👉 说明：  
# **不同 store 本身就处在不同的“销售能级”上**
#
# ---
#
# ##### 3. 门店之间的波动性存在差异
#
# - 一些门店箱体较窄 → 销售较稳定  
# - 一些门店箱体较高 → 波动较大  
# - 部分门店存在较多异常高值（可能对应节假日或促销冲击）
#
# 👉 说明：  
# 不同门店不仅规模不同，**波动结构也不同**
#
# ---
#
# #### 解释（核心结构）
#
# 这一现象可以从系统结构角度理解：
#
# - `store` 主要影响的是：
#   - 客流量
#   - 地理位置
#   - 门店规模
# - 因此它本质上决定的是：
#   
# 👉 **销售额的“基线水平（baseline）”**
#
# 而不是：
#
# 👉 商品结构（family）或时间模式
#
# ---
#
# #### 与前面分析的关系
#
# 结合之前的结论：
#
# - `family` → 决定“卖什么”
# - `time`（dow / seasonality）→ 决定“什么时候卖多”
# - `promotion` → 决定“是否产生额外拉动”
# - `store` → 决定“整体卖多少（scale / baseline）”
#
# 👉 四个维度形成完整结构
#
# ---
#
# #### 小结
#
# - store 对销售额有显著影响，且主要体现在“规模差异”上  
# - 不同门店具有稳定的销售基线  
# - 门店之间存在不同的波动模式  
#
# ---
#
# #### 建模启示（非常关键）
#
# - `store_nbr` 必须作为模型特征  
# - 可以考虑：
#   - 直接 one-hot / label encoding
#   - 或学习 store embedding（进阶）
#
# 更重要的是：
#
# 👉 **在建模中需要显式建模“baseline差异”**
#
# 否则模型会把 store 差异错误归因给其他特征（如 promotion 或时间）
#
# ---
#
# #### 一句话总结
#
# store 决定的是销售的“地基”，  
# 而不是“波动的形状”。

# %%
##transaction的结构探究
df_tran=df_train_1.copy()
df_tran=df_tran.groupby(["date","store_nbr"],as_index=False).agg({"sales":"sum","onpromotion":"sum"})
df_transactions_0["date"]=pd.to_datetime(df_transactions_0["date"])
df_tran=df_tran.merge(df_transactions_0,on=["date","store_nbr"],how="left")
df_tran["transactions"]=df_tran["transactions"].fillna(0)


# %%
##transactions与sales之间的关系
fig,ax=plt.subplots(1,1,figsize=(14,6))
sns.scatterplot(x="transactions",y="sales",data=df_tran,alpha=0.5)



# %%
###transactions与dow之间的关系
df_tran["dow"]=df_tran["date"].dt.dayofweek
df_dow_tran=df_tran.groupby(["dow"],as_index=False)["transactions"].mean()
sns.lineplot(x="dow",y="transactions",data=df_dow_tran)


# %%
###transactions和onpromotion的关系
sns.scatterplot(x="onpromotion",y="transactions",data=df_tran,alpha=0.5)
print(df_tran)

# %% [markdown]
# ### Transactions（交易次数）与销售的关系
#
# 在前面的分析中，我们已经从时间、商品类别、促销和门店角度解释了销售结构。本节引入 transactions（交易次数），从“客流”角度进一步理解销售的驱动机制。
#
# ---
#
# #### 方法
#
# 本部分从三个层面分析 transactions：
#
# 1. **transactions 与 sales 的关系**
#    - 按日期聚合整体销售额与交易次数
#    - 使用散点图分析二者关系
#
# 2. **transactions 的时间结构**
#    - 按 `day of week` 分组
#    - 计算平均交易次数并绘制趋势图
#
# 3. **transactions 与 promotion 的关系**
#    - 按日期聚合 promotion 强度与交易次数
#    - 使用散点图观察二者关系
#
# ---
#
# #### 结果
#
# ##### 1. transactions 与 sales 呈明显正相关，但存在“发散结构”
#
# - 整体来看，transactions 越高，sales 越高  
# - 二者呈现明显正相关关系  
#
# 但更重要的是：
#
# - 散点图呈现“扇形发散”结构  
# - 在高 transactions 区间，sales 的波动范围明显扩大  
#
# 👉 说明：
#
# - sales ≈ transactions × 客单价（basket size）  
# - 在高客流情况下，客单价的波动更大  
#
# ---
#
# ##### 2. transactions 与时间结构高度一致
#
# - transactions 的周内变化趋势与 sales 几乎完全一致  
# - 周末明显高于工作日  
#
# 👉 说明：
#
# - 时间对销售的影响，本质是通过“客流变化”传导的  
# - transactions 是时间效应的直接体现  
#
# ---
#
# ##### 3. promotion 并未显著提升 transactions
#
# - 随着 onpromotion 增加，transactions 并没有明显上升趋势  
# - 在高 promotion 区间，transactions 甚至较低  
#
# 👉 说明：
#
# - promotion 不一定是“拉动客流”的工具  
# - 更可能是用于刺激已有客流的消费行为  
#
# ---
#
# #### 解释（系统视角）
#
# 从整体结构来看：
#
# - transactions → 控制“流量”
# - promotion → 影响“转化/客单价”
# - store → 决定“基线规模”
# - time → 决定“节律”
#
# 可以理解为：
#
# > sales = transactions × basket_size
#
# 其中：
#
# - transactions ≈ 外部流量
# - basket_size ≈ 内部消费行为（受 promotion、family 等影响）
#
# ---
#
# #### 小结
#
# - transactions 是 sales 的强驱动变量  
# - sales 的波动不仅来自流量，还来自“单位流量价值”的变化  
# - promotion 主要作用于“消费行为”，而非“客流引入”  
#
# ---
#
# #### 建模启示
#
# - transactions 是一个高解释力特征  
# - 但在预测未来时通常不可获得（属于“未来信息”）  
# - 因此可以作为：
#   - 离线分析和解释变量  
#   - 或用于构建辅助模型（如预测 transactions）

# %% [markdown]
# ####根据eda得出的基本数据结构为
# sales = baseline(store)
#       × time_pattern
#       × promotion_effect
#       × category_structure
#       x transactions
