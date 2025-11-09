# 🔍 Bitcoin Address Balance Scanner (Blockstream API)

> ⚠️ **For Educational & Research Use Only**  
> This project demonstrates how to **extract Bitcoin addresses from log files**  
> and automatically check their **on-chain balances** using the  
> **Blockstream.info public API**.  
>
> It is intended for auditing, analysis, and research —  
> **not for unauthorized data collection or wallet tracking**.

---

## 🚀 Overview

This Python script:
- 🧩 Extracts all Bitcoin addresses (e.g., `addr=...`) from a log file (`attack_log.txt`)  
- 🔗 Queries the **Blockstream API** to fetch balance and transaction count  
- 🧮 Computes the current balance in **satoshis**  
- 💾 Saves all addresses with **non-zero balances** to `wyniki_saldo.txt`  

You can optionally filter addresses to include only **P2PKH** (`1...`) addresses  
and configure the number of worker threads for faster scanning.

---

## ✨ Features

| Feature | Description |
|----------|--------------|
| 📜 **Log parsing** | Automatically extracts `addr=` values from text logs |
| 🌐 **Blockchain query** | Fetches data from `https://blockstream.info/api/address/{addr}` |
| ⚙️ **Balance computation** | Calculates balance from funded and spent transaction sums |
| 💾 **Result output** | Saves addresses with positive balances to CSV format |
| 🚀 **Threaded performance** | Parallel API requests with retry/backoff |
| 🎯 **Filtering option** | Optionally check only addresses starting with “1” |
| 🧠 **Auto deduplication** | Removes duplicates while preserving order |

---

## 📂 File Structure

| File | Description |
|------|-------------|
| `check_balances.py` | Main script |
| `attack_log.txt` | Input log containing lines like `addr=...` |
| `wyniki_saldo.txt` | Output file (CSV: address, balance_satoshi, tx_count) |
| `README.md` | This documentation |

---

## ⚙️ Configuration

| Variable | Purpose |
|-----------|----------|
| `BLOCKSTREAM_API` | Base API URL (`https://blockstream.info/api`) |
| `INPUT_FILE` | Input log file (default: `attack_log.txt`) |
| `OUTPUT_FILE` | CSV file for results (default: `wyniki_saldo.txt`) |
| `ONLY_P2PKH` | If `True`, checks only addresses starting with `1` |
| `MAX_WORKERS` | Number of parallel threads (default: 10) |
| `MAX_RETRIES` | Retries for failed HTTP requests |
| `INITIAL_DELAY` | Starting backoff delay (in seconds) |
| `REQUEST_TIMEOUT` | Timeout for each API request |

**Dependencies**

pip install requests tqdm


---

## 🧠 How It Works

### 1️⃣ Extracting Addresses from Logs
The script scans the input file (`attack_log.txt`) for any `addr=...` occurrences:

```python
addr_regex = re.compile(r"addr=([A-Za-z0-9]+)")


It then deduplicates results while preserving the original order.

2️⃣ Querying the Blockstream API

Each address is queried at:

https://blockstream.info/api/address/<address>


The API returns JSON data including:

{
  "chain_stats": {
    "funded_txo_sum": 123456789,
    "spent_txo_sum": 10000000,
    "tx_count": 15
  }
}

3️⃣ Computing Balance

Balance is calculated as:

balance = funded_txo_sum - spent_txo_sum


Transaction count (tx_count) is included in the result.

4️⃣ Parallel Scanning with Retry

Up to 10 threads query addresses in parallel using ThreadPoolExecutor.
If rate-limited (HTTP 429), the script retries with exponential backoff.

for attempt in range(1, MAX_RETRIES + 1):
    time.sleep(delay)
    delay = min(15.0, delay * 1.7)

5️⃣ Saving Results

Addresses with a positive balance are saved as CSV:

address,balance_satoshi,tx_count
1FfmbHfnpaZjKFvyi1okTjJJusN455paPH,2500000,3
bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh,100000,1

🧾 Example Usage
✅ Basic run
python3 check_balances.py

✅ Only P2PKH addresses (1...)
python3 check_balances.py --only1

✅ Custom number of threads
python3 check_balances.py --workers 20

🧩 Example Output
[*] Wczytuję adresy z attack_log.txt
[*] Znalazłem 542 unikalnych adresów
Sprawdzanie adresów: 100%|████████████████████████████████| 542/542 [00:19<00:00, 27.6it/s]
[*] Zapisano 7 adresów z saldem > 0 do wyniki_saldo.txt

🧰 Core Components
Function	Description
extract_addresses_from_log()	Reads log and extracts Bitcoin addresses
get_address_info()	Fetches JSON data from Blockstream API with retry logic
compute_balance_from_chain_stats()	Calculates balance from API stats
check_address()	Wrapper that combines fetch, parse, and result formatting
main()	Coordinates parsing, multithreading, and saving results
⚡ Performance Tips

🚀 Increase --workers for faster scans (be cautious of rate limits).

🕒 Use tqdm for real-time progress visibility.

🔁 Adjust retry/backoff parameters for slow networks.

🧠 Use filters (--only1) to reduce unnecessary API calls.

💾 Save logs if scanning multiple large files.

🔒 Ethical & Legal Notice

This project is for educational blockchain analytics only.
It must not be used for surveillance, mass data scraping, or privacy violation.

You may:

Analyze blockchain address data you own.

Audit transaction histories for research.

Learn about rate-limiting and API reliability.

You must not:

Target addresses you don’t control.

Attempt to bypass API limits or anonymize illegal activity.

Unauthorized scanning of public APIs for private data is illegal and unethical.

🧰 Suggested Improvements

💾 Add CSV appending instead of overwrite mode.

📊 Include total BTC sum across all found addresses.

⚙️ Add support for other explorers (Blockchair, SoChain, etc).

🌐 Implement rotating proxies for stable large-scale scans.

🧩 Add JSON export with detailed API response data.

🪪 License

MIT License
© 2025 — Author: [Ethicbrudhack]

💡 Summary

This project provides a simple yet powerful tool for:

🔎 Extracting addresses from logs,

🔗 Querying blockchain APIs, and

💰 Identifying addresses with real balances.

A practical resource for blockchain researchers, security testers,
and anyone learning about API rate limits and parallel data processing.

🧠 Audit responsibly. Learn deeply. Respect user privacy.

BTC donation address: bc1q4nyq7kr4nwq6zw35pg0zl0k9jmdmtmadlfvqhr
