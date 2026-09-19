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

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
- Did AI help you design or understand any tests? How?

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.
