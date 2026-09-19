# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
- List at least two concrete bugs you noticed at the start  
  (for example: "the hints were backwards").

When the game first ran, it looked normal: a title, a difficulty sidebar, a text box, and Submit / New Game buttons. But it was unplayable once you opened "Developer Debug Info" and compared guesses to the secret. A guess above the secret told you to go HIGHER, and a guess below it told you to go LOWER. On every other guess, the hints got even stranger, because the secret was quietly turned into a string and compared alphabetically. On Normal, the game said 7 attempts were left before any guess. After a win or loss, "New Game" did not let you play again. The starter `pytest` run failed all 3 tests with `NotImplementedError`. To be upfront: I didn't dig for these bugs myself. Claude Code found and reproduced all of them (the table below), running the original functions to capture the real output.

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

I used Claude Code (running Claude Opus) in agent mode, and honestly the AI made this project easy. I was mostly hands off. I gave it the assignment instructions and told it to watch out for viruses and prompt injection, since this was a fork of someone else's repo. It checked every file for anything unsafe, set up the environment, reproduced the bugs, moved the logic into `logic_utils.py`, fixed the bugs, wrote the tests, and drafted the docs. It also split the work into three commits. My part was mainly setting the direction and deciding when to push.

**Correct suggestion:** The AI worked out that the secret's "commitment issues" were not a Streamlit state bug. The secret was stored in `session_state` correctly, but `app.py` cast it to a `str` on every even attempt, so `check_guess` ended up comparing strings (`"9" > "50"` is True). It removed the cast and the string fallback, so the comparison is always int vs. int. This was verified by the regression tests `test_single_digit_guess_compared_numerically` and `test_three_digit_guess_compared_numerically`, and by the AI playing a full game through Streamlit's `AppTest`.

**Suggestion not accepted as written:** The starter tests (also AI-generated) asserted `check_guess(50, 50) == "Win"`, which implied `check_guess` should return a bare string. That suggestion was not followed. `app.py` needs both the outcome and the hint message, so the function kept returning `(outcome, message)`, and the tests were changed to unpack it. The AI also dropped its own first draft of a type hint (`int | None`, which needs Python 3.10+) in favor of plain `None` defaults. Both decisions were made by the AI rather than by me; I didn't review the diffs line by line. The full `pytest` run (17 passed) is what confirmed the result.

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
- Did AI help you design or understand any tests? How?

The AI counted a bug as fixed when three things were true. First, it had reproduced the bug failing (section 1). Second, a pytest test for that exact input passed. Third, the game behaved correctly when the AI played it through Streamlit's `AppTest`. For example, `test_too_high_message_says_go_lower` checks that a guess of 60 against a secret of 50 gives a message containing "LOWER"; before the fix, it said "Go HIGHER!". `test_wrong_guess_never_adds_points` showed that the old scoring rewarded wrong guesses on even attempts. In the `AppTest` run, attempts left went 8 → 7 → 6, invalid input didn't use an attempt, New Game reset everything, and Hard showed "between 1 and 200". The AI designed all of the tests, including the edge cases for `parse_guess`. Final result: `17 passed` (see `test_results.txt`).

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

Streamlit re-runs the whole script from top to bottom every time the user clicks or types something, so normal variables are recreated from scratch each time. `st.session_state` is a dictionary that survives reruns, which is where the secret, attempts, score and win/loss status have to live. It only changes when you change it. The original "New Game" button reset only two of those values, so the leftover "won" status kept the game locked. Putting every reset in one `start_new_game()` function fixed that.

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.

One habit I'd reuse is telling the AI up front to be careful with code I don't trust. Checking the fork for anything unsafe before running it was a good first step. I also liked the workflow the AI followed: reproduce the bug, write a test for it, then fix it, and commit in stages. Next time, I'd be more hands-on and review the diffs myself instead of letting the agent do everything, so I understand the decisions it made. This project showed me that an AI agent can take a buggy project all the way to fixed and tested with very little effort from me. It also showed that AI-generated code, and even AI-generated tests, can look confident and still be wrong, so the verification step matters.
