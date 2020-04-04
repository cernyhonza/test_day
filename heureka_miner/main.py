#!/urs/bin/env python

import requests
import hashlib
from datetime import datetime
import binascii
import random

url_state = "https://teams-orange-coingame-testday.stage.k8s.heu.cz/api/coingame/state"
url_block = "https://teams-orange-coingame-testday.stage.k8s.heu.cz/api/coingame"


def create_new_block(last_hash, current_time, difficulty, nonce, transactions): #TODO remove last_hash
    block = []
    block.append(f"Timestamp: {current_time}")
    block.append(f"Difficulty: {difficulty}")
    block.append(f"Nonce: {nonce}")
    block.append("Miner: cernyhonza")
    block.append("Transactions:")
    block.extend(transactions)
    return "\n".join(block)

def create_transaction(fee, trans_id=None):
    transaction = ["  - !Transaction"]
    if trans_id:
        transaction.append(f"    Id: {trans_id}")
    transaction.append(f"    Fee: {fee}")
    if trans_id:
        transaction.append("    Data: !!binary |")
        transaction.append("      e0Ftb3VudDogMTUuMSwgRnJvbTogTzNSNzg2TzNHMkRXLCBUbzogSFdXOThBUzIwVU41fQo=")
    return "\n".join(transaction)


def get_new_digest(last_hash, new_block):
    new_hash = hashlib.sha384()

    new_hash.update(last_hash.encode())
    new_hash.update(new_block.encode())
    new_hash.update(last_hash.encode())
    new_hash.update(new_block.encode())
    return new_hash.hexdigest()


def check_hash(last_hash, new_block, difficulty):

    new_digest = get_new_digest(last_hash, new_block)
    binary_digest = binascii.unhexlify(new_digest)
    goal_string = b'0'*difficulty
    candidate_string = binary_digest[1:1+difficulty]
    if goal_string == candidate_string:
        return True
    else:
        return False

def construct_response(last_hash,new_block):
    return "\n".join([last_hash,new_block])


def generate_new_block():
    blockchain_state = requests.get(url_state).json()

    difficulty = blockchain_state['Difficulty']
    mining_fee = blockchain_state['Fee']
    difficulty = 3

    print(f"Server requested difficulty {difficulty}")

    blockchain_last = requests.get(url_block).content.decode()

    blockchain_last_lines = blockchain_last.splitlines()

    last_hash = "\n".join(blockchain_last_lines[-2:])

    transaction_id = random.randint(10000000000000000000000000000000000000,
                                    99999999999999999999999999999999999999)

    current_time = datetime.now().isoformat()
    nonce = 0
    transactions = [create_transaction(mining_fee)]
    for i in range(4):
        transactions.append(create_transaction(mining_fee, transaction_id))
        transaction_id += 1

    new_block = create_new_block(last_hash, current_time, difficulty, nonce, transactions)

    while not check_hash(last_hash, new_block, difficulty):
        nonce += 1
        new_block = create_new_block(last_hash, current_time, difficulty, nonce, transactions)
        
    r = requests.put(url_block, data = construct_response(last_hash,new_block))
    print(f"Server responded with status code {r.status_code}")

if __name__ == '__main__':
    generate_new_block()
