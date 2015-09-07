# Blot're Plays Atari 

Uses [Blot're][blotre] to croudsource controls for a game of Combat for the Atari 2600. 

# The Game
Player input is provided using two tags: `#player1` and `#player2`. Color status updates are converted to HSV values and translated into in-game commands for the two players:

* Black or very dark = press button/fire.
* Hue controls the direction of input (up, left, down, right).
* Saturation controls the duration of input. More saturation = longer button press.

## Resets
Automatically resets the game every ten minutes. Resets also randomly select a new game mode.

Edit your Combat rom to disable the timer, just make the following change:

```
F18C	EA E8
``` 

# Running
Uses [Blot're.py][blotre-py] to subscribe to the Blot're tag collections.


[blotre]: https://blot.re
[blotre-py]: https://github.com/mattbierner/blotre-py
