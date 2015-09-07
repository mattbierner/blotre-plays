# Blot're Plays Atari 

Uses [Blot're][blotre] to croudsource controls for a game of *[Combat][]* for the Atari 2600. 

# Playing
I've set up a [live stream of the game][stream]. Anyone can join and play, although I'm not sure how long I'll be able to keep the stream up for.

## Joining
Player input is provided using two tags: `#player1` and `#player2`. To play, create a Blot're account and add one of these tags to any stream.

![](https://raw.github.com/mattbierner/blotre-plays/master/documentation/add-tag-1.png)

![](https://raw.github.com/mattbierner/blotre-plays/master/documentation/add-tag-2.png)

![](https://raw.github.com/mattbierner/blotre-plays/master/documentation/add-tag-3.png)

Any status changes you make to those streams will now be treated as player input.

### Input
Color status updates are converted to HSV values and translated into in-game commands for the two players:

* Black or very dark = press button/fire.
* Hue controls the direction of input (up, left, down, right).
* Saturation controls the duration of input. More saturation = longer button press.


### Resets
Automatically resets the game every ten minutes. Resets also randomly select a new game mode.


# Running
The program is written in Python 3. Uses [Blot're.py][blotre-py] to subscribe to the Blot're tag collections and [websockets][] to receive real time status updates for the tags.

Edit your Combat rom to disable the timer, just make the following change:

```
F18C	EA E8
``` 


[blotre]: https://blot.re
[blotre-py]: https://github.com/mattbierner/blotre-py

[stream]: https://gaming.youtube.com/c/Mattbierner/live
[post]: s

[combat]: https://en.wikipedia.org/wiki/Combat_(1977_video_game)
[websockets]: https://pypi.python.org/pypi/websockets