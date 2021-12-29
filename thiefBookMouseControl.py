from pynput.mouse import Listener as MouseListener
from pynput.keyboard import Listener as KeyboardListener
import time
import sys
import pyautogui
import math
from pynput.keyboard import Controller, Key
from pynput.mouse import Button
import platform

valid_area = [[-1*(pyautogui.size().width/2),0], \
    [0,pyautogui.size().height]]


def on_release(key):
    # print("Key released: {0}".format(key))
    if key == Key.esc:
        # Stop listener
        plt = platform.system()
        key_controller = Controller()
        if plt == "Windows":
            key_controller.press(Key.ctrl)
            key_controller.press('m')
            key_controller.release(Key.ctrl)
            key_controller.release('m')
            key_controller.pressed(Key.ctrl,'m')
        elif plt == "Darwin":
            key_controller.press(Key.cmd)
            key_controller.press('m')
            key_controller.release(Key.cmd)
            key_controller.release('m')
            key_controller.pressed(Key.cmd,'m')
        else: print('os detect failed')
        mouse_listener.stop()
        return False

def on_mouse_click(x, y, button, pressed):
    if pressed:
        # print('Mouse clicked at ({0}, {1}) with {2}'.format(x, y, button))
        valid_area[0][0] = x
        valid_area[0][1] = y
    else:
        valid_area[1][0] = x
        valid_area[1][1] = y
        # print('Mouse released at ({0}, {1}) with {2}'.format(x, y, button))
        # Stop listener
        # choice = 'y'
        # choice = input('do you want to use this setting that from ({0:.0%},{0:.0%}) to ({0:.0%},{0:.0%})) [y/n/exit]: '.format(valid_area[0][0]/pyautogui.size().width,valid_area[0][1]/pyautogui.size().height,valid_area[1][0]/pyautogui.size().width,valid_area[1][1]/pyautogui.size().height))
        # if choice == 'y': return False
        return False

def on_mouse_release(x, y, button, pressed):
    if pressed:
        print('Mouse clicked at ({0}, {1}) with {2}'.format(x, y, button))
    else:
        print('Mouse released at ({0}, {1}) with {2}'.format(x, y, button))
        valid_area[1][0] = x
        valid_area[1][1] = y
        mouse_listener.stop()
    return False
def on_set_valid_position_mouse_release(x, y, button, pressed):
    if pressed:
        print('Mouse clicked at ({0}, {1}) with {2}'.format(x, y, button))
    else:
        print('Mouse released at ({0}, {1}) with {2}'.format(x, y, button))
        valid_area[1][0] = x
        valid_area[1][1] = y
    return False

def on_scroll(x, y, dx, dy):
    print('Mouse scrolled at ({0}, {1})({2}, {3})'.format(x, y, dx, dy))

def set_valid_position():
    choice = 0
    screen = pyautogui.size()
    global valid_area
    print('''plz select mode for valid area:
        0: full screen (not recommend)
        1: left screen
        2: right screen
        3: select by myself!
        ''')
    try:
        choice = int(input())
        if choice not in [0,1,2,3]: sys.exit()
    except: print('plz enter a number')

    if choice == 0:
        valid_area = [[-1*(screen.width/2),0], \
            [0,screen.height]]
    elif choice == 1:
        valid_area = [[-1*(screen.width),0], \
            [math.floor(-1*(screen.width/2)),screen.height]]
    elif choice == 2:
        valid_area = [[-1*(screen.width/2),0], \
            [0,screen.height]]
    elif choice == 3:
        print('plz select an area...')
        with MouseListener(on_click=on_mouse_click, on_release=on_set_valid_position_mouse_release) as mouse_listener:
            mouse_listener.join()
    else: print('NOT A CORRECT COMMAND')
    # print('selected ({0:.0%},{0:.0%}) to ({0:.0%},{0:.0%})'.format(valid_area[0][0]/pyautogui.size().width,valid_area[0][1]/pyautogui.size().height,valid_area[1][0]/pyautogui.size().width,valid_area[1][1]/pyautogui.size().height))

    print('finish setting')

def on_click(x, y, button, pressed):
    # print('Mouse clicked at ({0}, {1}) with {2}'.format(x, y, button))
    if pressed:
        if x >= valid_area[0][0] and x <= valid_area[1][0] and y >= valid_area[0][1] and y <= valid_area[1][1]:
            plt = platform.system()
            pos = '.' # next page
            if button == Button.right: pos = ',' # previous page
            key_controller = Controller()
            if plt == "Windows":
                key_controller.press(Key.ctrl)
                key_controller.press(Key.alt)
                key_controller.press(pos)
                key_controller.release(Key.ctrl)
                key_controller.release(Key.alt)
                key_controller.release(pos)
                key_controller.pressed(Key.ctrl,Key.alt,pos)
            elif plt == "Darwin":
                key_controller.press(Key.cmd)
                key_controller.press(pos)
                key_controller.release(Key.cmd)
                key_controller.release(pos)
                key_controller.pressed(Key.cmd,pos)
            else: print('os detect failed')
        else: print('not valid')

print('''
---------------------------------------------------
This is a script for vscode extension Thief-Book.
Left click for next page and right for previous page.
Press esc to terminate this script and It will reset to "hello world" page.
''')

set_valid_position() # func for setting validated area size. You can disable it if you don't need.
with KeyboardListener(on_release=on_release) as keyboard_listener, \
        MouseListener(on_click=on_click) as mouse_listener:
    keyboard_listener.join()
    mouse_listener.join()
