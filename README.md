# Crypto Hunter

A high-performance Ethereum wallet hunter that generates and checks random private keys for existing balances.

## Features

- Multi-threaded wallet generation and balance checking
- Real-time statistics display with live updates
- Clean terminal UI with progress animation
- Automatic logging of found wallets
- Efficient API usage with retry mechanism
- Thread-safe operations
- Graceful shutdown handling

## Requirements

- Python 3.8+
- An Ethereum node URL ([Infura](www.infura.io), [Alchemy](www.alchemy.com), or your own node)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/CoreZen/crypto-hunter.git
cd crypto-hunter
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
python crypto_hunter.py
```

The program will display:
- Runtime statistics
- Total attempts and speed
- API calls per second
- Latest generated key and address
- Any found wallets with balances

To stop the program, press Ctrl+C. The program will display final statistics before exiting.

## Configuration

You can modify these variables in `crypto_hunter.py`:
- `NUM_THREADS`: Number of concurrent threads (default: 30)
- `BATCH_SIZE`: Number of addresses to check in each batch (default: 5)
- `MAX_RETRIES`: Maximum number of API retry attempts (default: 3)

## Output

Found wallets are logged to `found_accounts.txt` with:
- Timestamp
- Currency
- Address
- Private Key
- Balance

## Security Note

- Never share your `.env` file
- Keep your found_accounts.txt secure
- Use this tool responsibly and ethically

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is for educational and research purposes only. Users are responsible for complying with applicable laws and regulations in their jurisdiction. 