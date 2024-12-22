from fastapi import HTTPException
from ..basic_functions import current_state, next_move, active_games
from ..prompts import system_prompt, repeat_concatenation_prompt
from loguru import logger
from openai import OpenAI
from utils.llm.models import InitLLMModel


async def start_llm(llm_data: InitLLMModel):
    llm_client = OpenAI(
        base_url=llm_data.base_url,
        api_key=llm_data.api_key,
    )

    session_id = llm_data.session_id

    llm_model = llm_data.model
    user_prompt = llm_data.prompt
    repeat_concatenation = llm_data.repeat_concatenation

    repeat = []
    if session_id not in active_games:
        raise HTTPException(
            status_code=404, detail="Session not found. Start a game first."
        )

    game_state = await current_state(session_id)

    while game_state["over"] is False:
        prompt = system_prompt(str(game_state["table"]), user_prompt)
        logger.debug(f"Base prompt: {prompt}")

        if repeat_concatenation:
            if len(repeat) > 2:
                addition_prompt = repeat_concatenation_prompt(
                    repeat_concatenation, repeat[-1]
                )
                prompt += addition_prompt
                logger.debug(
                    f"LLM has repeated its response for {len(repeat)} times. Concatenating the main prompt and this text: {addition_prompt}"
                )

        next_direction = await _send_prompt(
            llm_client,
            llm_model,
            prompt,
        )

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


async def _send_prompt(
    llm_client: OpenAI,
    model: str,
    prompt: str,
):
    chat_completion = llm_client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )

    response = chat_completion.choices[0].message.content

    logger.debug(f"Received response: {response}")

    return response
