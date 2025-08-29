import os
import asyncio
from kuwa.client import KuwaClient

# Usage (in PowerShell):
# cd "C:\kuwa\GenAI OS\src\library\client"
# $env:SETUPTOOLS_SCM_PRETEND_VERSION="v0.4.0"
# pip install .
# cd ..\..\..\scripts
# $env:KUWA_API_KEY="<your API key>"
# python kuwa_api_sample.py

client = KuwaClient(
    base_url="http://127.0.0.1",
    model=".bot/Llama 3.2 3B @NPU",
    auth_token=os.environ.get("KUWA_API_KEY"),
)


async def main():
    user_prompt = input("> ")
    message = [{"role": "user", "content": user_prompt}]

    generator = client.chat_complete(messages=message, streaming=True)

    async for chunk in generator:
        print(chunk, end="", flush=True)

    print()


if __name__ == "__main__":
    asyncio.run(main())
