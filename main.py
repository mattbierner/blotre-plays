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

# Extra config info used to get Blot're websocket address.
BLOTRE_CONF = { }

# Tag to listen to on Blotre for player 1
PLAYER1_TAG = "#player1"

# Tag to listen to on Blotre for player 2
PLAYER2_TAG = "#player2"

CONTROLS = ["up", "left", "down", "right"]

# Maximum length of time of a joystick button press 
MAX_PRESS = 2

# Minimum length of time of a joystick button press 
MIN_PRESS = 0.2

# Action to key mappings for player1
PLAYER1 = {
    "up": 0x11,     # w
    "right": 0x20,  # d
    "down": 0x1f,   # s
    "left": 0x1e,   # a
    "fire": 0x12    # e
}  

# Action to key mappings for player2
PLAYER2 = {
    "up": 0x15,     # y
    "right": 0x24,  # j
    "down": 0x23,   # h
    "left": 0x22,   # g
    "fire": 0x16    # u
}

# How long each round should last in seconds.
# Requires that Combat rom be modded to disable timer.
RESET_DELAY = 60 * 5

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

def hex_to_action(color):
    hsv = hex_to_hsv(color)
    input = hsv_to_control(hsv)
    if input == 'fire':
        return (0.2, 'fire')
    else:
        return ((MAX_PRESS - MIN_PRESS) * hsv[1] + MIN_PRESS, input)


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

def on_player_input(name, controls, color):
    action = hex_to_action(color)
    enter_input(name, controls, action)

def process_message(msg):
    try:
        data = json.loads(msg)
        color = None
        if data['type'] == "StatusUpdated": 
            color = data['status']['color']
        elif data['type'] == "ChildAdded":
            color = data['child']['status']['color']
        else:
            return
        
        if data['source'] == PLAYER1_TAG:
            return on_player_input('player1', PLAYER1, color)
        elif data['source'] == PLAYER2_TAG:
            return on_player_input('player2', PLAYER2, color)
    except Exception as e:
        debug(e)
        pass

def subscribe_tag(websocket, tagname):
    yield from websocket.send(json.dumps({
        'type': 'SubscribeCollection',
        'to': tagname
    }))

@asyncio.coroutine
def open_socket(client):
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


shell = win32com.client.Dispatch("WScript.Shell")
shell.AppActivate("Stella")

scheduled_reset()

client = blotre.Blotre({}, {}, BLOTRE_CONF)
loop.run_until_complete(open_socket(client))