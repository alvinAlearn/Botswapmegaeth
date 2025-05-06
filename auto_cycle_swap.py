
import json
import time
from web3 import Web3
from eth_account import Account

# --- Config ---
RPC_URL = "https://carrot.megaeth.com/rpc"
PRIVATE_KEY = "ISI_PRIVATE_KEY_KAMU"
WALLET_ADDRESS = "ISI_ADDRESS_KAMU"
ROUTER_ADDRESS = Web3.to_checksum_address("0x0a5168EeD4F5E7596dE9f9DfD54120E17Bbaf893")
AMOUNT_IN_ETH = 0.01
GAS_PRICE_GWEI = 2

# --- Setup ---
w3 = Web3(Web3.HTTPProvider(RPC_URL))
account = Account.from_key(PRIVATE_KEY)

with open("tokens.json") as f:
    tokens = json.load(f)

router_abi = [{
    "inputs": [
        {"internalType": "uint256","name": "amountOutMin","type": "uint256"},
        {"internalType": "address[]","name": "path","type": "address[]"},
        {"internalType": "address","name": "to","type": "address"},
        {"internalType": "uint256","name": "deadline","type": "uint256"}
    ],
    "name": "swapExactETHForTokens",
    "outputs": [{"internalType": "uint256[]","name": "amounts","type": "uint256[]"}],
    "stateMutability": "payable",
    "type": "function"
}, {
    "inputs": [
        {"internalType": "uint256","name": "amountIn","type": "uint256"},
        {"internalType": "uint256","name": "amountOutMin","type": "uint256"},
        {"internalType": "address[]","name": "path","type": "address[]"},
        {"internalType": "address","name": "to","type": "address"},
        {"internalType": "uint256","name": "deadline","type": "uint256"}
    ],
    "name": "swapExactTokensForETH",
    "outputs": [{"internalType": "uint256[]","name": "amounts","type": "uint256[]"}],
    "stateMutability": "nonpayable",
    "type": "function"
}]

router = w3.eth.contract(address=ROUTER_ADDRESS, abi=router_abi)

def swap_eth_to_token(token_out):
    print(f"🟢 Swapping ETH ➜ {token_out}")
    deadline = int(time.time()) + 300
    tx = router.functions.swapExactETHForTokens(
        0,
        [tokens['ETH'], token_out],
        WALLET_ADDRESS,
        deadline
    ).build_transaction({
        'from': WALLET_ADDRESS,
        'value': w3.to_wei(AMOUNT_IN_ETH, 'ether'),
        'gas': 300000,
        'gasPrice': w3.to_wei(GAS_PRICE_GWEI, 'gwei'),
        'nonce': w3.eth.get_transaction_count(WALLET_ADDRESS)
    })
    signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"✅ TX ETH➜Token: {w3.to_hex(tx_hash)}")

def swap_token_to_eth(token_in):
    print(f"🔴 Swapping {token_in} ➜ ETH")
    erc20_abi = [{
        "constant": True,
        "inputs": [{"name": "owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    }, {
        "constant": False,
        "inputs": [{"name": "spender", "type": "address"}, {"name": "amount", "type": "uint256"}],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function"
    }]
    token = w3.eth.contract(address=token_in, abi=erc20_abi)
    balance = token.functions.balanceOf(WALLET_ADDRESS).call()

    tx1 = token.functions.approve(ROUTER_ADDRESS, balance).build_transaction({
        'from': WALLET_ADDRESS,
        'gas': 100000,
        'gasPrice': w3.to_wei(GAS_PRICE_GWEI, 'gwei'),
        'nonce': w3.eth.get_transaction_count(WALLET_ADDRESS)
    })
    signed1 = w3.eth.account.sign_transaction(tx1, PRIVATE_KEY)
    w3.eth.send_raw_transaction(signed1.raw_transaction)
    time.sleep(2)

    deadline = int(time.time()) + 300
    tx2 = router.functions.swapExactTokensForETH(
        balance,
        0,
        [token_in, tokens['ETH']],
        WALLET_ADDRESS,
        deadline
    ).build_transaction({
        'from': WALLET_ADDRESS,
        'gas': 300000,
        'gasPrice': w3.to_wei(GAS_PRICE_GWEI, 'gwei'),
        'nonce': w3.eth.get_transaction_count(WALLET_ADDRESS)
    })
    signed2 = w3.eth.account.sign_transaction(tx2, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed2.raw_transaction)
    print(f"✅ TX Token➜ETH: {w3.to_hex(tx_hash)}")

print("🚀 STARTING AUTO SWAP LOOP...\n")
for symbol, address in tokens.items():
    if symbol == "ETH":
        continue
    swap_eth_to_token(address)
    time.sleep(10)
    swap_token_to_eth(address)
    time.sleep(10)

print("✅ LOOP SELESAI!")
