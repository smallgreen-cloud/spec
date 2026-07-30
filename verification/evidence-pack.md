# Evidence Pack 規格 v0.1（已凍結）

> **凍結狀態：schema_version 0.1.0 已於 2026-07-30 簽核凍結（S0 唯一不可逆件）。**
> 自此：新增欄位＝minor 版且必過欄位正當性判準（EP-4）；欄位刪除或語意變更＝major 版；舊 Pack 永不依新 schema 重寫（GOV-6）。

> 六件套 #4b。Evidence Pack＝一次真實驗證部署的 conformance 產物，是整個計畫的資料心臟：
> **驗證統計＝碳宣稱出處＝論文資料集，一條管線三次收穫。**
> 測量欄位隨標準凍結——數據不可回填，本 schema 是 S0 唯一不可逆的環節。Schema：[evidence-pack.schema.json](evidence-pack.schema.json)。

## 欄位正當性判準（進 schema 的門檻）

**不做研究，社群自己也需要的欄位才進標準；純研究用途欄位不准進。**

| 欄位群 | 社群自身用途 | 來源 |
|---|---|---|
| deploy_event | 服務卡「驗證次數／最近驗證日期」——沒有統計，驗證等級就是自說自話 | 自願提交 |
| code_metrics（LOC、依賴數） | 安全掃描與規模判定 | public repo |
| conformance.minutes | 免費額度實測（free_tier 佐證） | CI log |
| low_carbon | 服務卡低碳標示 | wrangler 設定推導 |
| spec_version | 驗證過期判定 | 本 Pack |
| agent_matrix | 服務卡「相容 agents」徽章；弱 agent 卡關位置＝spec bug 訊號 | 驗證 harness |
| network_behavior_report | 資料流向揭露（信任信號） | 行為分析器 |
| screenshots | 目錄站主圖（真實截圖，禁 mockup／AI 生圖） | shot-scraper（dogfooding：候選池工具給候選池截圖） |
| teardown | 「退得乾淨」承諾的證據；同測 maintenance.yaml uninstall 條款 | 驗證 harness |
| user_acceptance＋verifier_verdict | Community Verified 晉級證據 | 人工執行、裁判層記錄 |

## 條款（Requirements）

| ID | 條款（可判定句） | 判定方式 | 來源故障 |
|---|---|---|---|
| EP-1 | 每筆 Pack 通過 evidence-pack.schema.json 驗證 | registry CI | 欄位漂移＝資料集不可分析 |
| EP-2 | Pack 為 append-only：merge 後不可修改；更正＝提交新 Pack 並以 `supersedes` 指向舊筆 | registry CI 對已存在檔案的 diff 檢查（改動既有 Pack 的 PR 必 fail） | 數據可回填＝研究誠信破產（實驗數據 provenance 鐵則） |
| EP-3 | schema 不含任何使用者識別欄位（IP、裝置、安裝 ID、email）；submitter 僅自願 GitHub handle | schema `additionalProperties: false` 機械保證＋欄位審查 | Audacity 2021 遙測風暴；**統計對象是專案，永遠不是使用者** |
| EP-4 | 新增欄位需在本檔正當性表格補列「社群自身用途」，缺者 PR 不可 merge | spec PR review checklist | 欄位膨脹→變相遙測 |
| EP-5 | 彙總資料集（SmallGreen Evidence Dataset）以 CC 授權公開 | dataset repo LICENSE 檔存在性 | 公共財承諾（見 GOVERNANCE.md） |
| EP-6 | screenshot artifact 必附 sha256，architecture SVG 必附生成來源 profile.yaml 的 commit hash | schema required | 假圖／過期圖上卡（demo 要真鐵律） |
| EP-7 | agent_matrix 每列必含 human_interventions 與 stuck_state（未卡填 null），retry 上限 3 次 | schema required＋harness 紀律 | 無卡點紀錄＝spec 回饋迴圈斷炊 |
| EP-8 | network_behavior_report 的 undeclared 非空時 verdict 不得為 pass（僅能 fail 或 human_approved＋裁決人與理由） | schema 條件式驗證 | 宣告外連＝紅燈 fail-closed；灰區走人工裁決不走放行預設 |

## 提交流程

「我部署了」＝向 registry 提交 Evidence Pack PR（winget 模式）。CI 驗 EP-1…EP-8 → maintainer merge → 服務卡統計欄位由 Pack 聚合腳本重算（不可手改，SVC-3 同型的真值源往返）。

## test_matrix

| REQ | 驗證方式 | 測試類型 | 落點 |
|---|---|---|---|
| EP-1 | valid／invalid Pack fixture 對跑 | fixture truth-table | registry CI |
| EP-2 | 修改既有 Pack 的 PR fixture 必 fail；supersedes 鏈驗證 | invariant（append-only） | registry CI |
| EP-3 | 帶 email 欄位的 Pack fixture 必被 schema 拒絕 | fixture truth-table | registry CI |
| EP-4 | spec PR template checklist 含正當性欄位項 | process | spec repo PR template |
| EP-5 | dataset repo LICENSE 存在性斷言 | integration | dataset 發布 CI |
| EP-6 | 缺 sha256 fixture 必 fail | fixture truth-table | registry CI |
| EP-7 | 缺 stuck_state 欄位 fixture 必 fail | fixture truth-table | registry CI |
| EP-8 | undeclared 非空＋verdict: pass 的 fixture 必被 schema 拒絕 | invariant（fail-closed） | registry CI |

聚合腳本（Pack → 服務卡統計、Pack → Evidence Dataset）的回歸：對 fixture Pack 集重算兩次，第二次零變更（冪等）。
