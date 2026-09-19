# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
- List at least two concrete bugs you noticed at the start  
  (for example: "the hints were backwards").

The first time I ran it, the game looked normal: a title, a difficulty sidebar, a text box, and Submit / New Game buttons. But it was unplayable once I opened "Developer Debug Info" and compared my guesses to the secret. When I guessed above the secret, the hint told me to go HIGHER. When I guessed below it, the hint told me to go LOWER. On every other guess, the hints got even stranger, because the secret was quietly turned into a string and compared alphabetically. On Normal, the game said 7 attempts were left before I had guessed at all. After I won or lost, "New Game" did not actually let me play again. The starter `pytest` run failed all 3 tests with `NotImplementedError`, because the logic had never been moved into `logic_utils.py`.

**Bug Reproduction Log**

Document at least 3 bugs you found. Add rows as needed.

| Input | Expected Behavior | Actual Behavior | Console Output / Error |
|-------|-------------------|-----------------|------------------------|
| `check_guess(60, 50)` (guess above secret) | Outcome "Too High", message tells player to go **lower** | Outcome "Too High" but message says "📈 Go HIGHER!" | `('Too High', '📈 Go HIGHER!')` |
| Guess `9` on an even attempt, secret `50` | "Too Low" | "Too High": secret is cast to `str`, so `"9" > "50"` compares lexicographically | `check_guess(9, "50") -> ('Too High', '📈 Go HIGHER!')` |
| Guess `100` on an even attempt, secret `50` | "Too High" | "Too Low" (`"100" < "50"` as strings) | `check_guess(100, "50") -> ('Too Low', '📉 Go LOWER!')` |
| Fresh game on Normal (8 attempts) | "Attempts left: 8" | "Attempts left: 7": `attempts` starts at 1 | none (UI only) |
| Win or lose, then click "New Game" | Fresh playable game | Still shows "You already won" / "Game over": `status`, `score`, `history` never reset | none (UI only) |
| Select "Hard" difficulty | Harder (wider) range than Normal | Range is 1 to 50, easier than Normal's 1 to 100; banner still says "between 1 and 100" | `get_range_for_difficulty('Hard') -> (1, 50)` |
| Wrong "Too High" guess on attempt 2 | Score goes down (or stays the same) | Score goes **up** by 5 | `update_score(0, 'Too High', 2) -> 5` |
| Win on the first attempt | Full 100 points | 80 points (off by one: uses `attempt_number + 1`, and attempts already started at 1) | `update_score(0, 'Win', 1) -> 80` |
| `pytest` on the starter repo | Tests run against real logic | All 3 fail | `NotImplementedError: Refactor this function from app.py into logic_utils.py` |

---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
- Give one example of an AI suggestion you did not accept as written (including what the AI suggested, why you rejected or changed it, and how you verified your version). It does not have to be a suggestion that was wrong: over-engineered, out of scope, harder to read, or a poor fit for this codebase all count.

I used Claude Code (running Claude Opus) in agent mode. First I asked it to review the repo for anything unsafe, since this was a fork of someone else's code. Then I had it reproduce the bugs, move the logic into `logic_utils.py`, and write tests.

**Correct suggestion:** The AI pointed out that the "commitment issues" with the secret were not a Streamlit state bug. The secret was stored in `session_state` correctly, but `app.py` cast it to a `str` on every even attempt, and `check_guess` then fell back to comparing strings. It suggested deleting both the `str()` cast and the `TypeError` fallback, so `check_guess` only ever compares two ints. This was correct because string comparison is lexicographic. I checked by running the original function: `check_guess(9, "50")` returned "Too High". After the fix, the regression tests `test_single_digit_guess_compared_numerically` (9 vs 50 → "Too Low") and `test_three_digit_guess_compared_numerically` (100 vs 50 → "Too High") both pass. Watching the Debug Info panel in the app, the hints now stay consistent on every attempt.

**Suggestion I did not accept as written:** The starter tests (which were AI-generated too) asserted `check_guess(50, 50) == "Win"`. In effect, they suggested that `check_guess` should return a bare string. The quickest way to turn those tests green would have been to change `check_guess` to return only the outcome. I rejected that because `app.py` needs both values: it shows the message as the hint and uses the outcome for scoring. The docstring in `logic_utils.py` also says it returns `(outcome, message)`. So I kept the function's contract and changed the tests to unpack it (`outcome, _ = check_guess(...)`). I also added separate tests that check the message text, which is where the "Go HIGHER"/"Go LOWER" bug actually lived. A smaller change: the AI's first draft of `parse_guess` used the `int | None` type-hint syntax, which only works on Python 3.10+. I simplified it to plain `low=None, high=None` defaults so the code runs on older Python versions. I verified this with the full `pytest` run (17 passed) and by playing the game.

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
- Did AI help you design or understand any tests? How?

I counted a bug as fixed only when three things were true. First, I had a reproduction of it failing (the table in section 1). Second, a pytest test targeting that exact input passed after the change. Third, the live game behaved correctly. For example, `test_too_high_message_says_go_lower` checks that a guess of 60 against a secret of 50 produces a message containing "LOWER". Before the fix, the message said "Go HIGHER!". `test_wrong_guess_never_adds_points` loops over attempts 1–8 and showed that the old scoring rewarded a wrong guess on even attempts. For the UI-only bugs (the stuck "New Game" and the attempt counter), I drove the app with Streamlit's `AppTest`. I played a full game: a low guess, a high guess, invalid input, the win, "New Game", then a switch to Hard. I checked that attempts left went 8 → 7 → 6, that invalid input did not use an attempt, that the status reset to "playing" after New Game, and that Hard showed "between 1 and 200". AI helped me write the edge-case tests for `parse_guess` (decimals, whitespace, empty input, range boundaries). I read each one to make sure it tested the behavior I actually wanted, not just whatever the code happened to do. Final result: `17 passed` (see `test_results.txt`).

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

Streamlit re-runs your whole script from top to bottom every time the user does anything, like clicking a button or typing in a box. So a normal variable is recreated from scratch on every click. `st.session_state` is a dictionary that survives those reruns, so anything the game needs to remember (the secret, attempts, score, whether you already won) has to live there. The catch is that it only changes when you change it. The original "New Game" button reset only two of the five values, so the leftover `status = "won"` kept the game locked. Moving all the resets into one `start_new_game()` function made that mistake much harder to repeat.

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.

A habit I want to keep: reproduce the bug first (a function call and its actual output), then write a test for that exact case, then fix it. Having the "before" output made it obvious whether the AI's fix really worked. I also liked committing in stages (bug log → fixes → docs), because each diff was small enough to actually review. Next time, I would review the AI's changes one bug at a time instead of accepting a single large refactor, so each diff maps to one decision. This project showed me that AI-generated code, and even AI-generated tests, can look confident and still be wrong: the starter tests could never have passed against the real function. I now treat AI output as a draft that needs human-in-the-loop verification, not as a finished answer.
