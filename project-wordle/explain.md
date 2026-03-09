# Wordle — Ranking & Selection Algorithm Explanation

## 1. Context: Information Theory without Entropy

In classical Information Theory, a common strategy for Wordle uses **entropy** (average information gain) to pick the best guess. This solution deliberately avoids entropy and instead applies a simpler, equally principled idea from Information Theory: **Ranking & Selection based on letter frequency**.

---

## 2. The Word Pool

At the start, the **pool** contains every valid 5-letter word (~600+ words).  
After each guess, the pool is **filtered** — any word that could NOT have produced the observed feedback is removed.

> The pool is the set of all words still consistent with everything we know.

---

## 3. Feedback Mechanism (`get_feedback`)

Each guess produces a 5-character feedback string using three symbols:

| Symbol | Meaning |
|--------|---------|
| `G` (Green) | Correct letter, correct position |
| `Y` (Yellow) | Correct letter, wrong position |
| `X` (Gray) | Letter not in the word (at that count) |

**Two-pass algorithm** to handle duplicate letters correctly:
- **Pass 1** — mark all exact matches (`G`) and "consume" those positions.
- **Pass 2** — for remaining positions, mark `Y` if the letter still appears in the unconsumed part of the target, otherwise `X`.

**Example:** guess = `CRANE`, target = `BRAND`
```
C → X  (no C in brand)
R → Y  (R exists in brand, but not position 1)
A → G  (A is at position 2 in both)
N → Y  (N exists in brand, but not position 3)
E → X  (no E in brand)
→ feedback = "XYGYX"
```

---

## 4. Pool Filtering (`_consistent`)

After each guess+feedback pair, every word remaining in the pool is checked:

- **Green (`G`):** the candidate word must have exactly that letter at that position.
- **Yellow (`Y`):** the candidate word must NOT have that letter at that position, but MUST contain it somewhere else (at least as many times as confirmed by G/Y clues).
- **Gray (`X`):** the candidate word must NOT contain that letter more times than already confirmed by G/Y clues.

Only words that satisfy all three constraints survive in the pool.

---

## 5. Ranking & Selection (Core Algorithm)

### Step 1 — Letter Frequency

For each letter `c`, count how many words in the current pool contain it:

$$freq(c) = |\{ w \in \text{pool} : c \in w \}|$$

This tells us how "common" each letter is among the remaining candidates.

### Step 2 — Score Each Word

For each candidate word `w`, sum the frequencies of its **unique** letters:

$$Score(w) = \sum_{c \in \text{unique}(w)} freq(c)$$

Using unique letters avoids rewarding repeated letters (e.g. "spell" shouldn't double-count `l`).

### Step 3 — Rank

Sort all candidate words by `Score` in descending order.

### Step 4 — Select

**Select Rank #1** — the word with the highest score — as the recommended next guess.

**Why does this work?**  
A word with high-frequency letters will, on average, appear in more of the remaining candidates. Guessing it produces feedback (G/Y/X) that eliminates the maximum number of words from the pool, regardless of which color pattern comes back.

---

## 6. Worked Example

Suppose 4 words remain in the pool: `store`, `stare`, `score`, `snore`

**Letter frequencies:**

| letter | freq |
|--------|------|
| s | 4 | 
| t | 2 |
| o | 3 |
| r | 4 |
| e | 4 |
| a | 1 |
| c | 1 |
| n | 1 |

**Scores:**

| word | unique letters | score |
|------|---------------|-------|
| store | s,t,o,r,e | 4+2+3+4+4 = **17** |
| stare | s,t,a,r,e | 4+2+1+4+4 = **15** |
| score | s,c,o,r,e | 4+1+3+4+4 = **16** |
| snore | s,n,o,r,e | 4+1+3+4+4 = **16** |

→ **`store`** is ranked #1 and recommended as the best guess.

---

## 7. Why No Entropy?

| Entropy-based | Ranking & Selection (this project) |
|--------------|-----------------------------------|
| Measures expected bits of information gained | Measures total letter coverage across the pool |
| Requires log₂ calculations | Only requires counting and sorting |
| Optimal in information-theoretic sense | Near-optimal, simpler to explain and implement |
| Harder to explain intuitively | Directly interpretable: "pick the word whose letters appear most" |

Both approaches aim to eliminate as many candidates as possible per guess — Ranking & Selection achieves this without logarithms.

---

## 8. Algorithm Summary (5 lines)

```
1. Start with full pool of valid words
2. After each guess → filter pool by G/Y/X feedback
3. Count freq(c) = how many pool words contain letter c
4. Score(w) = sum of freq(c) for each unique letter in w
5. Recommend the highest-scored word (Rank #1)
```
