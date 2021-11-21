#!/usr/bin/env python
# coding: utf-8

# In[7]:


from textblob.classifiers import NaiveBayesClassifier
from colorama import init, Fore, Style
from tabulate import tabulate
import re, os
import numpy as np
import pandas as pd
import glob

class BankClassify():

    def __init__(self, data="../data/training/training_data.csv"):
        """Load in the previous data (by default from `data`) and initialise the classifier"""

        # allows dynamic training data to be used (i.e many accounts in a loop)
        self.trainingDataFile = data

        if os.path.exists(data):
            self.prev_data = pd.read_csv(self.trainingDataFile, parse_dates=['transaction_date'])
        else:
            self.prev_data = pd.DataFrame(columns=['transaction_date', 'amount', 'description', 'beneficiary', 'cat'])
            self.prev_data.to_csv(data)

        self.classifier = NaiveBayesClassifier(self._get_training(self.prev_data), self._extractor)
        
    def _get_training(self, df):
        """Get training data for the classifier, consisting of tuples of
        (text, category)"""
        train = []
        subset = df[df['cat'] != '']
        for i in subset.index:
            row = subset.iloc[i]
            train.append( (row['description'], row['cat']) )

        return train
    
    def _extractor(self, doc):
        """Extract tokens from a given string"""
        # TODO: Extend to extract words within words
        # For example, MUSICROOM should give MUSIC and ROOM
        tokens = self._split_by_multiple_delims(doc, [' ', '/'])

        features = {}

        for token in tokens:
            if token == "":
                continue
            features[token] = True

        return features
    
    def add_data(self, filename):
        """Add new data and interactively classify it.
        Arguments:
         - filename: filename
        """
        self.new_data = pd.read_csv(filename, parse_dates=['transaction_date'])

        self._ask_with_guess(self.new_data)

        self.prev_data = pd.concat([self.prev_data, self.new_data])
        # save data to the same file we loaded earlier
        self.prev_data.to_csv(self.trainingDataFile, index=False)
        
    def _ask_with_guess(self, df):
        """Interactively guess categories for each transaction in df, asking each time if the guess
        is correct"""
        # Initialise colorama
        init()

        df['cat'] = ""

        categories = self._read_categories()

        for index, row in df.iterrows():

            # Generate the category numbers table from the list of categories
            cats_list = [[idnum, cat] for idnum, cat in categories.items()]
            cats_table = tabulate(cats_list)

            stripped_text = row['description']

            # Guess a category using the classifier (only if there is data in the classifier)
            if len(self.classifier.train_set) > 1:
                guess = self.classifier.classify(stripped_text)
            else:
                guess = ""


            # Print list of categories
            print(chr(27) + "[2J")
            print(cats_table)
            print("\n\n")
            # Print transaction
            print("On: %s\t %.2f\n%s" % (row['transaction_date'], row['amount'], row['description']))
            print(Fore.RED  + Style.BRIGHT + "My guess is: " + str(guess) + Fore.RESET)

            input_value = input("> ")

            if input_value.lower() == 'q':
                # If the input was 'q' then quit
                return df
            if input_value == "":
                # If the input was blank then our guess was right!
                df.at[index, 'cat'] = guess
                self.classifier.update([(stripped_text, guess)])
            else:
                # Otherwise, our guess was wrong
                try:
                    # Try converting the input to an integer category number
                    # If it works then we've entered a category
                    category_number = int(input_value)
                    category = categories[category_number]
                except ValueError:
                    # Otherwise, we've entered a new category, so add it to the list of
                    # categories
                    category = input_value
                    self._add_new_category(category)
                    categories = self._read_categories()

                # Write correct answer
                df.at[index, 'cat'] = category
                # Update classifier
                self.classifier.update([(stripped_text, category)   ])

        return df
    
    def _read_categories(self, base_path="../data/training/"):
        """Read list of categories from categories.txt"""
        categories = {}
        cat_path = base_path + 'categories.txt'
        
        if not os.path.exists(cat_path):
            f = open(cat_path, 'w+')
            f.close()
        
        self.prev_data = pd.read_csv(self.trainingDataFile)
        
        with open(cat_path) as f:
            for i, line in enumerate(f.readlines()):
                categories[i] = line.strip()

        return categories

    def _add_new_category(self, category):
        """Add a new category to categories.txt"""
        with open('categories.txt', 'a') as f:
            f.write('\n' + category)
            
    def _split_by_multiple_delims(self, string, delims):
        """Split the given string by the list of delimiters given"""
        regexp = "|".join(delims)
        
        return re.split(regexp, string)


# In[10]:


df = read_transaction_data('barclays')
df


# In[ ]:




