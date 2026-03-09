"""
WORDLE — Ranking & Selection  (Information Theory, no entropy)
==============================================================

Core idea
---------
Instead of entropy we use FREQUENCY-BASED RANKING & SELECTION:

  1. Keep a POOL of candidate words consistent with all feedback.
  2. Compute letter frequency across the pool:
         freq(c)  =  |{ w ∈ pool : c ∈ w }|
  3. SCORE every candidate word:
         Score(w)  =  Σ  freq(c)       (unique letters in w)
  4. RANK words by Score descending.
  5. SELECT rank-1 word as the recommended next guess.

No logarithms, no entropy — pure frequency-based ranking.
"""

import tkinter as tk
import random
from collections import Counter


# ════════════════════════════════════════════════════════════════════
#  WORD LIST  (common 5-letter English words)
# ════════════════════════════════════════════════════════════════════
_RAW = (
    "about above abuse actor acute admit adopt adult after again agent agree "
    "ahead alarm album alert alike align alley allow alone along alter angel "
    "anger angle apple apply arena argue arise armor aroma arose array arrow "
    "aside asset avoid awake award aware awful beach beard beast began begin "
    "being below bench birth black blade blame bland blank blast blaze bleed "
    "blend bless blind block blood bloom blown blues blunt board bonus boost "
    "booth bound boxer brake brand brave bread break breed brick bride brief "
    "bring broad broke brown brush buddy build built bunch burst buyer cabin "
    "cable candy cargo carry catch cause chain chair chaos charm chart chase "
    "cheap check cheek chess chest chief child chord civic civil claim class "
    "clean clear clerk click cliff climb cling clock clone close cloth cloud "
    "coach coast color comic coral count court cover crack craft crane crash "
    "crazy cream creek crime crisp cross crowd crown cruel crush curve cycle "
    "daily dance death debut delay delta dense depot depth devil digit dirty "
    "dodge doubt dough draft drain drama drank dread dream dress dried drift "
    "drink drive drove drown eager early earth eight elite empty enter entry "
    "equal error event every exact extra fable faint fairy faith false fancy "
    "fatal fault feast fence fever field fifth fifty fight final first fixed "
    "flame flash fleet flesh float flood floor flour focus force forge forth "
    "forum found frame frank fraud fresh front froze fruit fully funds funny "
    "giant given glass globe gloom glory glove going grace grade grain grand "
    "grant grape grasp grass grave great greet grief grind groan gross group "
    "grown guard guess guide guild guilt guest habit harsh haven heart heavy "
    "hence honor horse hotel house human humor ideal image index inner input "
    "intro issue jewel joint joker judge juice juicy knife knock known label "
    "lance large laser later laugh layer learn lease least leave legal level "
    "light limit liver local lodge logic loose lover lower lucky lunar lunch "
    "magic major maker manor maple march marsh match mayor meant medal media "
    "merit metal meter might minor minus mixed model money month moral motor "
    "mount mouse mouth moved movie music naive nasty naval nerve never newer "
    "night noble noise north noted novel nurse ocean offer often olive opera "
    "orbit order other outer owned owner paint panel panic paper patch pause "
    "peace peach pearl penny phase phone photo piano piece pilot pitch pixel "
    "place plain plane plant plate plaza point poker porch pound power press "
    "price pride prime print prior prize probe prone proof prose proud prove "
    "pulse queen query quest quick quiet quota quote radar radio raise rally "
    "ranch range rapid ratio reach react ready realm rebel refer reign relax "
    "rider ridge rifle right rigid risky rival river robot rocky rough round "
    "route royal ruler rural rusty saint salad sales sandy sauce scale scare "
    "scene scope score sense serve setup seven shade shaft shake shall shame "
    "shape share shark sharp shelf shell shift shine shirt shock short shout "
    "sight since sixth sixty skill slate slave sleep slice slide slope small "
    "smart smell smile smoke snake solar solve south space spark speed spell "
    "spend spent spice spike spine spite split sport spray stack stage stain "
    "stake stale stall stamp stand stark start steal steel steep stern stick "
    "sting stock store storm story stove straw stray strip stuck study style "
    "sugar sunny super surge swamp swear sweep sweet swift sword table taken "
    "taste teach tense terms thorn three threw throw thumb tiger tight tired "
    "title toast today token topic total touch tough tower toxic trace track "
    "trade trail train trait trash treat trend trial tribe trick tried troop "
    "truck truly trust truth twist under union until upper upset urban usage "
    "usual valid value valve verse video viral visit vital vivid vocal voice "
    "voter waste watch water weary weave wedge weird wheat wheel where which "
    "while white whole whose witch woman women world worry worse worst worth "
    "would wound wrath wrist wrong yield young yours youth zebra irate stare "
    "audio ozone glint briny serum tangy perky burly stomp crimp trove bloke"
)

WORD_LIST = sorted({w for w in _RAW.split() if len(w) == 5 and w.isalpha()})


# ════════════════════════════════════════════════════════════════════
#  WORDLE FEEDBACK  (Green / Yellow / Gray)
# ════════════════════════════════════════════════════════════════════
def get_feedback(guess: str, target: str) -> str:
    """
    Returns 5-char string:
      G = letter at correct position
      Y = letter in word but wrong position
      X = letter absent from word
    Handles duplicate letters correctly.
    """
    fb   = ['X'] * 5
    pool = list(target)

    # Pass 1 — greens (exact matches)
    for i in range(5):
        if guess[i] == target[i]:
            fb[i] = 'G'
            pool[i] = None

    # Pass 2 — yellows (present but wrong position)
    for i in range(5):
        if fb[i] == 'X' and guess[i] in pool:
            fb[i] = 'Y'
            pool[pool.index(guess[i])] = None

    return ''.join(fb)


# ════════════════════════════════════════════════════════════════════
#  RANKING & SELECTION ALGORITHM  (no entropy)
# ════════════════════════════════════════════════════════════════════
class RankingSelector:
    """
    Ranking & Selection without entropy.

    Score(w)  =  Σ  freq(c)      for each UNIQUE letter c in w
    where freq(c) = |{ w' ∈ pool : c ∈ w' }|

    Words whose letters appear most often across the remaining
    pool get the highest score and are ranked first.
    """

    def __init__(self, word_list):
        self._full = list(word_list)
        self.pool  = list(word_list)

    def reset(self):
        self.pool = list(self._full)

    # ── filtering ────────────────────────────────────────────────
    def apply_feedback(self, guess: str, feedback: str):
        """Remove words inconsistent with the given feedback."""
        self.pool = [w for w in self.pool
                     if self._consistent(w, guess, feedback)]

    def _consistent(self, word: str, guess: str, feedback: str) -> bool:
        for i in range(5):
            g, f = guess[i], feedback[i]
            if f == 'G':
                if word[i] != g:
                    return False
            elif f == 'Y':
                if word[i] == g:                    # can't be at same position
                    return False
                needed = sum(1 for j in range(i + 1)
                             if guess[j] == g and feedback[j] in 'GY')
                if word.count(g) < needed:           # must appear at least 'needed' times
                    return False
            else:                                    # 'X'  — gray
                gy = sum(1 for j in range(5)
                         if guess[j] == g and feedback[j] in 'GY')
                if word.count(g) > gy:               # can't appear more than confirmed times
                    return False
        return True

    # ── scoring / ranking ────────────────────────────────────────
    def _letter_freq(self) -> Counter:
        freq = Counter()
        for w in self.pool:
            freq.update(set(w))      # count each letter once per word
        return freq

    def top_ranked(self, n: int = 5):
        """Return [(word, score), ...] sorted best-first."""
        freq   = self._letter_freq()
        scored = [(w, sum(freq[c] for c in set(w))) for w in self.pool]
        scored.sort(key=lambda x: -x[1])
        return scored[:n]

    def freq_bars(self, n: int = 8):
        return self._letter_freq().most_common(n)

    @property
    def remaining(self) -> int:
        return len(self.pool)


# ════════════════════════════════════════════════════════════════════
#  COLOURS & FONTS
# ════════════════════════════════════════════════════════════════════
C_BG     = "#1e1e2e"   # unified dark background
C_EMPTY  = "#313244"   # empty cell
C_BORDER = "#585b70"   # cell border
C_GREEN  = "#40a02b"
C_YELLOW = "#df8e1d"
C_GRAY   = "#6c6f85"

C_PBG    = "#181825"   # right panel (slightly darker)
C_PFG    = "#cdd6f4"   # panel fg
C_BLUE   = "#89b4fa"
C_PGREEN = "#a6e3a1"
C_PURP   = "#cba6f7"
C_YELL   = "#f9e2af"
C_RED    = "#f38ba8"
C_SEP    = "#45475a"

CELL     = 60

F_TITLE  = ("Helvetica Neue", 28, "bold")
F_SUB    = ("Helvetica Neue", 11)
F_CELL   = ("Helvetica Neue", 22, "bold")
F_BTN    = ("Helvetica Neue", 12, "bold")
F_MSG    = ("Helvetica Neue", 12)
F_MONO   = ("Courier New",    11)
F_MONO_B = ("Courier New",    12, "bold")
F_MONO_T = ("Courier New",    15, "bold")
F_BIG    = ("Courier New",    24, "bold")


# ════════════════════════════════════════════════════════════════════
#  APPLICATION
# ════════════════════════════════════════════════════════════════════
class WordleApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Wordle  ·  Ranking & Selection  (Information Theory)")
        self.configure(bg=C_BG)
        self.resizable(False, False)

        self.selector = RankingSelector(WORD_LIST)
        self._init_state()
        self._build_ui()
        self._refresh_panel()

    # ── state ────────────────────────────────────────────────────
    def _init_state(self):
        self.target = random.choice(WORD_LIST)
        self.row    = 0
        self.over   = False
        self.selector.reset()

    # ── build UI ─────────────────────────────────────────────────
    def _build_ui(self):
        outer = tk.Frame(self, bg=C_BG)
        outer.pack(padx=24, pady=24)

        # ─── LEFT  (game board) ───────────────────────────────────
        left = tk.Frame(outer, bg=C_BG)
        left.grid(row=0, column=0, padx=(0, 20), sticky="n")

        tk.Label(left, text="WORDLE", font=F_TITLE,
                 bg=C_BG, fg="#cdd6f4").pack()
        tk.Label(left, text="Information Theory  ·  Ranking & Selection",
                 font=F_SUB, bg=C_BG, fg="#89b4fa").pack(pady=(2, 18))

        # 6 × 5 board
        board = tk.Frame(left, bg=C_BG)
        board.pack()
        self.cells = []
        for r in range(6):
            row_cells = []
            for c in range(5):
                fr = tk.Frame(board, width=CELL, height=CELL,
                              bg=C_EMPTY,
                              highlightbackground=C_BORDER,
                              highlightthickness=2)
                fr.grid(row=r, column=c, padx=3, pady=3)
                fr.grid_propagate(False)
                lbl = tk.Label(fr, text="", font=F_CELL,
                               bg=C_EMPTY, fg="#cdd6f4")
                lbl.place(relx=.5, rely=.5, anchor="center")
                row_cells.append((fr, lbl))
            self.cells.append(row_cells)

        # input row
        inp = tk.Frame(left, bg=C_BG)
        inp.pack(pady=18)
        self.entry_var = tk.StringVar()
        self.entry_var.trace_add("write", self._sanitize)
        self.entry = tk.Entry(inp, textvariable=self.entry_var,
                              font=F_CELL, width=6, justify="center",
                              relief="solid", bd=2,
                              bg="#313244", fg="#cdd6f4",
                              insertbackground="#cdd6f4")
        self.entry.pack(side="left", padx=(0, 10))
        self.entry.bind("<Return>", lambda _: self._submit())

        self.btn = tk.Button(inp, text="GUESS", font=F_BTN,
                             bg=C_GREEN, fg="white", relief="flat",
                             padx=18, pady=7, cursor="hand2",
                             command=self._submit)
        self.btn.pack(side="left")

        self.msg_var = tk.StringVar(value="Type a 5-letter word and press GUESS")
        self.msg_lbl = tk.Label(left, textvariable=self.msg_var, font=F_MSG,
                 bg=C_BG, fg="#cdd6f4", wraplength=390)
        self.msg_lbl.pack()

        tk.Button(left, text="New Game", font=F_MSG,
                  bg="#45475a", fg="#cdd6f4", relief="flat",
                  padx=14, pady=5, cursor="hand2",
                  command=self._new_game).pack(pady=(14, 0))

        self.entry.focus_set()

        # ─── RIGHT  (algorithm panel) ────────────────────────────
        right = tk.Frame(outer, bg=C_PBG)
        right.grid(row=0, column=1, sticky="nsew")
        outer.columnconfigure(1, minsize=330)

        p = tk.Frame(right, bg=C_PBG)
        p.pack(padx=16, pady=16, fill="both", expand=True)

        # header
        tk.Label(p, text="ALGORITHM", font=F_MONO_T,
                 bg=C_PBG, fg=C_BLUE).pack(anchor="w")
        tk.Label(p, text="Ranking & Selection  (no entropy)",
                 font=F_MONO_B, bg=C_PBG, fg=C_PURP).pack(anchor="w", pady=(0, 10))

        # step-by-step explanation
        steps = (
            "Step 1  Build pool of candidate words\n"
            "Step 2  Filter pool by Green/Yellow/Gray\n"
            "Step 3  Count letter frequency in pool:\n"
            "          freq(c) = |{w in pool : c in w}|\n"
            "Step 4  Score & Rank each word:\n"
            "          Score(w) = SUM freq(c)\n"
            "                     c in unique(w)\n"
            "Step 5  SELECT rank-1 word as best guess"
        )
        tk.Label(p, text=steps, font=F_MONO, bg=C_PBG, fg=C_PGREEN,
                 justify="left").pack(anchor="w", pady=(0, 8))

        self._sep(p)

        # remaining count
        tk.Label(p, text="CANDIDATES REMAINING",
                 font=F_MONO_B, bg=C_PBG, fg=C_BLUE).pack(anchor="w", pady=(8, 2))
        self.lbl_count = tk.Label(p, text="—", font=F_BIG,
                                  bg=C_PBG, fg=C_RED)
        self.lbl_count.pack(anchor="w")

        self._sep(p)

        # ranked suggestions
        tk.Label(p, text="TOP 5 RANKED SUGGESTIONS",
                 font=F_MONO_B, bg=C_PBG, fg=C_BLUE).pack(anchor="w", pady=(8, 4))
        self.sug_lbls = []
        for _ in range(5):
            lbl = tk.Label(p, text="—", font=F_MONO,
                           bg=C_PBG, fg=C_PFG, anchor="w")
            lbl.pack(anchor="w", fill="x")
            self.sug_lbls.append(lbl)

        self._sep(p)

        # letter frequency bars
        tk.Label(p, text="LETTER FREQUENCIES IN POOL",
                 font=F_MONO_B, bg=C_PBG, fg=C_BLUE).pack(anchor="w", pady=(8, 4))
        self.freq_frame = tk.Frame(p, bg=C_PBG)
        self.freq_frame.pack(anchor="w", fill="x")

    # ── helpers ──────────────────────────────────────────────────
    def _sep(self, parent):
        tk.Frame(parent, bg=C_SEP, height=1).pack(fill="x", pady=4)

    def _sanitize(self, *_):
        raw   = self.entry_var.get()
        clean = ''.join(c for c in raw if c.isalpha())[:5].upper()
        if raw != clean:
            self.entry_var.set(clean)

    def _set_controls(self, on: bool):
        s = "normal" if on else "disabled"
        self.entry.config(state=s)
        self.btn.config(state=s)

    def _reset_board(self):
        for row in self.cells:
            for fr, lbl in row:
                fr.config(bg=C_EMPTY, highlightbackground=C_BORDER)
                lbl.config(text="", bg=C_EMPTY, fg="#cdd6f4")

    # ── game actions ─────────────────────────────────────────────
    def _submit(self):
        if self.over:
            return
        guess = self.entry_var.get().strip().lower()
        if len(guess) != 5:
            self.msg_var.set("Please type exactly 5 letters.")
            return
        if guess not in WORD_LIST:
            self.msg_var.set(f"'{guess.upper()}' is not in the word list.")
            return

        fb = get_feedback(guess, self.target)
        self._paint_row(self.row, guess, fb)
        self.selector.apply_feedback(guess, fb)
        self.row += 1
        self.entry_var.set("")
        self._refresh_panel()

        if fb == "GGGGG":
            self.msg_var.set(f"Correct!  The word was  {self.target.upper()}  :)")
            self.over = True
            self._set_controls(False)
        elif self.row >= 6:
            self.msg_var.set(f"Game over.  The word was  {self.target.upper()}")
            self.over = True
            self._set_controls(False)
        else:
            self.msg_var.set(f"Guess {self.row}/6 — keep going! "
                             f"(Hint: see rank #1 on the right)")

    def _paint_row(self, row: int, guess: str, fb: str):
        cmap = {'G': C_GREEN, 'Y': C_YELLOW, 'X': C_GRAY}
        for c, (letter, f) in enumerate(zip(guess.upper(), fb)):
            fr, lbl = self.cells[row][c]
            col = cmap[f]
            fr.config(bg=col, highlightbackground=col)
            lbl.config(text=letter, bg=col, fg="white")

    def _new_game(self):
        self._init_state()
        self._reset_board()
        self._set_controls(True)
        self.entry_var.set("")
        self.msg_var.set("New game!  Type a 5-letter word and press GUESS.")
        self._refresh_panel()
        self.entry.focus_set()

    # ── panel refresh ────────────────────────────────────────────
    def _refresh_panel(self):
        # remaining count
        n = self.selector.remaining
        self.lbl_count.config(text=str(n))

        # ranked suggestions
        ranked = self.selector.top_ranked(5)
        for i, lbl in enumerate(self.sug_lbls):
            if i < len(ranked):
                word, score = ranked[i]
                color = C_YELL if i == 0 else C_PFG
                lbl.config(
                    text=f"#{i+1}  {word.upper():6s}   score = {score}",
                    fg=color,
                )
            else:
                lbl.config(text="—", fg=C_PFG)

        # frequency bars
        for w in self.freq_frame.winfo_children():
            w.destroy()

        bars = self.selector.freq_bars(8)
        if bars:
            max_f = bars[0][1]
            for letter, cnt in bars:
                row = tk.Frame(self.freq_frame, bg=C_PBG)
                row.pack(anchor="w", fill="x", pady=1)

                tk.Label(row, text=f"{letter.upper()}", font=F_MONO_B,
                         bg=C_PBG, fg=C_PURP, width=2).pack(side="left")

                bar_len = max(1, round(cnt / max_f * 14))
                tk.Label(row, text="█" * bar_len, font=("Courier New", 9),
                         bg=C_PBG, fg=C_BLUE).pack(side="left")

                tk.Label(row, text=f"  {cnt:3d}", font=F_MONO,
                         bg=C_PBG, fg=C_PGREEN).pack(side="left")


# ════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = WordleApp()
    app.mainloop()
