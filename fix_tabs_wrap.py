import os

old = ".tabs{overflow-x:auto;flex-wrap:nowrap;-webkit-overflow-scrolling:touch;padding:8px 0 8px}"
new = ".tabs{overflow-x:visible;flex-wrap:wrap;justify-content:center;gap:8px;padding:8px 0 8px;-webkit-overflow-scrolling:auto}"

files = [
    r"C:\Users\Administrator\WorkBuddy\2026-07-20-17-46-20\dalian-deploy\cloud.html",
    r"C:\Users\Administrator\WorkBuddy\2026-07-20-17-46-20\dalian-deploy\index.html",
]

for f in files:
    s = open(f, encoding="utf-8").read()
    c = s.count(old)
    if c != 1:
        raise SystemExit(f"[FAIL] {os.path.basename(f)} matched {c} times (expect 1): {old!r}")
    s = s.replace(old, new)
    open(f, "w", encoding="utf-8").write(s)
    print("ok:", os.path.basename(f))

print("TABS NOW WRAP ON MOBILE.")
