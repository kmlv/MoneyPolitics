from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants

"""
The provisional structure for the pages of this app is going to be as follows:

1. Instructions

2. A real effort task: 
    Players will play a Tetris or another game in order to obtain some provisional income. This has to be one of the
    values of the following vector (depending on their ranking in the task)
    
    [9, 15, 15, 15, 25, 25, 40, 80, 125]
    
3. Information about whether their incomes are going to be random or from the real effort task:
    50% 3 people paid by luck; (1,2,3[a],4,5[b],6,7,8,9[c]) -> (1,2,c,4,a,6,7,8,b)
    50% 6 people paid by luck; similar, but 6 are shuffled

4. Preparing Communication: 
    Players will have the ability to send a single message to one or many players with 10 or 15 as endowment. This will 
    have a cost which should be edited on the models.py or on a txt imported into the models.py file to avoid 
    hard coding

5. Deciding which policy parameter should be chosen for voting
    
    They will be asked about which policy system they prefer: 
    1. Taxes: They can vote which should be the base tax rate (let's say 20%) that the people with low income should 
    pay, but not the proportion in which this tax rate will increase when people have a greater income (there could be 
    a fixed increase in 2% on the tax rate per each additional point) 
    
    2. Progressivity. They can't vote which should be the base tax rate (there is a fixed 20% tax rate) that the people
    with low income should pay, but they can choose the proportion in which this tax rate will increase when people have
    a greater income (an increase in 2% on the tax rate per each additional point or 4% if they prefer) 

6. Choosing the tax policy parameter: Depending on the chosen system, they will be able to say:

    1. Taxes: Which is their preferred base tax rate
    2. Progressivity: Which is their preferred increase on the base tax rate per additional point
    
    The median of the preferred parameters is going to be the one applied to everyone.

7. Payoffs:

"""


class Instructions(Page):
    group_by_arrival_time = True


class RealEffort(Page):
    pass


class PreparingMessage(Page):
    form_model = 'player'
    form_fields = ['message']

    def vars_for_template(self):
        player = self.player
        return {'message': player.message}


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
    PreparingMessage,
    ReceivingMessage,
    TaxSystem,
    TaxParameter,
    ResultsWaitPage,
    Results
]
