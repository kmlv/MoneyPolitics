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
    def is_displayed(self):
        if self.session.config['treatment'] == "Tetris":
            return True
        else: 
            return False
    
    form_model = 'player'
    form_fields = ['game_score'] # score currently determined by how many rows are eliminated
    timeout_seconds = 120 #60 # we may want to give players more time 

    def before_next_page(self):
        # for debugging (delete later)
        print(self.player.game_score)
	
class Diamonds(Page):
    def is_displayed(self):
        if self.session.config['treatment'] == "Diamonds":
            return True
        else: 
            return False

    form_model = 'player'
    form_fields = ['diamond_guess', 'diamond_actual']
    timeout_seconds = 60

    def before_next_page(self):
        self.player.game_score = abs(self.player.diamond_guess - self.player.diamond_actual)
        # for debugging (delete later)
        print(self.player.diamond_guess)
        print(self.player.diamond_actual)
        print(self.player.game_score)


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

    def get_form_fields(self):
        message = ['message']
        choices = self.player.message_receivers_choices()
        return message+choices

    def before_next_page(self):
        messages_sent = 0
        player = self.player
        # To count the messages, we won't use elif, because sending a message to someone is not exclusive: you can
        # send them to multiple people and that's independent from sending to another one before
        if player.income_9 is True:
            messages_sent += 1
        if player.income_15_1 is True:
            messages_sent += 1
        if player.income_15_2 is True:
            messages_sent += 1
        if player.income_15_3 is True:
            messages_sent += 1
        if player.income_25_1 is True:
            messages_sent += 1
        if player.income_25_2 is True:
            messages_sent += 1
        if player.income_40 is True:
            messages_sent += 1
        if player.income_80 is True:
            messages_sent += 1
        if player.income_125 is True:
            messages_sent += 1

        # Calculating and discounting the total message cost
        player.total_messaging_costs = messages_sent*Constants.message_cost
        player.after_message_earnings = player.base_earnings - player.total_messaging_costs


class ProcessingMessage(WaitPage):
    def after_all_players_arrive(self):
        messages_for_9 = ""
        messages_for_15_1 = ""
        messages_for_15_2 = ""
        messages_for_15_3 = ""
        messages_for_25_1 = ""
        messages_for_25_2 = ""
        messages_for_40 = ""
        messages_for_80 = ""
        messages_for_125 = ""

        # 1. It's necessary to identify the players with the repeated incomes in the same order obtained 
        # before (see models.py)
        players15 = []
        players25 = []

        for p in self.group.get_players():
            if p.base_earnings == 15:
                players15.append(p.id_in_group)
            elif p.base_earnings == 25:
                players25.append(p.id_in_group)

        # 2. The messages are going to be classified according to which player should receive them
        for p in self.group.get_players():
            if p.message != "":
                # Again, we won't use elif, because sending a message to someone is not exclusive
                if p.income_9 is True:
                    messages_for_9 = messages_for_9 + "<br>Player " + str(p.id_in_group) + ": " + p.message
                if p.income_15_1 is True:
                    messages_for_15_1 = messages_for_15_1 + "<br>Player " + str(p.id_in_group) + ": " + p.message
                if p.income_15_2 is True:
                    messages_for_15_2 = messages_for_15_2 + "<br>Player " + str(p.id_in_group) + ": " + p.message
                if p.income_15_3 is True:
                    messages_for_15_3 = messages_for_15_3 + "<br>Player " + str(p.id_in_group) + ": " + p.message
                if p.income_25_1 is True:
                    messages_for_25_1 = messages_for_25_1 + "<br>Player " + str(p.id_in_group) + ": " + p.message
                if p.income_25_2 is True:
                    messages_for_25_2 = messages_for_25_2 + "<br>Player " + str(p.id_in_group) + ": " + p.message
                if p.income_40 is True:
                    messages_for_40 = messages_for_40 + "<br>Player " + str(p.id_in_group) + ": " + p.message
                if p.income_80 is True:
                    messages_for_80 = messages_for_80 + "<br>Player " + str(p.id_in_group) + ": " + p.message
                if p.income_125 is True:
                    messages_for_125 = messages_for_125 + "<br>Player " + str(p.id_in_group) + ": " + p.message
        
        # 3. We'll assign the messages according to the players income
        for p in self.group.get_players():
            # Now we'll use elif because a player can only have a unique income
            if p.base_earnings == 9:
                p.messages_received = messages_for_9
            if p.base_earnings == 15:
                if players15.index(p.id_in_group) == 0:
                    p.messages_received = messages_for_15_1
                elif players15.index(p.id_in_group) == 1:
                    p.messages_received = messages_for_15_2
                elif players15.index(p.id_in_group) == 2:
                    p.messages_received = messages_for_15_3
            if p.base_earnings == 25:
                if players25.index(p.id_in_group) == 0:
                    p.messages_received = messages_for_25_1
                elif players25.index(p.id_in_group) == 1:
                    p.messages_received = messages_for_25_2
            if p.base_earnings == 40:
                p.messages_received = messages_for_40
            if p.base_earnings == 80:
                p.messages_received = messages_for_80
            if p.base_earnings == 125:
                p.messages_received = messages_for_125


class ReceivingMessage(Page):
    pass
    """
    def vars_for_template(self):
        player = self.player

        # Obtaining the received messages
        raw_messages = player.messages_received.split(";")
        # It'll create an extra item with an empty value (''), so we'll remove it
        raw_messages.remove('')
        # Because we'll probably want some treatment variable that display players income, id or both
        clean_messages_no_id_no_inc = {}
        clean_messages_with_id_no_inc = {}

        # for item in raw_messages:
            # We are creating a list of lists that have 2 items: sender's id and the respective message
            # 0 ids 1 msj (de ahi pensar en income)
        #    clean_messages_no_id_no_inc["player_{}_message".format(item.split(",", 1)[0])] = item.split(",", 1)[1]
        #    clean_messages_with_id_no_inc["player_{}_message".format(item.split(",", 1)[0])] = item.split(",", 1)[0]\
        #                                                                                        + ': '\
        #                                                                                        + item.split(",", 1)[1]

        # Loop across received messages in the html in order to show them distinctly (with another color, size, etc)
        # return clean_messages_no_id_no_inc
        # return clean_messages_no_id_no_inc
        return {'message': player.messages_received}
    """

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
	Diamonds, 
    EffortResultsWaitPage,
    RealEffortResults,
    PreparingMessage,
    ProcessingMessage,
    ReceivingMessage,
    TaxSystem,
    TaxDecisionWaitPage,
    ProgressivityParameter,
    TaxRateParameter,
    ResultsWaitPage,
    Results
]
