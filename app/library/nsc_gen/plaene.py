"""Module for generating random plans for the player character."""
import random

plaene_gross_de = [
    "Fähigkeit meistern",
    "Reichtum erlangen",
    "Unabhängigkeit erlangen",
    "Familie gründen",
    "Macht erlangen",
    "Berühmt werden",
    "Sucht besiegen",
    "Wissen erlangen",
]
plaene_gross_en = [
    "Master a skill",
    "Gain wealth",
    "Gain independence",
    "Start a family",
    "Gain power",
    "Become famous",
    "Defeat addiction",
    "Gain knowledge",
]
plaene_klein_de = [
    "Neue Sportart ausprobieren",
    "Reisen",
    "Fähigkeit erlernen",
    "Job finden",
    "Partner finden",
    "Freunde finden",
    "Entspannung finden",
    "Feind besiegen",
    "Konflikt beilegen",
    "Trainingsziel erreichen",
]
plaene_klein_en = [
    "Try a new sport",
    "Travel",
    "Learn a skill",
    "Find a job",
    "Find a partner",
    "Find friends",
    "Find relaxation",
    "Defeat an enemy",
    "Resolve a conflict",
    "Reach a training goal",
]


def get_random_gross(locale='en',exclude=None):
    """Get a random large plan."""
    return random.choice([
        plan 
        for plan in (plaene_gross_de if locale.startswith('de') else plaene_gross_en)
        if not exclude or plan not in exclude])


def get_random_klein(locale='en',num:int=2,exclude=None):
    """Get random small plans."""
    if num == 0:
        return ''
    return random.sample([
        plan 
        for plan in (plaene_klein_de if locale.startswith('de') else plaene_klein_en) 
        if not exclude or plan not in exclude],num)
