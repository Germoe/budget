import os
import pandas as pd

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
