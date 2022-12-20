from otree.api import (
    models, BaseConstants, BaseSubsession, BaseGroup, BasePlayer, widgets
)

from otree.api import Currency as c
from django import forms
from django.conf import settings

import csv
import settings
import controls as ctrl
import pandas as pd
import random
import numpy, os
import math


author = 'Marco Gutierrez, Skyler Stewart, and John Elliott'

doc = """
Money and Politics App
"""

class Constants(BaseConstants):
    name_in_url = 'DecisionStudy'
    num_rounds = 5 # total number of rounds
    practice_rounds = 0 # number of practice rounds
    players_per_group = 9

    instructions_template = "MoneyPolitics/Instructions.html"
    instructions_button = "MoneyPolitics/Instructions_Button.html"

    #Ravens config:
    config = {
            'test_number': 2,
            '1' : [2, 3, 3, 7, 5, 6, 4, 1, 7, 6] , 
            '2' : [6, 1, 2, 1, 7, 3, 4, 6, 5, 2],
            '3' : [3, 1, 3, 8, 2, 8, 8, 8, 5, 2], 
            '4' : [4, 2, 5, 6, 4, 3, 4, 2, 1, 6],
            'points': [1,1.5,2,2.5,3,3.5,4,4.5,5,5.5]
     }
    # Real Effort Tasks
    tetris = "MoneyPolitics/Tetris.html"
    diamonds = "MoneyPolitics/Diamonds.html"

    # There are some parameters that may vary during the development of this app. In order to make this as soft coded as
    # possible, the code should be flexible enough to allow changes in this ones and obtain them from an external
    # .py/txt file (If you find a better way, feel free to update the code with it)
    task_endowments = ctrl.task_endowments
    player_ids = ctrl.player_ids
    number_of_messages = ctrl.number_of_messages
    progressivity_levels = ctrl.progressivity_levels
    tax_step = 5

    # Private Sector Parameters
    alpha = ctrl.alpha
    beta = ctrl.beta

    # Max. Characters Allowed Per message
    max_chars = 280

    #Number of variables for effort tasks
    sum_variables = 25
    slider_variables = 60

def parse_config():
    with open('MoneyPolitics/payoffs.csv') as f:
        rows = list(csv.DictReader(f))

    rounds = []
    for row in rows:
        rounds.append({
            9: float(row['payoff_9']),
            15: float(row['payoff_15']),
            25: float(row['payoff_25']),
            40: float(row['payoff_40']),
            80: float(row['payoff_80']),
            125: float(row['payoff_125']),
        })
    return rounds

def parse_config_tasks():
    with open('MoneyPolitics/task_effort.csv') as f:
        rows = list(csv.DictReader(f))

    rounds = []
    for row in rows:
        rounds.append({
            'round_number': int(row['round_number']),
            'duration': int(row['duration']),
            'task': row['task'],
        })
    return rounds



class Subsession(BaseSubsession):
    def creating_session(self):
        if self.session.config["matching"] == "fixed":  # fixed random assignment to groups
            if self.round_number == 1: # creating random assignment
                self.group_randomly()
            else:
                self.group_like_round(1)

        elif self.session.config["matching"] == "random":
            self.group_randomly()
        #Ravenstask
        for player in self.get_players():
            player.test_num = Constants.config['test_number']
            player.Q1_ans = Constants.config[str(player.test_num)][0]
            player.Q2_ans = Constants.config[str(player.test_num)][1]
            player.Q3_ans = Constants.config[str(player.test_num)][2]
            player.Q4_ans = Constants.config[str(player.test_num)][3]
            player.Q5_ans = Constants.config[str(player.test_num)][4]
            player.Q6_ans = Constants.config[str(player.test_num)][5]
            player.Q7_ans = Constants.config[str(player.test_num)][6]
            player.Q8_ans = Constants.config[str(player.test_num)][7]
            player.Q9_ans = Constants.config[str(player.test_num)][8]
            player.Q10_ans = Constants.config[str(player.test_num)][9]
    


class Group(BaseGroup):

    def period_length(self):
        return parse_config_tasks()[self.round_number-1]['duration']

    def task(self):
        return parse_config_tasks()[self.round_number-1]['task']

    # Amount of players who will receive a luck based income
    lucky_players = models.IntegerField()

    # Votes for Tax Policy Systems
    progressivity_votes = models.IntegerField()
    tax_rate_votes = models.IntegerField()

    # Chosen Tax Policy Parameters
    chosen_progressivity = models.FloatField()
    chosen_tax_rate = models.FloatField()
    
    # Amount collected after the tax policy parameter has been decided
    tax_revenue = models.CurrencyField(min=0)

    # Luck (0 if luck is the system or 1 if performance)
    luck = models.IntegerField(min=0, max=1)

    def random_base_payments(self):
        """
        Assign payments at random for real effort game
        """

        # list with shuffled endowments
        endowments_for_shuffling = list(Constants.task_endowments)
        random.shuffle(endowments_for_shuffling)

        index_counter = 0
        for p in self.get_players():
            p.real_effort_earnings = endowments_for_shuffling[index_counter]
            p.base_earnings = p.real_effort_earnings
            index_counter += 1


    def ranking_income_assignment(self):
        """Assignment of endowment based on ranking"""

        game_scores = {}
        c = Constants

        for p in self.get_players():
            game_scores["{0}".format(p.id_in_group)] = p.game_score
        print(game_scores) # for debugging
        
        # Ranking scores
        ranked_scores = {}

        if self.session.config['real_effort_task'] == "Tetris":
            sorted_list = sorted(game_scores.values(), reverse=True)
        else: # the less is the diference between guess and actual number, the better
            sorted_list = sorted(game_scores.values(), reverse=False)

        # Control sorted_list
        print("sorted list of payoffs", sorted_list)

        for sorted_value in sorted_list:
            for key, value in game_scores.items():
                if value == sorted_value:
                    ranked_scores[key] = value
        print(ranked_scores) # for debugging
    
        # Control ranked_scores (They are correctly ranked)
        print(ranked_scores)

        # Assigning real effort incomes to players (Problem: each time a match occurs, the p.ranking increases in 1)
        for p in self.get_players():
            key_list = list(ranked_scores)
            for key, value in ranked_scores.items():
                num_key = int(key)
                # Control num_key (This one is also correct: ordered from lower game_score to max)
                print(num_key)
                if p.id_in_group == num_key:
                    ranking = int(key_list.index(key))
                    p.ranking = ranking + 1
                    p.real_effort_earnings = c.task_endowments[p.ranking - 1]
                    # This counter should increase only when the player id matches the key
                    print('Player Ranking: '+str(p.ranking))
                    print("Id of player "+str(p.id_in_group)+" matched with key "+str(num_key))
                elif p.id_in_group != num_key:
                    print("Id didn't match the respective key")
                else:
                    print("Error: No value of 'p.id_in_group' could be matched with any key")

    def base_income_assignment(self):
        """
        Method to assign income by luck/effort to each player inside a group

        Input: None
        Output: None
        """
        # assigning endowment to players in group by luck or effort
        raffler = random.SystemRandom().randrange(1, 101) # randrange doesn't include endpoint
        
        # if single value has been inputted as prob of luck
        if len(self.session.config["prob_of_luck"])==1:
            luck = raffler <= self.session.config["prob_of_luck"][0]
            print(f"raffler = {raffler}")
            print(f"prob_of_luck = {self.session.config['prob_of_luck'][0]}")
            print(f"luck for current group = {luck}")
        # if list
        elif len(self.session.config["prob_of_luck"])>1:
            luck = raffler <= self.session.config["prob_of_luck"][self.round_number - 1]
            print(f"raffler = {raffler}")
            print(f"prob_of_luck = {self.session.config['prob_of_luck'][self.round_number - 1]}")
            print(f"luck for current group = {luck}")

        self.luck = luck # storing the luck value

        to_shuffle_earnings = []

        shuffled_group_ids = []

        # Shuffling earnings and ids
        for p in self.get_players():
            shuffled_group_ids.append(p.id_in_group)
        random.SystemRandom().shuffle(shuffled_group_ids)

        # Tabulation variables used for indexing earnings into a list: dexrand is the index for the random list
        dexrand = 0
        dexskill = 0

        # NOTE: Here is were the income assignment takes place
        # Assigning income to players based on luck or skill in a 50/50 split
        for p in self.get_players():
            to_shuffle_earnings.append(p.real_effort_earnings)
        random.SystemRandom().shuffle(to_shuffle_earnings)
        for p in self.get_players():
            if luck == 0:
                p.base_earnings = to_shuffle_earnings[dexrand]
                dexrand = dexrand + 1
            elif luck == 1:
                p.base_earnings = Constants.task_endowments[dexskill]
                dexskill = dexskill + 1
                

    def set_payoffs(self):
        """
        Method to set round final payoffs (only from the interaction)

        Input: None
        Output: None
        """
        if self.session.config['tax_system'] == "tax_rate":
            chosen_tax_rates = []
            for p in self.get_players():
                chosen_tax_rates.append(p.tax_rate/100)

            # Sorting the values so we can take the median tax rate
            chosen_tax_rates.sort()
            if self.session.config['num_demo_participants'] == 9: # for production
                self.chosen_tax_rate = chosen_tax_rates[4]
            elif self.session.config['num_demo_participants'] == 2: # for testing
                self.chosen_tax_rate = (chosen_tax_rates[0] + chosen_tax_rates[1])/2

            for p in self.get_players():
                p.tax_payment = p.base_earnings * self.chosen_tax_rate

        elif self.session.config['tax_system'] == "progressivity":
            chosen_prog_level = []
            for p in self.get_players():
                chosen_prog_level.append(p.progressivity)

            # Sorting the values so we can take the median progressivity
            chosen_prog_level.sort()
            
            # assigning system 1 as default if all players timeout
            if chosen_prog_level[4] == float(0):
                self.chosen_progressivity = 1 
            else:   
                self.chosen_progressivity = chosen_prog_level[4]

            # To access to the tax rates of an specific progressivity level, turn chosen_progressivity into a string
            # so you can access the dictionary entry with the respective tax rates
            string_progressivity_level = str(self.chosen_progressivity)
            progressivity_tax_rates = ctrl.progressivity_levels_tax_rates[string_progressivity_level]

            # Using the tax endowments to define the income brackets (we'll create a new list with unique
            # endowments)
            task_endowments = list(dict.fromkeys(ctrl.task_endowments))
            task_endowments.sort()

            for p in self.get_players():
                if p.base_earnings <= task_endowments[0]:
                    p.tax_rate = progressivity_tax_rates[0]
                    p.tax_payment = progressivity_tax_rates[0]*p.base_earnings
                elif task_endowments[0] < p.base_earnings <= task_endowments[1]:
                    p.tax_rate = progressivity_tax_rates[1]
                    p.tax_payment = progressivity_tax_rates[1]*p.base_earnings
                elif task_endowments[1] < p.base_earnings <= task_endowments[2]:
                    p.tax_rate = progressivity_tax_rates[2]
                    p.tax_payment = progressivity_tax_rates[2]*p.base_earnings
                elif task_endowments[2] < p.base_earnings <= task_endowments[3]:
                    p.tax_rate = progressivity_tax_rates[3]
                    p.tax_payment = progressivity_tax_rates[3]*p.base_earnings
                elif task_endowments[3] < p.base_earnings <= task_endowments[4]:
                    p.tax_rate = progressivity_tax_rates[4]
                    p.tax_payment = progressivity_tax_rates[4]*p.base_earnings
                elif task_endowments[4] < p.base_earnings <= task_endowments[5]:
                    p.tax_rate = progressivity_tax_rates[5]
                    p.tax_payment = progressivity_tax_rates[5]*p.base_earnings

        # For both tax systems
        print(f"payoffs file = {self.session.config['payoffs_db']}")
        if self.session.config["payoffs_db"] == "": # if no file specified, use default system
            total_public_contribution = 0
            for p in self.get_players():
                total_public_contribution += p.tax_payment

            for p in self.get_players():
                if total_public_contribution <= 192:
                    p.public_income = 101 / (1 + 100 * math.exp(-0.025 * total_public_contribution)) - 1
                    private_productivity = Constants.alpha + Constants.beta * total_public_contribution
                else:
                    p.public_income = 101 / (1 + 100 * math.exp(-0.025 * 192)) - 1
                    private_productivity = Constants.alpha + Constants.beta * 192

                p.private_income = (p.base_earnings - p.tax_payment) * private_productivity
                # basline utility
                p.game_payoff = p.private_income + p.public_income - p.total_messaging_costs
        else:
            # TODO: define what to do in progressivity treatment

            # reading payoffs
            payoffs_db = pd.read_csv("MoneyPolitics/"+ self.session.config['payoffs_db'])
            print("payoffs db structure: ", payoffs_db)
            
            if self.session.config['tax_system'] == "tax_rate":            
                # getting payoffs db
                tax_rate = int(self.chosen_tax_rate*100)
                print("tax_rate: ", tax_rate)
                payoffs_selected_tax = payoffs_db.loc[payoffs_db["tax"]==tax_rate]

                for p in self.get_players():
                    string_payoff = str(int(p.base_earnings))
                    print("Selected tax: ", tax_rate)
                    print("Payoff selected tax: ", payoffs_selected_tax)
                    print("Payoff panda: ", payoffs_selected_tax[f"payoff_{string_payoff}"])
                    print("Payoff according to csv: ", payoffs_selected_tax[f"payoff_{string_payoff}"].iloc[0])
                    p.game_payoff = payoffs_selected_tax[f"payoff_{string_payoff}"].iloc[0] - p.total_messaging_costs

            else: # if progressivity
                for p in self.get_players():
                    tax_rate =  int(p.tax_rate*100)
                    print("tax_rate: ", tax_rate)
                    payoffs_selected_tax = payoffs_db.loc[payoffs_db["tax"]==tax_rate]

                    string_payoff = str(int(p.base_earnings))
                    print("Selected tax: ", tax_rate)
                    print("Payoff selected tax: ", payoffs_selected_tax)
                    print("Payoff panda: ", payoffs_selected_tax[f"payoff_{string_payoff}"])
                    print("Payoff according to csv: ", payoffs_selected_tax[f"payoff_{string_payoff}"].iloc[0])
                    p.game_payoff = payoffs_selected_tax[f"payoff_{string_payoff}"].iloc[0] - p.total_messaging_costs

                


            for p in self.get_players():
                string_payoff = str(int(p.base_earnings))
                print("Selected tax: ", tax_rate)
                print("Payoff selected tax: ", payoffs_selected_tax)
                print("Payoff panda: ", payoffs_selected_tax[f"payoff_{string_payoff}"])
                print("Payoff according to csv: ", payoffs_selected_tax[f"payoff_{string_payoff}"].iloc[0])
                p.game_payoff = payoffs_selected_tax[f"payoff_{string_payoff}"].iloc[0] - p.total_messaging_costs


# Function that creates a field to send messages according to the income of other player
def send_message_field(label):
    return models.BooleanField(
        # USar multiple checkbox
        blank=True,
        label=label,
        widget=forms.CheckboxInput
    )


class Player(BasePlayer):
    #Sum Game variables:
    for numb in range(1, Constants.sum_variables + 1):
        locals()['sum_{0}'.format(numb)] = models.IntegerField(blank = True)
    
    del numb

    for numb in range(1, Constants.sum_variables + 1):
        locals()['sum_{0}_correct'.format(numb)] = models.IntegerField(blank = True)
    
    del numb

    score_suma = models.IntegerField(initial=0)

    #Slider task:
    for numb in range(1, Constants.slider_variables + 1):
        locals()['slider_{0}'.format(numb)] = models.IntegerField(blank = True)

    del numb

    # def get_score(self):
    #     question_ans = [self.Q1_ans, self.Q2_ans, self.Q3_ans,self. Q4_ans, self.Q5_ans, self.Q6_ans, self.Q7_ans, self.Q8_ans, self.Q9_ans, self.Q10_ans]
    #     questions = [self.Question_1, self.Question_2, self.Question_3, self.Question_4, self.Question_5, self.Question_6, self.Question_7, self.Question_8, self.Question_9, self.Question_10]
    #     i = 0 
    #     for x in question_ans:
    #         if questions[i] == x:
    #             self.score += Constants.config['points'][i]
    #         i =i+1

    #     for x in questions:
    #         if x == 50:
    #             self.score_sliders += 1
    #     return self.score_sliders

    #TranscriptionTask:
    transcription_1 = models.StringField(default='')
    transcription_2 = models.StringField(default='')
    transcription_3 = models.StringField(default='')
    transcription_4 = models.StringField(default='')
    transcription_5 = models.StringField(default='')
    transcription_6 = models.StringField(default='')
    transcription_7 = models.StringField(default='')
    transcription_8 = models.StringField(default='')
    transcription_9 = models.StringField(default='')
    transcription_10 = models.StringField(default='')
    transcription_1_correct = models.StringField(default='')
    transcription_2_correct = models.StringField(default='')
    transcription_3_correct = models.StringField(default='')
    transcription_4_correct = models.StringField(default='')
    transcription_5_correct = models.StringField(default='')
    transcription_6_correct = models.StringField(default='')
    transcription_7_correct = models.StringField(default='')
    transcription_8_correct = models.StringField(default='')
    transcription_9_correct = models.StringField(default='')
    transcription_10_correct = models.StringField(default='')

    #RavensTask:
    rand_id = models.IntegerField(initial=0)
    test_num = models.IntegerField(initial=0)
    score = models.FloatField(initial=0)
    ranking = models.IntegerField(initial=0)
    Q1_ans = models.IntegerField(initial=0)
    Q2_ans = models.IntegerField(initial=0)
    Q3_ans = models.IntegerField(initial=0)
    Q4_ans = models.IntegerField(initial=0)
    Q5_ans = models.IntegerField(initial=0)
    Q6_ans = models.IntegerField(initial=0)
    Q7_ans = models.IntegerField(initial=0)
    Q8_ans = models.IntegerField(initial=0)
    Q9_ans = models.IntegerField(initial=0)
    Q10_ans = models.IntegerField(initial=0)
   
    Question_1 = models.IntegerField(
        choices=[1,2,3,4,5,6,7,8],
        label = '''
            Your Choice 
            '''
                )
    Question_2 = models.IntegerField(
        choices=[1,2,3,4,5,6,7,8],
        label = '''
            Your Choice 
            '''
                )
    Question_3 = models.IntegerField(
        choices=[1,2,3,4,5,6,7,8],
        label = '''
            Your Choice 
            '''
                )
    Question_4 = models.IntegerField(
        choices=[1,2,3,4,5,6,7,8],
        label = '''
            Your Choice 
            '''
                )
    Question_5 = models.IntegerField(
        choices=[1,2,3,4,5,6,7,8],
        label = '''
            Your Choice 
            '''
                )
    Question_6 = models.IntegerField(
        choices=[1,2,3,4,5,6,7,8],
        label = '''
            Your Choice 
            '''
                )
    Question_7 = models.IntegerField(
        choices=[1,2,3,4,5,6,7,8],
        label = '''
            Your Choice 
            '''
                )
    Question_8 = models.IntegerField(
        choices=[1,2,3,4,5,6,7,8],
        label = '''
            Your Choice 
            '''
                )
    Question_9 = models.IntegerField(
        choices=[1,2,3,4,5,6,7,8],
        label = '''
            Your Choice 
            '''
                )
    Question_10 = models.IntegerField(
        choices=[1,2,3,4,5,6,7,8],
        label = '''
            Your Choice 
            '''
                )
    def get_score(self):
        question_ans = [self.Q1_ans, self.Q2_ans, self.Q3_ans,self. Q4_ans, self.Q5_ans, self.Q6_ans, self.Q7_ans, self.Q8_ans, self.Q9_ans, self.Q10_ans]
        questions = [self.Question_1, self.Question_2, self.Question_3, self.Question_4, self.Question_5, self.Question_6, self.Question_7, self.Question_8, self.Question_9, self.Question_10]
        i = 0 
        for x in question_ans:
            if questions[i] == x:
                self.score += Constants.config['points'][i]
            i =i+1
        return self.score
    
    # Real Effort Earnings
    real_effort_earnings = models.CurrencyField(min=0)

    # Ranking on real effort task
    ranking = models.IntegerField(min=1, max=9)

    # Shuffled == True if player's income will be shuffled, False if not
    shuffled = models.BooleanField()

    # Earnings after the shuffling
    base_earnings = models.CurrencyField(min=0)

    # Earnings after messaging
    after_message_earnings = models.CurrencyField(min=0)

    # Possible messages
    message = models.LongStringField(max_length=Constants.max_chars, blank=True, label="")
    #if session.conf['msg_type'] == 'double': # Message when double msging is activated
    message_d = models.LongStringField(max_length=Constants.max_chars, blank=True, label="")

    # Number of Messages Sent
    num_messages_sent = models.IntegerField(min=0)
    # Messages Received in String Format
    messages_received = models.StringField(initial="")
    # Number of messages received
    amount_messages_received = models.IntegerField(min=0)
    # Total cost for sending the messages
    total_messaging_costs = models.CurrencyField(initial=0)

    # practice tax rate
    practice_tax_rate = models.FloatField(min=0, max=100, label="")

    # suggested policy parameter
    suggested_tax_rate = models.IntegerField(min=0, max=100, label="") # suggested tax rate
    suggested_progressivity = models.IntegerField(min=1, max=5, choices=Constants.progressivity_levels, label="") # suggested tax rate

    # Preferred Tax Policy Parameters
    progressivity = models.IntegerField(min=1, max=5, choices=Constants.progressivity_levels, label="", widget=widgets.RadioSelect)
    if settings.LANGUAGE_CODE=="en": # label in english
        #tax_rate = models.FloatField(min=0, max=100, label="", widget=widgets.RadioSelect, choices=[[round(item*100,0), str(int(round(item*100,0)))+"%"] for item in list(numpy.arange(0, 1.05, .05))])
        tax_rate = models.FloatField(min=0, max=100, label="")
    elif settings.LANGUAGE_CODE=="es": # labels in spanish
        # tax_rate = models.FloatField(min=0, max=100, label="", widget=widgets.RadioSelect, choices=[[round(item*100,0), str(int(round(item*100,0)))+"%"] for item in list(numpy.arange(0, 1.05, .05))])
        tax_rate = models.FloatField(min=0, max=100, label="")
    else:
        print("ERROR: Undefined LANGUAGE_CODE used")

    tax_payment = models.CurrencyField(min=0)

    # Player's score for game played
    game_score = models.IntegerField()
    diamond_guess = models.IntegerField(min=0, max=1000)
    diamond_actual = models.IntegerField()

    # Earnings of the player
    private_income = models.CurrencyField(min=0)
    public_income = models.CurrencyField(min=0)

    def message_receivers_choices(self):
        """
        Determines the list of possible message receivers in experiment.
        It can be a list with messaging

        Input: None
        Output: List with name of message receivers fields
            if single messaging is activated, it'll contain only the single msg receiver fields
            if double messaging is activated, it'll contain both the single and double msg receiver fields
        """

        # Converts self income from currency to string (eliminates points label)
        if self.base_earnings < 10:
            string_income = str(self.base_earnings)[:1]
        elif self.base_earnings < 100:
            string_income = str(self.base_earnings)[:2]
        else:
            string_income = str(self.base_earnings)[:3]

        # List with all the possible message receivers (each of them represented as an entry/field on this list) without
        # the players self income
        message_receivers = []

        # 1. Defining the complete set of choices without excluding ourselves

        # counter of players with income of 15 points (first message)
        counter15 = 1
        counter25 = 1

        # Because the task endowments are integers, we need to convert them to strings
        str_task_endowments = []
        for endowment in Constants.task_endowments:
            str_task_endowments.append(str(endowment))

        # 1.1. Defining list of message receiver fields for single messaging
        for earning in str_task_endowments:
            if earning != '15' and earning != '25':
                receiver = 'income_{}'.format(earning)
                message_receivers.append(receiver)
            elif earning == '15':
                receiver = 'income_{}'.format(earning)+'_{}'.format(str(counter15))
                message_receivers.append(receiver)
                counter15 += 1
            elif earning == '25':
                receiver = 'income_{}'.format(earning)+'_{}'.format(str(counter25))
                message_receivers.append(receiver)
                counter25 += 1
            else:
                print("Error: Invalid Income Analyzed")

        # 1.2. Defining list of message receiver fields for second message (double messaging only)
        if self.session.config['msg_type'] == 'double':
            # counter of players with income of 15 points (double messaging)
            counter15_d = 1
            counter25_d = 1

            for earning in str_task_endowments:
                if earning != '15' and earning != '25':
                    receiver = 'income_{}_d'.format(earning)
                    message_receivers.append(receiver)
                elif earning == '15':
                    receiver = 'income_{}'.format(earning)+'_{}_d'.format(str(counter15_d))
                    message_receivers.append(receiver)
                    counter15_d += 1
                elif earning == '25':
                    receiver = 'income_{}'.format(earning)+'_{}_d'.format(str(counter25_d))
                    message_receivers.append(receiver)
                    counter25_d += 1
                else:
                    print("Error: Invalid Income Analyzed")
        print(str(message_receivers))

        # 2. We'll identify who are the ids of the ones whose income is 15 or 25
        players15 = []
        players25 = []

        for p in self.group.get_players():
            if p.base_earnings == 15:
                players15.append(p.id_in_group)
            elif p.base_earnings == 25:
                players25.append(p.id_in_group)

        # 3. The exclusion of ourselves from the alternatives is going to take place
        
        # 3.1. Excluding in single messaging
        if self.id_in_group not in players15 and self.id_in_group not in players25:
            option_to_remove = 'income_{}'.format(string_income)
        elif self.id_in_group in players15:
            option_to_remove = 'income_{}'.format(string_income) + \
                               '_{}'.format(str(players15.index(self.id_in_group) + 1))
        elif self.id_in_group in players25:
            option_to_remove = 'income_{}'.format(string_income) + \
                               '_{}'.format(str(players25.index(self.id_in_group) + 1))
        message_receivers.remove(option_to_remove)

        # 3.2. Excluding in double messaging
        if self.session.config['msg_type'] == 'double':
            if self.id_in_group not in players15 and self.id_in_group not in players25:
                option_to_remove = 'income_{}_d'.format(string_income)
            elif self.id_in_group in players15:
                option_to_remove = 'income_{}'.format(string_income) + \
                                '_{}_d'.format(str(players15.index(self.id_in_group) + 1))
            elif self.id_in_group in players25:
                option_to_remove = 'income_{}'.format(string_income) + \
                                '_{}_d'.format(str(players25.index(self.id_in_group) + 1))
            message_receivers.remove(option_to_remove)

        return message_receivers

    # Id of players who received the message of an specific player
    messages_receivers = models.StringField(initial="")

    # Fields to choose the message receivers according to income
    if settings.LANGUAGE_CODE=="en": # labels in english
        # defining receiver fields for first message
        income_9 = send_message_field('Initial Wealth 9')
        income_15_1 = send_message_field('Initial Wealth 15 (#1)')
        income_15_2 = send_message_field('Initial Wealth 15 (#2)')
        income_15_3 = send_message_field('Initial Wealth 15 (#3)')
        income_25_1 = send_message_field('Initial Wealth 25 (#1)')
        income_25_2 = send_message_field('Initial Wealth 25 (#2)')
        income_40 = send_message_field('Initial Wealth 40')
        income_80 = send_message_field('Initial Wealth 80')
        income_125 = send_message_field('Initial Wealth 125')

        # if session.config['msg_type'] == 'double': # defining receiver fields for second message
        income_9_d = send_message_field('Initial Wealth 9')
        income_15_1_d = send_message_field('Initial Wealth 15 (#1)')
        income_15_2_d = send_message_field('Initial Wealth 15 (#2)')
        income_15_3_d = send_message_field('Initial Wealth 15 (#3)')
        income_25_1_d = send_message_field('Initial Wealth 25 (#1)')
        income_25_2_d = send_message_field('Initial Wealth 25 (#2)')
        income_40_d = send_message_field('Initial Wealth 40')
        income_80_d = send_message_field('Initial Wealth 80')
        income_125_d = send_message_field('Initial Wealth 125')

    elif settings.LANGUAGE_CODE=="es": # labels in spanish
        # defining receiver fields for first message
        income_9 = send_message_field('Ingreso 9')
        income_15_1 = send_message_field('Ingreso 15 (#1)')
        income_15_2 = send_message_field('Ingreso 15 (#2)')
        income_15_3 = send_message_field('Ingreso 15 (#3)')
        income_25_1 = send_message_field('Ingreso 25 (#1)')
        income_25_2 = send_message_field('Ingreso 25 (#2)')
        income_40 = send_message_field('Ingreso 40')
        income_80 = send_message_field('Ingreso 80')
        income_125 = send_message_field('Ingreso 125')
    
        # if session.config['msg_type'] == 'double': # defining receiver fields for second message
        income_9_d = send_message_field('Ingreso 9')
        income_15_1_d = send_message_field('Ingreso 15 (#1)')
        income_15_2_d = send_message_field('Ingreso 15 (#2)')
        income_15_3_d = send_message_field('Ingreso 15 (#3)')
        income_25_1_d = send_message_field('Ingreso 25 (#1)')
        income_25_2_d = send_message_field('Ingreso 25 (#2)')
        income_40_d = send_message_field('Ingreso 40')
        income_80_d = send_message_field('Ingreso 80')
        income_125_d = send_message_field('Ingreso 125')

    else:
        print("ERROR: Undefined LANGUAGE_CODE used")


    def calculate_messages_sent(self):
        """
        Calculates the number of messages sent

        Input: None
        Output: number of messages sent (int)
        """

        messages_sent = 0 # messages sent counter

        # First message
        if self.income_9 is True:
            messages_sent += 1
        if self.income_15_1 is True:
            messages_sent += 1
        if self.income_15_2 is True:
            messages_sent += 1
        if self.income_15_3 is True:
            messages_sent += 1
        if self.income_25_1 is True:
            messages_sent += 1
        if self.income_25_2 is True:
            messages_sent += 1
        if self.income_40 is True:
            messages_sent += 1
        if self.income_80 is True:
            messages_sent += 1
        if self.income_125 is True:
            messages_sent += 1

        # Second message
        if self.session.config['msg_type'] == "double":
            if self.income_9_d is True:
                messages_sent += 1
            if self.income_15_1_d is True:
                messages_sent += 1
            if self.income_15_2_d is True:
                messages_sent += 1
            if self.income_15_3_d is True:
                messages_sent += 1
            if self.income_25_1_d is True:
                messages_sent += 1
            if self.income_25_2_d is True:
                messages_sent += 1
            if self.income_40_d is True:
                messages_sent += 1
            if self.income_80_d is True:
                messages_sent += 1
            if self.income_125_d is True:
                messages_sent += 1

        return messages_sent

    # Game payoff (without belief elicitation payoff)
    game_payoff = models.CurrencyField(min=0)

    # Belief elicitation fields
    guessed_ranking = models.IntegerField(choices=[rank for rank in range(1,10)], widget=widgets.RadioSelect)
    guessed_ranking_payoff = models.CurrencyField(min=0)

    guessed_system = models.StringField(choices=["performance", "luck"], widget=widgets.RadioSelect)
    guessed_system_payoff = models.CurrencyField(min=0)

    belief_elicitation_payoff = models.CurrencyField(min=0)
