#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sprawdza salda adresów wyciągniętych z attack_log.txt (w formacie addr=...).
Zapisuje adresy z saldem > 0 do wyniki_saldo.txt (adres, balance_satoshi, tx_count).
Uruchom: python3 check_balances.py
Opcjonalnie: ustaw ONLY_P2PKH = True, aby sprawdzać tylko adresy zaczynające się od '1'.
"""

import re
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import argparse

BLOCKSTREAM_API = "https://blockstream.info/api"
INPUT_FILE = "attack_log.txt"
OUTPUT_FILE = "wyniki_saldo.txt"

# Domyślnie: sprawdzaj wszystkie adresy. Ustaw True aby filtrować tylko adresy zaczynające się od '1'.
ONLY_P2PKH = False

# Parametry równoległości / retry
MAX_WORKERS = 10
MAX_RETRIES = 3
INITIAL_DELAY = 1.0  # s, dla backoff
REQUEST_TIMEOUT = 10  # seconds

addr_regex = re.compile(r"addr=([A-Za-z0-9]+)")

def extract_addresses_from_log(path):
    """Wyciąga wszystkie wartości addr=... z pliku, zwraca unikalną listę."""
    addrs = []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            for m in addr_regex.finditer(line):
                addrs.append(m.group(1).strip())
    # deduplikacja, zachowując kolejność
    seen = set()
    unique = []
    for a in addrs:
        if a not in seen:
            seen.add(a)
            unique.append(a)
    return unique

def get_address_info(addr):
    """Pobiera info o adresie z Blockstream API. Zwraca dict lub None."""
    url = f"{BLOCKSTREAM_API}/address/{addr}"
    delay = INITIAL_DELAY
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(url, timeout=REQUEST_TIMEOUT)
            if resp.status_code == 200:
                return resp.json()
            elif resp.status_code == 429:
                # rate limit
                time.sleep(delay)
                delay = min(15.0, delay * 1.7)
            else:
                # inny błąd HTTP — spróbuj ponownie po krótkim backoff
                time.sleep(delay)
                delay = min(15.0, delay * 1.7)
        except requests.RequestException:
            time.sleep(delay)
            delay = min(15.0, delay * 1.7)
    return None

def compute_balance_from_chain_stats(chain_stats):
    """
    Blockstream zwraca chain_stats z polami typu funded_txo_sum i spent_txo_sum (wartości w satoshi).
    Balance = funded_txo_sum - spent_txo_sum
    Jeśli struktura inna, zwraca None.
    """
    if not chain_stats:
        return None
    funded = chain_stats.get("funded_txo_sum")
    spent = chain_stats.get("spent_txo_sum")
    if funded is None or spent is None:
        return None
    return int(funded) - int(spent)

def check_address(addr):
    """Właściwa funkcja robocza: zwraca tuple (addr, balance_satoshi, tx_count) lub None."""
    info = get_address_info(addr)
    if not info:
        return None
    # chain_stats może być w info["chain_stats"]
    chain_stats = info.get("chain_stats") or info.get("chain_stats", {})
    balance = compute_balance_from_chain_stats(chain_stats)
    tx_count = chain_stats.get("tx_count", 0) if chain_stats else 0
    return (addr, balance if balance is not None else 0, tx_count)

def main(args):
    global ONLY_P2PKH
    ONLY_P2PKH = args.only1

    print("[*] Wczytuję adresy z", INPUT_FILE)
    addrs = extract_addresses_from_log(INPUT_FILE)
    if ONLY_P2PKH:
        addrs = [a for a in addrs if a.startswith("1")]
        print(f"[*] Filtrowanie: pozostawiam tylko adresy zaczynające się od '1' -> {len(addrs)} adresów")
    else:
        print(f"[*] Znalazłem {len(addrs)} unikalnych adresów")

    if not addrs:
        print("[!] Brak adresów do przetworzenia.")
        return

    results = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as exe:
        futures = {exe.submit(check_address, a): a for a in addrs}
        for fut in tqdm(as_completed(futures), total=len(futures), desc="Sprawdzanie adresów"):
            try:
                res = fut.result()
                if res:
                    results.append(res)
            except Exception as e:
                # zabezpieczamy przed wyjątkiem jednego taska
                print(f"[!] Błąd podczas sprawdzania: {e}")

    # filtrujemy tylko z saldem > 0
    positive = [r for r in results if r[1] and int(r[1]) > 0]

    # zapis wyników
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("address,balance_satoshi,tx_count\n")
        for addr, bal, txc in positive:
            f.write(f"{addr},{bal},{txc}\n")

    print(f"[*] Zapisano {len(positive)} adresów z saldem > 0 do {OUTPUT_FILE}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Szybkie sprawdzenie sald adresów wyciągniętych z attack_log.txt")
    parser.add_argument("--only1", action="store_true", help="sprawdzaj tylko adresy zaczynające się od '1' (P2PKH)")
    parser.add_argument("--workers", type=int, default=MAX_WORKERS, help="liczba wątków równoległych")
    args = parser.parse_args()
    # nadpisanie max workers, jeśli podano
    MAX_WORKERS = args.workers
    main(args)
