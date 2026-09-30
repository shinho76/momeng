"""한글 -> 영어 플래시카드 (간격 반복). 카드 데이터는 cards.csv, 진행 상태는 progress.json."""
import argparse
import csv
import json
import os
import random
import threading
import tkinter as tk
from datetime import datetime, timedelta

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

CARDS_FILE = "cards.csv"
PROGRESS_FILE = "progress.json"
FONT = "맑은 고딕"

# 박스 1~5의 복습 간격
INTERVALS = {
    1: timedelta(minutes=10),
    2: timedelta(days=1),
    3: timedelta(days=3),
    4: timedelta(days=7),
    5: timedelta(days=21),
}
MASTER_STREAK = 3  # 박스 5에서 연속 정답 횟수


def load_cards(path=CARDS_FILE):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return {r["id"]: r for r in csv.DictReader(f)}


def load_progress(path=PROGRESS_FILE):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {"cards": {}, "daily": {"date": "", "new": 0}}


def save_progress(progress, path=PROGRESS_FILE):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)  # 저장 도중 종료되어도 기존 파일이 깨지지 않게


def apply_answer(state, known, now):
    """카드 상태(state)에 정답 여부를 반영해 새 상태를 돌려준다."""
    s = dict(state) if state else {"box": 1, "streak": 0, "tries": 0, "wrong": 0, "mastered": False}
    s["tries"] += 1
    if not known:
        s.update(box=1, streak=0)
        s["wrong"] += 1
    elif s["box"] >= 5:
        s["streak"] += 1
        if s["streak"] >= MASTER_STREAK:
            s["mastered"] = True
    else:
        s["box"] += 1
        s["streak"] = 0
    s["due"] = (now + INTERVALS[s["box"]]).isoformat()
    return s


def pick_next(cards, progress, now, daily_new, notebook=False, exclude=None):
    """다음에 낼 카드 id를 정한다. 없으면 None."""
    states = progress["cards"]
    if notebook:  # 오답 노트: 한 번이라도 틀렸고 아직 암기 완료가 아닌 카드
        pool = [i for i, s in states.items()
                if i in cards and s["wrong"] and not s["mastered"] and i != exclude]
        return random.choice(pool) if pool else None
    due = [(s["due"], i) for i, s in states.items()
           if i in cards and not s["mastered"] and datetime.fromisoformat(s["due"]) <= now]
    if due:
        return min(due)[1]
    today = now.date().isoformat()
    if progress["daily"]["date"] != today:
        progress["daily"] = {"date": today, "new": 0}
    if progress["daily"]["new"] < daily_new:
        new = [i for i in cards if i not in states]
        if new:
            return random.choice(new)
    return None


def stats(cards, progress, now):
    states = progress["cards"]
    due = sum(1 for i, s in states.items()
              if i in cards and not s["mastered"] and datetime.fromisoformat(s["due"]) <= now)
    mastered = sum(1 for s in states.values() if s["mastered"])
    new_left = len(cards) - len(states)
    return due, new_left, mastered


def speak(text):
    if pyttsx3 is None:
        return

    def run():
        try:
            engine = pyttsx3.init()
            for v in engine.getProperty("voices"):
                if "english" in (v.name or "").lower() or "en-" in str(v.id).lower():
                    engine.setProperty("voice", v.id)
                    break
            engine.say(text)
            engine.runAndWait()
        except Exception:
            pass

    threading.Thread(target=run, daemon=True).start()


class App:
    def __init__(self, root, daily_new):
        self.root = root
        self.daily_new = daily_new
        self.cards = load_cards()
        self.progress = load_progress()
        self.notebook = False
        self.current = None
        self.flipped = False

        root.title("영어 문장 플래시카드")
        root.geometry("900x520")
        self.stat = tk.Label(root, font=(FONT, 12), fg="#555")
        self.stat.pack(pady=10)
        self.card = tk.Label(root, font=(FONT, 28), wraplength=820, justify="center")
        self.card.pack(expand=True, fill="both", padx=30)
        self.hint = tk.Label(root, font=(FONT, 12), fg="#888")
        self.hint.pack(pady=12)

        root.bind("<space>", lambda e: self.on_space())
        root.bind("<Right>", lambda e: self.answer(True))
        root.bind("<Left>", lambda e: self.answer(False))
        root.bind("<k>", lambda e: self.answer(True))
        root.bind("<j>", lambda e: self.answer(False))
        root.bind("<n>", lambda e: self.toggle_notebook())
        root.bind("<Escape>", lambda e: root.destroy())
        self.next_card()

    def refresh_stats(self):
        due, new_left, mastered = stats(self.cards, self.progress, datetime.now())
        mode = "오답 노트" if self.notebook else "학습"
        self.stat.config(text=f"[{mode}]  복습 {due}  |  신규 {new_left}  |  암기 완료 {mastered}")

    def next_card(self):
        now = datetime.now()
        self.current = pick_next(self.cards, self.progress, now, self.daily_new,
                                 self.notebook, exclude=self.current)
        self.flipped = False
        self.refresh_stats()
        if self.current is None:
            msg = "오답 노트가 비어 있어요." if self.notebook else "지금 볼 카드가 없어요. 나중에 다시 오세요!"
            self.card.config(text=msg, fg="#333")
            self.hint.config(text="N: 학습/오답 노트 전환   Esc: 종료")
            return
        self.card.config(text=self.cards[self.current]["korean"], fg="#0441B6")
        self.hint.config(text="Space: 영어 문장 보기   N: 오답 노트   Esc: 종료")

    def on_space(self):
        if self.current is None:
            return
        eng = self.cards[self.current]["english"]
        if not self.flipped:
            self.flipped = True
            self.card.config(text=eng, fg="#111")
            self.hint.config(text="→ 알아요   ← 몰라요   Space: 다시 듣기")
        speak(eng)

    def answer(self, known):
        if self.current is None or not self.flipped:
            return  # 뒷면을 확인한 뒤에만 평가
        now = datetime.now()
        states = self.progress["cards"]
        if self.current not in states:
            if self.progress["daily"]["date"] != now.date().isoformat():
                self.progress["daily"] = {"date": now.date().isoformat(), "new": 0}
            self.progress["daily"]["new"] += 1
        states[self.current] = apply_answer(states.get(self.current), known, now)
        save_progress(self.progress)
        self.next_card()

    def toggle_notebook(self):
        self.notebook = not self.notebook
        self.current = None
        self.next_card()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--new", type=int, default=20, help="하루 신규 카드 수")
    args = ap.parse_args()
    root = tk.Tk()
    App(root, args.new)
    root.mainloop()
