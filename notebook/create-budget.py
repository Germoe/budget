# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.13.3
#   kernelspec:
#     display_name: budget_3_8_0
#     language: python
#     name: budget_3_8_0
# ---

# %%
from budget.budget import Budget

# %%
budget = Budget(path='../data/budget/budget_new.csv')
budget.budget