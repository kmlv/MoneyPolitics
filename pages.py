from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants


class Instructions(Page):
    group_by_arrival_time = True


class RealEffort(Page):
    pass


class LuckEffortInformation(Page):

    def before_next_page(self):
        # This page was created in order to define a method in which the eligibility to receive a message is defined
        player = self.player
        if player.base_earnings <= Constants.poverty_line:
            player.eligible_receiver = True
        else:
            player.eligible_receiver = False


class PreparingMessage(Page):
    form_model = 'player'
    form_fields = ['message', 'message_receivers']

    def error_message(self, values):
        player = self.player
        if player.message == '' and player.message_receivers != 0:
            return "If you don't want to send a message, choose 0 as the amount of message receivers"



class ReceivingMessage(Page):
    pass


class TaxSystem(Page):
    pass


class TaxParameter(Page):
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
    TaxParameter,
    ResultsWaitPage,
    Results
]
