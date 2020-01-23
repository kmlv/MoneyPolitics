from otree.api import (
    models, BaseConstants, BaseSubsession, BaseGroup, BasePlayer
)

import controls as ctrl

author = 'Marco Gutierrez and Skyler Stewart'

doc = """
Money and Politics App
"""


class Constants(BaseConstants):
    name_in_url = 'DecisionStudy'
    players_per_group = 9
    num_rounds = 1

    # There are some parameters that may vary during the development of this app. In order to make this as soft coded as
    # possible, the code should be flexible enough to allow changes in this ones and obtain them from an external
    # .py/txt file (If you find a better way, feel free to update the code with it)
    task_endowments = ctrl.task_endowments
    number_of_messages = ctrl.number_of_messages
    message_cost = ctrl.message_cost


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):

    # Amount of players who will receive a luck based income
    lucky_players = models.IntegerField()

    # Chosen Tax Policy Parameters
    chosen_progressivity = models.FloatField(min=0)
    chosen_tax_rate = models.FloatField(min=0)

    # Amount collected after the tax policy parameter has been decided
    tax_revenue = models.CurrencyField(min=0)


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
    message_receivers = models.IntegerField(min=0, max=Constants.players_per_group, label='Write your preferred number '
                                                                                          'of message receivers')
    # Eligible receiver (player with 9 or 15 as endowment)
    eligible_receiver = models.BooleanField()
    # Actual receiver of at least one of the messages
    actual_receiver = models.BooleanField()
    # Number of messages received
    messages_received = models.IntegerField(min=0)
    # Total cost for sending the messages
    total_messaging_costs = models.CurrencyField()

    # Preferred Tax Policy Parameters
    progressivity = models.FloatField(min=0)
    tax_rate = models.FloatField(min=0)
