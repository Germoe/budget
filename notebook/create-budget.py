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
import os
from budget.functions import add_categories
import pandas as pd 
import warnings
import questionary

class Budget():
    budget = None
    schema = ['budget_amount']
    
    def __init__(self, path, budget_dict=None):
        """
        Initialize Budget Object.
        """
        self.path = path
        
        try:
            budget = pd.read_csv(self.path, index_col=0)
        except:
            if os.path.exists(self.path) == True:
                raise ValueError('Attempted to create new budget but file already exists at this location.')
            budget = self.create_budget(budget_dict=budget_dict)
            self.budget.to_csv(self.path)
        
        self.budget = budget

    def create_budget(self, budget_dict=None):
        if budget_dict is None:
            budget_dict = {
                'budget_amount': {
                    'income': int(input("What is your total monthly income? >")),
                },
             }

            running_total = 0

            while input('Add another Expense Category (y/n) >') == 'y':
                key = input('Name of Expense: ')
                val = int(input(f'Amount (Current Total Expenses: {running_total}): '))
                budget_dict['budget_amount'][key] = -val

                running_total += val
            
        return pd.DataFrame(budget_dict)
            
    def update_budget(self, key):
        self.budget['budget_amount'][key] = -int(input(f'Amount: '))
        self.budget.to_csv(self.path)


# %%
budget = Budget(path='../data/budget/budget_new.csv')
budget.budget
