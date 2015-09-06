import asyncio
import blotre
import colorsys
import codecs
from datetime import datetime
from input import tap_key, PressKey, ReleaseKey
import json
import math
import random
import struct
import sys
import time
import threading
import websockets
import win32com.client


BLOTRE_CONF = {
}

# Tag to listen to on Blotre for player 1
PLAYER1_TAG = "player1"

# Tag to listen to on Blotre for player 2
PLAYER2_TAG = "player2"

CONTROLS = ["up", "left", "down", "right"]

MAX_PRESS = 2
MIN_PRESS = 0.2

PLAYER1 = {
    "up": 0x11,
    "right": 0x20,
    "down": 0x1f,
    "left": 0x1e,
    "fire": 0x12 }

PLAYER2 = {
    "up": 0x15,
    "right": 0x24,
    "down": 0x23,
    "left": 0x22,
    "fire": 0x16 }

RESET_DELAY = 60 * 5

TIMEOUT_DELAY = 45

last_input_time = datetime.now()

current_inputs = {
    'player1': { 'index': 0, 'value': 0 },
    'player2': { 'index': 0, 'value': 0 } }

loop = asyncio.get_event_loop()

def debug(*x):
    print(*x)
    sys.stdout.flush()

def hex_to_rgb(hex):
    """Convert a hex string to rgb."""
    return struct.unpack('BBB', codecs.decode(hex[1:], 'hex'))

def hex_to_hsv(hex):
    """Convert a hex string to hsv."""
    rgb = hex_to_rgb(hex)
    return colorsys.rgb_to_hsv(rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0)

def is_dark(hsv, threshold=0.15):
    """Check if a color is close to black"""
    return hsv[2] <= threshold

def hsv_to_control(hsv):
    """Map a color to a control."""
    if is_dark(hsv):
        return 'fire'
    sector = math.ceil(hsv[0] / 0.125)
    return CONTROLS[int((sector % 7) / 2)]

def reset_game():
    """Trigger a game reset"""
    tap_key(0x3C)

def select_new_mode():
    reset_game()
    for x in range(random.randint(0, 5)):
        tap_key(0x3b)

def start_new_game():
    """Trigger a game reset"""
    select_new_mode()
    reset_game()

def scheduled_reset():
    start_new_game()
    loop.call_later(RESET_DELAY, scheduled_reset)

def check_timeout():
    global last_input_time
    if (datetime.now() - last_input_time).total_seconds() > TIMEOUT_DELAY:
        start_new_game()
    loop.call_later(TIMEOUT_DELAY, check_timeout)

def clamp(lower, upper, x):
    return max(lower, min(upper, x))

def try_release_key(player, key, target_index):
    global current_inputs
    current = current_inputs[player]
    if current['index'] != target_index or current['value'] != key:
        return
    ReleaseKey(key)
    current['value'] = 0

def enter_input(player, controls, action):
    global current_inputs
    delay, input = action
    key = controls.get(input, '0')
    current = current_inputs[player]
    ReleaseKey(current['value'])
    PressKey(key)
    index = current['index'] + 1
    current['index'] = index
    current['value'] = key
    loop.call_later(delay, try_release_key, player, key, index)

def subscribe_tag(websocket, tagname):
    yield from websocket.send(json.dumps({
        'type': 'SubscribeCollection',
        'to': "#" + tagname
    }))

def color_to_action(color):
    hsv = hex_to_hsv(color)
    input = hsv_to_control(hsv)
    if input == 'fire':
        return (0.2, 'fire')
    else:
        return (clamp(MIN_PRESS, MAX_PRESS, MAX_PRESS * hsv[1]), input)

def on_player1_input(color):
    global last_input_time
    last_input_time = datetime.now()
    action = color_to_action(color)
    enter_input('player1', PLAYER1, action)

def on_player2_input(color):
    global last_input_time
    last_input_time = datetime.now()
    action = color_to_action(color)
    enter_input('player2', PLAYER2, action)

def process_message(msg):
    try:
        data = json.loads(msg)
        if data['type'] == "StatusUpdated":
            color = data['status']['color']
            if data['source'] == '#' + PLAYER1_TAG:
                return on_player1_input(color)
            elif data['source'] == '#' + PLAYER2_TAG:
                return on_player2_input(color)
    except Exception as e:
        debug(e)
        pass

@asyncio.coroutine
def hello(client):
    debug('opened socket')
    websocket = yield from websockets.connect(client.get_websocket_url())
    yield from subscribe_tag(websocket, PLAYER1_TAG)
    yield from subscribe_tag(websocket, PLAYER2_TAG)
    while True:
        msg = yield from websocket.recv()
        if msg is None:
            break
        else:
            process_message(msg)
    yield from websocket.close()


client = blotre.Blotre({}, {}, BLOTRE_CONF)

shell = win32com.client.Dispatch("WScript.Shell")
shell.AppActivate("Stella")

scheduled_reset()
loop.call_later(TIMEOUT_DELAY, check_timeout)

loop.run_until_complete(hello(client))