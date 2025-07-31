import os
import sys
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Folder yang dipantau (hanya src/)
WATCH_DIR = os.path.join(os.getcwd(), "src")
ENTRY_FILE = "main.py"

def debug_prefix(msg):
    print(f"[WATCHDOG] {msg}")

class ChangeHandler(FileSystemEventHandler):
    def __init__(self, restart_callback):
        self.restart_callback = restart_callback

    def on_any_event(self, event):
        if not event.is_directory and event.src_path.endswith(".py"):
            debug_prefix(f"📁 Detected change in: {os.path.basename(event.src_path)}")
            self.restart_callback()

class DevRunner:
    def __init__(self):
        self.process = None
        self.observer = Observer()

    def start(self):
        debug_prefix(f"👁 Watching directory: {WATCH_DIR}")
        self.start_watching()
        self.start_process()

        try:
            while True:
                if self.process.poll() is not None:
                    debug_prefix(f"💥 Program exited with code {self.process.returncode}")
                    self.process = None
                    time.sleep(0.5)
                    self.start_process()
                time.sleep(1)
        except KeyboardInterrupt:
            debug_prefix("👋 Exit requested. Cleaning up...")
            self.cleanup()

    def start_process(self):
        debug_prefix(f"🚀 Starting {ENTRY_FILE}...")
        self.process = subprocess.Popen(
            [sys.executable, ENTRY_FILE],
            cwd=WATCH_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        # Menampilkan output dari program utama
        def stream_output():
            for line in self.process.stdout:
                print(line, end='')

        import threading
        threading.Thread(target=stream_output, daemon=True).start()

    def restart_process(self):
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()
        self.start_process()

    def start_watching(self):
        event_handler = ChangeHandler(self.restart_process)
        self.observer.schedule(event_handler, WATCH_DIR, recursive=True)
        self.observer.start()

    def cleanup(self):
        if self.process:
            self.process.terminate()
        self.observer.stop()
        self.observer.join()

if __name__ == "__main__":
    runner = DevRunner()
    runner.start()
