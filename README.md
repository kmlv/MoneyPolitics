# Money in Politics
**Programmers:** Marco Gutierrez and John Elliott

## Instructions

1. Install otree: `pip3 install -U otree`
1. Create a project: `otree startproject klo_lp_apps`. The name doesn't
really matter.
1. In settings.py, add this at the beggining

```
from os.path import dirname, abspath
import gettext as _

DJANGO_ROOT = dirname(dirname(abspath(__file__)))
SITE_ROOT = dirname(DJANGO_ROOT)
USE_I18N = True
```

This should be at the end:
```
LOCALE_PATHS = (
    SITE_ROOT + '/locale',
)
```

Also, edit SESSION CONFIGS to look like this: 
```
SESSION_CONFIGS = [
    {
        'name': 'MoneyPolitics',
        'display_name': 'Base Code MoneyPolitics',
        #Set to 2 for demo but will be 9 for actual testing
        'num_demo_participants': 9, #Constants.players_per_group must also be changed in models.py
        'app_sequence': ['MoneyPolitics'],
        # Which tax system is going to be used (tax_rate or progressivity)
        'tax_system': "tax_rate",
        # Cost per message
        'msg': float(2),
        # The number of messages, 'single' or 'double'
        'msg_type': 'single',
        # The randomness system used. 'system1' TBD
        'randomness': 'system1'
    },
    {
        'name': 'MoneyPoliticsTest',
        'display_name': 'MoneyPolitics (Test with 2 players)',
        #Set to 2 for demo but will be 9 for actual testing
        'num_demo_participants': 2, #Constants.players_per_group must also be changed in models.py
        'app_sequence': ['MoneyPolitics'],
        # Which tax system is going to be used (tax_rate or progressivity)
        'tax_system': "tax_rate",
        # Cost per message
        'msg': float(2),
        # The number of messages, 'single' or 'double'
        'msg_type': 'single',
        # The randomness system used. 'system1' TBD
        'randomness': 'system1'
    },
    {
        'name': 'MP_Free_Cost_x_Single_MSG',
        'display_name': 'MoneyPolitics with Free Single Messaging',
        #Set to 2 for demo but will be 9 for actual testing
        'num_demo_participants': 9, #Constants.players_per_group must also be changed in models.py
        'app_sequence': ['MoneyPolitics'],
        # Which tax system is going to be used (tax_rate or progressivity)
        'tax_system': "tax_rate",
        # Cost per message
        'msg': float(0),
        # The number of messages, 'single' or 'double'
        'msg_type': 'single',
        # The randomness system used. 'system1' TBD
        'randomness': 'system1'
    },
    {
        'name': 'MP_Free_Cost_x_Double_MSG',
        'display_name': 'MoneyPolitics with Free Dual Messaging',
        #Set to 2 for demo but will be 9 for actual testing
        'num_demo_participants': 9, #Constants.players_per_group must also be changed in models.py
        'app_sequence': ['MoneyPolitics'],
        # Which tax system is going to be used (tax_rate or progressivity)
        'tax_system': "tax_rate",
        # Cost per message
        'msg': float(0),
        # The number of messages, 'single' or 'double'
        'msg_type': 'double',
        # The randomness system used. 'system1' TBD
        'randomness': 'system1'
    },
    {
        'name': 'MP_2Point_Cost_x_Single_MSG',
        'display_name': 'MoneyPolitics with 2 Point Cost Single Messaging',
        #Set to 2 for demo but will be 9 for actual testing
        'num_demo_participants': 9, #Constants.players_per_group must also be changed in models.py
        'app_sequence': ['MoneyPolitics'],
        # Which tax system is going to be used (tax_rate or progressivity)
        'tax_system': "tax_rate",
        # Cost per message
        'msg': float(2),
        # The number of messages, 'single' or 'double'
        'msg_type': 'single',
        # The randomness system used. 'system1' TBD
        'randomness': 'system1'
    },
    {
        'name': 'MP_2Point_x_Double_MSG',
        'display_name': 'MoneyPolitics with 2 Point Cost Dual Messaging',
        #Set to 2 for demo but will be 9 for actual testing
        'num_demo_participants': 9, #Constants.players_per_group must also be changed in models.py
        'app_sequence': ['MoneyPolitics'],
        # Which tax system is going to be used (tax_rate or progressivity)
        'tax_system': "tax_rate",
        # Cost per message
        'msg': float(2),
        # The number of messages, 'single' or 'double'
        'msg_type': 'double',
        # The randomness system used. 'system1' TBD
        'randomness': 'system1'
    },
]
```

1. Add a file on the project folder called controls.py. Inside, it should look like this

```
doc = """
Control parameters for MoneyPolitics
"""

task_endowments = [125, 80, 40, 25, 25, 15, 15, 15, 9]

# Because oTree doesn't let us work with the multiple checkbox multiple choiice widget, we are going to create a list
# of options with the income and if its the 1st, 2nd or 3rd person with the same income
possible_message_receivers = [['1251', 'Income 125'], ['801', 'Income 80'], ['401', 'Income 40'],
                              ['252', 'Income 25 (Player 2)'], ['251', 'Income 25 (Player 1)'],
                              ['153', 'Income 15 (Player 3)'], ['152', 'Income 15 (Player 2)'],
                              ['151', 'Income 15 (Player 1)'], ['91', 'Income 9']]

possible_message_receivers_125 = list(possible_message_receivers)
possible_message_receivers_80 = list(possible_message_receivers)
possible_message_receivers_40 = list(possible_message_receivers)
possible_message_receivers_252 = list(possible_message_receivers)
possible_message_receivers_251 = list(possible_message_receivers)
possible_message_receivers_153 = list(possible_message_receivers)
possible_message_receivers_152 = list(possible_message_receivers)
possible_message_receivers_151 = list(possible_message_receivers)
possible_message_receivers_9 = list(possible_message_receivers)

possible_message_receivers_125.remove(possible_message_receivers[0])
possible_message_receivers_80.remove(possible_message_receivers[1])
possible_message_receivers_40.remove(possible_message_receivers[2])
possible_message_receivers_252.remove(possible_message_receivers[3])
possible_message_receivers_251.remove(possible_message_receivers[4])
possible_message_receivers_153.remove(possible_message_receivers[5])
possible_message_receivers_152.remove(possible_message_receivers[6])
possible_message_receivers_151.remove(possible_message_receivers[7])
possible_message_receivers_9.remove(possible_message_receivers[8])

message_cost = 2 or 0
number_of_messages = 1
progressivity_levels = [[1, 'Level 1'], [2, 'Level 2'], [3, 'Level 3'],
                        [4, 'Level 4'], [5, 'Level 5']]

progressivity_levels_tax_rates = {'1': [0.4, 0.4, 0.4, 0.4, 0.4, 0.4],
                                  '2': [0.3, 0.32, 0.342, 0.364, 0.407, 0.458],
                                  '3': [0.2, 0.24, 0.284, 0.328, 0.439, 0.515],
                                  '4': [0.1, 0.14, 0.204, 0.278, 0.464, 0.585],
                                  '5': [0, 0, 0.06, 0.263, 0.531, 0.664]}

# Private Sector Parameters
alpha = 5
beta = 1/16

# Steps for tax rate
tax_step = '0.05'

```
# Gitignore Code:

```
__pycache__/
*.py[cod]

_builtin/

### Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]

### C extensions
*.so

### Distribution / packaging
.Python

env/

build/

develop-eggs/

dist/

downloads/

eggs/

.eggs/

lib/

lib64/

parts/

sdist/

var/

*.egg-info/

.installed.cfg

*.egg


### PyInstaller
### Usually these files are written by a python script from a template
### before PyInstaller builds the exe, so as to inject date/other infos into it.
*.manifest

*.spec

### Installer logs
pip-log.txt

pip-delete-this-directory.txt


### Unit test / coverage reports
htmlcov/

.tox/

.coverage

.coverage.*

.cache

nosetests.xml

coverage.xml

*,cover


### Translations
*.mo

*.pot


### Django stuff:
*.log



### Sphinx documentation
docs/_build/


### PyBuilder
target/


```

## Basic Outiline

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
    
    There are two possibilities: 
    
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

### About Diamond Game

A version of the diamond game has been coded, but requires debugging (it only supports a square board for now). The size of the board is currently set to 15x15. 

The player enters their guess, which is compared to the actual number of diamonds on their board. Their score is equal to: 
    | guess - actual |
Therefore the highest possible score is 0. The greater their score, the further their guess was from the actual number of diamonds. 

There is also a value in Diamonds.html (diamondAmount, a number between 1 and 10) which determines the approximate amount of diamonds on the board. If diamondAmount is set to 3, then about 30% of the board will be diamonds and 70% will be circles. 
```
A task in which the player counts the number of small diamonds in rectangular screens filled 
mainly with small circles
```

After testing, bring your changes to the main branch
### Main space: branch `master`

###

### Note:
Remember that because this is app is for an ongoing project, there are going to be many changes in its structure
so try to program it as dynamically as possible, avoiding hard coding and documenting everything that is required.

Also, try to define what was done in every commit pushed to the remote repo 

Might be difficult to set up the real effort tasks as includable templates (the game is just on a separate page for now). Most browsers don't allow local files (like a tetris game) to be embedded inside of another page for security reasons. This would also make it difficult to pick which game to play (currently, you only have to change SESSION_CONFIGS in settings.py). May also cause problems when passing values from the game back to otree pages/models. 


