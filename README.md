# Money in Politics
**Programmers:** Marco Gutierrez and Skyler Stewart

# Instructions

1. Install otree: `pip3 install -U otree`
1. Create a project: `otree startproject klo_lp_apps`. The name doesn't
really matter.
1. Add a file on the project folder called controls.py. Inside, it should look like this

 ```
    doc = """"
    Control parameters for MoneyPolitics
    """
    
    task_endowments = [9, 15, 15, 15, 25, 25, 40, 80, 125]
    poverty_line = task_endowments[3]
    message_cost = 1
    number_of_messages = 1
    possible_tax_systems = [[0, 'Progressivity System'], [1, "Tax Rate System"]]
 ```
 
# TODO - Marco and Skyler

Every change should be first implemented here:
### Working space: branch `working_space`

The main tasks are to program an app following this provisional structure:

1. Instructions

1. A real effort task: 
    Players will play a Tetris or another game in order to obtain some provisional income. This has to be one of the
    values of the following vector (depending on their ranking in the task)
    
    `task_endowments = [9, 15, 15, 15, 25, 25, 40, 80, 125]`
    
1. Information about whether their incomes are going to be random or from the real effort task:
    1. 50% 3 people paid by luck; `(1,2,3[a],4,5[b],6,7,8,9[c]) -> (1,2,c,4,a,6,7,8,b)`
    1. 50% 6 people paid by luck; similar, but 6 are shuffled

1. Preparing Communication: 
    Players will have the ability to send a single message to one or many players with 10 or 15 as endowment. This will 
    have a cost which should be edited on the models.py or on a txt imported into the models.py file to avoid 
    hard coding

1. Deciding which policy parameter should be chosen for voting
    
    They will be asked about which policy system they prefer: 
    
    1. Taxes: They can vote which should be the base tax rate (let's say 20%) that the people with low income should 
    pay, but not the proportion in which this tax rate will increase when people have a greater income (there could be 
    a fixed increase in 2% on the tax rate per each additional point) 
    
    2. Progressivity. They can't vote which should be the base tax rate (there is a fixed 20% tax rate) that the people
    with low income should pay, but they can choose the proportion in which this tax rate will increase when people have
    a greater income (an increase in 2% on the tax rate per each additional point or 4% if they prefer) 

1. Choosing the tax policy parameter: Depending on the chosen system, they will be able to say:

    1. Taxes: Which is their preferred base tax rate
    1. Progressivity: Which is their preferred increase on the base tax rate per additional point
    
    The median of the preferred parameters is going to be the one applied to everyone.

1. Payoffs: Still need to be defined

If you want to test something that may cause some troubles, it should be done here:
### Testing space: branch `testing`

After testing, bring your changes to the main branch
### Main space: branch `master`

### Note:
Remember that because this is app is for an ongoing project, there are going to be many changes in its structure
so try to program it as dynamically as possible, avoiding hard coding and documenting everything that is required.

Also, try to define what was done in every commit pushed to the remote repo 