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
    num_rounds = 1
    instructions_template = "MoneyPolitics/Instructions.html"
    instructions_button = "MoneyPolitics/Instructions_Button.html"

    # Real Effort Tasks
    tetris = "MoneyPolitics/Tetris.html"
    diamonds = "MoneyPolitics/Diamonds.html"

    # Players whose income is going to be shuffled
    shuffled_ranks_3 = ctrl.shuffled_ranks_3
    shuffled_ranks_6 = ctrl.shuffled_ranks_6

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

    # Amount collected after the tax policy parameter has been decided
    tax_revenue = models.CurrencyField(min=0)

    def provisional_ranking_income_assignment(self):
        # Provisional assignment of endowment (Created only for the next meeting with LP)
        for p in self.get_players():
            p_id = p.id_in_group
            p.real_effort_earnings = Constants.task_endowments[p_id - 1]
            p.ranking = p_id

    def base_income_assignment(self):
        # Assignment of income by luck/effort

        # luck: 0 if 3 people is going to be paid by luck, 1 if they are going to be 6
        luck = random.SystemRandom().randint(0, 1)
        c = Constants

        to_shuffle_earnings3 = []
        to_shuffle_earnings6 = []

        # Randomizing the real effort income for later assignment
        if luck == 0:
            for x in c.shuffled_ranks_3:
                to_shuffle_earnings3.append(c.task_endowments[x])
            self.lucky_players = 3
            random.SystemRandom().shuffle(to_shuffle_earnings3)
        elif luck == 1:
            for x in c.shuffled_ranks_6:
                to_shuffle_earnings6.append(c.task_endowments[x])
            self.lucky_players = 6
            random.SystemRandom().shuffle(to_shuffle_earnings6)
        else:
            print("Error: No luck values registered for shuffling")

        # Assignment of shuffled earnings
        j3 = 0
        j6 = 0
        for p in self.get_players():
            if luck == 0:
                if p.ranking in c.shuffled_ranks_3:
                    p.base_earnings = to_shuffle_earnings3[j3]
                    j3 += 1
                elif p.ranking not in c.shuffled_ranks_3:
                    p.base_earnings = p.real_effort_earnings
                else:
                    print("Error: No 'player.ranking' value for assignment of shuffled earning")
            elif luck == 1:
                if p.ranking in c.shuffled_ranks_6:
                    p.base_earnings = to_shuffle_earnings6[j6]
                    j6 += 1
                elif p.ranking not in c.shuffled_ranks_6:
                    p.base_earnings = p.real_effort_earnings
                else:
                    print("Error: No 'player.ranking' value for assignment of shuffled earning")
            else:
                print("Error: No 'luck' value for assignment of shuffled earning")

    def choosing_message_receiver(self):
        receivers = []
        for p in self.get_players():
            if p.real_effort_earnings <= Constants.poverty_line:
                receivers.append(p.id_in_group)

        # To select randomly the ones that will receive the messages (Note that with this, ff the first one on the
        # list receives one message, he will receive the other ones too)
        random.SystemRandom().shuffle(receivers)
        return receivers


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
