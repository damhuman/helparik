from database.connector import DbConnector
from configuration import ua_config

from bot.utils.eth_accounts import WalletManager
from bot.utils.eth_connector import ETHConnector
from bot.utils.intmax_connector import IntMaxConnector


async def generate_initial_message(telegram_id: int):
    db_con = DbConnector()
    user = await db_con.get_user(telegram_id=telegram_id)
    private_key = WalletManager.load_private_key(user.keystore)
    eth_con = ETHConnector(private_key_hex=private_key)
    balance = await eth_con.get_balance()
    return ua_config.get('main', 'start_info').format(
        balance=balance,
        wallet_address=user.wallet_address
    )


async def generate_contacts(telegram_id: int):
    db_con = DbConnector()
    contacts = await db_con.get_contacts(telegram_id=telegram_id)
    contacts_text = []
    for contact in contacts:
        contacts_text.append(ua_config.get('contact', 'single_contact').format(contact_name=contact.contact_name, contact_address=contact.wallet_address))
    if len(contacts_text) == 0:
        return ua_config.get('contact', 'no_contacts')
    return '\n------------------------------------------\n'.join(contacts_text)


async def generate_intmax_balance_message(telegram_id: int):
    db_con = DbConnector()
    user = await db_con.get_user(telegram_id=telegram_id)
    private_key = WalletManager.load_private_key(user.keystore)
    async with IntMaxConnector() as connector:
        data = await connector.login(f'0x{private_key}')
        balances = await connector.get_balances()
    balances = balances['balances']
    eth_balance = 0
    for balance in balances:
        if balance['token']['tokenIndex'] == 0:
            eth_balance = float(balance['amount']) / float(pow(10, balance['token']['decimals']))
    eth_con = ETHConnector(private_key_hex=private_key)
    balance = await eth_con.get_balance()
    return ua_config.get('main', 'start_info').format(
        balance=eth_balance,
        wallet_address=data['address']
    )
