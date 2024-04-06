"""Generates random relationships between characters."""
import random

relationships = [
    {
        "name": {
            'de': "ist verliebt in",
            'en': 'is in love',
        },
        "probability": 1,
    },
    {
        "name": {
            'de': "mag",
            'en': 'likes',
        },
        "probability": 4,
    },
    {
        "name": {
            'de': "bewundert",
            'en': 'admires',
        },
        "probability": 2,
    },
    {
        "name": {
            'de': "lernt von",
            'en': 'learns from',
        },
        "probability": 2,
    },
    {
        "name": {
            'de': "kennt",
            'en': 'knows',
        },
        "probability": 6,
    },
    {
        "name": {
            'de': "mag nicht",
            'en': 'dislikes',
        },
        "probability": 5,
    },
    {
        "name": {
            'de': "beneidet",
            'en': 'envies',
        },
        "probability": 3,
    },
    {
        "name": {
            'de': "hasst",
            'en': 'hates',
        },
        "probability": 2,
    },
]

drawable_list = []
for relation in relationships:
    drawable_list.extend(relation["name"] for _ in range(relation["probability"]))


def get_random(locale:str='en'):
    """Get a random relationship."""
    return random.choice(drawable_list)[locale]
