import threading
import time
from typing import Optional

class SharedMemoryMonitor:
    """Manages shared memory for storing and processing transcribed text."""
    
    def __init__(self) -> None:
        self.shared_memory: Optional[str] = ""
        self.long_term_memory: str = ""
        self.last_update_time: float = time.time()
        self.running: bool = False
        self.check_every: int = 4

    def update_memory(self, new_value: str) -> None:
        """Update shared memory with new transcribed text."""
        if self.shared_memory is None:
            self.shared_memory = ""
        self.shared_memory += new_value + " "
        self.last_update_time = time.time()

    def _monitor(self) -> None:
        """Monitor shared memory for updates and execute processing when needed."""
        while self.running:
            time_since_update = time.time() - self.last_update_time
            if time_since_update > self.check_every:
                self.execute()
                self.last_update_time = time.time()
            time.sleep(1)

    def execute(self) -> None:
        """Process shared memory content based on triggers and timing."""
        if self.shared_memory is None:
            return

        if "study buddy" in self.shared_memory:
            print(f"IMMEDIATE: {self.shared_memory}")
        else:
            self.long_term_memory += self.shared_memory

        self.shared_memory = None

    def start(self) -> None:
        """Start the memory monitoring thread."""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._monitor)
            self.thread.daemon = True
            self.thread.start()

    def stop(self) -> None:
        """Stop the memory monitoring thread."""
        if self.running:
            self.running = False
            self.thread.join()