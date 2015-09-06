# Blot're Plays Atari 

Uses [Blot're][blotre] to croudsource controls for a game of Combat for the Atari 2600. 

# The Game
Player input is provided using two tags: `#player1` and `#player2`. Color status updates are converted to HSV values and translated into in-game commands:

* Black or very dark = press button /fire.
* Hue controls the direction of input.
* Saturation controls the duration of input. More saturation = longer button press.

## Resets
Automatically resets the game every five minutes or if no player input is provied for 45 seconds. Resets also randomly select a new game mode.


# Running 
Uses [Blot're.py][blotre-py] to subscribe to the Blot're tag collections.


[blotre]: https://blot.re
[blotre-py]: https://github.com/mattbierner/blotre-py
