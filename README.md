# Plant're

Demonstrates using Python with [Blot're.py][blotre-py] to upload plant soil moisture readings from a Raspberry Pi to [Blot're][blotre].

# Hardware
I used [these supplies and instructions][hardware-tut] to hookup a very basic soil moisture sensor to my Raspberry Pi. That tutorial's hookup for the MCP3008 analog-to-digital-converter didn't work for me, so I used the wiring and Python sample from [an Adafruit tutorial][ada-tut].

By default the script reads data from pin 0 on the MCP3008.

# Software

### Dependencies
* [Blot're.py][blotre-py]
* [Spectra][]
* rpi.gpio

```
$ pip install spectra blotre 
$ easy_install rpi.gpio
```

### Running
You must run `main.py` with sudo on a Raspberry Pi in order to use GPIO.

```
$ sudo python main.py
```

### Adjusting
You can adjust a few constants to customize the script's behavior.

* `TARGET_STREAM_NAME` - Name of top level stream uploaded to. This stream will be created under the root stream of the user who authorizes the app. Defaults to `"Mr Tree"`.
* `MOISTURE_SENSOR_MAX` - Maximum (most wet) value of moisture sensor. Only used to determine the health color of the plant. For best results, take reading immediately after watering the plant in question.
* `MOISTURE_SENSOR_MIN` - Minimum (most dry) value of moisture sensor. For best results, take reading when the plant has dried out and needs to be watered.
* `MOISTURE_SCALE` - You can adjust the colors in the scale (from dry to wet) if you like.
* `INTERVAL` - How often (in seconds) to try reading a from the moisture sensor. Defaults to every 5 minutes.

### Starting Script At Boot
`plantre.init.d.sh` is a sample init.d script that you can use to start `main.py` on boot. To use it:

* In `plantre.init.d.sh`, update `DIR` to point to where your copy of `main.py` lives.
* Copy `plantre.init.d.sh` into `/etc/init`
* Make sure both `main.py` and `plantre.init.d.sh` are executable: `chmod 755 main.py`, `chmod 755 /etc/init.d/plantre.init.d.sh`
* Run `sudo update-rc.d plantre.init.d.sh defaults` to register script to be run at init.

Start or stop the script by running:

```
$ sudo /etc/init.d/plantre.init.d.sh start
```


[blotre]: https://blot.re
[blotre-py]: https://github.com/mattbierner/blotre-py

[spectra]: https://github.com/jsvine/spectra

[hardware-tut]: http://computers.tutsplus.com/tutorials/build-a-raspberry-pi-moisture-sensor-to-monitor-your-plants--mac-52875
[ada-tut]: https://learn.adafruit.com/reading-a-analog-in-and-controlling-audio-volume-with-the-raspberry-pi