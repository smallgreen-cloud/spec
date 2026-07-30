# Pipeline Profile v0.1（判定規則）

> 六件套 #1b。判定「一個 repo 是否為以 GitHub Actions 當批次運算層、以 Cloudflare 免費資源或 GitHub 原生設施當儲存／閘道／展示層的免費 pipeline 服務」。
> 「CF 閘道＋GH Actions 批次運算」pattern 幾乎無人標準化，是本 spec 的獨有貢獻空間。代表：Upptime（GH-only 軸）、會議摘要系統（多服務編排旗艦）、blog-post-workflow（聚合 pattern 最簡代表）。

## 與 Small App Profile 的分界

| | Small App | Pipeline |
|---|---|---|
| 運算 | Cloudflare Workers（請求驅動） | GitHub Actions（排程／事件批次） |
| 儲存 | D1 / KV / R2 | repo 本身（git 時序庫）、Issues、CF 儲存皆可 |
| 展示 | Workers / Pages | GitHub Pages 或 CF Pages |
| 典型 | 名片 MCP、Sink | Upptime、osmosfeed 復活版 |

兩檔可組合：雙平台整合專案（如 Decap CMS 組合包）同時受兩檔判定，各自出報告。

## 條款（Requirements）

| ID | 條款（可判定句） | 判定方式 | 來源故障 |
|---|---|---|---|
| PIP-1 | `.github/workflows/` 存在至少一個以 `schedule` 或 `workflow_dispatch` 觸發的 workflow | YAML 解析觸發器 | 無排程＝非批次 pipeline，錯掛 profile |
| PIP-2 | repo 為 public（GitHub Actions 分鐘數免費之前提） | gh api visibility 欄位 | private repo 2,000 分鐘/月上限＝免費承諾破產 |
| PIP-3 | workflow 排程最短間隔 ≥ 5 分鐘，且宣告單次預估分鐘數（profile.yaml `pipeline.estimated_minutes_per_run`） | cron 表達式解析＋欄位存在性 | GH Actions 排程下限即 5 分鐘；無預估值＝額度不可審計 |
| PIP-4 | secrets 全數走 GitHub Actions secrets，repo 內零真實 secret，manifest 列於 profile.yaml | secret 掃描零命中＋manifest 存在性 | 同 SAP-3 |
| PIP-5 | 若使用 Cloudflare 側資源，該側宣告受 Small App Profile SAP-1／SAP-2 判定 | 條件式：wrangler 存在則跑 SAP-1/2 | 免費承諾必須兩側同時成立 |
| PIP-6 | acceptance.yaml 必含「重跑冪等」測試：同一 workflow 連跑兩次，第二次零重複副作用 | acceptance suite 斷言（產出 diff 為空或宣告為 append-only 並驗證去重） | 資料修復被重生沖掉類事故（pipeline 通病） |
| PIP-7 | outbound 網路目標全數被 profile.yaml `external_services` 宣告涵蓋（Actions 端以靜態掃描為主） | 行為分析器靜態層；動態層 v0.2（Actions 沙盒攔截未完成） | 同 SAP-5 |
| PIP-8 | 具 OSI-approved license | gh api | 同 SAP-6 |
| PIP-9 | 具備完整移除路徑：uninstall＝刪除 fork repo（含 Actions 排程隨之停止）＋CF 側（若有）資源歸零 | teardown 驗證：repo 刪除確認＋SAP-8 diff | 殭屍 cron 永久跑＝浪費運算（低碳主軸反面） |

## 判定輸出格式

同 [small-app-profile.md](small-app-profile.md)，`"profile": "pipeline"`。

## test_matrix

| REQ | 驗證方式 | 測試類型 | 落點 |
|---|---|---|---|
| PIP-1 | fixture（有 schedule／只有 push 觸發／無 workflow）三向判定 | fixture truth-table | conformance CI |
| PIP-2 | gh api visibility 斷言 | integration | conformance CI＋季度巡邏 detector（可能轉 private） |
| PIP-3 | cron `*/4` fixture 必 fail；缺 estimated_minutes fixture 必 fail | fixture truth-table | conformance CI |
| PIP-4 | 同 SAP-3 fixture | fixture truth-table | conformance CI |
| PIP-5 | 帶 wrangler 的 pipeline fixture 觸發 SAP-1/2 子判定 | integration | conformance CI |
| PIP-6 | 沙盒連跑兩次，diff 斷言 | invariant（冪等） | conformance CI＋每輪驗證 |
| PIP-7 | 靜態掃描 fixture（隱藏 fetch 必被列出） | fixture truth-table | conformance CI |
| PIP-8 | 同 SAP-6 | integration | conformance CI＋季度巡邏 |
| PIP-9 | 沙盒帳號：fork→跑→刪→確認 Actions 停止＋資源歸零 | invariant（真值源往返） | 驗證 harness 每輪必跑 |

註：PIP-7 動態層（GH Actions egress 攔截）v0.1 明示不覆蓋，列 v0.2 缺口——缺列理由：Actions runner 網路攔截無現成免費機制，先以靜態層＋人工 diff 裁決補位。
