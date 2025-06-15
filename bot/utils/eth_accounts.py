from eth_account import Account

from configuration import ENCRYPTION_PASSWORD


class WalletManager:
    """
    Управління створенням та зберіганням гаманців з шифруванням приватних ключів.
    """

    @staticmethod
    def create_wallet() -> dict:
        acct = Account.create()
        keystore = Account.encrypt(acct.key, ENCRYPTION_PASSWORD)
        return {"address": acct.address, "keystore": keystore}

    @staticmethod
    def load_private_key(keystore: dict) -> str:
        priv = Account.decrypt(keystore, ENCRYPTION_PASSWORD)
        return priv.hex()
