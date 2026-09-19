# FIX: Refactored all game logic out of app.py into this module with Claude Code
# (agent mode) so it can be unit tested without running Streamlit.

DIFFICULTY_RANGES = {
    "Easy": (1, 20),
    "Normal": (1, 100),
    # FIX: Hard used to be 1-50 (easier than Normal). Widened so Hard is actually harder.
    "Hard": (1, 200),
}


def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty."""
    return DIFFICULTY_RANGES.get(difficulty, DIFFICULTY_RANGES["Normal"])


def parse_guess(raw: str, low=None, high=None):
    """
    Parse user input into an int guess.

    If low/high are given, guesses outside that inclusive range are rejected.

    Returns: (ok: bool, guess_int: int | None, error_message: str | None)
    """
    if raw is None or raw.strip() == "":
        return False, None, "Enter a guess."

    try:
        value = int(raw.strip())
    except ValueError:
        # FIX: decimals like "12.9" used to be silently truncated to 12; now rejected.
        return False, None, "That is not a whole number."

    if low is not None and high is not None and not (low <= value <= high):
        return False, None, f"Guess must be between {low} and {high}."

    return True, value, None


def check_guess(guess: int, secret: int):
    """
    Compare guess to secret and return (outcome, message).

    outcome examples: "Win", "Too High", "Too Low"
    """
    # FIX: Messages were swapped ("Too High" told you to go HIGHER). The old
    # TypeError/str fallback was removed too: it compared strings
    # lexicographically ("9" > "50"). Both ints are now compared numerically.
    if guess == secret:
        return "Win", "🎉 Correct!"
    if guess > secret:
        return "Too High", "📉 Go LOWER!"
    return "Too Low", "📈 Go HIGHER!"


def update_score(current_score: int, outcome: str, attempt_number: int):
    """
    Update score based on outcome and attempt number.

    attempt_number is 1-based: the first guess is attempt 1.
    """
    if outcome == "Win":
        # FIX: Was 100 - 10 * (attempt_number + 1), so a first-try win scored 80.
        points = 100 - 10 * (attempt_number - 1)
        return current_score + max(points, 10)

    # FIX: A wrong "Too High" guess used to *add* 5 points on even attempts.
    # Any wrong guess now costs 5 points.
    if outcome in ("Too High", "Too Low"):
        return current_score - 5

    return current_score
