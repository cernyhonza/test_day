#!/urs/bin/env python
"""
Před nazazením do produkce:
    - Víc testů
    - Lepší dokumentace
    - Všechny URL přesunout do konfigurace a oddělit server a zbytek cesty
    - Funkci 'send_new_block' rozdělit a zkrátit
    - Zrychlit 'find_nonce'
"""

import hashlib
from datetime import datetime

import requests

url_state = "https://teams-orange-coingame-testday.stage.k8s.heu.cz/api/coingame/state"
url_block = "https://teams-orange-coingame-testday.stage.k8s.heu.cz/api/coingame"
url_transaction = "https://teams-orange-coingame-testday.stage.k8s.heu.cz/api/coingame/txpool"


def create_transaction(fee):
    """
    Get some profit for miner
    """
    transaction = ["  - !Transaction"]
    transaction.append(f"    Fee: {fee}")
    return "\n".join(transaction)


def check_dificulty(new_hash, difficulty):
    """
    Check if hash begins with sufficient number of zeros

    returns: bool
    """
    return bool(int(new_hash.hexdigest(), 16) // (2**(384-difficulty)))


def find_nonce(last_hash, current_time, difficulty, transactions):
    """
    Get known parts of block and find good nonce

    returns: new block
    """
    last_hash_enc = last_hash.encode()
    block_start = f"\n--- !Block\nTimestamp: {current_time}\nDifficulty: {difficulty}\n"
    block_start_enc = block_start.encode()
    block_end = "\nMiner: cernyhonza\nTransactions:\n" + \
        "\n".join(transactions) + "\n"
    block_end_enc = block_end.encode()

    test_hash = hashlib.sha384()

    nonce = 0
    block = ""
    while check_dificulty(test_hash, difficulty):
        test_hash = hashlib.sha384()
        nonce += 1
        block = last_hash + block_start + f"Nonce: {nonce}" + block_end
        block_enc = block.encode()

        test_hash.update(block_enc)
        test_hash.update(block_enc)

    return block


def construct_response(last_hash, new_block):
    return "\n".join([last_hash, "--- !Block", new_block])


def send_new_block():
    blockchain_state = requests.get(url_state).json()

    difficulty = blockchain_state['Difficulty']
    mining_fee = blockchain_state['Fee']

    print(f"Server requested difficulty {difficulty}")

    blockchain_last = requests.get(url_block).content.decode()

    blockchain_last_lines = blockchain_last.splitlines()

    last_hash = "--- !Hash\n" + blockchain_last_lines[-1]

    current_time = datetime.now().isoformat()

    transactions_response = requests.get(url_transaction).content.decode()
    transactions_list = transactions_response.split("--- !Transaction")

    transactions = [create_transaction(mining_fee)]

    new_transactions = []
    for transaction in transactions_list[-5:]:
        trnasaction_lines = transaction.splitlines()
        prefix = " "*4
        tr_id = prefix + trnasaction_lines[4]
        tr_fee = prefix + trnasaction_lines[3]
        tr_data1 = prefix + trnasaction_lines[1]
        tr_data2 = prefix + trnasaction_lines[2]
        new_transactions.append(
            "\n".join(["  - !Transaction", tr_id, tr_fee, tr_data1, tr_data2]))

    transactions.extend(new_transactions)

    new_block = find_nonce(last_hash, current_time,
                       difficulty, transactions)

    r = requests.put(url_block, data=new_block)
    print(f"Server responded with status code {r.status_code}")
    print(f"Message: {r.text}")


if __name__ == '__main__':
    send_new_block()
