def system_prompt(game_table_state: str, user_prompt: str = None) -> str:
    if user_prompt:
        try:
            return user_prompt.format(game_table_state)
        except KeyError:
            return user_prompt

    return f"""
    You're playing 2048. The board is 4x4, and tiles with the same number merge when they touch.

    Game state format: [[x,x,x,x],[x,x,x,x],[x,x,x,x],[x,x,x,x]]
    - Arrays represent rows from top to bottom
    - 'x' represents empty tiles
    - Numbers represent tile values

    Examples:

    - If current game state is: [["x","x","x","x"],["x","x","x","x"],["x","x","x","2"],["4","x","x","x"]] - This means if you return 0 (up), the game state will be: [["4","x","x","2"],["x","x","x","x"],["x","x","x","x"],["x","x","x","2"]]
    - If you then return 3 (left), the game state will be: [["4","2","x","x"],["x","x","x","x"],["x","x","x","x"],["2","2","x","x"]]
    - If you then return 2 (down), the game state will be: [["2","x","x","x"],["x","x","x","x"],["4","x","x","x"],["2","4","x","x"]]
    - If you then return 1 (right), the game state will be: [["x","x","x","2"],["x","x","x","x"],["x","x","2","4"],["x","x","2","4"]]

    If you have a game table that looks like this: [["2","x","2","x"],["x","x","x","x"],["2","4","x","x"],["2","4","x","x"]], then:
    - a good move would be 2 (down) because you would merge two and four in the third and fourth rows. The new game state would then be: [["x","x","x","x"],["x","x","x","x"],["2","x","x","2"],["4","8","2","x"]]

    Your task: Choose the single best move direction.
    Reply with only:
    0 = up
    1 = right
    2 = down
    3 = left

    Key strategy:
    - Prioritize moves that create immediate merges
    - Avoid moves that don't change the board state
    - Consider moves that create space for future merges

    Current game state: {game_table_state}
    
    Reply with only a single digit (0, 1, 2, or 3). 
    
    Do not, under any circumstance, reply with anything else than a single digit. Do not use any special characters. If you do, you will be disqualified.

    """


def repeat_concatenation_prompt(user_prompt: str, latest_llm_direction) -> str:
    final_prompt = ""
    if user_prompt:
        try:
            final_prompt = user_prompt.format(direction=latest_llm_direction)
        except KeyError:
            return user_prompt

    return (
        final_prompt
        + "Do not, under any circumstance, reply with anything else than a single digit. Do not use any special characters. If you do, you will be disqualified."
    )
