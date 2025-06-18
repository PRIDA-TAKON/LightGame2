import sys
import time
import requests
import pygame
from pygame.locals import *
from pynput import keyboard
from threading import Thread
from threading import Event
import ctypes
import win32con
import win32api
import win32gui
import os


# --- QR Listener ---
def on_key_press(key):
    global qr_buffer, qr_start_time, qr_ready, profile_id, accepting_qr 

    if not accepting_qr:
        return

    try:
        if key.char:
            if qr_start_time is None:
                qr_start_time = time.time()
            qr_buffer += key.char 
    except AttributeError:
        if key == keyboard.Key.enter:
            if not qr_buffer:
                print("⚠️ SKIP\n")
                return

            qr_buffer += '\n'
            print(f"🔵 ENTER PRESSED → buffer = {repr(qr_buffer)}")

            if qr_start_time is None or time.time() - qr_start_time > 5:
                print("⏱️ Timeout / Scan QR! Again")
            else:
                profile_id = qr_buffer.strip()
                qr_ready = True
                accepting_qr = False
                print(f"✅ QR Code Data : {profile_id}")
                state_text = "✅ QR scanned. Ready for joystick"
            qr_buffer = ""
            qr_start_time = None


# --- POST to Server ---
def PostToServer(profile_id, score):
    try:
        url = "http://jobworld.digitalpicnic.co.th/api/v1/access"
        token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkRpZ2l0YWwgUGljbmljIiwiaWF0IjoxNTE2MjM5MDIyfQ.EalKGZx1I7BWcMAEEvNEWFnDoFEstH1SWcFKVqZezwo'
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "profile_id": profile_id,
            "result": score,
            "zone": "S7",
            "station": "bodily_kinesthetic"
        }
        response = requests.post(url, headers=headers, json=payload)
        if response.ok:
            print("✅ POST SUCCESSFUL :", response.status_code , score)
        else:
            print("⚠️ POST FAIL :", response.status_code, response.text)
        return response
    except Exception as ex:
        print("❌ ERROR:", str(ex))

