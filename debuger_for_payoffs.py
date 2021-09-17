import pandas as pd
import os

script_dir = os.getcwd()
print(script_dir)

payoffs_db = pd.read_csv("payoffs.csv", delimiter=";")
chosen_tax_rate = 5
payoff = 9
payoffs_selected_tax = payoffs_db.loc[payoffs_db["tax"]==chosen_tax_rate][f"payoff_{payoff}"]
print(payoffs_db.head())
print(payoffs_selected_tax.iloc[0])