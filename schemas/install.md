# Agent Install Contract v0.1

`.smallgreen/install.yaml` 是給部署 Agent 讀取的 Sites-only 安裝交接契約。人看服務卡；Agent 依這份契約核對來源、使用原生 Sites 能力部署、要求最少確認並執行驗收。

本契約不取代 `.openai/hosting.json`。Sites 資源仍由平台 manifest 宣告；本契約只描述可信來源、互動邊界、操作順序、驗收與阻擋狀態。`candidate` 可公開供檢視，但不得宣傳成已驗證的一句話安裝；只有沒有 blockers 的 `ready` 才能顯示可安裝狀態。

## Requirements

| ID | 可判定要求 |
|---|---|
| INS-1 | 契約必須通過 `install.schema.json`，且 protocol 固定為 `smallgreen-install/v1`。 |
| INS-2 | v0.1 只支援 `chatgpt-work` 以 `native-sites` 部署 Sites。 |
| INS-3 | 來源必須鎖定公開 repository、40 位 commit 與 license；有發布包時可另列 SHA-256。 |
| INS-4 | Sites 資源必須由 `.openai/hosting.json` 宣告，外部基礎設施清單必須為空。 |
| INS-5 | 最多兩次必要確認；契約不得以任意 shell command 取代受限 action。 |
| INS-6 | Agent 生成的 secret 只能進 Sites Secret 且不得顯示於聊天。 |
| INS-7 | 使用者提供的 runtime secret 只能在部署後由 application UI 輸入，聊天處理固定 forbidden。 |
| INS-8 | 驗收必須區分 deployment、runtime-setup 與 operational，不得把網站部署成功等同服務可用。 |
| INS-9 | `ready` 契約的 blockers 必須為空；`candidate` 的未驗證能力必須列入 blockers。 |
| INS-10 | 契約必須指向 teardown 文件並聲明移除前是否需匯出資料。 |

## State boundary

```text
candidate + blockers
  → sandbox deployment
  → runtime setup
  → operational acceptance
  → teardown / zero diff
  → ready + no blockers
```

## Boundary conditions

1. Work 帳號沒有 Sites 能力時停止，不改用外部 Cloudflare。
2. 來源 commit 不存在或 license 不符時停止。
3. `.openai/hosting.json` 缺失時停止，不猜 D1／R2 綁定。
4. 已有 project ID 時重用前先確認專案身份，不覆蓋其他 Site。
5. 新部署只能建立契約列出的 Sites 受管資源。
6. 產生的加密金鑰不輸出到聊天、日誌或原始碼。
7. 使用者的 Groq Key 不得在聊天、shell history 或瀏覽器 storage 出現。
8. 部署完成但 Groq 尚未設定時，只能回報「網站已部署」。
9. Groq 驗證成功但附件傳輸未驗收時，不能回報完整 operational success。
10. `candidate` 契約不得在服務卡顯示 SmallGreen Ready。
11. teardown 不得刪除使用者既有的非本案 Sites 專案。
12. 正式資料存在時，移除前必須依 maintenance 契約處理匯出。

## test_matrix

| REQ | 驗證方式 | 測試類型 | 落點 |
|---|---|---|---|
| INS-1 | valid／invalid fixture 對跑 | fixture truth-table | spec CI |
| INS-2 | 非 Work、非 Sites、非 native-sites fixture 必被拒 | contract | spec CI |
| INS-3 | 非 40 位 commit fixture 必被拒 | contract | spec CI |
| INS-4 | 錯誤 manifest 或非空 external infrastructure 必被拒 | invariant | spec CI |
| INS-5 | 超過兩次確認或未知 action 必被拒 | boundary | spec CI |
| INS-6 | expose_to_chat=true 或非 Sites Secret 必被拒 | security invariant | spec CI |
| INS-7 | before-deploy、chat 輸入或 allowed chat handling 必被拒 | security invariant | spec CI |
| INS-8 | 空 acceptance 必被拒；三階段實際結果寫 Evidence | contract + integration | spec CI + Evidence Pack |
| INS-9 | ready 帶 blocker 必被拒 | state invariant | spec CI |
| INS-10 | 空 teardown 文件必被拒 | contract | spec CI |
