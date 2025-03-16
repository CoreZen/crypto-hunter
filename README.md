# EtherHunter

A high-performance Ethereum wallet hunter that generates and checks random private keys for existing balances.

## Features

- Multi-threaded wallet generation and balance checking
- Real-time statistics display with live updates
- Clean terminal UI with progress animation
- Automatic logging of found wallets
- Efficient API usage with a retry mechanism
- Thread-safe operations
- Graceful shutdown handling

## Requirements

- Python 3.8+
- An Ethereum node URL ([Infura](https://www.infura.io), [Alchemy](https://www.alchemy.com), or your own node)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/CoreZen/ether-hunter.git
cd ether-hunter
```

2. Install required packages:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project directory:

```bash
ETH_NODE_URL=your_ethereum_node_url_here
```

## Usage

Run the script:

```bash
python ether_hunter.py
```

The program will display:
- Runtime statistics
- Total attempts and speed
- API calls per second
- Latest generated key and address
- Any found wallets with balances

To stop the program, press `Ctrl+C`. The program will display final statistics before exiting.

## Configuration

Modify the following variables in `ether_hunter.py` to suit your needs:
- `NUM_THREADS`: Number of concurrent threads (default: 30)
- `BATCH_SIZE`: Number of addresses to check in each batch (default: 5)
- `MAX_RETRIES`: Maximum number of API retry attempts (default: 3)

## Output

Found wallets are logged to `found_accounts.txt` with the following details:
- Timestamp
- Currency
- Address
- Private Key
- Balance

## Security Considerations

- Never share your `.env` file.
- Keep `found_accounts.txt` secure and encrypted.
- Use this tool responsibly and ethically.

## Probability and Feasibility

The probability of randomly finding an Ethereum wallet with a balance is **astronomically low**. Consider the following:

- The total number of possible private keys is **2^256** (~1.15 x 10^77).
- This is **more than the number of atoms in the observable universe** (~10^80).
- Statistically, you are:
  - **42 billion times** more likely to win the Powerball lottery (1 in 292 million).
  - **250 million times** more likely to be struck by lightning in your lifetime (1 in 15,300).
  - **2.5 million times** more likely to become a saint (1 in 20 million).
  - **10 million times** more likely to become an astronaut (1 in 12 million).
  - **7 billion times** more likely to win an Olympic gold medal (1 in 662,000).

Even at **1 million attempts per second**, scanning just **1%** of all possible keys would take longer than the current age of the universe (13.8 billion years).

This tool is intended for **educational purposes** to illustrate:
- Cryptographic security principles.
- The enormity of large numbers in cryptography.
- The resilience of properly generated private keys.
- Multi-threaded programming techniques.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is for **educational and research purposes only**. Users are responsible for complying with applicable laws and regulations in their jurisdiction.
