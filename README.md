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

## Test Coverage  Report



```
Name                                     Current  Last    Change
-----------------------------------------------
. --------------------------------------- 0.132  (0.12)     +0.01
  - __init__.py                           1.0    (1.00)     -0.00
  - config.py                             0.0    (0.00)     -0.00
  - localizer.py                          0.171  (0.16)     +0.01
  - main.py                               0.0    (0.00)     -0.00
 exts ----------------------------------- 0.7616 (0.36)     +0.40
  - charsheetmanager.py                   0.6507 (0.35)     +0.30
  - initiative.py                         0.9398 (0.41)     +0.53
  - nsc_gen.py                            0.9815 (0.39)     +0.59
  - roll_complex.py                       0.8837 (0.35)     +0.53
 interactions_unittest ------------------ 0.8685 (0.47)     +0.40
  - __init__.py                           1.0    (0.48)     +0.52
  - actions.py                            0.9028 (0.71)     +0.19
  - fake_contexts.py                      0.7801 (0.35)     +0.43
  - fake_models.py                        0.8772 (0.46)     +0.41
  - helpers.py                            0.9333 (0.40)     +0.53
 library -------------------------------  0.6987 (0.39)     +0.31
  - __init__.py                           1.0    (1.00)     -0.00
  - charsheet.py                          0.643  (0.43)     +0.22
  - complex_dice_parser.py                0.8675 (0.35)     +0.52
  - db_models.py                          1.0    (1.00)     -0.00
  - initiativatracking.py                 0.9655 (0.23)     +0.74
  - polydice.py                           0.6579 (0.38)     +0.28
  - saved_rolls.py                        1.0    (0.76)     +0.24
  - werewolf_gifts.py                     0.0    (0.00)     -0.00
 library.nsc_gen -----------------------  0.9355 (0.71)     +0.23
  - __init__.py                           1.0    (1.00)     -0.00
  - aengste.py                            1.0    (0.80)     +0.20
  - beziehungen.py                        1.0    (0.86)     +0.14
  - charaktereigenschaften.py             0.8571 (0.57)     +0.29
  - plaene.py                             0.9091 (0.64)     +0.27
  - speciesnames.py                       1.0    (1.00)     -0.00
```