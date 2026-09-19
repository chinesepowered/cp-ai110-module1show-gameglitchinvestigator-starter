# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the broken app: `python -m streamlit run app.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

- [x] **Game purpose:** A Streamlit number-guessing game. The player picks a difficulty (Easy 1–20, Normal 1–100, Hard 1–200) and tries to guess a secret number within a limited number of attempts. The game gives "Go HIGHER" / "Go LOWER" hints and keeps a score that rewards winning in fewer attempts.
- [x] **Bugs found:**
  1. The hint messages were backwards: a guess that was too high said "Go HIGHER!".
  2. On every even attempt, the secret was cast to a `str`, so guesses were compared alphabetically (`"9" > "50"`).
  3. `attempts` started at 1, so the player lost an attempt before guessing.
  4. "New Game" did not reset `status`, `score` or `history`, so after a win or loss the game stayed stuck. It also ignored the difficulty range.
  5. Hard (1–50) was easier than Normal (1–100), and the banner always said "between 1 and 100".
  6. Scoring: a wrong "Too High" guess *added* 5 points on even attempts, and a first-try win scored 80 instead of 100.
  7. Decimals like `12.9` were silently truncated, and out-of-range guesses were accepted.
  8. The logic in `logic_utils.py` was all `NotImplementedError` stubs, so every test failed.
- [x] **Fixes applied:**
  - Moved all game logic from `app.py` into `logic_utils.py`, so `app.py` is only UI.
  - `check_guess` compares ints numerically and returns the correct message. The string fallback was removed.
  - Added a `start_new_game()` helper that resets all session state. It runs on first load, on "New Game", and when the difficulty changes.
  - Attempts start at 0, and invalid input no longer uses up an attempt.
  - Hard is now 1–200 with 7 attempts, and the banner shows the real range.
  - Any wrong guess costs 5 points. A win is worth `100 - 10 * (attempt - 1)`, with a minimum of 10.
  - `parse_guess` rejects decimals and guesses outside the difficulty range.
  - Fixed the starter tests (they compared a tuple to a string) and added regression and edge-case tests.

## 📸 Demo Walkthrough

A sample game on **Normal** difficulty (range 1–100, 8 attempts). The Debug Info panel showed the secret as 68:

1. The game loads with "Guess a number between 1 and 100. Attempts left: 8". Score is 0.
2. User enters a guess of **67**. The game shows "📈 Go HIGHER!", the score drops to -5, and attempts left drops to 7.
3. User enters a guess of **69**. The game shows "📉 Go LOWER!", the score drops to -10, and attempts left drops to 6.
4. User enters **abc**. The game shows "That is not a whole number." No attempt is used and the score is unchanged.
5. User enters **68**. Balloons appear, and the game shows "You won! The secret was 68. Final score: 70" (80 points for a 3rd-attempt win, minus 10 from the two wrong guesses).
6. Clicking Submit again shows "You already won. Start a new game to play again."
7. User clicks **New Game 🔁**. Attempts reset to 8 left, the score resets to 0, and a new secret is picked.
8. User switches the difficulty to **Hard**. The banner updates to "Guess a number between 1 and 200. Attempts left: 7", and a new secret is picked inside that range.

**Screenshot** *(optional)*: not included.

## 🧪 Test Results

```
$ pytest -v
============================= test session starts =============================
platform win32 -- Python 3.13.15, pytest-9.1.1, pluggy-1.6.0 -- C:\code\cp-ai110-module1show-gameglitchinvestigator-starter\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\code\cp-ai110-module1show-gameglitchinvestigator-starter
plugins: anyio-4.15.1
collecting ... collected 17 items

tests/test_game_logic.py::test_winning_guess PASSED                      [  5%]
tests/test_game_logic.py::test_guess_too_high PASSED                     [ 11%]
tests/test_game_logic.py::test_guess_too_low PASSED                      [ 17%]
tests/test_game_logic.py::test_too_high_message_says_go_lower PASSED     [ 23%]
tests/test_game_logic.py::test_too_low_message_says_go_higher PASSED     [ 29%]
tests/test_game_logic.py::test_single_digit_guess_compared_numerically PASSED [ 35%]
tests/test_game_logic.py::test_three_digit_guess_compared_numerically PASSED [ 41%]
tests/test_game_logic.py::test_wrong_guess_never_adds_points PASSED      [ 47%]
tests/test_game_logic.py::test_first_try_win_scores_100 PASSED           [ 52%]
tests/test_game_logic.py::test_win_score_has_floor_of_10 PASSED          [ 58%]
tests/test_game_logic.py::test_hard_range_is_wider_than_normal PASSED    [ 64%]
tests/test_game_logic.py::test_parse_valid_number_with_whitespace PASSED [ 70%]
tests/test_game_logic.py::test_parse_empty_input PASSED                  [ 76%]
tests/test_game_logic.py::test_parse_non_number PASSED                   [ 82%]
tests/test_game_logic.py::test_parse_decimal_rejected PASSED             [ 88%]
tests/test_game_logic.py::test_parse_out_of_range_rejected PASSED        [ 94%]
tests/test_game_logic.py::test_parse_boundaries_accepted PASSED          [100%]

============================= 17 passed in 0.12s ==============================
```

## 🚀 Stretch Features

- [x] Challenge 1 (Advanced Edge-Case Testing): tests for decimals, non-numeric input, empty input, whitespace, out-of-range guesses and range boundaries (see `tests/test_game_logic.py`).
