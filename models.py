from otree.api import (
    models, BaseConstants, BaseSubsession, BaseGroup, BasePlayer
)

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
    # Maximum endowment considered for a player to be in "poverty"
    poverty_line = ctrl.poverty_line
    # Possible Tax Systems
    possible_tax_systems = ctrl.possible_tax_systems


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):

    # Amount of players who will receive a luck based income
    lucky_players = models.IntegerField()

    # Votes for Tax Policy Systems
    progressivity_votes = models.IntegerField()
    tax_rate_votes = models.IntegerField()

    # Chosen Tax Policy System
    tax_policy_system = models.IntegerField(choices=Constants.possible_tax_systems)

    # Chosen Tax Policy Parameters
    chosen_progressivity = models.FloatField()
    chosen_tax_rate = models.FloatField()

    # Amount collected after the tax policy parameter has been decided
    tax_revenue = models.CurrencyField(min=0)

    def ranking_income_assignment(self):
        # Assignment of endowment based on ranking
        game_scores = {}
        c = Constants

        for p in self.get_players():
            game_scores["{0}".format(p.id_in_group)] = p.game_score

        # Ranking scores
        ranked_scores = {}
        sorted_list = sorted(game_scores.values())

        for sorted_value in sorted_list:
            for key, value in game_scores.items():
                if value == sorted_value:
                    ranked_scores[key] = value

        # Assigning real effort incomes to players
        counter_ranking = 0
        for p in self.get_players():
            for key, value in ranked_scores.items():
                num_key = int(key)
                if p.id_in_group == num_key:
                    p.ranking = counter_ranking
                    p.real_effort_earnings = c.task_endowments[p.ranking]
                    counter_ranking += 1

    def base_income_assignment(self):
        # Assignment of income by luck/effort

        # luck: 0 if 3 people is going to be paid by luck, 1 if they are going to be 6
        luck = random.SystemRandom().randint(0, 1)
        c = Constants

        to_shuffle_earnings3 = []
        to_shuffle_earnings6 = []

        shuffled_ranks = []

        all_the_players = self.get_players()
        shuffled_players = random.SystemRandom().shuffle(all_the_players)

        for p in shuffled_players:
            shuffled_ranks.append(p.id_in_group)

        shuffled_ranks_3 = shuffled_ranks[:3]
        shuffled_ranks_6 = shuffled_ranks[:6]

        # Randomizing the real effort income for later assignment
        if luck == 0:
            for x in shuffled_ranks_3:
                to_shuffle_earnings3.append(c.task_endowments[x-1])
            self.lucky_players = 3
            random.SystemRandom().shuffle(to_shuffle_earnings3)
        elif luck == 1:
            for x in shuffled_ranks_6:
                to_shuffle_earnings6.append(c.task_endowments[x-1])
            self.lucky_players = 6
            random.SystemRandom().shuffle(to_shuffle_earnings6)
        else:
            print("Error: No luck values registered for shuffling")

        # Counters for assignment of shuffled earnings
        j3 = 0
        j6 = 0

        # Assignment of shuffled earnings
        for p in self.get_players():
            if luck == 0:
                if p.ranking in shuffled_ranks_3:
                    p.base_earnings = to_shuffle_earnings3[j3]
                    p.shuffled = True
                    j3 += 1
                elif p.ranking not in shuffled_ranks_3:
                    p.base_earnings = p.real_effort_earnings
                    p.shuffled = False
                else:
                    print("Error: No 'player.ranking' value for assignment of shuffled earning")
            elif luck == 1:
                if p.ranking in shuffled_ranks_6:
                    p.base_earnings = to_shuffle_earnings6[j6]
                    p.shuffled = True
                    j6 += 1
                elif p.ranking not in shuffled_ranks_6:
                    p.base_earnings = p.real_effort_earnings
                    p.shuffled = False
                else:
                    print("Error: No 'player.ranking' value for assignment of shuffled earning")
            else:
                print("Error: No 'luck' value for assignment of shuffled earning")

    def tax_parameter_selection(self):
        # Provisional function to determine the tax parameter (has to be changed later/only for demo purposes)

        for p in self.get_players():
            if p.id_in_group == 1:
                self.chosen_progressivity = p.progressivity
                self.chosen_tax_rate = p.tax_rate

    def set_payoffs(self):
        for p in self.get_players():
            p.payoff = p.base_earnings


class Player(BasePlayer):

    # Real Effort Earnings
    real_effort_earnings = models.CurrencyField(min=0)

    # Ranking on real effort task
    ranking = models.IntegerField(min=1, max=9)

    # Shuffled == True if player's income will be shuffled, False if not
    shuffled = models.BooleanField()

    # Earnings after the shuffling
    base_earnings = models.CurrencyField(min=0)

    # Message to be sent (It should only have 500 characters. This has been implemented on PreparingMessage.html)
    message = models.CharField(max_length=500, label='Write the message you want to send (max. 500 characters)')
    # Amount of receivers of player's message (players with 9 or 15)
    amount_message_receivers = models.IntegerField(min=0, max=Constants.players_per_group, label='Write your preferred '
                                                                                                 'number of message '
                                                                                                 'receivers')
    # Id of players who received the message of an specific player
    messages_receivers = models.StringField(initial="")

    messages_received = models.StringField(initial="")
    # Number of messages received
    amount_messages_received = models.IntegerField(min=0)
    # Total cost for sending the messages
    total_messaging_costs = models.CurrencyField()

    preferred_tax_system = models.CharField(choices=Constants.possible_tax_systems)
    # Preferred Tax Policy Parameters
    progressivity = models.FloatField(min=0)
    tax_rate = models.FloatField(min=0)

    # Player's score for game played
    game_score = models.IntegerField()
