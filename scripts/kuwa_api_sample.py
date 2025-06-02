import os
import asyncio
from kuwa.client import KuwaClient

client = KuwaClient(
    base_url="http://127.0.0.1",
    model=".bot/Translate and Summarize",
    auth_token=os.environ.get("KUWA_API_KEY"),
)


async def main():
    user_prompt = input("> ")
    message = [{"role": "user", "content": user_prompt}]

    generator = client.chat_complete(messages=message, streaming=True)

    async for chunk in generator:
        print(chunk, end="")

    print()


if __name__ == "__main__":
    asyncio.run(main())
