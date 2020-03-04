from otree.api import (
    models, BaseConstants, BaseSubsession, BaseGroup, BasePlayer, widgets
)

from django import forms

import controls as ctrl
import random


author = 'Marco Gutierrez and Skyler Stewart'

doc = """
Money and Politics App
"""


class Constants(BaseConstants):
    name_in_url = 'DecisionStudy'
    players_per_group = 9
    num_rounds = 2
    instructions_template = "MoneyPolitics/Instructions.html"
    instructions_button = "MoneyPolitics/Instructions_Button.html"

    # Real Effort Tasks
    tetris = "MoneyPolitics/Tetris.html"
    diamonds = "MoneyPolitics/Diamonds.html"

    # There are some parameters that may vary during the development of this app. In order to make this as soft coded as
    # possible, the code should be flexible enough to allow changes in this ones and obtain them from an external
    # .py/txt file (If you find a better way, feel free to update the code with it)
    task_endowments = ctrl.task_endowments
    number_of_messages = ctrl.number_of_messages
    message_cost = ctrl.message_cost
    progressivity_levels = ctrl.progressivity_levels


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):

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

    # TODO: The ranking_income_assignment is assigning values, but not according to the game scores
    # (We need to fix that)

    def ranking_income_assignment(self):
        # Assignment of endowment based on ranking
        game_scores = {}
        c = Constants

        for p in self.get_players():
            game_scores["{0}".format(p.id_in_group)] = p.game_score
        print(game_scores) # for debugging
        
        # Ranking scores
        ranked_scores = {}

        if self.session.config['treatment'] == "Tetris":
            sorted_list = sorted(game_scores.values(), reverse=True)
        else:
            # When playing Diamonds a higher score is worse (so we reverse the sort)
            sorted_list = sorted(game_scores.values()) 
        print(sorted_list) # for debugging

        # Control sorted_list
        print(sorted_list)

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
        # Assignment of income by luck/effort
        # Not working properly: People who earn sth by luck/effort are getting the same endowments (e.g. 125)
        # luck: 0 if 3 people is going to be paid by luck, 1 if they are going to be 6
        luck = random.SystemRandom().randint(0, 1)

        to_shuffle_earnings = []

        shuffled_group_ids = []

        # Shuffling earnings and ids
        for p in self.get_players():
            shuffled_group_ids.append(p.id_in_group)
        random.SystemRandom().shuffle(shuffled_group_ids)

        shuffled_ids_3 = shuffled_group_ids[:3]
        shuffled_ids_6 = shuffled_group_ids[:6]

        for p in self.get_players():
            if luck == 0:
                if p.id_in_group in shuffled_ids_3:
                    to_shuffle_earnings.append(p.real_effort_earnings)
                elif p.id_in_group in shuffled_ids_3:
                    print("Player "+str(p.id_in_group)+" was not shuffled")
                else:
                    print("Error: No 'p.id_in_group' value for comparison")
                to_shuffle_earnings3 = to_shuffle_earnings[:3]
                print(to_shuffle_earnings3)
                random.SystemRandom().shuffle(to_shuffle_earnings3)
                print(to_shuffle_earnings3)
            elif luck == 1:
                if p.id_in_group in shuffled_ids_6:
                    to_shuffle_earnings.append(p.real_effort_earnings)
                elif p.id_in_group in shuffled_ids_6:
                    print("Player "+str(p.id_in_group)+" was not shuffled")
                else:
                    print("Error: No 'p.id_in_group' value for comparison")
                to_shuffle_earnings6 = to_shuffle_earnings[:6]
                print(to_shuffle_earnings6)
                random.SystemRandom().shuffle(to_shuffle_earnings6)
                print(to_shuffle_earnings6)
            else:
                print("Error: No 'luck' value for assignment to to_shuffle_earning")

        print(shuffled_ids_3)
        print(shuffled_ids_6)

        # Counters for assignment of shuffled earnings
        j3 = 0
        j6 = 0

        # Assignment of shuffled earnings
        for p in self.get_players():
            if luck == 0:
                if p.id_in_group in shuffled_ids_3:
                    p.base_earnings = to_shuffle_earnings3[j3]
                    p.shuffled = True
                    j3 += 1
                    print("Player "+str(p.id_in_group)+" has now an income of "+str(p.base_earnings))
                elif p.id_in_group not in shuffled_ids_3:
                    p.base_earnings = p.real_effort_earnings
                    p.shuffled = False
                else:
                    print("Error: No 'player.id_in_group' value for assignment of shuffled earning")
            elif luck == 1:
                if p.id_in_group in shuffled_ids_6:
                    p.base_earnings = to_shuffle_earnings6[j6]
                    p.shuffled = True
                    j6 += 1
                elif p.id_in_group not in shuffled_ids_6:
                    p.base_earnings = p.real_effort_earnings
                    p.shuffled = False
                else:
                    print("Error: No 'player.id_in_group' value for assignment of shuffled earning")
            else:
                print("Error: No 'luck' value for assignment of shuffled earning")

    def tax_parameter_selection(self):
        # Provisional function to determine the tax parameter (has to be changed later/only for demo purposes)

        for p in self.get_players():
            if p.id_in_group == 1:
                self.chosen_progressivity = p.progressivity
                self.chosen_tax_rate = p.tax_rate

    def set_payoffs(self):
        if self.session.config['tax_system'] == "tax_rate":
            chosen_tax_rates = []
            for p in self.get_players():
                chosen_tax_rates.append(p.tax_rate)

            # Sorting the values so we can take the median tax rate
            chosen_tax_rates.sort()
            self.chosen_tax_rate = chosen_tax_rates[4]

            for p in self.get_players():
                p.payoff = (1 - self.chosen_tax_rate)*p.after_message_earnings

        elif self.session.config['tax_system'] == "progressivity":
            chosen_prog_level = []
            for p in self.get_players():
                chosen_prog_level.append(p.progressivity)

            # Sorting the values so we can take the median progressivity
            chosen_prog_level.sort()
            self.chosen_progressivity = chosen_prog_level[4]

            # Before setting the payoffs, we need to acknowledge that at this point of the game, the players may have
            # spent their money in sending messages to all the other players, so the income brackets would be income_{i}
            # - 8 points (max possible total messaging costs)
            for p in self.get_players():
                if p.after_message_earnings >=1 or p.after_message_earnings <= 9:
                    p.payoff = (1 - self.chosen_tax_rate)*p.after_message_earnings
                elif p.after_message_earnings >=7 or p.after_message_earnings <= 15:
                elif p.after_message_earnings >=17 or p.after_message_earnings <= 25:
                elif p.after_message_earnings >=33 or p.after_message_earnings <= 40:
                elif p.after_message_earnings >=73 or p.after_message_earnings <= 80:
                elif p.after_message_earnings >=118 or p.after_message_earnings <= 125:


# Function that creates a field to send messages according to the income of other player
def send_message_field(label):
    return models.BooleanField(
        # USar multiple checkbox
        blank=True,
        label=label,
        widget=forms.CheckboxInput
    )


class Player(BasePlayer):

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

    message = models.LongStringField(max_length=500, blank=True, label='Write the message you want to send (max. 500 characters)')

    # Field for deciding the message receiver
    # message_receivers = models.CharField(label='', initial = None, default='Unspecified',
    #                                     widget=forms.widgets.CheckboxSelectMultiple)

    # Messages Received in String Format
    messages_received = models.StringField(initial="")
    # Number of messages received
    amount_messages_received = models.IntegerField(min=0)
    # Total cost for sending the messages
    total_messaging_costs = models.CurrencyField()

    # Preferred Tax Policy Parameters
    progressivity = models.IntegerField(choices=Constants.progressivity_levels)
    tax_rate = models.FloatField(min=0, max=1, widget=widgets.Slider(attrs={'step': '0.05'}))
    
    # Player's score for game played
    game_score = models.IntegerField()
    diamond_guess = models.IntegerField(min=0, max=1000)
    diamond_actual = models.IntegerField()

    def message_receivers_choices(self):
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

        # 1. The complete set of choices without excluding ourselves is going to be defined
        counter15 = 1
        counter25 = 1

        # 1.5 Because the task endowments are integers, we need to convert them to strings
        str_task_endowments = []
        for endowment in Constants.task_endowments:
            str_task_endowments.append(str(endowment))

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
        if self.id_in_group not in players15 and self.id_in_group not in players25:
            option_to_remove = 'income_{}'.format(string_income)
        elif self.id_in_group in players15:
            option_to_remove = 'income_{}'.format(string_income) + \
                               '_{}'.format(str(players15.index(self.id_in_group) + 1))
        elif self.id_in_group in players25:
            option_to_remove = 'income_{}'.format(string_income) + \
                               '_{}'.format(str(players25.index(self.id_in_group) + 1))
        message_receivers.remove(option_to_remove)

        print(str(message_receivers))
        return message_receivers

    # Id of players who received the message of an specific player
    messages_receivers = models.StringField(initial="")

    # Fields to choose the message receivers according to income
    income_9 = send_message_field('Income 9')
    income_15_1 = send_message_field('Income 15 (Player 1)')
    income_15_2 = send_message_field('Income 15 (Player 2)')
    income_15_3 = send_message_field('Income 15 (Player 3)')
    income_25_1 = send_message_field('Income 25 (Player 1)')
    income_25_2 = send_message_field('Income 25 (Player 2)')
    income_40 = send_message_field('Income 40')
    income_80 = send_message_field('Income 80')
    income_125 = send_message_field('Income 125')
