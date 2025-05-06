import json
from web3 import Web3

with open("tokens.json") as f:
    tokens = json.load(f)

# Convert semua address ke checksum format
checksum_tokens = {symbol: Web3.to_checksum_address(address) for symbol, address in tokens.items()}

with open("tokens.json", "w") as f:
    json.dump(checksum_tokens, f, indent=2)

print("✅ Semua address sudah diubah ke checksum!")
