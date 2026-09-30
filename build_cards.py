"""번역 TSV(번호<TAB>한글)를 mom_eng.txt 순서와 맞춰 cards.csv로 합친다. '-'는 번역 불가로 제외."""
import csv, glob, hashlib
from prep import load

def card_id(english):
    return hashlib.sha1(english.encode("utf-8")).hexdigest()[:10]

def main():
    sentences = load()
    tr = {}
    for path in sorted(glob.glob("tr_*.tsv")):
        for line in open(path, encoding="utf-8"):
            line = line.rstrip("\r\n")
            if not line:
                continue
            num, kor = line.split("\t", 1)
            tr[int(num)] = kor.strip()
    rows, skipped = [], []
    for num in sorted(tr):
        if tr[num] == "-":
            skipped.append((num, sentences[num - 1]))
            continue
        eng = sentences[num - 1]
        rows.append((card_id(eng), tr[num], eng))
    with open("cards.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "korean", "english"])
        w.writerows(rows)
    print(f"cards.csv: {len(rows)}장, 제외 {len(skipped)}건")
    for n, s in skipped:
        print(" 제외", n, s[:60])

if __name__ == "__main__":
    main()
