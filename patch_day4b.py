import re
f = "沈阳行程_方案攻略.txt"
s = open(f, encoding="utf-8").read()

# note fix
note_old = ("※ Day4 说明：G8101 12:28 到沈阳站，约 13:30 起有半天空闲。下午以轻量逛吃为主，"
            "西塔/彩电塔与 Day5/Day6 可二选一不重复跑。详情见下方各方案 Day4。")
note_new = ("※ Day4 说明：G8101 12:28 到沈阳站，约 13:30 起有半天空闲。下午直接打卡重头戏"
            "「沈阳故宫」（14:00–16:00），晚上西塔晚餐 + 彩电塔夜市；故宫从 Day5 提前到 Day4，"
            "Day5/Day6 更从容。详情见下方各方案 Day4。")
print("note replaced:", note_old in s)
s = s.replace(note_old, note_new)

# 方案C/D Day5 flexible: 故宫 line (any paren) ... 中街午餐 (any paren)
pat = re.compile(
    "  09:00–11:00  沈阳故宫（游览约 2 小时[^\n]*\n"
    "  11:00–11:10  步行约 10 分钟到张氏帅府\n"
    "  11:15–12:30  张氏帅府（游览约 1.5 小时）\n"
    "  12:30–12:45  步行/打车约 10 分钟到沈阳博物馆（市府广场，离帅府很近）\n"
    "  12:45–13:45  沈阳博物馆（游览约 1 小时）\n"
    "  13:45–14:00  打车约 10 分钟到中街\n"
    "  14:00–15:30  中街午餐[^\n]*\n"
    "  15:30–17:30  中街逛街、休息", re.S)
new = ("  09:00–10:30  张氏帅府（游览约 1.5 小时，需提前约票）\n"
       "  10:45–11:45  沈阳博物馆（市府广场，离帅府很近，游览约 1 小时）\n"
       "  12:00–13:30  中街午餐\n"
       "  13:30–17:30  中街逛街、休息")
c = len(pat.findall(s))
s = pat.sub(new, s)
print("CD Day5 replaced:", c)

open(f, "w", encoding="utf-8").write(s)
print("TXT WRITTEN")
