# 廣告法規期中考題庫 — Claude Code 交接文件

## 專案概覽
這是一個單頁 HTML 廣告法規練習題庫，部署於 GitHub Pages。

- **本地路徑**：`C:\Users\user\Downloads\廣告法規\advertising-law\index.html`
- **GitHub Pages**：https://lml679939-cmyk.github.io/advertising-law/
- **GitHub Repo**：https://github.com/lml679939-cmyk/advertising-law
- **本地預覽**：`python -m http.server 7788 --directory C:/Users/user/Downloads/廣告法規/advertising-law`（launch.json 已設定，可用 `quiz` 啟動）

---

## 題庫現況（2026-04-17）

| 模式 | 公開題 | 隱藏題 | 合計 |
|------|--------|--------|------|
| 是非題 | 54 | 37 | **91** |
| 選擇題 | 48 | 38 | **86** |
| 填充題 | 30 | 0 | **30** |
| **合計** | **132** | **75** | **207** |

---

## 密碼解鎖系統
- **URL**：`?key=More1620`（加在網址後面）
- **原理**：`sessionStorage` 記憶解鎖狀態，解鎖後標題顯示 🔓
- **隱藏題標記**：題目物件加上 `hidden: true` 屬性
- **過濾邏輯**：
  ```javascript
  const activeQuestions    = questions.filter(q => isUnlocked || !q.hidden);
  const activeMCQuestions  = mcQuestions.filter(q => isUnlocked || !q.hidden);
  const activeFillQuestions = fillQuestions.filter(q => isUnlocked || !q.hidden);
  ```

---

## 程式架構重點

### 資料結構
- **是非題**：`const questions = [...]`，欄位：`q`、`ans`（"O"/"X"）、`exp`、`page`、`hidden`（選填）
- **選擇題**：`const mcQuestions = [...]`，欄位：`q`、`options`（陣列）、`ans`（0-3 整數）、`exp`、`page`、`hidden`（選填）
- **填充題**：`const fillQuestions = [...]`，欄位：`q`、`blanks`（接受答案陣列的陣列）、`answers`（顯示用）、`exp`、`page`

### 選擇題選項洗牌
每次建題時執行 `shuffleArray([0,1,2,3])`，結果存於：
- `mcOptionOrders[]`：每題的選項順序
- `mcMappedAns[]`：洗牌後正確答案的位置索引

### 筆記功能（已修復）
- `saveNote(idx)`：寫入 `localStorage`，key = `'note_' + q.q.slice(0, 60)`
- `buildQuiz/buildMCQuiz/buildFillQuiz`：建題後自動從 `localStorage` 載入筆記

### 已知修復的 Bug（本對話中完成）
1. 筆記無法儲存（`saveNote` 未接 `localStorage`）→ 已修
2. 傳統模式「對答案」後進度條不更新 → 已修（`checkAll` 加 `updateBar()`）
3. HTML `total-count` 初始值硬編碼為 45 → 已改為 0

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
  exp: "解析 HTML", page: "p.xx" }
```

### 新增位置
- **是非題**：加在 `const questions = [...]` 陣列最後一個 `}` 後，加逗號接新題
- **選擇題**：加在 `const mcQuestions = [...]` 陣列最後
- **填充題**：加在 `const fillQuestions = [...]` 陣列最後

---

## 題庫匯出腳本
`C:\Users\user\Downloads\廣告法規\extract_quiz.py`
執行後輸出至 `C:\Users\user\Downloads\廣告法規\quiz_export.txt`，供 NotebookLM 驗證。

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
- **化粧品**衛生安全管理法（法定用字為「粧」非「妝」）
- **化粧品§20**：違反§10第1項（虛偽誇大）→ 4萬～20萬；違反第2項（宣稱醫療效能）→ 60萬～500萬
- **釋字414**（藥物廣告事前審查）→ **合憲**；**釋字744**（化粧品廣告事前審查）→ **違憲**

---

## Git 提交習慣
```bash
git add index.html
git commit -m "說明"
git push origin main
```
推送後約 1 分鐘 GitHub Pages 生效。

---

## 下一步可能的工作
- 繼續新增隱藏題目（使用者會提供題目內容）
- NotebookLM 驗證後修正錯誤答案或解析
- 其他功能需求
