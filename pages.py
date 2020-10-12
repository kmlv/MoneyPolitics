from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants

import re

from django.conf import settings

class GroupingPage(WaitPage):
    group_by_arrival_time = True


class Introduction(Page):
    def vars_for_template(self):
        int_msg_cost = int(self.session.config['msg'])
        return {'tax_system': self.session.config['tax_system'],
                  'msg_type': self.session.config['msg_type'], 'message_cost': int_msg_cost}


class RealEffort(Page):
    pass


class Tetris(Page):
    form_model = 'player'
    form_fields = ['game_score'] # score currently determined by how many rows are eliminated
    timeout_seconds = 120 #60 # we may want to give players more time 

    def before_next_page(self):
        # for debugging (delete later)
        print(self.player.game_score)

    def vars_for_template(self):
        return {'tax_system': self.session.config['tax_system'], "message_cost": self.session.config['msg'],
                  'msg_type': self.session.config['msg_type'], 'score': self.player.game_score}


class EffortResultsWaitPage(WaitPage):

    # Provisional assignment of scores (This has to be changed to a func that uses the ranking obtained in the real
    # effort game)
    def after_all_players_arrive(self):
        self.group.ranking_income_assignment()
        self.group.base_income_assignment()
    
    def vars_for_template(self):
        return {'tax_system': self.session.config['tax_system'], "message_cost": self.session.config['msg'],
                  'msg_type': self.session.config['msg_type']}


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
        ranking_string = None # str, will store the ranking as a string (i.e. "1st")

        if ranking == 1:
            ranking_string = str(ranking)+"st"
        elif ranking == 2:
            ranking_string = str(ranking)+"nd"
        elif ranking == 3:
            ranking_string = str(ranking)+"rd"
        elif ranking > 3:
            ranking_string = str(ranking)+"th"

        return {'ranking_string': ranking_string, 'income': income, 'effort_or_luck': effort_or_luck, 'tax_system': self.session.config['tax_system'], "message_cost": self.session.config['msg'],
                  'msg_type': self.session.config['msg_type'], 'score': self.player.game_score}


class PreparingMessage(Page):
    form_model = 'player'

    def get_form_fields(self):
        message = ['message']
        
        if self.session.config['msg_type'] == 'single':
            choices = self.player.message_receivers_choices()
            return message+choices            
        
        elif self.session.config['msg_type'] == 'double':
            numb_of_receivers = len(self.player.message_receivers_choices())
            
            # keeping only the first half of receivers for the first message field
            choices = self.player.message_receivers_choices()[:int(numb_of_receivers/2)]

            # keeping the second half of receivers for the second message field
            message_d = [message[0] + "_d"]
            choices_d = self.player.message_receivers_choices()[int(numb_of_receivers/2):]
            
            return message+choices+message_d+choices_d  

        else:
            print(f"Error: invalid value for self.session.config['msg_type'] {self.session.config['msg_type']}")

    def vars_for_template(self):
        income_id_dict = {} # dict with ids ordered by income (from lower to higher)
        players = self.group.get_players() # list of players objects in group
        unique_task_endowments = list(set(Constants.task_endowments)) # ordered from lower to higher
        unique_task_endowments.sort()
        msg_cost_int = int(self.session.config['msg'])

        income_15_counter = 1 
        income_25_counter = 1 

        for income in unique_task_endowments: # looping accross incomes to get income ordered list                       
            for p in players: # looping accross player ids to capture income specific ids 
                if p.base_earnings == income: # if player has current income, append id to ordered list
                    
                    # extracting the base earnings without zeros
                    if p.base_earnings < 10:
                        string_income = str(p.base_earnings)[:1]
                    elif p.base_earnings < 100:
                        string_income = str(p.base_earnings)[:2]
                    else:
                        string_income = str(p.base_earnings)[:3]

                    if p.base_earnings == 15:
                        income_id_dict[f"income_{string_income}_{income_15_counter}"] = p.id_in_group
                        income_15_counter += 1 # updating each time a player of income 15 is found
                    elif p.base_earnings == 25:
                        income_id_dict[f"income_{string_income}_{income_25_counter}"] = p.id_in_group
                        income_25_counter += 1 # updating each time a player of income 25 is found
                    else:
                        income_id_dict[f"income_{string_income}"] = p.id_in_group

        # merging our dictionaries to create our variables
        output = {'msg_cost_int': msg_cost_int, 'tax_system': self.session.config['tax_system'], "message_cost": self.session.config['msg'],
                  'msg_type': self.session.config['msg_type'], **income_id_dict}
        
        print(output)
        return {**output}
            

    def before_next_page(self):
        messages_sent = 0
        player = self.player
        #NOTE: To count the messages, we won't use elif, because sending a message to someone is not exclusive; 
        # you can send them to multiple people and that's independent from sending to another one before

        # First message
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

        # Second message
        if self.session.config['msg_type'] == "double":
            if player.income_9_d is True:
                messages_sent += 1
            if player.income_15_1_d is True:
                messages_sent += 1
            if player.income_15_2_d is True:
                messages_sent += 1
            if player.income_15_3_d is True:
                messages_sent += 1
            if player.income_25_1_d is True:
                messages_sent += 1
            if player.income_25_2_d is True:
                messages_sent += 1
            if player.income_40_d is True:
                messages_sent += 1
            if player.income_80_d is True:
                messages_sent += 1
            if player.income_125_d is True:
                messages_sent += 1

        # Calculating and discounting the total message cost
        player.total_messaging_costs += messages_sent*self.session.config['msg']
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
            # To obtain each player income for our identifier
            if p.base_earnings < 10:
                string_income = str(p.base_earnings)[:1]
            elif p.base_earnings < 100:
                string_income = str(p.base_earnings)[:2]

                # adding an identifier for same income players
                if p.base_earnings == 15:
                    string_income = string_income + " (#" + str(players15.index(p.id_in_group) + 1) + ")"
                elif p.base_earnings == 25:
                    string_income = string_income + " (#" + str(players25.index(p.id_in_group) + 1) + ")"
            else:
                string_income = str(p.base_earnings)[:3]
            
            sender_identifier = ""
            player_income_str = None

            if settings.LANGUAGE_CODE=="en":
                player_income_str = "<b>Message from Player with "
            elif settings.LANGUAGE_CODE=="es":
                player_income_str = "<b>Mensaje del Jugador con  "

            sender_identifier = player_income_str + string_income + " points" + "</b>: "

            if p.message != "":
                # Again, we won't use elif, because sending a message to someone is not exclusive
                if p.income_9 is True:
                    messages_for_9 = messages_for_9 + "<li><p>" + sender_identifier + '"' + p.message + '"' + "</p></li>"
                if p.income_15_1 is True:
                    messages_for_15_1 = messages_for_15_1 + "<li><p>" + sender_identifier + '"' + p.message + '"' + "</p></li>"
                if p.income_15_2 is True:
                    messages_for_15_2 = messages_for_15_2 + "<li><p>" + sender_identifier + '"' + p.message + '"' + "</p></li>"
                if p.income_15_3 is True:
                    messages_for_15_3 = messages_for_15_3 + "<li><p>" + sender_identifier + '"' + p.message + '"' + "</p></li>"
                if p.income_25_1 is True:
                    messages_for_25_1 = messages_for_25_1 + "<li><p>" + sender_identifier + '"' + p.message + '"' + "</p></li>"
                if p.income_25_2 is True:
                    messages_for_25_2 = messages_for_25_2 + "<li><p>" + sender_identifier + '"' + p.message + '"' + "</p></li>"
                if p.income_40 is True:
                    messages_for_40 = messages_for_40 + "<li><p>" + sender_identifier + '"' + p.message + '"' + "</p></li>"
                if p.income_80 is True:
                    messages_for_80 = messages_for_80 + "<li><p>" + sender_identifier + '"' + p.message + '"' + "</p></li>"
                if p.income_125 is True:
                    messages_for_125 = messages_for_125 + "<li><p>" + sender_identifier + '"' + p.message + '"' + "</p></li>"
        
            # required confiditonal for double messaging and  send_id + p.msg_d
            if self.session.config['msg_type'] == 'double':
                if p.message_d != "":
                    # Again, we won't use elif, because sending a message to someone is not exclusive
                    if p.income_9 is True:
                        messages_for_9 = messages_for_9 + "<li><p>" + sender_identifier + '"' + p.message_d + '"' + "</p></li>"
                    if p.income_15_1 is True:
                        messages_for_15_1 = messages_for_15_1 + "<li><p>" + sender_identifier + '"' + p.message_d + '"' + "</p></li>"
                    if p.income_15_2 is True:
                        messages_for_15_2 = messages_for_15_2 + "<li><p>" + sender_identifier + '"' + p.message_d + '"' + "</p></li>"
                    if p.income_15_3 is True:
                        messages_for_15_3 = messages_for_15_3 + "<li><p>" + sender_identifier + '"' + p.message_d + '"' + "</p></li>"
                    if p.income_25_1 is True:
                        messages_for_25_1 = messages_for_25_1 + "<li><p>" + sender_identifier + '"' + p.message_d + '"' + "</p></li>"
                    if p.income_25_2 is True:
                        messages_for_25_2 = messages_for_25_2 + "<li><p>" + sender_identifier + '"' + p.message_d + '"' + "</p></li>"
                    if p.income_40 is True:
                        messages_for_40 = messages_for_40 + "<li><p>" + sender_identifier + '"' + p.message_d + '"' + "</p></li>"
                    if p.income_80 is True:
                        messages_for_80 = messages_for_80 + "<li><p>" + sender_identifier + '"' + p.message_d + '"' + "</p></li>"
                    if p.income_125 is True:
                        messages_for_125 = messages_for_125 + "<li><p>" + sender_identifier + '"' + p.message_d + '"' + "</p></li>"

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

    def vars_for_template(self):
        return {'tax_system': self.session.config['tax_system'], "message_cost": self.session.config['msg'],
                  'msg_type': self.session.config['msg_type']}

class ReceivingMessage(Page):
    def vars_for_template(self):
        return {'tax_system': self.session.config['tax_system'], "message_cost": self.session.config['msg'],
                  'msg_type': self.session.config['msg_type']}


class ProgressivityParameter(Page):
    # Displayed only if tax rate sys is selected on the session config

    form_model = 'player'
    form_fields = ['progressivity']

    def is_displayed(self):
        if self.session.config['tax_system'] == "progressivity":
            return True
        else:
            return False
    def vars_for_template(self):
        return {'tax_system': self.session.config['tax_system'], "message_cost": self.session.config['msg'],
                  'msg_type': self.session.config['msg_type']}


class TaxRateParameter(Page):
    # Displayed only if tax rate sys is selected on the session config

    form_model = 'player'
    form_fields = ['tax_rate']

    def is_displayed(self):
        if self.session.config['tax_system'] == "tax_rate":
            return True
        else:
            return False
    def vars_for_template(self):
        return {'tax_system': self.session.config['tax_system'], "message_cost": self.session.config['msg'],
                  'msg_type': self.session.config['msg_type']}


class ResultsWaitPage(WaitPage):
    def after_all_players_arrive(self):
        self.group.set_payoffs()


class Results(Page):
    def vars_for_template(self):
        tax_system = self.session.config['tax_system']
        msg_cost_int = int(self.session.config['msg'])
        if self.session.config['tax_system'] == "tax_rate":
            tax_rate = round(self.group.chosen_tax_rate, 2)
            return {'player_tax_rate': str(int(self.player.tax_rate))+"%", 'msg_cost_int': msg_cost_int, 'tax_system': tax_system, 'tax_rate': str(int(tax_rate*100))+"%", "message_cost": self.session.config['msg'],
                  'msg_type': self.session.config['msg_type']}
        elif self.session.config['tax_system'] == "progressivity":
            progressivity = round(self.group.chosen_progressivity)
            return {'msg_cost_int': msg_cost_int, 'tax_system': tax_system, 'progressivity': progressivity, "message_cost": self.session.config['msg'], 'msg_type': self.session.config['msg_type']}
        else:
            print('Tax system undefined')


# There should be a waiting page after preparing the message and before receiving one
page_sequence = [
    GroupingPage,
    Introduction,
    Tetris,
    EffortResultsWaitPage,
    RealEffortResults,
    PreparingMessage,
    ProcessingMessage,
    ReceivingMessage,
    ProgressivityParameter,
    TaxRateParameter,
    ResultsWaitPage,
    Results
]
