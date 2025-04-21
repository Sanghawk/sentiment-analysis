import asyncio

from manager import ResearchManager
from dotenv import load_dotenv
import os
from agents import set_default_openai_key

load_dotenv()

set_default_openai_key(os.getenv("OPENAI_API_KEY"))

async def main() -> None:
    query = input("What would you like to research? ")
    await ResearchManager().run(query)


if __name__ == "__main__":
    asyncio.run(main())