# 部署狀態機 v0.1

> 六件套 #6。狀態由裁判層 server 持久化（JDG-4）：agent 是導遊不是裁判——agent 讀狀態、引導使用者，但 transition 只能由對應 gate 的機械綠燈觸發。弱 agent 最壞卡關，不會假裝成功。

## 狀態與 transition

| # | 狀態 | 進入條件（guard，全機械） | 觸發工具 |
|---|---|---|---|
| 1 | RECEIVED | 收到 repo URL | — |
| 2 | INSPECTING | inspect_repository 開始 | #1 |
| 3 | RISK_REVIEW_READY | check_profile＋scan_project_security 完成（pass 或 fail 都到此態——結果給人看） | #2 #3 |
| 4 | AUTHORIZED | 使用者看過風險摘要後明示同意（server 記錄同意事件；profile fail 者不可授權，終止） | 人 |
| 5 | USER_COPY_CREATED | create_user_copy 成功＋upstream commit 鎖定 | #4 |
| 6 | LOCAL_TEST_PASSED | conformance 檢核全綠（契約 schema、wrangler 一致性、secrets 掃描、migration 空庫重放） | conformance CI |
| 7 | PREVIEW_DEPLOYED | deploy_preview 成功（先 Preview，不直接 Production） | #6 |
| 8 | AUTOMATED_TEST_PASSED | run_acceptance_suite smoke 全綠＋network_behavior_report verdict ≠ fail | #7 |
| 9 | USER_ACCEPTANCE_PASSED | acceptance.yaml user_acceptance 任務全數 pass（人執行、server 記錄） | #7 full |
| 10 | PRODUCTION_DEPLOYED | promote_to_production 成功 | #8 |
| 11 | HANDOFF_COMPLETED | 交付卡生成（服務 URL、登入方式、備份與移除指引） | server |
| 12 | MAINTENANCE_MODE | 交付完成後常駐態 | — |

MAINTENANCE_MODE 內的子流程（不離開主態）：health check（#9）、safe update（#10）、backup/restore（#11）。uninstall（#12 工具）從任意狀態可達，走 teardown 驗證後進 ABORTED（終止態，附 teardown_report）。

```
RECEIVED → INSPECTING → RISK_REVIEW_READY → AUTHORIZED → USER_COPY_CREATED
  → LOCAL_TEST_PASSED → PREVIEW_DEPLOYED → AUTOMATED_TEST_PASSED
  → USER_ACCEPTANCE_PASSED → PRODUCTION_DEPLOYED → HANDOFF_COMPLETED → MAINTENANCE_MODE
（任意狀態）→ ABORTED（經 uninstall teardown）
```

## 條款（Requirements）

| ID | 條款（可判定句） | 判定方式 | 來源故障 |
|---|---|---|---|
| SM-1 | 每個部署 session 恰有一個當前狀態，持久化於 server，重連可恢復 | 狀態查詢 API 冪等斷言 | 「每次重新判斷」＝agent 失憶重跑（原計畫明文） |
| SM-2 | transition 僅沿上表定義的邊行進，跳關請求被拒 | server 端 transition 表驗證 | 弱 agent 跳關假裝成功 |
| SM-3 | 同一 gate 連續 3 次不過 → 狀態標 `stuck`＋記錄卡點（stuck_state 進 Evidence Pack），停止自動重試 | retry 計數器 | 無限迴圈燒 token（retry budget 鐵則）；卡點＝spec bug 訊號 |
| SM-4 | AUTHORIZED 之前不得發生任何資源開通或 repo 寫入 | 審計：#4 之前的 audit log 零破壞性紀錄 | 未經同意動使用者帳號＝信任破產 |
| SM-5 | 從任意狀態執行 uninstall 皆到達 ABORTED 且附 teardown_report | 狀態可達性測試 | 半途而廢的部署殘留資源塞爆免費額度 |

## test_matrix

| REQ | 驗證方式 | 測試類型 | 落點 |
|---|---|---|---|
| SM-1 | 斷線重連 fixture：狀態一致斷言 | integration | mcp repo CI |
| SM-2 | 全部非法邊各一 fixture（12×11 中抽代表集＋全枚舉腳本） | fixture truth-table | mcp repo CI |
| SM-3 | 連續 3 次 fail 的 fixture → stuck 斷言＋第 4 次拒絕 | invariant | mcp repo CI＋驗證 harness |
| SM-4 | AUTHORIZED 前呼叫 #4 斷言被拒＋零副作用 | invariant | mcp repo CI |
| SM-5 | 每個狀態各發一次 uninstall，全部到 ABORTED＋teardown_report | fixture truth-table（全狀態枚舉） | mcp repo CI |

本檔為行為規格（S0 凍結狀態集與 guard）；server 實作落 S3。S2 期間人照 checklist 跑同一狀態機（人也是合規執行器），每站在 Evidence Pack 留人工紀錄——這正是「Agent 難產標準照樣可用」的驗證。
