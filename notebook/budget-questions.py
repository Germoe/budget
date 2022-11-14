#!/usr/bin/env python
# coding: utf-8
# %%
import numpy as np
import pandas as pd
from ipywidgets import interact, widgets
import datetime
from budget.functions import add_categories, get_categories, read_transaction_data
from budget.budget import Budget, Transaction

import plotly.express as px
import plotly.graph_objects as go

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
    df = budget_last_month_cat.reset_index()
    return df.loc[(df['cat'] == cat),:]


# %%
today = datetime.date.today()
first = today.replace(day=1)
last_month = (first - datetime.timedelta(days=1)).replace(day=1)
last_month_str = last_month.strftime("%Y-%m-%d")

print(last_month_str)


# %%
# Did we spent our money the way we planned?


# %%
# Budget Plan
budget = Budget('../data/budget/budget_new.csv').budget
budget = budget#.reset_index().rename({'index': 'cat'},axis=1)
budget.index.name = 'cat'
# budget, cats = add_categories(budget, return_cats = True)
# budget_last_month = budget.loc[budget['budget_month'] == last_month_str,:].groupby(['budget_month','type','cat','label']).sum()
budget_last_month_cat = budget# budget.loc[budget['budget_month'] == last_month_str,:].groupby(['budget_month','type','cat']).sum()

# Actuals
names = ['bofa-sebastian','bofa-brett','barclays','dkb-credit','dkb','n26-sebastian','n26-brett','capital-one']
df_raw = pd.concat([Transaction(name).transactions for name in names]).set_index('transaction_date')
df_raw = df_raw.loc[df_raw.index >= '2021-10-01',:]
df_raw = add_categories(df_raw)

## Remove Transactions to ignore
df_raw = df_raw.loc[df_raw['cat'] != 'ignore', :]
df_raw['budget_month'] = df_raw.index.to_numpy().astype('datetime64[M]')

## Last Month Actuals
df_last_month = df_raw[df_raw['budget_month'] == last_month_str].sort_index()
df_last_month_cat = df_last_month.groupby(['cat']).sum()[['amount']]
df_last_month_cat = budget_last_month_cat.join(df_last_month_cat, how='outer').reset_index()
df_last_month_cat['diff'] = df_last_month_cat['amount'] - df_last_month_cat['budget_amount']
diff_last_month_pivot = df_last_month_cat.pivot_table(index=['cat'], values=['amount','budget_amount','diff'], aggfunc='sum')
diff_last_month_pivot = diff_last_month_pivot.drop(['savings','transfer'])
diff_last_month_pivot


# %%
excl_income = ~((diff_last_month_pivot.index == 'income'))
total_expenses = diff_last_month_pivot.loc[excl_income,'amount'].sum()
print(f'Total Expenses: {total_expenses} EUR')

# %%
diff_last_month_pivot[['diff']].plot(kind='bar')

# %%
df_raw.loc[(df_raw['cat'].isna()) & (df_raw.index >= last_month_str),'label'].unique()

# %%
# Show Actual Category Breakdowns 
cats = get_categories()
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
diff_last_month_pivot.sum()

# %%
last_month_total = diff_last_month_pivot.loc[:,['amount']].fillna(0)
last_month_total['diff_to_budget'] = diff_last_month_pivot.loc[:,'diff']
last_month_total.sum()


# %%
# Average Net Worth


# %%
df_raw = df_raw.reset_index()
last_transact_date = df_raw.groupby('source').max()['transaction_date'].reset_index()
last_transact_cond = df_raw[['source','transaction_date']].apply(tuple, axis=1).isin(last_transact_date.apply(tuple, axis=1))

# %%
total_source_df = df_raw.loc[(last_transact_cond)]
total_source_df = total_source_df.groupby('source').agg({'total': [np.max,np.min,np.mean]})
total_source_df, total_source_df.sum()

# %%
roll_avg = df_raw.groupby(['source','transaction_date']).agg({'total': [np.max, np.min, np.mean]})
start = df_raw.transaction_date.min()
end = df_raw.transaction_date.max()
time_index = pd.date_range(start=start, end=end)
roll_avg = pd.concat([roll_avg.loc[(source, slice(None)),:].reset_index().set_index('transaction_date').reindex(time_index, method='ffill') for source in df_raw['source'].unique()]).reset_index()
roll_avg = roll_avg.groupby('index').sum()
roll_avg['rolling_mean_mean'] = roll_avg[('total','mean')].rolling(window=28).mean()
roll_avg.columns = [f'{i}{j}' for i, j in roll_avg.columns]

fig = go.Figure()
fig.add_traces([go.Scatter(x=roll_avg.index,y=roll_avg['totalmean'], line={'color': 'rgba(31,119,180,1)'}, name='daily_avg'),
                go.Scatter(x=roll_avg.index,y=roll_avg['rolling_mean_mean'], line={'color': 'rgba(255,127,14,1)'}, name='mvg_28')])

# %%
df_raw['cat'].unique()

# %%
df_expenses = df_raw.loc[~df_raw['cat'].isin(['income','transfer','ignore','savings']),:]
df_income = df_raw.loc[df_raw['cat'].isin(['income']),:]

# %%
roll_avg = df_expenses.groupby(['transaction_date']).agg({'amount': [np.sum]})
start = df_expenses.transaction_date.min()
end = df_expenses.transaction_date.max()
time_index = pd.date_range(start=start, end=end)
roll_avg = roll_avg.reindex(time_index).reset_index()
roll_avg = roll_avg.groupby('index').sum()
roll_avg['daily'] = roll_avg[('amount','sum')].rolling(window=1).sum() * 7
roll_avg['weekly_avg'] = roll_avg[('amount','sum')].rolling(window=7).sum() / 7 * 7
roll_avg['monthly_avg'] = roll_avg[('amount','sum')].rolling(window=28).sum() / 28 * 7
roll_avg['three_month_avg'] = roll_avg[('amount','sum')].rolling(window=84).sum() / 3 / 4 / 7 * 7
roll_avg.columns = [f'{i}{j}' for i, j in roll_avg.columns]

fig = go.Figure()
fig.add_traces([go.Scatter(x=roll_avg.index,y=roll_avg['daily'], line={'color': 'rgba(227,119,194,1)'}, name='daily'),
               go.Scatter(x=roll_avg.index,y=roll_avg['weekly_avg'], line={'color': 'rgba(148,103,189,1)'}, name='weekly_avg'),
               go.Scatter(x=roll_avg.index,y=roll_avg['monthly_avg'], line={'color': 'rgba(31,119,180,1)'}, name='monthly_avg'),
               go.Scatter(x=roll_avg.index,y=roll_avg['three_month_avg'], line={'color': 'rgba(255,127,14,1)'}, name='three_month_avg')])

# %%
avg_method = 'monthly_avg'
start = df_raw.transaction_date.min()
end = df_raw.transaction_date.max()
time_index = pd.date_range(start=start, end=end)

inc_exp_dfs = []
for df, val_type in zip([df_income,df_expenses], ['income','expenses']):
    roll_avg = df.groupby(['transaction_date']).agg({'amount': [np.sum]})
    roll_avg = roll_avg.reindex(time_index).reset_index()
    roll_avg = roll_avg.groupby('index').sum()
    roll_avg['monthly_avg'] = roll_avg[('amount','sum')].rolling(window=30).sum().abs()
    roll_avg.columns = [f'{i}{j}' for i, j in roll_avg.columns]

    roll_avg['yearmonth'] = roll_avg.index.floor('30D') 
    roll_avg = roll_avg.groupby(['yearmonth']).median()
    if val_type == 'expenses':
        roll_avg['expenses_share'] = (roll_avg['monthly_avg'] / inc_exp_dfs[0]['monthly_avg'] * 100).round()
#         roll_avg = roll_avg.reset_index()
    else:
        roll_avg['expenses_share'] = 0
    roll_avg['type'] = val_type
    inc_exp_dfs.append(roll_avg)

roll_avg = pd.concat(inc_exp_dfs)

fig = px.bar(roll_avg.reset_index(), x='yearmonth', y=avg_method, color='type', custom_data=['expenses_share'], barmode='group')
fig.update_traces(hovertemplate="%{y} %{customdata[0]}% of income")
fig.update_layout(hovermode="x unified")


# %%
# category = 'subscription'
def ts_category_view(category):
    df_category = df_raw.loc[df_raw['cat'] == category,:]
    roll_avg = df_category.groupby(['transaction_date']).agg({'amount': [np.sum]})
    start = df_category.transaction_date.min()
    end = df_category.transaction_date.max()
    time_index = pd.date_range(start=start, end=end)
    roll_avg = roll_avg.reindex(time_index).reset_index()
    roll_avg = roll_avg.groupby('index').sum()
    roll_avg['daily'] = roll_avg[('amount','sum')].rolling(window=1).sum() * 28
    roll_avg['weekly_avg'] = roll_avg[('amount','sum')].rolling(window=7).sum() / 7 * 28
    roll_avg['monthly_avg'] = roll_avg[('amount','sum')].rolling(window=28).sum() / 28 * 28
    roll_avg['three_month_avg'] = roll_avg[('amount','sum')].rolling(window=84).sum() / 3 / 4 / 7 * 28
    roll_avg.columns = [f'{i}{j}' for i, j in roll_avg.columns]

    fig = go.Figure()
    fig.add_traces([go.Scatter(x=roll_avg.index,y=roll_avg['monthly_avg'], line={'color': 'rgba(31,119,180,1)'}, name='monthly_avg'),
                   go.Scatter(x=roll_avg.index,y=roll_avg['three_month_avg'], line={'color': 'rgba(255,127,14,1)'}, name='three_month_avg')])
    fig.show()
    

# Show Actual Category Breakdowns 
interact(ts_category_view, category=list(cats.keys()));

# %%
# # category = 'subscription'

# def reindex_by_date(df, dates=time_index):
#     return df.reindex(dates)

# def category_breakdown(avg_method):
#     roll_avg_cats = []
#     start = df_expenses.transaction_date.min()
#     end = df_expenses.transaction_date.max()
#     time_index = pd.date_range(start=start, end=end)
    
#     for category in df_expenses['cat'].dropna().unique():
#         df_category = df_expenses.loc[df_raw['cat'] == category,:]
#         roll_avg = df_category.groupby(['transaction_date']).agg({'amount': [np.sum]})
#         roll_avg = roll_avg.reindex(time_index).reset_index()
#         roll_avg = roll_avg.groupby('index').sum()
#         roll_avg['daily'] = roll_avg[('amount','sum')].rolling(window=1).sum() * 7
#         roll_avg['weekly_avg'] = roll_avg[('amount','sum')].rolling(window=7).sum() / 7 * 7
#         roll_avg['monthly_avg'] = roll_avg[('amount','sum')].rolling(window=28).sum() / 28 * 7
#         roll_avg['three_month_avg'] = roll_avg[('amount','sum')].rolling(window=84).sum() / 3 / 4 / 7 * 7
#         roll_avg.columns = [f'{i}{j}' for i, j in roll_avg.columns]
#         roll_avg['cat'] = category
#         roll_avg_cats.append(roll_avg)

#     roll_avg = pd.concat(roll_avg_cats)
# #     roll_avg['monthly_avg_total'] = roll_avg.groupby('index').sum()['monthly_avg']
# #     roll_avg['monthly_avg'] = roll_avg['monthly_avg'] / roll_avg['monthly_avg_total']
# #     roll_avg['three_month_avg_total'] = roll_avg.groupby('index').sum()['three_month_avg']
# #     roll_avg['three_month_avg'] = roll_avg['three_month_avg'] / roll_avg['three_month_avg_total']


#     fig = px.area(roll_avg.reset_index(), x='index', y=avg_method, color='cat')

#     # #     fig = go.Figure()
#     # #     fig.add_traces([go.Scatter(x=roll_avg.index,y=roll_avg['monthly_avg'], line={'color': 'rgba(31,119,180,1)'}, name='monthly_avg'),
#     # #                    go.Scatter(x=roll_avg.index,y=roll_avg['three_month_avg'], line={'color': 'rgba(255,127,14,1)'}, name='three_month_avg')])
#     fig.show()
    
# interact(category_breakdown, avg_method=['daily','weekly_avg','monthly_avg','three_month_avg']);

# %%
def reindex_by_date(df, dates=time_index):
    return df.reindex(dates)

def share_of_exp_by_cat(avg_method):
    roll_avg_cats = []
    start = df_expenses.transaction_date.min()
    end = df_expenses.transaction_date.max()
    time_index = pd.date_range(start=start, end=end)
    
    for category in df_expenses['cat'].dropna().unique():
        df_category = df_expenses.loc[df_raw['cat'] == category,:]
        roll_avg = df_category.groupby(['transaction_date']).agg({'amount': [np.sum]})
        roll_avg = roll_avg.reindex(time_index).reset_index()
        roll_avg = roll_avg.groupby('index').sum()
        roll_avg['monthly_avg'] = (roll_avg[('amount','sum')].rolling(window=30).sum()).round()
        roll_avg['three_month_avg'] = (roll_avg[('amount','sum')].rolling(window=90).sum() / 3).round()
        roll_avg.columns = [f'{i}{j}' for i, j in roll_avg.columns]
        roll_avg['cat'] = category
        roll_avg_cats.append(roll_avg)

    roll_avg = pd.concat(roll_avg_cats)
    roll_avg['monthly_avg_total'] = roll_avg.groupby('index').sum()['monthly_avg']
    roll_avg['monthly_avg_share'] = (roll_avg['monthly_avg'] / roll_avg['monthly_avg_total'] * 100).round()
    roll_avg['three_month_avg_total'] = roll_avg.groupby('index').sum()['three_month_avg']
    roll_avg['three_month_avg_share'] = (roll_avg['three_month_avg'] / roll_avg['three_month_avg_total'] * 100).round()
    roll_avg['yearmonth'] = roll_avg.index.floor('30D') 
    roll_avg = roll_avg.groupby(['yearmonth','cat'], as_index=False).median()
    roll_avg['yearmonth'] = roll_avg['yearmonth']

    fig = px.bar(roll_avg.reset_index(), x='yearmonth', y=avg_method, color='cat', custom_data=["monthly_avg_share","monthly_avg_total"])
    fig.update_traces(hovertemplate="%{y} of %{customdata[1]} (%{customdata[0]}%)")
    fig.update_layout(hovermode="x unified")
    
    fig.show()
    
interact(share_of_exp_by_cat, avg_method=['monthly_avg','monthly_avg_share','three_month_avg','three_month_avg_share']);

# %%

# %%

# %%
