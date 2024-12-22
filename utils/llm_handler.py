from fastapi import HTTPException
from .basic_functions import current_state, next_move, active_games
from .prompts import system_prompt
from loguru import logger
from openai import OpenAI

llm_client = OpenAI(
    base_url="http://10.0.0.7:11434/v1",
    api_key="ollama",
)


async def start_llm(session_id: str):
    repeat = []
    if session_id not in active_games:
        raise HTTPException(
            status_code=404, detail="Session not found. Start a game first."
        )

    game_state = await current_state(session_id)

    while game_state["over"] is False:
        prompt = system_prompt(str(game_state["table"]))
        next_direction = await _send_prompt(prompt)

        try:
            next_direction = int(next_direction)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid response received (not able to convert value to int).",
            )

        if len(repeat) > 0 and repeat[-1] != next_direction:
            repeat = []

        if len(repeat) <= 5:
            game_state = await next_move(session_id, int(next_direction))
            repeat.append(next_direction)
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid response received (repeated moves).",
            )


async def _send_prompt(prompt: str):
    chat_completion = llm_client.chat.completions.create(
        model="llama3.2:3b",
        messages=[{"role": "user", "content": prompt}],
    )

    response = chat_completion.choices[0].message.content

    logger.debug(f"Received response: {response}")

    return response
