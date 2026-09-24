# Public Feedback Pack v0.1.0（draft）

Public Feedback Pack 是部署到達終止狀態後，由使用者自願公開的結構化改善訊號。成功、失敗、卡住或中止都可產生；它與 Evidence Pack 分離，**不得直接用來升級服務卡驗證等級或支持「已驗證」宣稱**。

Schema：[public-feedback-pack.schema.json](public-feedback-pack.schema.json)。參考工具位於 `smallgreen-cloud/conformance/scripts/public_feedback.py`。

## 信任與隱私模型

- 統計對象是專案與契約版本，不建立安裝 ID，也不追蹤使用者。
- Pack 內容不含 GitHub handle；公開 Issue 的作者與時間由 GitHub 顯示，因此是「內容去識別化」，不是匿名提交。
- Agent 不得自行拼接 Issue、不持有提交權，也不得直接呼叫 `gh issue create`。參考工具只產生可編輯的 GitHub Issue 草稿，由使用者在瀏覽器完成公開提交。
- 防護不只依賴 Agent 遵約：部署 Agent 的程序環境不得取得 GitHub Issue 寫入憑證。GitHub 登入只留在 Agent 無法讀取的使用者瀏覽器邊界。若執行環境已把同一組 GitHub 寫入能力交給 Agent，SmallGreen 無法保證它不繞過工具，該次回饋流程不符合本規格。
- Schema 的欄位白名單只是第一道閘。任何編輯後都必須重新執行規則式 secret scanner；偵測不確定時 fail closed。
- GitHub Issue 發布後可以編輯，但上傳後刪除不構成安全控制。Secret 一旦公開，必須視為洩漏並立即撤銷與輪替。

## 欄位用途

| 欄位 | 社群用途 | 來源 |
|---|---|---|
| project_id、contract_commit、contract_sha256、spec_version | 將問題定位到可復現契約版本 | 契約所在 repo；hash 涵蓋 AGENTS.md、`.smallgreen/` 三件，以及存在時的 UPSTREAM.md 與 `patches/` |
| agent | 確認跨 Agent／模型的相容性缺口 | 執行環境版本資訊 |
| outcome、preflight_result、failed_step_id、error_codes | 找出卡點並建立回歸案例 | 驗證器／執行狀態 |
| retry_count、human_debug_interventions、duration_seconds | 判斷是否達到一次委派、零人工除錯 | 執行器計數器 |
| verifier_result | 區分 Agent 自述與機械驗證結果 | 獨立 verifier |

沒有自由文字、完整 log、附件、部署 URL、帳號／資源 ID、本機路徑、環境變數或 HTTP headers 欄位。純研究用途欄位不得加入；新增欄位必須先說明社群自身用途。

## Requirements

| ID | 可判定條款 | 判定方式 |
|---|---|---|
| PFB-1 | 每份 Pack 必須通過 JSON Schema，且不得有未列欄位 | Draft 2020-12 validator |
| PFB-2 | Pack 不得含識別欄位、完整 log、自由文字、附件、網址、帳號或資源 ID | `additionalProperties: false`＋欄位審查 |
| PFB-3 | `contract_commit` 與 `contract_sha256` 必須由工具從已提交的契約 repo 推導，不得由 Agent 猜測 | 參考工具 dirty-tree gate＋hash |
| PFB-4 | 常見 Secret 格式或泛用高熵憑證命中時必須阻擋，不得自動放行 | 規則式 scanner，fail closed |
| PFB-5 | 使用者編輯後必須完整重驗；預覽內容以 SHA-256 綁定 | validator＋payload hash |
| PFB-6 | 發布前必須顯示最終 payload、目標公開 repo，以及 GitHub 帳號與提交時間會公開 | 草稿頁固定揭露文案 |
| PFB-7 | 參考工具不得建立 Issue 或持有 GitHub 寫入憑證；公開動作由使用者在 GitHub UI 完成 | 工具無 GitHub API／`gh` submit 路徑 |
| PFB-8 | 未同意、驗證失敗或安全工具不可用時，不得發出回饋提交 | fail closed |
| PFB-9 | Public Feedback Pack 不得作為驗證通過證據；可信宣稱仍以 Evidence Pack 為準 | registry 聚合器只讀 Evidence Pack |
| PFB-10 | 部署 Agent 不得取得 GitHub Issue 寫入憑證；公開權限只存在於使用者瀏覽器 | learner／community harness 權限檢查＋無真實 `GH_TOKEN`／可寫 `gh` session |

## 閉環處理

```text
terminal outcome
→ deterministic pack generation
→ schema and secret gates
→ local edit and revalidation
→ exact payload and public identity disclosure
→ user submits public GitHub issue
→ maintainer reproduces against contract_commit and contract_sha256
→ regression fixture starts RED
→ contract or tool fix reaches GREEN
→ issue links the fixing version
```

## test_matrix

| REQ | 測試 | 落點 |
|---|---|---|
| PFB-1/2 | valid Pack 通過；多出 `stdout` 的 invalid Pack 必被拒 | spec fixture truth-table |
| PFB-3 | 任一契約檔變動會改變 contract hash；dirty 契約拒絕產生 commit 宣稱 | conformance unit test |
| PFB-4 | 供應商 Token 與泛用高熵字串放入允許欄位仍被拒 | conformance unit test |
| PFB-5 | 編輯後重驗會阻擋 Secret；內容改變會改變 payload hash | conformance unit test |
| PFB-6/7/8 | 草稿含固定揭露；無直接 submit 路徑；非法 target 被拒 | conformance unit test＋code review |
| PFB-9 | registry 不讀 Public Feedback Pack 生成驗證欄位 | registry integration test（發布前） |
| PFB-10 | harness 以不可寫 GitHub 的 Agent 環境執行；可觀測假 `gh` 驗證 Agent 未嘗試繞過 | learner pilot security scenario |
