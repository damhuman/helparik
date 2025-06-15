from typing import Tuple

from openai import AsyncOpenAI

from bot.utils.message_generator import generate_contacts
from configuration import OPENAI_API_KEY
from database.connector import DbConnector

client = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def understand_action(input_message: str, telegram_id: int) -> Tuple[str, str, str, str, str, bool]:
    content = await get_response_from_model(input_message, telegram_id)
    await DbConnector.add_message(telegram_id=telegram_id, content=content, role="assistant", mtype="ai-response")
    return parse_ai_response(content)


async def transcribe_audio(buffer: bytes, telegram_id: int) -> str:
    transcription = await client.audio.transcriptions.create(
        model="whisper-1",
        file=("voice.ogg", buffer, "audio/ogg"),
    )
    await DbConnector.add_message(
        telegram_id=telegram_id, content=transcription.text, role="user", mtype="transcribed-voice")
    return transcription.text


async def generate_prompt_message(telegram_id: int) -> str:
    contact_list = await generate_contacts(telegram_id=telegram_id)
    prompt = f"""
    You are a smart assistant in a Web3 wallet application.

    Your primary task is to interpret user intent based on a provided input message. From the user's natural language text, you should extract key actionable information and return your result in a strictly structured format.

    === Output Format ===
    Always return the result in this format:
    1. ACTION
    2. CONTACT_NAME;CONTACT_ADDRESS
    3. AMOUNT
    4. NETWORK

    === Interpretation Rules ===

    1. ACTION
    - Determine what the user wants to do. Match to one of the following options:
      - TRANSFER – if the user wants to send tokens or crypto assets to someone.
      - SEND_INVOICE – if the user wants to issue or request payment via invoice.
    - If you cannot confidently detect an action — return ERROR.

    2. CONTACT_NAME;CONTACT_ADDRESS
    - Identify the recipient from the message using the provided contact list.
    - Match based on names, nicknames, or contextual references.
    - Return in format: name;address (e.g. Alice;0x123...).
    - If the recipient cannot be found — return ERROR.

    3. AMOUNT
    - Extract the amount to be transferred or invoiced.
    - Return it in a numeric and symbolic format (e.g. 0.05 ETH, 100 USDC).
    - If the amount is missing or unclear — return ERROR.

    4. NETWORK
    - Determine the blockchain network.
    - Options: Ethereum, Intmax
    - If not mentioned — return Intmax as the default.

    === Guidance ===
    - Do not invent contact names or addresses. Only use those from the provided contact list.
    - Use best-effort inference if the user is informal or vague (e.g., “Send John some ETH”).
    - If any part is missing or cannot be confidently extracted — return ERROR for that part.
    - Always return all 4 lines of output, even if some are ERROR.

    === Example ===
    User message: "Send 0.5 ETH to Kate on Ethereum"
    Your response:
    1. TRANSFER
    2. Kate;0xabc123...
    3. 0.5 ETH
    4. Ethereum

    Contacts will be provided under {contact_list}.
    """
    return prompt


async def generate_valid_input(input_message: str, telegram_id: str) -> list[dict]:
    prompt = await generate_prompt_message(telegram_id)
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": input_message},
    ]
    return messages


async def get_response_from_model(input_message: str, telegram_id: str, model: str = "gpt-4.1-2025-04-14") -> str:
    messages = await generate_valid_input(input_message, telegram_id)
    stream = await client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True,
    )
    content = ''
    async for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            content += chunk.choices[0].delta.content or ""

    return content

def parse_ai_response(response: str) -> Tuple[str, str, str, str, str, bool]:
    action, contact, amount, network = response.split("\n")
    action = action.replace('1. ', '')
    contact = contact.replace('2. ', '')
    amount = amount.replace('3. ', '')
    network = network.replace('4. ', '')
    status = True
    if action == "ERROR":
        status = False
    if contact == "ERROR":
        username = "ERROR"
        address = "ERROR"
        status = False
    else:
        username, address = contact.split(";")
    if amount == "ERROR":
        status = False
    return action, username, address, amount, network, status