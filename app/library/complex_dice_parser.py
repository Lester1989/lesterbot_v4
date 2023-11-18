from enum import Enum

from app.library.polydice import ComplexPool, ExplodingBehavior


class ParsingState(Enum):
    NONE = 0
    SUCCESS = 1
    FAILURE = 2
    EXPLODE = 3
    EXPLODE_CASC = 4
    HIGHEST = 5
    LOWEST = 6
    POOL_BONUS = 7
    POOL_MALUS = 8
    DICE_BONUS = 9
    DICE_MALUS = 10
    NUMBER = 11
    SIDES = 12


# * Each Description can start with number, if none is given 1 is assumed
# * Normal Dice Types are defined by a letter(w  / W / d / D) followed by the number of sides on the dice, if none is given 6 is assumed
# * after the number of sides you can be more special dice behaviors:
# s for success (greater or equal)
# f for failure (less or equal)
# ! for single exploding dice (greater or equal)
# !! for recursively exploding dice (greater or equal)
# h to use only the highest values (amount)
# b to use only the lowest values (amount)
# +/- to add a modifier to the dice pool (success count if s is used, sum if not)
# ++/-- to add a modifier to each dice result


class Parser:
    tokens = {
        "w": ParsingState.SIDES,
        "d": ParsingState.SIDES,
        "W": ParsingState.SIDES,
        "D": ParsingState.SIDES,
        "s": ParsingState.SUCCESS,
        "f": ParsingState.FAILURE,
        "!": ParsingState.EXPLODE,
        "!!": ParsingState.EXPLODE_CASC,
        "h": ParsingState.HIGHEST,
        "b": ParsingState.LOWEST,
        "+": ParsingState.POOL_BONUS,
        "-": ParsingState.POOL_MALUS,
        "++": ParsingState.DICE_BONUS,
        "--": ParsingState.DICE_MALUS,
    }
    tokens_list = sorted(tokens.keys(), key=len, reverse=True)
    state: ParsingState = ParsingState.NUMBER
    tokens_found: list[tuple[str, int]] = []
    stack: str = ""
    input_string: str = ""

    def __init__(self, description: str):
        self.input_string = description
        self.state = ParsingState.NUMBER
        self.stack = ""
        self.tokens_found = []
        while description:
            if description[0].isdigit():
                self.stack += description[0]
                description = description[1:]
            else:
                self.tokens_found.append((self.state, int(self.stack) if self.stack else 1))
                self.stack = ""
                self.state = ParsingState.NONE
                for token in self.tokens_list:
                    if description.startswith(token):
                        self.state = self.tokens[token]
                        description = description[len(token) :]
                        break
                else:
                    raise ValueError(f"Unknown token {description[0]}")
        if self.stack:
            self.tokens_found.append((self.state, int(self.stack) if self.stack else 1))
            self.stack = ""

    def build_pool(self):
        pool = ComplexPool(description=self.input_string)
        for token in self.tokens_found:
            if token[0] == ParsingState.SUCCESS:
                pool.success_threshold = token[1]
            elif token[0] == ParsingState.FAILURE:
                pool.failure_threshold = token[1]
            elif token[0] == ParsingState.EXPLODE:
                pool.explode = ExplodingBehavior.ONCE
                pool.explode_threshold = token[1]
            elif token[0] == ParsingState.EXPLODE_CASC:
                pool.explode = ExplodingBehavior.CASCADING
                pool.explode_threshold = token[1]
            elif token[0] == ParsingState.HIGHEST:
                pool.highest_count = token[1]
            elif token[0] == ParsingState.LOWEST:
                pool.lowest_count = token[1]
            elif token[0] == ParsingState.POOL_BONUS:
                pool.pool_modifier += token[1]
            elif token[0] == ParsingState.POOL_MALUS:
                pool.pool_modifier -= token[1]
            elif token[0] == ParsingState.DICE_BONUS:
                pool.dice_modifier += token[1]
            elif token[0] == ParsingState.DICE_MALUS:
                pool.dice_modifier -= token[1]
            elif token[0] == ParsingState.NUMBER:
                pool.number = token[1]
            elif token[0] == ParsingState.SIDES:
                pool.sides = token[1]
            else:
                raise ValueError(
                    f"Unknown token {token[0]} with {token[1]} from {self.input_string}"
                )
        return pool
