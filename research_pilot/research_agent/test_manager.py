import asyncio
from dotenv import load_dotenv

load_dotenv()

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from .research_manager import research_manager


async def main():

    session_service = InMemorySessionService()

    runner = Runner(
        agent=research_manager,
        app_name="research_pilot_test",
        session_service=session_service,
    )

    session = await session_service.create_session(
        app_name="research_pilot_test",
        user_id="test_user",
    )

    message = types.Content(
        role="user",
        parts=[
            types.Part(
                text="What are the latest developments in electric vehicles in India in 2026?"
            )
        ],
    )

    async for event in runner.run_async(
        user_id="test_user",
        session_id=session.id,
        new_message=message,
    ):
        if event.is_final_response() and event.content:
            print("\nMANAGER OUTPUT:\n")

            for part in event.content.parts:
                if part.text:
                    print(part.text)


if __name__ == "__main__":
    asyncio.run(main())