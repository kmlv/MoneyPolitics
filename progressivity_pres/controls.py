doc = """"
Control parameters for MoneyPolitics
"""

task_endowments = [125, 80, 40, 25, 25, 15, 15, 15, 9]

# Because oTree doesn't let us work with the multiple checkbox multiple choiice widget, we are going to create a list
# of options with the income and if its the 1st, 2nd or 3rd person with the same income
possible_message_receivers = [['1251', 'Income 125'], ['801', 'Income 80'], ['401', 'Income 40'],
                              ['252', 'Income 25 (Player 2)'], ['251', 'Income 25 (Player 1)'],
                              ['153', 'Income 15 (Player 3)'], ['152', 'Income 15 (Player 2)'],
                              ['151', 'Income 15 (Player 1)'], ['91', 'Income 9']]

possible_message_receivers_125 = list(possible_message_receivers)
possible_message_receivers_80 = list(possible_message_receivers)
possible_message_receivers_40 = list(possible_message_receivers)
possible_message_receivers_252 = list(possible_message_receivers)
possible_message_receivers_251 = list(possible_message_receivers)
possible_message_receivers_153 = list(possible_message_receivers)
possible_message_receivers_152 = list(possible_message_receivers)
possible_message_receivers_151 = list(possible_message_receivers)
possible_message_receivers_9 = list(possible_message_receivers)

possible_message_receivers_125.remove(possible_message_receivers[0])
possible_message_receivers_80.remove(possible_message_receivers[1])
possible_message_receivers_40.remove(possible_message_receivers[2])
possible_message_receivers_252.remove(possible_message_receivers[3])
possible_message_receivers_251.remove(possible_message_receivers[4])
possible_message_receivers_153.remove(possible_message_receivers[5])
possible_message_receivers_152.remove(possible_message_receivers[6])
possible_message_receivers_151.remove(possible_message_receivers[7])
possible_message_receivers_9.remove(possible_message_receivers[8])

message_cost = 1
number_of_messages = 1
progressivity_levels = [[1, 'Level 1'], [2, 'Level 2'], [3, 'Level 3'],
                        [4, 'Level 4'], [5, 'Level 5']]

progressivity_levels_tax_rates = {'1': [0.4, 0.4, 0.4, 0.4, 0.4, 0.4],
                                  '2': [0.3, 0.32, 0.342, 0.364, 0.407, 0.458],
                                  '3': [0.2, 0.24, 0.284, 0.328, 0.439, 0.515],
                                  '4': [0.1, 0.14, 0.204, 0.278, 0.464, 0.585],
                                  '5': [0, 0, 0.06, 0.263, 0.531, 0.664]}

# Private Sector Parameters
alpha = 5
beta = 1/16

# Steps for tax rate
tax_step = '0.05'
