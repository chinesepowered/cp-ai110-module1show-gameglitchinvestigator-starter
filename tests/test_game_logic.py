from logic_utils import check_guess, get_range_for_difficulty, parse_guess, update_score

# check_guess returns (outcome, message); the starter tests compared the whole
# tuple to a string, so they unpack the outcome now.


def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    outcome, _ = check_guess(50, 50)
    assert outcome == "Win"


def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    outcome, _ = check_guess(60, 50)
    assert outcome == "Too High"


def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    outcome, _ = check_guess(40, 50)
    assert outcome == "Too Low"


# --- Regression tests for the bugs fixed in this project ---

def test_too_high_message_says_go_lower():
    # Bug: guessing above the secret told the player to go HIGHER.
    _, message = check_guess(60, 50)
    assert "LOWER" in message


def test_too_low_message_says_go_higher():
    _, message = check_guess(40, 50)
    assert "HIGHER" in message


def test_single_digit_guess_compared_numerically():
    # Bug: secret became a str on even attempts, so "9" > "50" returned "Too High".
    outcome, _ = check_guess(9, 50)
    assert outcome == "Too Low"


def test_three_digit_guess_compared_numerically():
    outcome, _ = check_guess(100, 50)
    assert outcome == "Too High"


def test_wrong_guess_never_adds_points():
    # Bug: "Too High" on an even attempt added 5 points.
    for attempt in range(1, 9):
        assert update_score(0, "Too High", attempt) == -5
        assert update_score(0, "Too Low", attempt) == -5


def test_first_try_win_scores_100():
    # Bug: off-by-one made a first-attempt win worth 80.
    assert update_score(0, "Win", 1) == 100


def test_win_score_has_floor_of_10():
    assert update_score(0, "Win", 20) == 10


def test_hard_range_is_wider_than_normal():
    # Bug: Hard was 1-50, easier than Normal's 1-100.
    _, normal_high = get_range_for_difficulty("Normal")
    _, hard_high = get_range_for_difficulty("Hard")
    assert hard_high > normal_high


# --- Edge cases for parse_guess ---

def test_parse_valid_number_with_whitespace():
    assert parse_guess("  42 ") == (True, 42, None)


def test_parse_empty_input():
    ok, value, err = parse_guess("")
    assert not ok and value is None and err


def test_parse_non_number():
    ok, _, _ = parse_guess("abc")
    assert not ok


def test_parse_decimal_rejected():
    ok, _, _ = parse_guess("12.9")
    assert not ok


def test_parse_out_of_range_rejected():
    ok, _, err = parse_guess("150", 1, 100)
    assert not ok and "between 1 and 100" in err


def test_parse_boundaries_accepted():
    assert parse_guess("1", 1, 100)[0]
    assert parse_guess("100", 1, 100)[0]
