from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants
from .progressivity_pres import controls as ctrl
import re

from django.conf import settings

def linear_payoff(endowment, slope, tax):
    """Linear payoff function for Money Politics

    y=income+slope*t
    """

    return endowment+slope*tax

class GroupingPage(WaitPage):
    group_by_arrival_time = True


class Introduction(Page):
    def vars_for_template(self):
        int_msg_cost = int(self.session.config['msg'])
        return {'tax_system': self.session.config['tax_system'],
                  'msg_type': self.session.config['msg_type'], 'message_cost': int_msg_cost}

    def is_displayed(self):
        return self.round_number == 1

    def before_next_page(self):
        if not self.session.config["effort_on_practice"]:
            self.group.random_base_payments()


class PauseTetris(Page):
    timeout_seconds = 10

    def is_displayed(self):
        if not self.session.config["effort_on_practice"] and self.round_number <= Constants.practice_rounds:
            return False
        else:
            return True


class RealEffort(Page):
    pass


class EffortResultsWaitPage(WaitPage):
    # Provisional assignment of scores (This has to be changed to a func that uses the ranking obtained in the real
    # effort game)

    def after_all_players_arrive(self):
        self.group.ranking_income_assignment()
        self.group.base_income_assignment()
    
    def vars_for_template(self):
        return {'tax_system': self.session.config['tax_system'], "message_cost": self.session.config['msg'],
                  'msg_type': self.session.config['msg_type']}

    def is_displayed(self):
        if not self.session.config["effort_on_practice"] and self.round_number <= Constants.practice_rounds:
            return False
        else:
            return True


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

    def is_displayed(self):
        if not self.session.config["effort_on_practice"] and self.round_number <= Constants.practice_rounds:
            return False
        else:
            return True


class Tetris(Page):
    # def is_displayed(self):
    #     if self.session.config['treatment'] == "Tetris":
    #         return True
    #     else: 
    #         return False
    form_model = 'player'
    form_fields = ['game_score'] # score currently determined by how many rows are eliminated
    timeout_seconds = 120 #60 # we may want to give players more time 

    def before_next_page(self):
        # for debugging (delete later)
        print(self.player.game_score)

    def vars_for_template(self):
        return {'tax_system': self.session.config['tax_system'], "message_cost": self.session.config['msg'],
                  'msg_type': self.session.config['msg_type'], 'score': self.player.game_score}

    def is_displayed(self):
        if not self.session.config["effort_on_practice"] and self.round_number <= Constants.practice_rounds:
            return False
        elif self.session.config['treatment'] == "Tetris":
            return True

class Diamonds(Page):
    # def is_displayed(self):
    #     if self.session.config['treatment'] == "Diamonds":
    #         return True
    #     else: 
    #         return False
    def is_displayed(self):
        if not self.session.config["effort_on_practice"] and self.round_number <= Constants.practice_rounds:
            return False
        elif self.session.config['treatment'] == "Diamonds":
            return True

    form_model = 'player'
    form_fields = ['diamond_guess', 'diamond_actual']
    timeout_seconds = 60

    def before_next_page(self):
        self.player.game_score = abs(self.player.diamond_guess - self.player.diamond_actual)
        # for debugging (delete later)
        print(self.player.diamond_guess)
        print(self.player.diamond_actual)
        print(self.player.game_score)

class Slider(Page):
    def vars_for_template(self):
        #Define COnstants
        original_task_endowments = ctrl.task_endowments
        total_endowment = sum(original_task_endowments)
        unique_task_endowments = list(set(ctrl.task_endowments))
        unique_task_endowments.sort()

        # defining tax rates
        tax_rates = []
        for i in range(0,11, 1):
            tax_rates.append(i/10)

            
        # defining alternative tax rates 
        alt_tax_rates = []
        for i in range(0,105, 5):
            alt_tax_rates.append(i/100)


        # new parameters
        optimal_taxes = [1, 0.85, 0.7, 0.55, 0.4, 0]
        income_max_tax = 40

        # obtaining its intercept
        b_highest = (max(unique_task_endowments)-income_max_tax)/(min(optimal_taxes)-max(optimal_taxes))

        intersections_high_function = {} # payoffs when tax rate is the optimal in the highest payoff function

        # evaluating payoffs for all the endowments but the max

        index = 0 # index for accessing the optimal tax rates
        for endowment in unique_task_endowments:
            if endowment != max(unique_task_endowments):
                intersections_high_function[f"endowment_{endowment}"] = linear_payoff(max(unique_task_endowments), b_highest, 
                                                                                    optimal_taxes[index])
            else:
                intersections_high_function[f"endowment_{endowment}"] = max(unique_task_endowments)
            index += 1
        
        list_of_slopes = {}
        # evaluating payoffs for all the endowments but the max

        index = 0 # index for accessing the optimal tax rates
        for endowment in unique_task_endowments:
            
            if endowment != max(unique_task_endowments):
                current_intersection = intersections_high_function[f"endowment_{endowment}"]
                optimal_tax = optimal_taxes[index]
                list_of_slopes[endowment] = (endowment - current_intersection)/(0 - optimal_tax)
            
            else:
                list_of_slopes[endowment] = b_highest
                
            index += 1
        print(list_of_slopes)

        final_payoffs = {}

        endowment_index = 0
        for endowment in unique_task_endowments:
            index = 0 # index for calling the private income/public contrib that corresponds to an specific tax rate
            
            endowment_string = f"endowment_{endowment}"
            current_slope = list_of_slopes[endowment]
            current_intersection = intersections_high_function[endowment_string]
            final_payoffs[endowment] = [] # list with all the final_payoffs for a player
            
            print("endowment = ", endowment)
            for tax_rate in tax_rates: # calculating all the final payoffs for an specific player
                print("tax rate = ", tax_rate)
                current_final_payoff = linear_payoff(endowment, slope=current_slope, tax=tax_rate)
                print("current_final_payoff = ", current_final_payoff)
                final_payoffs[endowment].append(round(current_final_payoff, 3))
                index += 1
                print("---")
                
            endowment_index += 1
            print("---------------------")
        #final_payoffs
        xvals = [tax_rate*100 for tax_rate in alt_tax_rates]

        xvals_dict = {}
        plots_dict = {}

        index = 0 # index for calling the optimal tax rate
        for endowment in unique_task_endowments:
            if endowment != max(unique_task_endowments):
                xvals_dict[endowment] = [(x) for x in xvals if x <= optimal_taxes[index]*100]
            else:
                xvals_dict[endowment] = xvals
            index += 1

        return {'slopes': list_of_slopes,
                'endowments': unique_task_endowments,
                'final_payoffs':final_payoffs,
                'xvals_dict': xvals_dict,
                'base_earnings': float(self.player.base_earnings)
                }

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
        
        player = self.player
        #NOTE: To count the messages, we won't use elif, because sending a message to someone is not exclusive; 
        # you can send them to multiple people and that's independent from sending to another one before

        messages_sent = self.player.calculate_messages_sent()

        # Calculating and discounting the total message cost
        player.total_messaging_costs += messages_sent*self.session.config['msg']
        player.after_message_earnings = player.base_earnings - player.total_messaging_costs

        # Storing the number of messages sent
        player.num_messages_sent = messages_sent
    
    def error_message(self, values):
        player = self.player

        choices = self.player.message_receivers_choices() # getting the receivers items 

        current_message_count = 0

        # Calculating the number of msgs to be sent (not sent yet)
        for choice in choices:
            if values[choice] is True:
                current_message_count += 1
        print("msgs", current_message_count)

        total_messaging_costs = current_message_count*self.session.config['msg'] 
        print("total_messaging_costs",total_messaging_costs)
        current_earnings = player.base_earnings - total_messaging_costs
        print("current_earnings",current_earnings)

        if current_earnings < 0: # if player tries to spend more than what he has
            # telling the player the correct answer
            if settings.LANGUAGE_CODE=="en":
                error_msg = f"You tried to send {current_message_count} message(s), spending {total_messaging_costs} points when you only have {player.base_earnings}. Decrease the number of messages you want to send"
            elif settings.LANGUAGE_CODE=="es":
                error_msg = f"Trataste de enviar {current_message_count} mensaje(s), gastando {total_messaging_costs} puntos cuando solo tienes {player.base_earnings}. Disminuye el número de mensajes que quieres enviar"
            return error_msg
        
        # Checking if "tax" or "because" in msg
        print("player_message: ", values["message"])
        print("message_count: ", current_message_count)
        print("tax and because not in message", "tax" not in values["message"] and "because" not in values["message"])
        
        error_msg = "Only messages containing both words 'tax' and 'because' are admissible."
        if current_message_count>0:
            print("first step")
            if self.session.config["msg_type"] == "single":
                if ("tax" not in values["message"] or "because" not in values["message"]):
                    return error_msg
            elif self.session.config["msg_type"] == "double":
                if ("tax" not in values["message"] or "because" not in values["message"]) or ("tax" not in values["message_d"] or "because" not in values["message_d"]):
                    return error_msg





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
                player_income_str = "<b>From a citizen with a wealth of "
            elif settings.LANGUAGE_CODE=="es":
                player_income_str = "<b>De un ciudadano con una riqueza de "

            sender_identifier = player_income_str + string_income + " points" + "</b>: "

            #TODO: add condition here so that if msg != "" and choices_d >0, then process the msg
            if p.message != "":
                # Again, we won't use elif, because sending a message to someone is not exclusive
                if p.income_9 is True:
                    messages_for_9 = messages_for_9 + "<li><p>" + sender_identifier + '"<i>' + p.message + '</i>"' + "</p></li>"
                if p.income_15_1 is True:
                    messages_for_15_1 = messages_for_15_1 + "<li><p>" + sender_identifier + '"<i>' + p.message + '</i>"' + "</p></li>"
                if p.income_15_2 is True:
                    messages_for_15_2 = messages_for_15_2 + "<li><p>" + sender_identifier + '"<i>' + p.message + '</i>"' + "</p></li>"
                if p.income_15_3 is True:
                    messages_for_15_3 = messages_for_15_3 + "<li><p>" + sender_identifier + '"<i>' + p.message + '</i>"' + "</p></li>"
                if p.income_25_1 is True:
                    messages_for_25_1 = messages_for_25_1 + "<li><p>" + sender_identifier + '"<i>' + p.message + '</i>"' + "</p></li>"
                if p.income_25_2 is True:
                    messages_for_25_2 = messages_for_25_2 + "<li><p>" + sender_identifier + '"<i>' + p.message + '</i>"' + "</p></li>"
                if p.income_40 is True:
                    messages_for_40 = messages_for_40 + "<li><p>" + sender_identifier + '"<i>' + p.message + '</i>"' + "</p></li>"
                if p.income_80 is True:
                    messages_for_80 = messages_for_80 + "<li><p>" + sender_identifier + '"<i>' + p.message + '</i>"' + "</p></li>"
                if p.income_125 is True:
                    messages_for_125 = messages_for_125 + "<li><p>" + sender_identifier + '"<i>' + p.message + '</i>"' + "</p></li>"
        
            # required confiditonal for double messaging and  send_id + p.msg_d
            if self.session.config['msg_type'] == 'double':
                if p.message_d != "":
                    # Again, we won't use elif, because sending a message to someone is not exclusive
                    if p.income_9_d is True:
                        messages_for_9 = messages_for_9 + "<li><p>" + sender_identifier + '"<i>' + p.message_d + '</i>"' + "</p></li>"
                    if p.income_15_1_d is True:
                        messages_for_15_1 = messages_for_15_1 + "<li><p>" + sender_identifier + '"<i>' + p.message_d + '</i>"' + "</p></li>"
                    if p.income_15_2_d is True:
                        messages_for_15_2 = messages_for_15_2 + "<li><p>" + sender_identifier + '"<i>' + p.message_d + '</i>"' + "</p></li>"
                    if p.income_15_3_d is True:
                        messages_for_15_3 = messages_for_15_3 + "<li><p>" + sender_identifier + '"<i>' + p.message_d + '</i>"' + "</p></li>"
                    if p.income_25_1_d is True:
                        messages_for_25_1 = messages_for_25_1 + "<li><p>" + sender_identifier + '"<i>' + p.message_d + '</i>"' + "</p></li>"
                    if p.income_25_2_d is True:
                        messages_for_25_2 = messages_for_25_2 + "<li><p>" + sender_identifier + '"<i>' + p.message_d + '</i>"' + "</p></li>"
                    if p.income_40_d is True:
                        messages_for_40 = messages_for_40 + "<li><p>" + sender_identifier + '"<i>' + p.message_d + '</i>"' + "</p></li>"
                    if p.income_80_d is True:
                        messages_for_80 = messages_for_80 + "<li><p>" + sender_identifier + '"<i>' + p.message_d + '</i>"' + "</p></li>"
                    if p.income_125_d is True:
                        messages_for_125 = messages_for_125 + "<li><p>" + sender_identifier + '"<i>' + p.message_d + '</i>"' + "</p></li>"

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


class PracticeTaxRateParameter(Page):
    # Displayed only if tax rate sys is selected on the session config

    form_model = 'player'
    form_fields = ['practice_tax_rate']

    def is_displayed(self):
        if self.session.config['tax_system'] == "tax_rate" and self.round_number<=Constants.practice_rounds:
            return True
        else:
            return False

    def vars_for_template(self):
        #Define COnstants
        original_task_endowments = ctrl.task_endowments
        total_endowment = sum(original_task_endowments)
        unique_task_endowments = list(set(ctrl.task_endowments))
        unique_task_endowments.sort()

        # defining tax rates
        tax_rates = []
        for i in range(0,11, 1):
            tax_rates.append(i/10)

            
        # defining alternative tax rates 
        alt_tax_rates = []
        for i in range(0,105, 5):
            alt_tax_rates.append(i/100)


        # new parameters
        optimal_taxes = [1, 0.85, 0.7, 0.55, 0.4, 0]
        income_max_tax = 40

        # obtaining its intercept
        b_highest = (max(unique_task_endowments)-income_max_tax)/(min(optimal_taxes)-max(optimal_taxes))

        intersections_high_function = {} # payoffs when tax rate is the optimal in the highest payoff function

        # evaluating payoffs for all the endowments but the max

        index = 0 # index for accessing the optimal tax rates
        for endowment in unique_task_endowments:
            if endowment != max(unique_task_endowments):
                intersections_high_function[f"endowment_{endowment}"] = linear_payoff(max(unique_task_endowments), b_highest, 
                                                                                    optimal_taxes[index])
            else:
                intersections_high_function[f"endowment_{endowment}"] = max(unique_task_endowments)
            index += 1
        
        list_of_slopes = {}
        # evaluating payoffs for all the endowments but the max

        index = 0 # index for accessing the optimal tax rates
        for endowment in unique_task_endowments:
            
            if endowment != max(unique_task_endowments):
                current_intersection = intersections_high_function[f"endowment_{endowment}"]
                optimal_tax = optimal_taxes[index]
                list_of_slopes[endowment] = (endowment - current_intersection)/(0 - optimal_tax)
            
            else:
                list_of_slopes[endowment] = b_highest
                
            index += 1
        print(list_of_slopes)

        final_payoffs = {}

        endowment_index = 0
        for endowment in unique_task_endowments:
            index = 0 # index for calling the private income/public contrib that corresponds to an specific tax rate
            
            endowment_string = f"endowment_{endowment}"
            current_slope = list_of_slopes[endowment]
            current_intersection = intersections_high_function[endowment_string]
            final_payoffs[endowment] = [] # list with all the final_payoffs for a player
            
            print("endowment = ", endowment)
            for tax_rate in tax_rates: # calculating all the final payoffs for an specific player
                print("tax rate = ", tax_rate)
                current_final_payoff = linear_payoff(endowment, slope=current_slope, tax=tax_rate)
                print("current_final_payoff = ", current_final_payoff)
                final_payoffs[endowment].append(round(current_final_payoff, 3))
                index += 1
                print("---")
                
            endowment_index += 1
            print("---------------------")
        #final_payoffs
        xvals = [tax_rate*100 for tax_rate in alt_tax_rates]

        xvals_dict = {}
        plots_dict = {}

        index = 0 # index for calling the optimal tax rate
        for endowment in unique_task_endowments:
            if endowment != max(unique_task_endowments):
                xvals_dict[endowment] = [(x) for x in xvals if x <= optimal_taxes[index]*100]
            else:
                xvals_dict[endowment] = xvals
            index += 1

        return {'tax_system': self.session.config['tax_system'], 
                "message_cost": self.session.config['msg'],
                'msg_type': self.session.config['msg_type'],
                'slopes': list_of_slopes,
                'endowments': unique_task_endowments,
                'final_payoffs':final_payoffs,
                'xvals_dict': xvals_dict,
                'base_earnings': float(self.player.base_earnings)
                }
         

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
        #Define COnstants
        original_task_endowments = ctrl.task_endowments
        total_endowment = sum(original_task_endowments)
        unique_task_endowments = list(set(ctrl.task_endowments))
        unique_task_endowments.sort()

        # defining tax rates
        tax_rates = []
        for i in range(0,11, 1):
            tax_rates.append(i/10)

            
        # defining alternative tax rates 
        alt_tax_rates = []
        for i in range(0,105, 5):
            alt_tax_rates.append(i/100)


        # new parameters
        optimal_taxes = [1, 0.85, 0.7, 0.55, 0.4, 0]
        income_max_tax = 40

        # obtaining its intercept
        b_highest = (max(unique_task_endowments)-income_max_tax)/(min(optimal_taxes)-max(optimal_taxes))

        intersections_high_function = {} # payoffs when tax rate is the optimal in the highest payoff function

        # evaluating payoffs for all the endowments but the max

        index = 0 # index for accessing the optimal tax rates
        for endowment in unique_task_endowments:
            if endowment != max(unique_task_endowments):
                intersections_high_function[f"endowment_{endowment}"] = linear_payoff(max(unique_task_endowments), b_highest, 
                                                                                    optimal_taxes[index])
            else:
                intersections_high_function[f"endowment_{endowment}"] = max(unique_task_endowments)
            index += 1
        
        list_of_slopes = {}
        # evaluating payoffs for all the endowments but the max

        index = 0 # index for accessing the optimal tax rates
        for endowment in unique_task_endowments:
            
            if endowment != max(unique_task_endowments):
                current_intersection = intersections_high_function[f"endowment_{endowment}"]
                optimal_tax = optimal_taxes[index]
                list_of_slopes[endowment] = (endowment - current_intersection)/(0 - optimal_tax)
            
            else:
                list_of_slopes[endowment] = b_highest
                
            index += 1
        print(list_of_slopes)

        final_payoffs = {}

        endowment_index = 0
        for endowment in unique_task_endowments:
            index = 0 # index for calling the private income/public contrib that corresponds to an specific tax rate
            
            endowment_string = f"endowment_{endowment}"
            current_slope = list_of_slopes[endowment]
            current_intersection = intersections_high_function[endowment_string]
            final_payoffs[endowment] = [] # list with all the final_payoffs for a player
            
            print("endowment = ", endowment)
            for tax_rate in tax_rates: # calculating all the final payoffs for an specific player
                print("tax rate = ", tax_rate)
                current_final_payoff = linear_payoff(endowment, slope=current_slope, tax=tax_rate)
                print("current_final_payoff = ", current_final_payoff)
                final_payoffs[endowment].append(round(current_final_payoff, 3))
                index += 1
                print("---")
                
            endowment_index += 1
            print("---------------------")
        #final_payoffs
        xvals = [tax_rate*100 for tax_rate in alt_tax_rates]

        xvals_dict = {}
        plots_dict = {}

        index = 0 # index for calling the optimal tax rate
        for endowment in unique_task_endowments:
            if endowment != max(unique_task_endowments):
                xvals_dict[endowment] = [(x) for x in xvals if x <= optimal_taxes[index]*100]
            else:
                xvals_dict[endowment] = xvals
            index += 1

        return {'tax_system': self.session.config['tax_system'], 
                "message_cost": self.session.config['msg'],
                'msg_type': self.session.config['msg_type'],
                'slopes': list_of_slopes,
                'endowments': unique_task_endowments,
                'final_payoffs':final_payoffs,
                'xvals_dict': xvals_dict,
                'base_earnings': float(self.player.base_earnings)
                }
         

class ResultsWaitPage(WaitPage):
    def after_all_players_arrive(self):
        self.group.set_payoffs()

        for player in self.group.get_players():
            # quadratic payoffs for guessed_ranking_payoff
            if player.guessed_ranking == player.ranking:
                player.guessed_ranking_payoff = 900
            elif player.guessed_ranking == player.ranking + 1 or player.guessed_ranking == player.ranking - 1:
                player.guessed_ranking_payoff = 400
            elif player.guessed_ranking == player.ranking + 2 or player.guessed_ranking == player.ranking - 2:
                player.guessed_ranking_payoff = 100
            else:
                player.guessed_ranking_payoff = 0

            # # payoff for guessed_system_payoff
            # luck = self.group.luck
            # selected_system = "" # string that will tell the current system used for income assignment

            # if luck == 0:
            #     selected_system = "luck"
            #     print(selected_system)
            # elif luck == 1:
            #     selected_system = "performance"
            #     print(selected_system)

            # # assigning payoff
            # if player.guessed_system == selected_system:
            #     player.guessed_system_payoff = 900
            # else:
            #     player.guessed_system_payoff = 0

            # player.belief_elicitation_payoff = player.guessed_ranking_payoff + player.guessed_system_payoff
            player.belief_elicitation_payoff = player.guessed_ranking_payoff 
            player.payoff = player.game_payoff + player.belief_elicitation_payoff


class Results(Page):
    def vars_for_template(self):
        tax_system = self.session.config['tax_system']
        msg_cost_int = int(self.session.config['msg'])
        luck = self.group.luck
        selected_systems = "" # string that will tell the current system used for income assignment
        if luck == 0:
            selected_systems = "luck"
        elif luck == 1:
            selected_systems = "performance"
        
        if self.session.config['tax_system'] == "tax_rate":
            print("Player Tax Rate = " + str(self.player.tax_rate))
            tax_rate = round(self.group.chosen_tax_rate, 2)
            return {
                    'player_tax_rate': str(int(self.player.tax_rate))+"%", 
                    'msg_cost_int': msg_cost_int, 
                    'tax_system': tax_system, 
                    'tax_rate': str(int(tax_rate*100))+"%", 
                    "message_cost": self.session.config['msg'],
                    'msg_type': self.session.config['msg_type'],
                    'system_guess': self.player.guessed_system,
                    'system_actual': selected_systems,
                    'ranking_guess': self.player.guessed_ranking,
                    'ranking_actual': self.player.ranking,
                    'game_payoff': self.player.game_payoff,
                    'system_guess_payoff': self.player.guessed_system_payoff,
                    'ranking_guess_payoff': self.player.guessed_ranking_payoff,
                    'total_guess_payoff': int(0 if self.player.guessed_ranking_payoff is None else self.player.guessed_ranking_payoff) + int(0 if self.player.guessed_system_payoff is None else self.player.guessed_system_payoff)
                    }
        elif self.session.config['tax_system'] == "progressivity":
            progressivity = round(self.group.chosen_progressivity)
            if progressivity == 0:
                progressivity = 1 # changing the progressivity to 1 as a default if everyone times out
            return {
                    'msg_cost_int': msg_cost_int, 
                    'tax_system': tax_system, 
                    'progressivity': progressivity, 
                    "message_cost": self.session.config['msg'], 
                    'msg_type': self.session.config['msg_type'],
                    'system_guess': self.player.guessed_system,
                    'system_actual': selected_systems,
                    'ranking_guess': self.player.guessed_ranking,
                    'ranking_actual': self.player.ranking,
                    'game_payoff': self.player.game_payoff,
                    'system_guess_payoff': self.player.guessed_system_payoff,
                    'ranking_guess_payoff': self.player.guessed_ranking_payoff,
                    'total_guess_payoff': int(0 if self.player.guessed_ranking_payoff is None else self.player.guessed_ranking_payoff) + int(0 if self.player.guessed_system_payoff is None else self.player.guessed_system_payoff)
                    }
        else:
            print('Tax system undefined')


class BeliefElicitation(Page):
    """
    Page for guessing your current ranking
    and  the system that defined your current 
    base income
    """
    form_model = 'player'
    form_fields = ['guessed_ranking']

    def vars_for_template(self):
        return {'tax_system': self.session.config['tax_system'], "message_cost": self.session.config['msg'],
                  'msg_type': self.session.config['msg_type']}

    def is_displayed(self):
        if not self.session.config["effort_on_practice"] and self.round_number <= Constants.practice_rounds:
            return False
        else:
            return True


class ResultsAfterBeliefs(Page):
    def vars_for_template(self):
        luck = self.group.luck

        selected_systems = "" # string that will tell the current system used for income assignment
        if luck == 0:
            selected_systems = "luck"
        elif luck == 1:
            selected_systems = "performance"
        
        return {
                'system_actual': selected_systems,
                'ranking_guess': self.player.guessed_ranking,
                'ranking_actual': self.player.ranking,
                'ranking_guess_payoff': self.player.guessed_ranking_payoff
                }

    def is_displayed(self):
        if not self.session.config["effort_on_practice"] and self.round_number <= Constants.practice_rounds:
            return False
        else:
            return True

# There should be a waiting page after preparing the message and before receiving one
page_sequence = [
    GroupingPage,
    Introduction,
    PauseTetris,
    Tetris,
    Diamonds,
    BeliefElicitation,
    EffortResultsWaitPage,
    RealEffortResults,
    PracticeTaxRateParameter,
    PreparingMessage,
    ProcessingMessage,
    ReceivingMessage,
    ProgressivityParameter,
    TaxRateParameter,
    ResultsWaitPage,
    Results,
    ResultsAfterBeliefs
]
