from eth_account import Account
import secrets
from web3 import Web3
import time
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
import termios
import tty
import select

# Load environment variables from .env file
load_dotenv()

# Initialize Web3 with your Ethereum node URL
ETHEREUM_NODE_URL = os.getenv('ETH_NODE_URL')
if not ETHEREUM_NODE_URL:
    raise ValueError("ETH_NODE_URL not found in .env file")

# Configuration
NUM_THREADS = 30
BATCH_SIZE = 5
MAX_RETRIES = 3

# Animation state
ANIMATION_STATES = ["", "⚡", "⚡⚡", "⚡⚡⚡"]
animation_idx = 0

# ANSI escape codes for colors and cursor movement
CYAN = '\033[96m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
RESET = '\033[0m'
BOLD = '\033[1m'
CLEAR = '\033[2J\033[H'

# Create a thread-local Web3 instance to avoid sharing connections between threads
thread_local = threading.local()

def get_w3():
    """Get thread-local Web3 instance"""
    if not hasattr(thread_local, "w3"):
        thread_local.w3 = Web3(Web3.HTTPProvider(ETHEREUM_NODE_URL))
    return thread_local.w3

class Stats:
    def __init__(self):
        self.attempts = 0
        self.api_calls = 0
        self.errors = 0
        self.lock = threading.Lock()
        self.last_private_key = ""
        self.last_address = ""
    
    def increment(self, amount=1):
        with self.lock:
            self.attempts += amount
            return self.attempts
    
    def increment_api_calls(self):
        with self.lock:
            self.api_calls += 1
    
    def increment_errors(self):
        with self.lock:
            self.errors += 1
    
    def update_last(self, private_key, address):
        with self.lock:
            self.last_private_key = private_key
            self.last_address = address

def generate_random_private_key():
    """Generate a random 32-byte private key"""
    return secrets.token_hex(32)

def check_eth_balance(address, stats):
    """Check the ETH balance of an address with retries"""
    for attempt in range(MAX_RETRIES):
        try:
            w3 = get_w3()
            balance = w3.eth.get_balance(address)
            stats.increment_api_calls()
            return w3.from_wei(balance, 'ether')
        except Exception as e:
            if attempt == MAX_RETRIES - 1:
                stats.increment_errors()
            time.sleep(0.1 * (attempt + 1))  # Exponential backoff
    return 0

def check_addresses_batch(private_keys, stats):
    """Check a batch of addresses in parallel"""
    results = []
    for private_key in private_keys:
        account = Account.from_key(private_key)
        address = account.address
        stats.update_last(private_key, address)
        balance = check_eth_balance(address, stats)
        if balance > 0:
            results.append((private_key, address, balance))
    return results

def log_found_account(address, private_key, balance, currency):
    """Log any found accounts with balance to a file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open('found_accounts.txt', 'a') as f:
        f.write(f"\nFound at: {timestamp}\n")
        f.write(f"Currency: {currency}\n")
        f.write(f"Address: {address}\n")
        f.write(f"Private Key: {private_key}\n")
        f.write(f"Balance: {balance} {currency}\n")
        f.write("-" * 50 + "\n")

def format_duration(seconds):
    """Format duration in a readable way"""
    return str(timedelta(seconds=int(seconds)))

def setup_display():
    """Initialize the static parts of the display"""
    sys.stdout.write(CLEAR)
    
    title = f"{BOLD}{CYAN}ETHER HUNTER{RESET}"
    lines = [
        f"  {title} {ANIMATION_STATES[0]}",
        f"{YELLOW}═{RESET}" * 80,
        f"{BOLD}Runtime:{RESET} 0:00:00",
        f"{BOLD}Threads:{RESET} {NUM_THREADS}",
        f"{BOLD}Batch Size:{RESET} {BATCH_SIZE}",
        f"{BOLD}Total Attempts:{RESET} 0",
        f"{BOLD}Speed:{RESET} 0.00/s",
        f"{BOLD}API Calls/sec:{RESET} 0.00",
        f"{BOLD}Errors:{RESET} 0",
        f"{YELLOW}═{RESET}" * 80,
        f"{BOLD}Latest Key:{RESET} ",
        f"{BOLD}Latest Address:{RESET} ",
        f"{YELLOW}═{RESET}" * 80
    ]
    print('\n'.join(lines))
    sys.stdout.flush()

def update_display(stats, start_time):
    """Update the dynamic parts of the display"""
    global animation_idx
    elapsed_time = time.time() - start_time
    attempts_per_sec = stats.attempts / elapsed_time if elapsed_time > 0 else 0
    api_calls_per_sec = stats.api_calls / elapsed_time if elapsed_time > 0 else 0
    
    animation_idx = (animation_idx + 1) % len(ANIMATION_STATES)
    sys.stdout.write('\033[H')
    
    title = f"{BOLD}{CYAN}ETHER HUNTER{RESET}"
    lines = [
        f"  {title} {YELLOW}{ANIMATION_STATES[animation_idx]}{RESET}",
        f"{YELLOW}═{RESET}" * 80,
        f"{BOLD}Runtime:{RESET} {BLUE}{format_duration(elapsed_time)}{RESET}",
        f"{BOLD}Threads:{RESET} {BLUE}{NUM_THREADS}{RESET}",
        f"{BOLD}Batch Size:{RESET} {BLUE}{BATCH_SIZE}{RESET}",
        f"{BOLD}Total Attempts:{RESET} {MAGENTA}{stats.attempts:,}{RESET}",
        f"{BOLD}Speed:{RESET} {GREEN}{attempts_per_sec:.2f}/s{RESET}",
        f"{BOLD}API Calls/sec:{RESET} {GREEN}{api_calls_per_sec:.2f}{RESET}",
        f"{BOLD}Errors:{RESET} {YELLOW}{stats.errors}{RESET}",
        f"{YELLOW}═{RESET}" * 80,
        f"{BOLD}Latest Key:{RESET} {CYAN}{stats.last_private_key}{RESET}",
        f"{BOLD}Latest Address:{RESET} {CYAN}{stats.last_address}{RESET}",
        f"{YELLOW}═{RESET}" * 80
    ]
    
    for line in lines:
        sys.stdout.write('\r' + line + '\033[K\n')
    sys.stdout.flush()

def main():
    old_settings = termios.tcgetattr(sys.stdin.fileno())
    sys.stdout.write('\033[?25l' + CLEAR)
    setup_display()
    tty.setraw(sys.stdin.fileno())
    
    stats = Stats()
    start_time = time.time()
    display_lock = threading.Lock()
    
    try:
        with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
            futures = []
            
            for _ in range(NUM_THREADS):
                private_keys = [generate_random_private_key() for _ in range(BATCH_SIZE)]
                future = executor.submit(check_addresses_batch, private_keys, stats)
                futures.append(future)
            
            while True:
                with display_lock:
                    update_display(stats, start_time)
                
                # Check for Ctrl+C
                if sys.stdin in select.select([sys.stdin], [], [], 0.0)[0]:
                    char = sys.stdin.read(1)
                    if char == '\x03':  # Ctrl+C
                        raise KeyboardInterrupt
                
                done, futures = futures, []
                for future in as_completed(done):
                    results = future.result()
                    stats.increment(BATCH_SIZE)
                    
                    for private_key, address, balance in results:
                        if balance > 0:
                            with display_lock:
                                sys.stdout.write('\033[s')
                                sys.stdout.write('\033[0;0H\033[12B')
                                print(f"{BOLD}{GREEN}╔══ FOUND ETH WALLET WITH BALANCE ══╗{RESET}")
                                print(f"{BOLD}{GREEN}║{RESET} {CYAN}Address:{RESET}    {address}")
                                print(f"{BOLD}{GREEN}║{RESET} {CYAN}Private Key:{RESET} {private_key}")
                                print(f"{BOLD}{GREEN}║{RESET} {CYAN}Balance:{RESET}    {balance} ETH")
                                print(f"{BOLD}{GREEN}╚{'═' * 34}╝{RESET}")
                                sys.stdout.write('\033[u')
                            log_found_account(address, private_key, balance, "ETH")
                    
                    private_keys = [generate_random_private_key() for _ in range(BATCH_SIZE)]
                    future = executor.submit(check_addresses_batch, private_keys, stats)
                    futures.append(future)
                
                time.sleep(0.1)
                
    except KeyboardInterrupt:
        # First restore terminal to normal mode
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old_settings)
        sys.stdout.write('\033[?25h')  # Show cursor
        
        print("\n\nStopping gracefully, please wait...")
        sys.stdout.flush()
        
        # Cancel all pending futures
        for future in futures:
            future.cancel()
        
        # Wait for everything to settle
        time.sleep(1)
        
        # Clear screen and move to home
        print('\033c\033[3J\033[H')
        
        # Print final stats with minimal formatting
        elapsed_time = time.time() - start_time
        print(f"{BOLD}{CYAN}ETHER HUNTER - FINAL STATS{RESET}")
        print("-" * 80)
        print(f"Total Runtime:      {format_duration(elapsed_time)}")
        print(f"Total Attempts:     {stats.attempts:,}")
        print(f"Total API Calls:    {stats.api_calls:,}")
        print(f"Total Errors:       {stats.errors}")
        print(f"Average Speed:      {stats.attempts/elapsed_time:.2f} attempts/sec")
        print(f"API Call Rate:      {stats.api_calls/elapsed_time:.2f} calls/sec")
        print("-" * 80)
        print()
        sys.stdout.flush()
        sys.exit(0)
    finally:
        # Only restore terminal settings if we haven't already
        try:
            termios.tcgetattr(sys.stdin.fileno())
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old_settings)
            sys.stdout.write('\033[?25h')
        except:
            pass

if __name__ == "__main__":
    main() 