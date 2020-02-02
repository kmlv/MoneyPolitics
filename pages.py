from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants

import re


class GroupingPage(WaitPage):
    group_by_arrival_time = True


class Introduction(Page):
    pass


class RealEffort(Page):
    pass


class Tetris(Page):
    form_model = 'player'
    form_fields = ['game_score']
    timeout_seconds = 60


class EffortResultsWaitPage(WaitPage):

    # Provisional assignment of scores (This has to be changed to a func that uses the ranking obtained in the real
    # effort game)
    def after_all_players_arrive(self):
        self.group.ranking_income_assignment()
        self.group.base_income_assignment()


class RealEffortResults(Page):

    def vars_for_template(self):
        player = self.player

        effort_or_luck = ""

        if player.shuffled is True:
            effort_or_luck = "Luck"
        elif player.shuffled is False:
            effort_or_luck = "Effort"
        else:
            print("Error: 'player.shuffled' has no value")

        income = player.base_earnings
        ranking = player.ranking

        return {'ranking': ranking, 'income': income, 'effort_or_luck': effort_or_luck}


class PreparingMessage(Page):
    form_model = 'player'
    form_fields = ['message', 'amount_message_receivers']

    # This page has to change to the new version required in the todo list

    def error_message(self, values):
        player = self.player
        if player.message == '' and player.message_receivers != 0:
            return "If you don't want to send a message, choose 0 as the amount of message receivers"


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

    def before_next_page(self):
        player = self.player
        group = self.group

        if player.preffered_tax_system == 0:
            group.progressivity_votes += 1
        elif player.preffered_tax_system == 1:
            group.tax_rate_votes += 1
        else:
            print("Error: No value for tax_rate_votes")


class TaxDecisionWaitPage(WaitPage):
    def after_all_players_arrive(self):
        # Count the number of 0s and 1s. According to that, decide which system is going to be implemented

        group = self.group
        if group.progressivity_votes >= group.tax_rate_votes:
            # System Chosen: Progressivity Sys
            group.tax_policy_system = 0
        elif group.progressivity_votes < group.tax_rate_votes:
            # System Chosen: Tax Rate Sys
            group.tax_policy_system = 1
        else:
            print("Error: No value for Tax Policy System")


class ProgressivityParameter(Page):
    # Displayed only if tax rate sys loses

    form_model = 'player'
    form_fields = ['progressivity']

    def is_displayed(self):
        return self.group.tax_policy_system == 0


class TaxRateParameter(Page):
    # Displayed only if tax rate sys wins

    form_model = 'player'
    form_fields = ['tax_rate']

    def is_displayed(self):
        return self.group.tax_policy_system == 1


class ResultsWaitPage(WaitPage):
    def after_all_players_arrive(self):
        pass


class Results(Page):
    pass


# There should be a waiting page after preparing the message and before receiving one
page_sequence = [
    GroupingPage,
    Introduction,
    RealEffort,
    Tetris,
    EffortResultsWaitPage,
    RealEffortResults,
    PreparingMessage,
    ReceivingMessage,
    TaxSystem,
    TaxDecisionWaitPage,
    ProgressivityParameter,
    TaxRateParameter,
    ResultsWaitPage,
    Results
]
