# this is a discord bot for tabletop rpgs like world of darkness, DnD, Pathfinder, Beyond the Wall, The Dark Eye, Hexxen 1733 and many more

It can be hosted in a docker container for easiest deployment

# Features

* [x] Rolling multiple Dice (with specified side count)
* [x] Complex Dice Pools with optional parameters
* [x] exploding dice
* [x] roll against difficulty and count successes
* [x] sum all rolled dice
* [x] modify each dice result or the pool result
* [x] save complex dicepools for easy reuse
* [x] manage initiative
* [ ] WIP (65% coverage) manage system agnostic charactersheets
* [x] Create random NPC (for roleplay, without stats but with motivations and fears)
* [x] gift lookup for Werewolf:20th Edition. (Needs Upload of JSON formatted Gifts, not included in REPO due to copyright)
* [x] localisation for different languages
* [x] x-card
* [ ] safety tools (questioneer and summary)

## Test Coverage  Report



```
Name                                     Current  Last    Change
-----------------------------------------------
 .--------------------------------------- 0.132  (0.13)     -0.00
  - __init__.py                           1.0    (1.00)     -0.00
  - config.py                             0.0    (0.00)     -0.00
  - localizer.py                          0.171  (0.17)     -0.00
  - main.py                               0.0    (0.00)     -0.00
 exts------------------------------------ 0.849  (0.86)     --0.01
  - charsheetmanager.py                   0.8129 (0.81)     -0.00
  - initiative.py                         0.9398 (0.94)     -0.00
  - nsc_gen.py                            0.9815 (0.98)     -0.00
  - roll_complex.py                       0.8837 (0.88)     -0.00
  - werewolf_w20.py                       0.7981 (0.00)     +0.80
 interactions_unittest------------------- 0.8784 (0.87)     +0.01
  - __init__.py                           1.0    (1.00)     -0.00
  - actions.py                            0.9028 (0.90)     -0.00
  - fake_contexts.py                      0.8085 (0.78)     +0.03
  - fake_models.py                        0.8772 (0.88)     -0.00
  - helpers.py                            0.9333 (0.93)     -0.00
 library--------------------------------- 0.7601 (0.73)     +0.03
  - __init__.py                           1.0    (1.00)     -0.00
  - charsheet.py                          0.7098 (0.71)     -0.00
  - complex_dice_parser.py                0.8675 (0.87)     -0.00
  - db_models.py                          1.0    (1.00)     -0.00
  - initiativatracking.py                 0.9655 (0.97)     -0.00
  - polydice.py                           0.6842 (0.66)     +0.03
  - saved_rolls.py                        1.0    (1.00)     -0.00
  - werewolf_gifts.py                     0.8696 (0.00)     +0.87
 library.nsc_gen------------------------- 0.9677 (0.97)     -0.00
  - __init__.py                           1.0    (1.00)     -0.00
  - aengste.py                            1.0    (1.00)     -0.00
  - beziehungen.py                        1.0    (1.00)     -0.00
  - charaktereigenschaften.py             0.8571 (0.86)     -0.00
  - plaene.py                             1.0    (1.00)     -0.00
  - speciesnames.py                       1.0    (1.00)     -0.00
```