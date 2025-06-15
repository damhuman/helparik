from eth_account import Account
from web3 import AsyncWeb3, AsyncHTTPProvider, Web3

from configuration import L1_RPC_URL


class ETHConnector:
    def __init__(self, private_key_hex: str):
        key = private_key_hex[2:] if private_key_hex.startswith('0x') else private_key_hex
        self.w3 = AsyncWeb3(AsyncHTTPProvider(L1_RPC_URL))
        self.account = Account.from_key(bytes.fromhex(key))
        self.address = self.account.address

    async def get_balance(self) -> float:
        bal = await self.w3.eth.get_balance(self.address)
        return Web3.from_wei(bal, 'ether')

    async def send_native(self, to_address: str, amount: float, gas_price_gwei: float = None) -> str:
        nonce = await self.w3.eth.get_transaction_count(self.address)
        chain_id = await self.w3.eth.chain_id
        tx = {
            'nonce': nonce,
            'to': Web3.to_checksum_address(to_address),
            'value': Web3.to_wei(amount, 'ether'),
            'chainId': chain_id,
            'gas': 21000,
            'gasPrice': Web3.to_wei(gas_price_gwei or 10, 'gwei')
        }
        signed = self.account.sign_transaction(tx)
        raw = signed.raw_transaction
        h = await self.w3.eth.send_raw_transaction(raw)
        return h.hex()
