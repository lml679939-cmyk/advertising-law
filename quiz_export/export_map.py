"""
export_map.py
解析 final/index.html 中的概念地圖結構，
將各子概念對應題目清單附加到 NotebookLM 確認用 TXT。
"""
import re
import sys
from pathlib import Path
from html.parser import HTMLParser

HTML_FILE = Path(__file__).parent.parent / "final" / "index.html"
OUT_TXT   = Path(__file__).parent.parent / "final-exam" / "期末題庫完整內容_NotebookLM確認用.txt"


class TagStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
    def handle_data(self, d):
        self.parts.append(d)
    def handle_starttag(self, tag, attrs):
        if tag == "br":
            self.parts.append("\n")
    def get_text(self):
        return "".join(self.parts).strip()

def strip_html(s):
    p = TagStripper(); p.feed(s); return p.get_text()

def unescape_js(s):
    return (s.replace('\\"', '"')
             .replace("\\'", "'")
             .replace("\\n", "\n")
             .replace("\\\\", "\\"))

_STR_PAT = re.compile(r'"((?:[^"\\]|\\.)*)"')

def get_field(block, field):
    m = re.compile(r'\b' + re.escape(field) + r'\s*:\s*"((?:[^"\\]|\\.)*)"').search(block)
    return unescape_js(m.group(1)) if m else None

def get_int_field(block, field):
    m = re.compile(r'\b' + re.escape(field) + r'\s*:\s*(\d+)').search(block)
    return int(m.group(1)) if m else None

def get_options(block):
    m = re.search(r'options\s*:\s*\[(.*?)\]', block, re.DOTALL)
    return [unescape_js(s) for s in _STR_PAT.findall(m.group(1))] if m else []

def get_blanks_answers(block):
    m = re.search(r'answers\s*:\s*\[(.*?)\]', block, re.DOTALL)
    return [unescape_js(s) for s in _STR_PAT.findall(m.group(1))] if m else []

def has_hidden(block):
    return bool(re.search(r'\bhidden\s*:\s*true', block))

_OBJ_START = re.compile(r'\{\s*\n?\s*q\s*:')

def split_objects(arr_src):
    objects = []; i = 0
    while True:
        m = _OBJ_START.search(arr_src, i)
        if not m: break
        start = m.start(); depth = 0; j = start
        in_str = False; escape = False
        while j < len(arr_src):
            c = arr_src[j]
            if escape: escape = False
            elif c == '\\' and in_str: escape = True
            elif c == '"': in_str = not in_str
            elif not in_str:
                if c == '{': depth += 1
                elif c == '}':
                    depth -= 1
                    if depth == 0:
                        objects.append(arr_src[start:j+1]); i = j+1; break
            j += 1
        else: break
    return objects

def extract_array_src(src, var_name, end_marker):
    start = src.find(f"const {var_name} = [")
    if start == -1: raise ValueError(f"找不到 {var_name}")
    end = src.find(end_marker, start)
    return src[start:end]


def parse_tf(src):
    arr = extract_array_src(src, "questions", "\nconst mcQuestions")
    results = []
    for i, block in enumerate(split_objects(arr), 1):
        q = get_field(block, "q"); ans = get_field(block, "ans")
        exp = get_field(block, "exp"); pg = get_field(block, "page")
        if q and ans and exp:
            results.append({"no": i, "q": q, "ans": ans,
                            "exp": strip_html(exp), "page": pg or "",
                            "hidden": has_hidden(block)})
    return results

def parse_mc(src):
    arr = extract_array_src(src, "mcQuestions", "\nconst fillQuestions")
    results = []
    for i, block in enumerate(split_objects(arr), 1):
        q = get_field(block, "q"); opts = get_options(block)
        ans_idx = get_int_field(block, "ans"); exp = get_field(block, "exp")
        pg = get_field(block, "page")
        if q and opts and ans_idx is not None and exp:
            results.append({"no": i, "q": q, "options": opts, "ans_idx": ans_idx,
                            "ans_text": opts[ans_idx] if ans_idx < len(opts) else "?",
                            "exp": strip_html(exp), "page": pg or "",
                            "hidden": has_hidden(block)})
    return results

def parse_fill(src):
    arr = extract_array_src(src, "fillQuestions", "\n];\n\nlet ")
    results = []
    for i, block in enumerate(split_objects(arr), 1):
        q = get_field(block, "q"); answers = get_blanks_answers(block)
        exp = get_field(block, "exp"); pg = get_field(block, "page")
        if q and exp:
            results.append({"no": i, "q": q, "answers": answers,
                            "exp": strip_html(exp), "page": pg or ""})
    return results

def _find_balanced(src, start, open_ch, close_ch):
    """從 src[start] 處的 open_ch 開始，找到對應 close_ch 的位置（含字串感知）。"""
    depth = 0; j = start; in_str = False; quote = None; escape = False
    while j < len(src):
        c = src[j]
        if escape:
            escape = False
        elif in_str:
            if c == '\\':
                escape = True
            elif c == quote:
                in_str = False; quote = None
        else:
            if c == '"' or c == "'":
                in_str = True; quote = c
            elif c == open_ch:
                depth += 1
            elif c == close_ch:
                depth -= 1
                if depth == 0:
                    return j
        j += 1
    return -1


def _get_field_any_quote(block, field):
    """支援單引號或雙引號的字串欄位取值（劇情模式用單引號）。"""
    for quote in ('"', "'"):
        pat = re.compile(
            r'\b' + re.escape(field) + r'\s*:\s*' + quote +
            r'((?:[^' + quote + r'\\]|\\.)*)' + quote
        )
        m = pat.search(block)
        if m:
            return unescape_js(m.group(1))
    return None


def _get_options_any_quote(block):
    m = re.search(r'options\s*:\s*\[(.*?)\]', block, re.DOTALL)
    if not m:
        return []
    inner = m.group(1)
    # 抓單／雙引號字串
    items = re.findall(r"'((?:[^'\\]|\\.)*)'|\"((?:[^\"\\]|\\.)*)\"", inner)
    return [unescape_js(a or b) for a, b in items]


def parse_story_days(src):
    """擷取 storyDay1~N 的 questions（含每題 q/ans/options/exp/page/client），供 NotebookLM 驗證法條正確性。"""
    days = []
    for m in re.finditer(r"const (storyDay\d+) = (\{)", src):
        var = m.group(1)
        brace_pos = m.start(2)
        end_pos = _find_balanced(src, brace_pos, '{', '}')
        if end_pos < 0:
            continue
        block = src[brace_pos:end_pos + 1]
        title    = re.search(r"dayTitle:\s*'([^']+)'", block)
        subtitle = re.search(r"daySubtitle:\s*'([^']+)'", block)
        # 取 questions 陣列範圍
        qarr_m = re.search(r"questions:\s*\[", block)
        if not qarr_m:
            continue
        qbracket_pos = qarr_m.end() - 1  # 指向 '['
        qend_pos = _find_balanced(block, qbracket_pos, '[', ']')
        if qend_pos < 0:
            continue
        arr_src = block[qbracket_pos:qend_pos + 1]

        # 找到每題物件（以 setup: 為起點，因為 q: 在物件內較晚出現會被 split_objects 誤判）
        # 改用 setup: 為錨點抓物件
        objs = []
        for sm in re.finditer(r"\{\s*\n?\s*setup\s*:", arr_src):
            ostart = sm.start()
            oend = _find_balanced(arr_src, ostart, '{', '}')
            if oend > 0:
                objs.append(arr_src[ostart:oend + 1])
        qs = []
        for k, ob in enumerate(objs, 1):
            qtext = _get_field_any_quote(ob, "q")
            qtype = _get_field_any_quote(ob, "type")
            exp   = _get_field_any_quote(ob, "exp")
            pg    = _get_field_any_quote(ob, "page")
            client = _get_field_any_quote(ob, "client")
            if not qtext or not exp:
                continue
            entry = {"no": k, "q": qtext, "type": qtype or "tf",
                     "exp": strip_html(exp), "page": pg or "",
                     "client": client or ""}
            if qtype == "mc":
                entry["options"] = _get_options_any_quote(ob)
                entry["ans_idx"] = get_int_field(ob, "ans")
            else:
                entry["ans"] = _get_field_any_quote(ob, "ans")
            qs.append(entry)
        days.append({"var": var,
                     "title": title.group(1) if title else var,
                     "subtitle": subtitle.group(1) if subtitle else "",
                     "questions": qs})
    return days


def build_story_section(days):
    LABELS = ["A", "B", "C", "D"]
    lines = []
    lines.append("\n\n" + "═"*72)
    lines.append("【劇情模式題目】— Day 1~N 法條情境題（VN 視覺小說）")
    lines.append("═"*72)
    lines.append("（說明：劇情模式為情境式法律問答，每題附情境角色與對話；以下僅列法條題幹/答案/詳解，供 NotebookLM 驗證法條正確性）\n")
    for d in days:
        lines.append(f"\n▌ {d['title']}")
        lines.append(f"   ({d['subtitle']})")
        lines.append("─"*72)
        for q in d["questions"]:
            cli = f"  ｜客戶：{q['client']}" if q['client'] else ""
            lines.append(f"\n  [Day-{d['var'][-1]} {q['no']:>2}] {q['type'].upper()}{cli}")
            lines.append(f"  題目：{q['q']}")
            if q['type'] == 'mc':
                for j, opt in enumerate(q.get('options', [])):
                    mark = " ◀ 正確答案" if j == q.get('ans_idx') else ""
                    lines.append(f"    ({LABELS[j]}) {opt}{mark}")
                if q.get('ans_idx') is not None and q.get('options'):
                    lines.append(f"  答案：({LABELS[q['ans_idx']]}) {q['options'][q['ans_idx']]}")
            else:
                ans = "○（正確）" if q.get('ans') == "O" else "✕（錯誤）"
                lines.append(f"  答案：{ans}")
            lines.append(f"  詳解：{q['exp']}")
    lines.append("\n" + "═"*72)
    lines.append("（劇情模式段落由 export_map.py 自動生成）")
    return "\n".join(lines)


def parse_concepts(src):
    m = re.search(r"const concepts = \[(.*?)\];\s*\n\s*/\* 概念地圖", src, re.DOTALL)
    if not m: return []
    cblock = m.group(1)
    cats = []
    main_positions = [(mm.start(), mm.group(1))
                      for mm in re.finditer(r"mainTopic:\s*'([^']+)'", cblock)]
    for mi, (mpos, mtopic) in enumerate(main_positions):
        end = main_positions[mi+1][0] if mi+1 < len(main_positions) else len(cblock)
        seg = cblock[mpos:end]
        subs = []
        for sub_m in re.finditer(
                r"id:\s*'([^']+)',\s*name:\s*'([^']+)',\s*matchPages:\s*\[([^\]]+)\]", seg):
            pages = re.findall(r"'([^']+)'", sub_m.group(3))
            subs.append({"id": sub_m.group(1), "name": sub_m.group(2), "matchPages": pages})
        cats.append({"mainTopic": mtopic, "subTopics": subs})
    return cats

def build_map_section(cats, tf_qs, mc_qs, fill_qs):
    LABELS = ["A", "B", "C", "D"]
    lines = []
    lines.append("\n\n" + "═"*72)
    lines.append("【概念地圖索引】— 各子概念對應題目清單")
    lines.append("═"*72)
    lines.append("（說明：概念地圖模式依 matchPages 動態篩題，以下顯示各子概念可抽到的題目）\n")

    for cat in cats:
        lines.append(f"\n▌ {cat['mainTopic']}")
        lines.append("─"*72)
        for sub in cat["subTopics"]:
            pages = sub["matchPages"]
            def matched(q, pages=pages):
                return any(p in q["page"] for p in pages)
            tf_m   = [q for q in tf_qs   if matched(q)]
            mc_m   = [q for q in mc_qs   if matched(q)]
            fill_m = [q for q in fill_qs if matched(q)]
            total  = len(tf_m) + len(mc_m) + len(fill_m)
            lines.append(f"\n  ◆ {sub['name']}")
            lines.append(f"    matchPages: {', '.join(pages)}")
            lines.append(f"    題庫命中：是非 {len(tf_m)} 題 / 選擇 {len(mc_m)} 題 / 填充 {len(fill_m)} 題（共 {total} 題）")
            if tf_m:
                lines.append("    【是非題】")
                for q in tf_m:
                    tag = "🔒" if q["hidden"] else ""
                    ans = "○" if q["ans"] == "O" else "✕"
                    text = q["q"][:65] + ("…" if len(q["q"]) > 65 else "")
                    lines.append(f"      [是非{q['no']:>3}]{tag} {ans}  {text}")
            if mc_m:
                lines.append("    【選擇題】")
                for q in mc_m:
                    tag = "🔒" if q["hidden"] else ""
                    text = q["q"][:55] + ("…" if len(q["q"]) > 55 else "")
                    lines.append(f"      [選擇{q['no']:>3}]{tag} ({LABELS[q['ans_idx']]}) {q['ans_text'][:25]}  ｜ {text}")
            if fill_m:
                lines.append("    【填充題】")
                for q in fill_m:
                    ans_str = " ／ ".join(q["answers"])
                    text = q["q"][:55] + ("…" if len(q["q"]) > 55 else "")
                    lines.append(f"      [填充{q['no']:>3}] 答：{ans_str}  ｜ {text}")

    lines.append("\n" + "═"*72)
    lines.append("（概念地圖段落由 export_map.py 自動生成）")
    return "\n".join(lines)


if __name__ == "__main__":
    print(f"讀取：{HTML_FILE}")
    src = HTML_FILE.read_text(encoding="utf-8")

    tf_qs   = parse_tf(src)
    mc_qs   = parse_mc(src)
    fill_qs = parse_fill(src)
    cats    = parse_concepts(src)
    days    = parse_story_days(src)

    print(f"題庫：是非 {len(tf_qs)} / 選擇 {len(mc_qs)} / 填充 {len(fill_qs)}")
    print(f"概念地圖：{len(cats)} 大類，{sum(len(c['subTopics']) for c in cats)} 子概念")
    print(f"劇情模式：{len(days)} 天，共 {sum(len(d['questions']) for d in days)} 題")

    # 讀入現有 TXT，截斷舊的概念地圖／劇情段落（若存在）
    existing = OUT_TXT.read_text(encoding="utf-8")
    for cut_marker in ("\n\n" + "═"*72 + "\n【概念地圖索引】",
                       "\n\n" + "═"*72 + "\n【劇情模式題目】"):
        cut = existing.find(cut_marker)
        if cut != -1:
            existing = existing[:cut]
            print(f"已移除舊段落：{cut_marker.strip()[-15:]}")

    map_section   = build_map_section(cats, tf_qs, mc_qs, fill_qs)
    story_section = build_story_section(days)
    OUT_TXT.write_text(existing + map_section + story_section, encoding="utf-8")
    print(f"已更新：{OUT_TXT}")
