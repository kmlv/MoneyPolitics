from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants

import re


class Instructions(Page):
    group_by_arrival_time = True


class RealEffort(Page):
    pass


class LuckEffortInformation(Page):
    pass
"""
    def before_next_page(self):
        # This page was created in order to define a method in which the eligibility to receive a message is defined
        # Only used for future analysis, but no current relevance on the code
        player = self.player
        if player.base_earnings <= Constants.poverty_line:
            player.eligible_receiver = True
        else:
            player.eligible_receiver = False
"""


class PreparingMessage(Page):
    form_model = 'player'
    form_fields = ['message', 'amount_message_receivers']

    def error_message(self, values):
        player = self.player
        if player.message == '' and player.message_receivers != 0:
            return "If you don't want to send a message, choose 0 as the amount of message receivers"

    def before_next_page(self):
        group = self.group
        player = self.player

        # Sender id
        sender_id = player.id_in_group

        # List of players who can receive a message
        receivers = group.choosing_message_receiver()

        counter = 1
        # To send the message only to players who have received a
        for p in group.get_players() and counter <= player.amount_message_receivers:
            if p.id_in_group in receivers:
                # Assigning a message to the p.id_in_group player
                p.messages_received += str(sender_id) + "," + player.message + ";"
                player.messages_receivers += str(p.id_in_group) + ","
            counter += 1


class ReceivingMessage(Page):

    def vars_for_template(self):
        player = self.player

        # Obtaining the received messages
        raw_messages = player.messages_received.split(";")
        clean_messages = []

        for item in raw_messages:
            clean_messages.append(item.split(",", 1)[1])

        # Loop across received messages in the html in order to show them distinctly (with another color, size, etc)
        return {"received_messages": clean_messages}


class TaxSystem(Page):
    form_model = 'player'
    form_fields = ['preferred_tax_system']


class TaxDecision(WaitPage):
    def after_all_players_arrive(self):
        # Count the number of 0s and 1s. According to that, decide which system is going to be implemented
        pass


class TaxRateParameter(Page):
    # Displayed only if tax rate sys wins
    pass


class ProgressivityParameter(Page):
    # Displayed only if tax rate sys loses
    pass


class ResultsWaitPage(WaitPage):
    def after_all_players_arrive(self):
        pass


class Results(Page):
    pass


page_sequence = [
    Instructions,
    RealEffort,
    LuckEffortInformation,
    PreparingMessage,
    ReceivingMessage,
    TaxSystem,
    ProgressivityParameter,
    TaxRateParameter,
    ResultsWaitPage,
    Results
]
