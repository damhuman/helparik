from typing import Tuple

from openai import AsyncOpenAI

from bot.utils.message_generator import generate_contacts
from configuration import OPENAI_API_KEY
from database.connector import DbConnector

client = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def understand_action(input_message: str, telegram_id: int) -> str:
    content, role = await get_response_from_model(input_message, telegram_id)
    await DbConnector.add_message(telegram_id=telegram_id, content=content, role=role, mtype="ai-response")
    return content


async def transcribe_audio(buffer: bytes) -> str:
    transcription = await client.audio.transcriptions.create(
        model="whisper-1",
        file=("voice.ogg", buffer, "audio/ogg"),
    )
    return transcription.text


async def generate_prompt_message(telegram_id: int) -> str:
    contact_list = await generate_contacts(telegram_id=telegram_id)
    prompt = f"""
    You're helper in web3 wallet.
    By provided text you should understand what user want to do.
    If this is about sending transfer you should pick best matching from contacts list that i'll provide to you later.
    As result you always should answer in such format:
    1. What action to do(available actions will be provided later if nothing from matched action return ERROR)
    2. What contact user speaking about(if you cant find contact from text return ERROR)
    3. Amount of transfer(if you cant recognise amount return ERROR)
    Available actions:
    - TRANSFER(if user wants to transfer money)
    Contacts:
    {contact_list}
    """
    return prompt


async def generate_valid_input(input_message: str, telegram_id: str) -> list[dict]:
    prompt = await generate_prompt_message(telegram_id)
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": input_message},
    ]
    return messages

async def get_response_from_model(input_message: str, telegram_id: str, model: str = "gpt-4.1-2025-04-14") -> Tuple[str, str]:
    messages = await generate_valid_input(input_message, telegram_id)
    print(
        f"Sending messages to model: {model} with messages: {messages}"
    )
    stream = await client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True,
    )
    content = ''
    role = 'assistant'
    async for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            content += chunk.choices[0].delta.content or ""

    return content, role