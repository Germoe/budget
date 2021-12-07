#!/usr/bin/env python
# coding: utf-8
# %%

# %%

import pandas as pd
from budget.functions import print_file


# %%


f_path = '../data/budget/budget.csv'


# %%


print_file(f_path)


# %%


df = pd.read_csv(f_path, skiprows=7)
df.columns = [col.lower() for col in df.columns]

df['type'] = df['type'].str.lower()

df = df.loc[df['type'].isin(['income','expense'])]
df = df.melt(id_vars=['type','name','label'], var_name='budget_month', value_name='budget_amount')

df['budget_amount'] = pd.to_numeric(df['budget_amount'].str.replace(',',''), downcast='float')
df['budget_month'] = pd.to_datetime(df['budget_month'], format="%b %Y")

df.loc[(df['type'] == 'expense') & (df['budget_amount'] > 0),'budget_amount'] = -df.loc[(df['type'] == 'expense') & (df['budget_amount'] > 0),'budget_amount']
df.to_csv('../data/budget/budget_cln.csv', index=False)budget_amount


# %%





# %%
