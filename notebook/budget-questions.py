#!/usr/bin/env python
# coding: utf-8
# %%
import numpy as np
import pandas as pd
from ipywidgets import interact, widgets
import datetime
from budget.functions import add_categories, read_transaction_data

pd.options.plotting.backend = "plotly"

def show_last_month_cat(cat):
    df = df_last_month.reset_index()
    return df.loc[(df['cat'] == cat),:]

def filter_last_month(lower_bound=None, upper_bound=None):
    df = df_last_month.reset_index()
    if (lower_bound is not None) and (upper_bound is not None):
        return df.loc[(df['amount'] > lower_bound) & (df['amount'] < upper_bound),:]
    elif lower_bound is not None and upper_bound is None:
        return df.loc[(df['amount'] > lower_bound),:]
    elif lower_bound is None and upper_bound is not None:
        return df.loc[(df['amount'] < upper_bound),:]
    else:
        return df

def show_last_month_cat_budget(cat):
    df = budget_last_month.reset_index()
    return df.loc[(df['cat'] == cat),:]


# %%
today = datetime.date.today()
first = today.replace(day=1)
last_month = (first - datetime.timedelta(days=1)).replace(day=1)
last_month_str = last_month.strftime("%Y-%m-%d")


# %%
# Did we spent our money the way we planned?


# %%
# Budget Plan
budget = pd.read_csv('../data/budget/budget_cln.csv', parse_dates=['budget_month'])
budget, cats = add_categories(budget, return_cats = True)
budget_last_month = budget.loc[budget['budget_month'] == last_month_str,:].groupby(['budget_month','type','cat','label']).sum()
budget_last_month_cat = budget.loc[budget['budget_month'] == last_month_str,:].groupby(['budget_month','type','cat']).sum()

# Actuals
names = ['bofa-sebastian','bofa-brett','barclays','dkb-credit','dkb','n26-sebastian','n26-brett','capital-one']
df_raw = pd.concat([read_transaction_data(name) for name in names]).set_index('transaction_date')
df_raw = df_raw.loc[df_raw.index >= '2021-09-01',:]
df_raw = add_categories(df_raw)

## Remove Transactions to ignore
df_raw = df_raw.loc[df_raw['cat'] != 'ignore', :]
df_raw['budget_month'] = df_raw.index.to_numpy().astype('datetime64[M]')

## Last Month Actuals
df_last_month = df_raw[df_raw['budget_month'] == last_month_str].sort_index()
df_last_month_cat = df_last_month.groupby(['budget_month','cat']).sum()['amount']

df_last_month_cat = budget_last_month.join(df_last_month_cat).reset_index()
df_last_month_cat['diff'] = df_last_month_cat['amount'] - df_last_month_cat['budget_amount']
diff_last_month_pivot = df_last_month_cat.pivot_table(index=['budget_month','cat'], columns=['type'], values=['amount','budget_amount','diff'])
diff_last_month_pivot


# %%
# Show Budget Category Breakdowns 
interact(show_last_month_cat_budget, cat=list(cats.keys()));


# %%
# Show Actual Category Breakdowns 
interact(show_last_month_cat, cat=list(cats.keys()));


# %%
# Filter Actuals by Amount
interact(filter_last_month, 
         lower_bound=widgets.IntSlider(min=df_last_month['amount'].min(), max=df_last_month['amount'].max(), step=1, value=df_last_month['amount'].min()), 
         upper_bound=widgets.IntSlider(min=df_last_month['amount'].min(), max=df_last_month['amount'].max(), step=1, value=df_last_month['amount'].max()));


# %%
# How much money do we have left every month?


# %%
last_month_total = diff_last_month_pivot.loc[:,('amount',slice(None))].droplevel(0, axis=1).fillna(0)
last_month_total['savings/debt'] = last_month_total['income'] + last_month_total['expense']
last_month_total.sum()


# %%
# Average Net Worth


# %%
roll_avg = df_raw.reset_index().groupby('transaction_date').agg({'total': np.average})
roll_avg['rolling_mean'] = roll_avg['total'].rolling(window=28).mean()
roll_avg.plot()


# %%
