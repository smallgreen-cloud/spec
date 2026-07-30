# 裁判層 MCP 介面規格 v0.1（先介面後實作）

> 六件套 #5。**MCP 不是功能層，是裁判層：它存在的理由是產生 agent 無法竄改的 gate 紀錄，把執行者和裁判分開。**
> 歸屬規則：掃描結果、gate 通過與否、資源開通、健康狀態必在 server 端；引導話術、流程順序、人話翻譯留 skill／AGENTS.md 端。實作時任何「圖方便把判斷塞回 agent」的做法都違反本規格。
> 協議基準：MCP 2026-07-28 規範。工具共 12 個（沿自原計畫清單；`check_cloudflare_free_profile` 因 Profile 拆二更名為 `check_profile`）。

## 通用約定

- 所有工具回傳皆含 `{"gate_record_id": "...", "spec_version": "..."}`——每次呼叫在 server 留審計紀錄（不可竄改、可稽核，供徽章簽署引用）
- 破壞性工具（標 D）必支援 `dry_run: true` 且預設 `dry_run: true`；實際執行需帶 server 發的 `confirm_token`（由前一次 dry-run 回傳，一次有效）
- 錯誤格式統一：`{"error": {"code", "message", "recoverable": bool}}`
- 工具只吃沙盒／使用者自帶 token（env 注入），server 永不保管長期憑證

## 12 工具

| # | 工具 | D | Input（required） | Output（核心欄位） | 狀態機 gate |
|---|---|---|---|---|---|
| 1 | `inspect_repository` | | `repo`（owner/name）, `ref?` | `summary`（用途／功能／元件／資料類型／登入方式，人話）, `contract_found: bool` | RECEIVED→INSPECTING |
| 2 | `scan_project_security` | | `repo`, `ref?` | `secrets_hits[]`, `static_network: {declared[], detected[], undeclared[]}`, `dependency_audit`, `verdict: pass\|fail` | INSPECTING 內 |
| 3 | `check_profile` | | `repo`, `ref?`, `profile: small-app\|pipeline\|auto` | Profile 判定輸出格式（見 profiles/，逐條 SAP／PIP checks＋pending 清單） | INSPECTING→RISK_REVIEW_READY |
| 4 | `create_user_copy` | D | `repo`, `target_account`, `confirm_token?` | `new_repo`, `upstream_locked_commit` | AUTHORIZED→USER_COPY_CREATED |
| 5 | `create_adaptation_pr` | D | `repo`, `changes_summary`, `confirm_token?` | `pr_url`, `files_changed[]`（契約檔生成走此工具，Path B/C） | USER_COPY_CREATED 內 |
| 6 | `deploy_preview` | D | `repo`, `confirm_token?` | `preview_url`, `resources_created[]`, `migration_log` | LOCAL_TEST_PASSED→PREVIEW_DEPLOYED |
| 7 | `run_acceptance_suite` | | `repo`, `target: preview\|production`, `suite: smoke\|full` | 逐測項結果, `network_behavior_report`（沙盒動態攔截含於此）, `verdict` | PREVIEW_DEPLOYED→AUTOMATED_TEST_PASSED |
| 8 | `promote_to_production` | D | `repo`, `confirm_token?` | `production_url`, `resources_diff` | USER_ACCEPTANCE_PASSED→PRODUCTION_DEPLOYED |
| 9 | `check_application_health` | | `repo` | `health: pass\|fail`, `quota_snapshot[]`（maintenance.yaml watchdog 宣告項實測值） | MAINTENANCE_MODE 內 |
| 10 | `prepare_safe_update` | D | `repo`, `confirm_token?` | `backup_ref`, `update_pr_url`, `preview_url`（更新前備份→更新 PR→Preview，三步一體） | MAINTENANCE_MODE 內 |
| 11 | `backup_and_restore` | D | `repo`, `mode: backup\|restore`, `backup_ref?`, `confirm_token?` | `backup_ref` 或 `restore_report` | MAINTENANCE_MODE 內 |
| 12 | `uninstall_application` | D | `repo`, `export_data_first: bool`, `confirm_token?` | `teardown_report`（residual_resources[], pass）——資源歸零 diff 由 server 驗證 | 任意狀態→ABORTED／MAINTENANCE_MODE→終止 |

行為分析器是 #2（靜態層）與 #7（動態層：miniflare/wrangler dev 沙盒攔截 outbound fetch）的內部配套工具，`network_behavior_report` 進 Evidence Pack（EP-8）。

`user_acceptance` 的勾核走 #7 `suite: full` 的互動子流程：任務清單來自 acceptance.yaml，人執行、server 記錄結果——人在迴圈但紀錄在裁判。

## 條款（Requirements）

| ID | 條款（可判定句） | 判定方式 | 來源故障 |
|---|---|---|---|
| JDG-1 | 12 工具的 input/output 通過本檔宣告的 schema（介面凍結；欄位增刪＝spec minor/major） | 介面 schema 對照測試 | 介面漂移＝所有 agent 端同時壞 |
| JDG-2 | 每次工具呼叫產生不可竄改的 gate 紀錄（server 端 append-only audit log） | audit log 存在性＋append-only 檢查 | agent 自己當裁判「覺得過了就往下走」（裁判層原則的成因） |
| JDG-3 | 破壞性工具未帶有效 confirm_token 時一律以 dry_run 執行，直接執行請求被拒 | 介面測試：無 token 呼叫斷言 dry-run 行為 | 誤觸生產操作（validate-before-scale 探針事故同型） |
| JDG-4 | 狀態機 transition 只能由對應工具的 server 端綠燈觸發，agent 不可直接寫狀態 | 狀態寫入 API 不對外暴露（介面層機械保證） | 弱 agent 假裝成功跳關 |
| JDG-5 | teardown 的資源歸零 diff 由 server 比對（部署前 snapshot vs 移除後清單），不採信 agent 回報 | #12 輸出必含 server 側 diff | agent 回報「已清乾淨」不可信 |
| JDG-6 | server 不保管長期憑證；token 一律由呼叫方 env 注入，audit log 不含 token 值 | log 掃描零 secret 命中 | token 集中保管＝爆炸半徑最大化（帳號分層原則） |

## test_matrix

| REQ | 驗證方式 | 測試類型 | 落點 |
|---|---|---|---|
| JDG-1 | 12 工具各一組 valid／invalid I/O fixture 對跑 | fixture truth-table | mcp repo CI（S3 實作時） |
| JDG-2 | 呼叫後 audit log 行數＋1 斷言；修改既有紀錄的操作必 fail | invariant（append-only） | mcp repo CI＋生產 |
| JDG-3 | 無 token 呼叫 #4/#5/#6/#8/#10/#11/#12 斷言零副作用（沙盒帳號資源清單前後 diff 為空） | invariant（無副作用探針：查資源清單，不賭 fail-closed） | mcp repo CI |
| JDG-4 | 直接 POST 狀態端點斷言 404/403 | integration | mcp repo CI |
| JDG-5 | 沙盒故意留一個 KV → teardown 報告必列殘留 | fixture truth-table | 驗證 harness |
| JDG-6 | audit log 全量 secret 掃描零命中 | invariant | mcp repo CI＋生產 detector |

本檔為介面規格（S0）；實作落 S3（裁判層 MCP 最小集：#1 #2 #3 #7 #12 先行——判定與驗收先於部署自動化，Deploy Button 已吃掉中段）。
