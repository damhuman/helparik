from openai import AsyncOpenAI

from bot.utils.message_generator import generate_contacts
from configuration import OPENAI_API_KEY

client = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def understand_action(input_message: str, telegram_id: int) -> str:
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
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": input_message}
    ]
    response = await client.get_completion(messages, temperature=0.7)
    print(response["choices"][0]["message"]["content"])


async def transcribe_audio(buffer: bytes) -> str:
    transcription = await client.audio.transcriptions.create(
        model="whisper-1",
        file=("voice.ogg", buffer, "audio/ogg"),
    )
    return transcription.text
