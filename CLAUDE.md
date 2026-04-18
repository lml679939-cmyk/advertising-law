# 廣告法規期中考題庫 — Claude Code 交接文件

## 專案概覽
這是一個單頁 HTML 廣告法規練習題庫，部署於 GitHub Pages。

- **本地路徑**：`C:\Users\user\Downloads\廣告法規\advertising-law\index.html`
- **GitHub Pages**：https://lml679939-cmyk.github.io/advertising-law/
- **GitHub Repo**：https://github.com/lml679939-cmyk/advertising-law
- **本地預覽**：`python -m http.server 7788 --directory C:/Users/user/Downloads/廣告法規/advertising-law`（launch.json 已設定，可用 `quiz` 啟動）

---

## 題庫現況（2026-04-19）

| 模式 | 公開題 | 隱藏題 | 合計 |
|------|--------|--------|------|
| 是非題 | 54 | 41 | **95** |
| 選擇題 | 48 | 41 | **89** |
| 填充題 | 30 | 25 | **55** |
| **合計** | **132** | **107** | **239** |

---

## 五種模式（`currentMode`）

| ID | 按鈕 | 說明 |
|----|------|------|
| `learn` | 📖 學習模式 | 答題後立即顯示對錯與詳解 |
| `classic` | 📝 傳統模式 | 全部作答後點「對答案」 |
| `mc` | 📋 選擇題 | 選擇題四選一，答後立即顯示 |
| `fill` | ✏️ 填空題 | 填入關鍵數字/詞彙 |
| `story` | 🎭 劇情模式 | **密碼解鎖限定**，菜鳥律師小廣的廣告法求生記 |

切換模式時 `switchMode(mode)` 會：
1. 切換按鈕 active 狀態
2. story 模式：隱藏 `.sticky-bar`、`.exam-header`、`#quiz-container`，顯示 `#story-panel`
3. 非 story 模式：反向操作
4. 呼叫 `resetAll()` → 若為 story 則 `initStoryMode()`，否則走原本流程

---

## 密碼解鎖系統
- **URL**：`?key=@new1376omg`（加在網址後面）
- **原理**：`sessionStorage` 記憶解鎖狀態，解鎖後標題顯示 🔓
- **隱藏題標記**：題目物件加上 `hidden: true` 屬性
- **劇情模式按鈕**：未解鎖時按鈕隱藏（`display:none`），解鎖後才顯示
- **劇情模式**：`initStoryMode()` 一開始檢查 `isUnlocked`，未解鎖顯示鎖定提示
- **過濾邏輯**：
  ```javascript
  const activeQuestions     = questions.filter(q => isUnlocked || !q.hidden);
  const activeMCQuestions   = mcQuestions.filter(q => isUnlocked || !q.hidden);
  const activeFillQuestions = fillQuestions.filter(q => isUnlocked || !q.hidden);
  ```

---

## 程式架構重點

### 資料結構
- **是非題**：`const questions = [...]`，欄位：`q`、`ans`（"O"/"X"）、`exp`、`page`、`hidden`（選填）
- **選擇題**：`const mcQuestions = [...]`，欄位：`q`、`options`（陣列）、`ans`（0-3 整數）、`exp`、`page`、`hidden`（選填）
- **填充題**：`const fillQuestions = [...]`，欄位：`q`、`blanks`（接受答案陣列的陣列）、`answers`（顯示用）、`exp`、`page`、`hidden`（選填）

### 選擇題選項洗牌
每次建題時執行 `shuffleArray([0,1,2,3])`，結果存於：
- `mcOptionOrders[]`：每題的選項順序
- `mcMappedAns[]`：洗牌後正確答案的位置索引

### 複製為圖片功能
- 每張題目卡右下角有複製 icon（雙頁圖示）
- 點擊後呼叫 `captureCard(idx)`，使用 `html2canvas` 擷取題目卡
- 擷取結果透過 `navigator.clipboard.write()` 複製到剪貼簿，可直接 `Ctrl+V` 貼上
- 依賴：`html2canvas 1.4.1`（CDN）

### 重要函式守則
- `updateBar()`：story 模式開頭有 `if (currentMode === 'story') return;`
- `buildQuiz()`：story 模式開頭有 `if (currentMode === 'story') return;`
- `resetAll()`：story 模式執行 `initStoryMode(); return;`

---

## 劇情模式架構（多關卡 VN 視覺小說系統）

### 已完成關卡

| 關卡 | 常數 | 主題 | 題數 | 客戶角色 |
|------|------|------|------|---------|
| Day 1 | `storyDay1` | 藥事法・藥物廣告・釋字414/744 | 10 | 藥廠業務陳經理、電視台業務小陳 |
| Day 2 | `storyDay2` | 廣播電視法・有線廣電法・衛星廣電法 | 10 | 全台電視林法務 |

### 固定角色陣容
| 角色 | 功能 |
|------|------|
| 王鐵嘴主任 | 答對時誇獎（罕見），答錯時怒吼；「😡 主任發飆」指令 |
| 林酸酸資深律師 | 毒舌版解析；「🧊 酸酸講解」指令 |
| 阿肥實習生 | 共患難，答對超開心、答錯超緊張 |

### 題目資料結構
```javascript
{
  setup: '情境描述（含時間地點，white-space:pre-line 格式）',
  client: '說話的角色名稱',         // 用於查找 storyCharacters 頭像
  clientLine: '角色說的話',
  type: 'tf' | 'mc',
  q: '法律判斷題目文字',
  ans: 'O' | 'X',                 // tf 用
  options: ['A','B','C','D'],      // mc 用
  ans: 0,                          // mc 用（0-3）
  exp: '詳解 HTML',
  sour: '酸酸版講解文字',
  rage: '主任發飆文字',
  correctR: ['答對反應1','答對反應2','答對反應3'],
  wrongR:   ['答錯反應1','答錯反應2','答錯反應3'],
}
```

### 關卡常數結構
```javascript
const storyDayN = {
  dayTitle: 'Day N ── 標題',
  daySubtitle: '菜鳥律師小廣的廣告法求生記',
  dayIntro: '開場白（pre-line 格式）',
  questions: [ /* 10 題 */ ]
};
```

### 核心狀態與函式
```
storyState          → { qIdx, score, hearts(0-5), streak, answered, wrongList[] }
currentDay          → 當前遊玩的 storyDayN 物件（切換關卡時更新）
initStoryMode()     → 顯示關卡選擇畫面（含密碼鎖檢查）
startStoryDay(data) → 設定 currentDay、重置 storyState、建立 HTML
storyBuildScene(idx)→ 渲染 VN 舞台（呼叫 getCharacter + getSceneBackground）
storyTF / storyMC   → 作答（讀 currentDay.questions）
storyCmd(cmd)       → 'sour'|'rage'|'end' 指令
storyNext()         → 下一題
storyShowEnd(early) → 結算（顯示「重新挑戰」+「選擇關卡」按鈕）
```

### VN 視覺小說舞台（2026-04-19 新增）
```
┌─────────────────────────────┐
│  【場景說明浮板 - 頂部】       │  ← .story-vn-setup，半透明黑底
│                             │
│      [角色大圖 230×230]      │  ← .story-vn-sprite，浮立中央
│      .story-vn-sprite       │     視覺上壓住對話條
│                             │
├─── .story-vn-dbox（底部） ───┤  ← 深色半透明對話條
│ [小頭像] [角色名牌＋職稱]     │
│  對話文字...                 │
└─────────────────────────────┘
```

**背景系統 `getSceneBackground(setupText)`**：
- 解析 setup 文字中的時間關鍵字，自動對應場景漸層
  - 早上 9-11 點 → 藍天曙光
  - 中午 12 點 → 暖金陽光
  - 下午 2-3 點 → 午後藍天
  - 下午 4 點 → 橘紅夕陽
  - 下午 5 點 / 夜晚 → 深藍夜空

### 角色頭像系統
```javascript
// 定義在 storyCharacters 物件
{ color, emoji, title,
  avatar: 'https://api.dicebear.com/9.x/avataaars/svg?seed=XXX&backgroundColor=YYY' }

// 查找（自動剝除括號補述如「陳經理（驚慌失措）」）
function getCharacter(name) → storyCharacters 物件 | null
```
現有角色：王鐵嘴主任、林酸酸、阿肥、陳經理、電視台業務小陳、林法務
> 替換自製圖片：把 `avatar` 改為本地路徑（如 `'./images/boss.png'`）即可。

### 新增 Day（正確流程）
1. 在 `storyDay2` **之後**新增 `const storyDay3 = { ... }`
2. 在 `initStoryMode()` 的關卡選擇按鈕區加一顆按鈕：
   ```html
   <button class="story-day-select-btn" onclick="startStoryDay(storyDay3)">...</button>
   ```
3. 在 `storyShowEnd()` 的 `dayLabel` 判斷邏輯加入 Day 3 的名稱
4. 把新客戶角色加入 `storyCharacters`（如有新角色）

### 好感度邏輯
- 答對：streak++；連對 3 題 → hearts+1（幸運事件）；hearts < 3 時答對也 +1
- 答錯：streak=0；hearts-1
- 初始值：hearts=3（中立）

---

## 題目新增規則

### 是非題格式
```javascript
{ q: "題目文字", ans: "O", exp: "解析 HTML", page: "p.xx", hidden: true }
```

### 選擇題格式
```javascript
{ q: "題目文字",
  options: ["選項A","選項B","選項C","選項D"],
  ans: 0,  // 0=A, 1=B, 2=C, 3=D
  exp: "解析 HTML", page: "p.xx", hidden: true }
```

### 填充題格式
```javascript
{ q: "題目含___空格",
  blanks: [["正確答案","另一種寫法","..."]],
  answers: ["顯示用答案"],
  exp: "解析 HTML", page: "p.xx", hidden: true }
```

### 新增位置
- **是非題**：加在 `const questions = [...]` 陣列最後
- **選擇題**：加在 `const mcQuestions = [...]` 陣列最後
- **填充題**：加在 `const fillQuestions = [...]` 陣列最後

---

## 題庫匯出腳本（供 NotebookLM）

```
C:\Users\user\Downloads\廣告法規\advertising-law\quiz_export\
├── export_all.py                  ← 主腳本（支援全三種題型）
├── 題庫完整內容_NotebookLM確認用.txt  ← 輸出結果（直接上傳 NotebookLM）
└── quiz_data.json                 ← JSON 格式（程式調用）
```

執行方式：
```bash
python quiz_export/export_all.py
```

---

## 已修正的重要題目錯誤

| 題號/類型 | 錯誤內容 | 修正後 |
|-----------|---------|--------|
| 是非第23題（藥事法§4） | 詳解誤稱「醫療器材已從藥事法移除」 | 已修正：§4 仍包含醫療器材；答案維持✕ |
| 選擇題（藥事法§4定義） | 題目問「不再包含哪項」+ 解析說醫療器材已移除 | 已翻轉：題目改為「仍屬藥物範圍卻常被誤認排除」 |
| 是非第35題（施行細則§20） | 題目「五日前」但詳解說「十日前」矛盾 | 已確認：五日前正確，詳解已更新 |
| 是非第37題（有線廣電法§27鎖碼） | 詳解誤稱應為「備查」 | 已確認：正確用語為「核定」 |
| 是非第25題（藥事法§95傳播業者） | 詳解誤稱金額為「6萬～30萬」 | 已修正：傳播業者初次違反§66第3項為「20萬～500萬」 |
| 是非第9題（廣電法§27） | 頁碼標示 p.70 | 已修正為 p.65 |

---

## 重要法條筆記（已確認正確）

### 藥事法罰則（最易混淆）
| 對象 | 條文 | 情境 | 罰鍰 |
|------|------|------|------|
| 藥商 | §92 | 違反§66第1項（初次） | 20萬～500萬 |
| 傳播業者 | §95第1項 | 違反§66第3項（初次） | 20萬～500萬 |
| 傳播業者 | §95第1項 | 通知後仍繼續刊播（加重） | 60萬～2500萬 |
| 傳播業者 | §95第1項 | 違反§66第4項（未保存資料） | 6萬～30萬 |
| 任何人 | §91第2項 | 違反§69（非藥物宣稱醫療效能） | 60萬～2500萬 |

### 廣播電視法罰則
| 違規類型 | 初次 | 經警告不改正 |
|---------|------|------------|
| 一般違規 | §42 警告 | §43 罰鍰 |
| §21第2、3款情節重大（電視） | §44 40萬～200萬 + 停播3日～3個月 | — |
| §21第2、3款情節重大（廣播） | §44 9萬～120萬 + 停播3日～3個月 | — |

### 時間數字整理
| 規定 | 數字 |
|------|------|
| 電視節目廣告區隔辦法§16（贊助揭露，電視） | 20秒 |
| 廣播節目廣告區隔辦法§16（贊助揭露，廣播） | 45秒 |
| 廣播節目廣告區隔辦法§11（置入揭露，廣播） | 45秒 |
| 衛星廣播電視法§36（廣告時間上限） | 節目總時間六分之一 |
| 衛星廣播電視法§36（單則廣告標示門檻） | 超過3分鐘須標示「廣告」 |
| 廣播電視法§23（更正期限） | 7日內 |
| 廣播電視法施行細則§19（資料保存） | 20日 |
| 廣播電視法施行細則§20（節目時間表） | 播送5日前 |
| 藥事法§66第4項（資料保存） | 6個月 |
| 藥事法§66-1（廣告核准有效期間） | 1年；展延每次不超過1年 |
| 廣播電視法§19（本國自製節目下限） | 70% |
| 廣播電視法施行細則§22（節目中報台名） | 每半小時一次 |

### 置入 vs 贊助禁止清單（陷阱）
| 商品 | 禁止置入（§8） | 禁止贊助（§13） |
|------|--------------|----------------|
| 菸品 | ✅ | ✅ |
| 酒類 | ✅ | ❌（可以贊助！） |
| 跨國境婚姻媒合 | ✅ | ✅ |
| 須醫師處方藥物 | ✅ | ❌ |

### 其他重要陷阱
- **有線廣電法§24**：訂戶數上限 **三分之一**（非四分之一）
- **有線廣電法§25**：節目頻道上限 **四分之一**
- **有線廣電法§27**：鎖碼方式報請中央主管機關**核定**（非核准、非備查）
- **廣電法§27**：節目時間表事前檢送主管機關**核備**（非核定）
- **藥事法§4**：藥物 = 藥品 + 醫療器材（包含醫療器材！）
- **藥事法§67**：處方藥廣告只能刊登於學術性醫療刊物，不得向大眾刊播
- **藥事法施行細則§45**：中藥材廣告效能宣傳以《本草綱目》所載者為限
- **化粧品**衛生安全管理法（法定用字為「粧」非「妝」）
- **化粧品§20**：違反§10第1項（虛偽誇大）→ 4萬～20萬；違反第2項（宣稱醫療效能）→ 60萬～500萬
- **釋字414**（藥物廣告事前審查）→ **合憲**；**釋字744**（化粧品廣告事前審查）→ **違憲**
- **釋字364**：媒體近用權須兼顧傳播媒體「編輯自由」，不得無條件強制
- **衛廣法§4**：外國人直接持股應低於 50%
- **衛廣法§5**：政府、政黨及其捐助財團法人不得直接**或間接**投資衛星廣播電視事業
- **衛廣法§24**：購物頻道數應低於頻道總數 10%
- **消保法§19**：通訊交易、訪問交易 → 七日內無條件解除契約
- **NCC組織法§8**：委員離職後 3 年不得任職相關業者；追溯離職前 5 年職務
- **公平交易法§21**：素人薦證者連帶賠償上限為所受報酬 10 倍

---

## Git 提交習慣
```bash
git add index.html
git commit -m "說明"
git push origin main
```
推送後約 1 分鐘 GitHub Pages 生效。
**只 add `index.html`**（和 CLAUDE.md），不要 add `.claude/` 等目錄。
commit 訊息**不得含有密碼明文**。

---

## 工作流程慣例（本專案適用）

1. **題目修正流程**：
   - 使用者提供正確法條 → Claude 直接修改 `index.html` → push
   - 修正後同步更新 CLAUDE.md「已修正的重要題目錯誤」表格

2. **新增題目流程**：
   - 使用者提供題目內容 → Claude 依格式插入對應陣列末尾 → push

3. **NotebookLM 匯出流程**：
   - 執行 `python quiz_export/export_all.py`
   - 上傳 `quiz_export/題庫完整內容_NotebookLM確認用.txt` 給 NotebookLM

4. **題目驗證流程（NotebookLM 回報問題後）**：
   - 逐一確認題目文字、答案、詳解三者是否一致
   - 與 CLAUDE.md「重要法條筆記」交叉核對
   - 若與法條衝突，以使用者提供的法條原文為最終依據

---

## ⚡ 高效工作指令（節省 Token 的方式）

### 讀檔策略
`index.html` 超過 2000 行，全文讀取非常消耗 token。可以直接告訴 Claude：

> **「不用讀完整檔案，用 grep 找就好」**

Claude 會改用 `Grep` 搜尋函式名稱或關鍵字，再用 `Read + offset/limit` 只讀必要段落，效率提升 5～10 倍。

**常用 grep 目標：**
| 要找的東西 | 搜尋關鍵字 |
|-----------|-----------|
| 劇情題目資料 | `storyDay1` / `storyDay2` |
| 角色頭像設定 | `storyCharacters` |
| 場景背景函式 | `getSceneBackground` |
| VN 舞台 CSS | `story-vn-stage` |
| 是非題陣列結尾 | `hidden: true` 附近 |

### 開 Agent 平行作業

> **「幫我開一個 agent 寫劇情模式 Day3」**

Claude 會用 Agent 工具在背景啟動一個子代理，讓它：
- 讀 storyDay2 的格式作為範本
- 根據指定法規主題（如化粧品法）撰寫 10 題
- 完成後回報，主對話不被阻擋

這讓你可以同時進行：「agent 寫 Day3 題目」＋「主對話繼續改其他 bug」。

**觸發範例：**
```
「幫我開 agent 寫 Day3，主題是化粧品法，
 比照 storyDay2 格式，不用push，先給我看題目」
```

---

## 下一步可能的工作
- 繼續新增隱藏題目（使用者會提供題目內容）
- NotebookLM 驗證後修正錯誤答案或解析
- 劇情模式 **Day 3**（化粧品法）、**Day 4**（衛星廣電法・消保法）
- 替換角色頭像為自製動漫風圖片（修改 `storyCharacters[*].avatar`）
