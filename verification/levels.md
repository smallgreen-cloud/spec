# 三級驗證制度 v0.1

> 六件套 #4a。**收錄 ≠ 驗證；等級不可宣告取得，只能由檢核產物晉級**（Smithery 教訓：登錄站收錄與安全審查是兩回事）。每級檢核清單全部機械可判定或有明確人工裁決點；人工裁決限定三件事：體驗判讀、行為 diff 裁決、上架最終決定。

## 等級定義與晉級檢核

### Level 1 — Discovered

已發現，未經社群實測。收錄門檻（全機械）：

| 檢核 | 判定 |
|---|---|
| VER-1.1 repo 存在且未 archived | gh api |
| VER-1.2 license 欄位已記錄（可為空，空者標注「待補授權」） | gh api |
| VER-1.3 服務卡通過 schema（level: discovered 最小欄位集） | registry CI |

無 license 專案可收錄為 Discovered（附「待補授權」標注＋開 issue 請作者補），但**永久卡在 Discovered 直到 license 出現**。

### Level 2 — Community Verified

至少一位社群成員完成真實部署與功能驗收。晉級檢核：

| 檢核 | 判定 | 性質 |
|---|---|---|
| VER-2.1 ≥1 筆 Evidence Pack 含 deploy_event | registry CI 引用檢查 | 機械 |
| VER-2.2 該 Pack 的 user_acceptance 全數 pass（人勾核、裁判層記錄） | Evidence Pack 欄位 | 人工執行＋機械記錄 |
| VER-2.3 免費額度確認：conformance_minutes 與 free_tier 欄位齊備 | Evidence Pack 欄位 | 機械 |
| VER-2.4 OSI-approved license 存在（SAP-6／PIP-8） | gh api | 機械 |
| VER-2.5 ≥1 位具名 verifier 掛卡 | 服務卡欄位 | 機械 |
| VER-2.6 ≥1 則 scenario story（verifier 撰寫，reviewed: true） | 服務卡欄位 | 人工產出＋機械檢查 |
| VER-2.7 體驗判讀：verifier 對「真的好用嗎」留下一句話裁決 | Evidence Pack `verifier_verdict` | 人工（機械閘擋不了好不好用） |

### Level 3 — SmallGreen Ready

通過完整標準，可由 AI agent 依標準流程安裝與維護。晉級檢核（在 Community Verified 之上疊加）：

| 檢核 | 判定 | 性質 |
|---|---|---|
| VER-3.1 契約三檔存在且 conformance 全綠（CON-1…CON-7） | conformance CI | 機械 |
| VER-3.2 Profile 判定 pass（SAP 或 PIP 全條款，含 pending 項補齊） | 判定腳本 | 機械 |
| VER-3.3 agent matrix ≥1 列 result: autonomous（全自主走完狀態機，human_interventions ≤ 3） | Evidence Pack agent_matrix | 機械 |
| VER-3.4 network_behavior_report diff 零宣告外連；灰區外連經人工裁決標記 | 行為分析器＋人工 diff 裁決 | 機械產證據＋人裁決 |
| VER-3.5 teardown 驗證 pass（資源歸零 diff 為空） | Evidence Pack teardown | 機械 |
| VER-3.6 上架最終決定：maintainer 簽核 | registry PR review | 人工 |

## 降級與過期

| 規則 | 判定 | 落點 |
|---|---|---|
| VER-D.1 spec minor 版升級後，舊驗證卡標 stale（SVC-5）；major 版升級後降一級 | semver 比對 | registry 巡邏 detector |
| VER-D.2 上游 repo archived 或 last_push 停滯 >12 個月 → maintenance_status 降 stalled，卡面標示 | gh api 巡邏 | 季度巡邏＋TG 告警 |
| VER-D.3 已驗證專案被發現宣告外連（任何來源回報）→ 立即降回 Discovered＋公開 incident 記錄 | 行為分析器複測 | 事件驅動 |

## test_matrix

| REQ | 驗證方式 | 測試類型 | 落點 |
|---|---|---|---|
| VER-1.x | fixture 卡（archived repo／無 license）收錄判定 | fixture truth-table | registry CI |
| VER-2.1–2.6 | 欄位不齊的晉級 PR 必被 CI 拒絕 | fixture truth-table | registry CI |
| VER-2.7 | verifier_verdict 缺失時 Pack 不計入晉級 | invariant | registry CI |
| VER-3.1–3.5 | 各缺一項的 fixture 必卡在 Community Verified | fixture truth-table | registry CI |
| VER-3.6 | 無 maintainer approval 的 PR 不可 merge | branch protection | GitHub 設定（部署驗證斷言存在） |
| VER-D.1 | 模擬 spec 升版 → stale 斷言 | cache/staleness | 巡邏 detector |
| VER-D.2 | 每卡 freshness 個體斷言（聚合綠燈不掩蓋個體死亡） | detector（per-member） | 季度巡邏＋TG 告警 |
| VER-D.3 | 降級流程 dry-run 演練一次並留紀錄 | integration | S4 上線前一次性＋事件驅動 |
