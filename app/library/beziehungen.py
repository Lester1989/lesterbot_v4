import random

relationships = [
    {
        'name':'ist verliebt in',
        'probability':1,
    },
    {
        'name':'mag',
        'probability':4,

    },
    {
        'name':'bewundert',
        'probability':2,

    },
    {
        'name':'lernt von',
        'probability':2,

    },
    {
        'name':'kennt',
        'probability':6,

    },
    {
        'name':'mag nicht',
        'probability':5,

    },
    {
        'name':'beneidet',
        'probability':3,

    },
    {
        'name':'hasst',
        'probability':2,

    },

]

drawable_list = []
for relation in relationships:
    drawable_list.extend(relation['name'] for _ in range(relation['probability']))

def get_random():
    return random.choice(drawable_list)
