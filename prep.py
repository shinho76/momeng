import sys
def load(path="mom_eng.txt"):
    seen, out = set(), []
    for line in open(path, encoding="utf-8-sig"):
        s = line.strip()
        if s and s not in seen:
            seen.add(s); out.append(s)
    return out
if __name__ == "__main__":
    a, b = int(sys.argv[1]), int(sys.argv[2])
    for i, s in enumerate(load()[a:b], start=a+1):
        print(f"{i}\t{s}")
