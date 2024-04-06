"""Module for generating random fears."""
import random

aengste_de = [
    "Armut",
    "Verletzung",
    "Einsamkeit",
    "Bloßstellung",
    "Spott",
    "Gewalt",
    "Tieren",
    "Dunkelheit",
    "Gewitter",
    "Fremde",
    "Krankheit",
    "Sexualität",
    "Versagen",
    "Schwäche zeigen",
    "Intimität",
]
aengste_en = [
    "Poverty",
    "Injury",
    "Loneliness",
    "Exposure",
    "Mockery",
    "Violence",
    "Animals",
    "Darkness",
    "Thunderstorm",
    "Strangers",
    "Illness",
    "Sexuality",
    "Failure",
    "Showing weakness",
    "Intimacy",
]



def get_randoms(locale:str='en',num=1):
    """Get a list of random fears."""
    return random.sample(aengste_en if locale == 'en' else aengste_de, num)
