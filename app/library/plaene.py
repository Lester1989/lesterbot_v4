
import random

plaene_gross =[
    'Fähigkeit meistern',
    'Reichtum erlangen',
    'Unabhängigkeit erlangen',
    'Familie gründen',
    'Macht erlangen',
    'Berühmt werden',
    'Sucht besiegen',
    'Wissen erlangen'
]
plaene_klein =[
    'Neue Sportart ausprobieren',
    'Reisen',
    'Fähigkeit erlernen',
    'Job finden',
    'Partner finden',
    'Freunde finden',
    'Entspannung finden',
    'Feind besiegen',
    'Konflikt beilegen',
    'Trainingsziel erreichen'
]


def get_random_gross(exclude =None):
    return random.choice([plan for plan in plaene_gross if not exclude or plan not in exclude])
def get_random_klein(exclude =None):
    return random.choice([plan for plan in plaene_klein if not exclude or plan not in exclude])
