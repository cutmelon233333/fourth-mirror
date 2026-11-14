# 第四面鏡：我是誰？（The Fourth Mirror）

一個給**沒有哲學或心理學基礎的大學生**的 12 幕互動式哲學情境，搭配一份可查核來源的 Markdown LLM Wiki。

透過一個「小組訊息已讀不回」的虛構情境，依序看見：

- **Self 1｜我眼中的自己**（自我認知）
- **Self 2｜別人實際如何看待我**（他人實際說出的評價）
- **Self 3｜我想像別人如何看待我**（後設知覺；Cooley 的鏡中自我已討論「想像的他人評判」）
- **Self 4｜三者不一致時，我是誰？**（開放的哲學提問，不是第四種人格類型）

最後以 SN 22.59《無我相經》與學術百科介紹佛教「無我」：它質疑的是固定、獨立、可永久主宰的自我，**不是**說人不存在。

> **重要聲明：**「四面鏡（Self 1～4）」是本作**自創的教學設計**，不是 Cooley、現代心理學或佛教經典的正式分類；故事與三條分支皆為虛構教學情境，不是實驗結果。

---

## 如何使用

| 內容 | 開啟方式 |
|---|---|
| 互動簡報（12 幕） | 直接用瀏覽器開啟 `slides/deck.html`（離線可用）。公開網址：**待部署後填入** |
| Wiki（網頁版） | 開啟 `slides/wiki.html`（可搜尋；簡報右下角也有連結） |
| Wiki（Markdown 原檔） | `wiki/index.md` → `wiki/concepts/`（9 個概念）、`wiki/sources/`（6 份來源）、`wiki/claims.json`（11 筆主張） |
| Workflow 流程圖 | `workflow/fourth-mirror-workflow.png`（3840×2160，適合匯入 FigJam）；向量原檔 `workflow/fourth-mirror-workflow.svg`；文字說明 `workflow/graph.md`。FigJam：[第四面鏡 Workflow Graph](https://www.figma.com/board/ZvPNYyw8YTz3DzNUI49Wp5/%E7%AC%AC%E5%9B%9B%E9%9D%A2%E9%8F%A1-Workflow-Graph?node-id=0-1&t=5SNsFuIbsMc3QBfJ-1) |
| 檢查結果 | `tests/*_results.json`（每項檢查的實際輸出）、`tests/screenshot_*.png`（瀏覽器實測截圖） |

簡報操作：按鈕或鍵盤（Tab／Enter）選擇、← → 換頁、右上「文獻證據」開啟來源抽屜（Esc 關閉）。

## 來源

| ID | 來源 | 讀到的範圍 |
|---|---|---|
| S01 | Cooley (1902) *Human Nature and the Social Order*, Ch. 5〈The Looking-Glass Self〉 | 公有領域原文節錄 |
| S02 | Donnelly, Moon & Critcher (2022), *Curr Opin Psychol*, PMID 34352724 | **僅摘要** |
| S03 | Harper et al. (2026), *J Pers*, PMID 42083441 | **僅結構化摘要** |
| S04 | SEP〈Personal Identity〉（Olson） | 全文網頁，保存短引文 |
| S05 | SN 22.59 Anatta-lakkhana Sutta（Ñāṇamoli 英譯，Access to Insight） | 全篇網頁，保存關鍵段落 |
| S06 | SEP〈Mind in Indian Buddhist Philosophy〉（Coseru） | 全文網頁，保存短引文 |

受著作權保護的期刊與百科**全文未存入本專案**，只保留書目、錨點與短引文。

## 檔案結構

```text
├── README.md                 # 本檔：簡介、查看方式、來源
├── AGENTS.md                 # 學術紅線與維護規則
├── raw/                      # 原始證據（只新增、不覆寫）
│   ├── source_registry.json, ingest_manifest.json, S01–S06_source_record.md
│   └── original/             # S01–S06 驗證節錄 + S01 複核紀錄
├── wiki/                     # Markdown LLM Wiki（index、claims.json、concepts/、sources/）
├── slides/                   # deck.html（簡報）、wiki.html（Wiki 網頁版）、scene_claim_map.json（逐幕對應 Claim）
├── workflow/                 # fourth-mirror-workflow.svg／.png、graph.md
├── tools/                    # quality_gate.py、sync_manifest_and_wiki_html.py
├── tests/                    # check_project.py + fixtures.json、browser_test.py、結果 JSON 與截圖
└── .github/workflows/pages.yml  # GitHub Pages 部署設定（只發佈 slides 兩頁）
```

## 執行檢查

需要 Python 3（Windows 可用 `py -3`）。瀏覽器測試需 `pip install playwright`，並會使用本機已安裝的 Chrome 或 Edge。

```bash
python tests/check_project.py
```

```bash
python tools/quality_gate.py --strict
```

```bash
python tests/browser_test.py
```

修改 `wiki/` 後，執行下列指令重建 `slides/wiki.html` 並更新 checksum：

```bash
python tools/sync_manifest_and_wiki_html.py
```

## 自行部署到 GitHub Pages

1. 在 GitHub 建立一個**公開** repository。
2. 在本機加入遠端並推送（請把網址換成你的 repo）：
   ```bash
   git remote add origin https://github.com/<帳號>/<repo>.git
   ```
   ```bash
   git push -u origin master
   ```
3. 到 repo → **Settings → Pages → Source** 選 **GitHub Actions**。若 Actions 還沒執行，可在 **Actions** 分頁手動執行「Deploy slides to GitHub Pages」。
4. 部署完成後網址為 `https://<帳號>.github.io/<repo>/`（首頁就是簡報，Wiki 在 `/wiki.html`）。請用無痕視窗確認能開啟，再把網址填回本 README。

注意：repo 公開後，`raw/`、`wiki/` 等 Markdown 也會公開；其中只有短引文與公有領域節錄。
