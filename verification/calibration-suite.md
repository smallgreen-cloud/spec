# Calibration Suite v0.2

> 支撐層規格。Calibration Suite 不是專案測試資料，而是部署批次開始前用來校正 verifier、harness 與環境的 known-answer reference。未通過校正時，後續專案 run 不具統計資格。

## 目的與邊界

SmallGreen 的部署結果同時可能被五個責任層影響：project、contract、agent、environment、verifier。若直接拿真實專案測 verifier，錯誤來源無法分離；因此必須先用真值固定的「砝碼」確認量測鏈。

校正分兩層：

- **L0 instrument calibration**：離線 known-answer fixtures，校正結構化 oracle、錯誤碼與 Calibration Report。
- **L1 environment calibration**：SmallGreen 自有最小 live canary，校正平台原生認證、CLI、runtime、網路、平台、功能驗收與 teardown observation。Public 預設只觀察契約擁有資源；Judge 可選帳號級 snapshot。L1 尚未完成真實 lifecycle 前，不得宣稱部署環境已完成校正。

Calibration Report schema：[calibration-report.schema.json](calibration-report.schema.json)。L0 參考實作位於 `smallgreen-cloud/conformance` 的 `scripts/calibration.py`。

## L0 五個必要砝碼

| Fixture ID | 真值 | 必須證明 |
|---|---|---|
| `W0-PREFLIGHT-PASS` | pass at `PREFLIGHT` | 合法 preflight 不被誤擋，且不建立雲端資源 |
| `W1-KNOWN-PASS` | pass at `COMPLETE` | deployment、功能驗收、teardown 全通過才成功 |
| `W2-PREFLIGHT-FAIL` | fail at `PREFLIGHT` | 前置條件失敗時 fail-closed，不先建立資源 |
| `W3-ACCEPTANCE-FAIL` | fail at `ACCEPTANCE` | HTTP 200 不能掩蓋功能 smoke failure |
| `W4-TEARDOWN-FAIL` | fail at `TEARDOWN` | uninstall command exit 0 不能掩蓋殘留資源 |

砝碼只提供原始 observation 與 expected truth，不提供可被 verifier 採信的自述 verdict。Observed result 必須由 verifier 程式依 observation 重算。

## L0 Calibration Report

報告必須包含：

- `run_type: calibration`，避免混入 project run。
- suite ID、版本、內容 SHA-256、來源 commit 與 dirty 狀態。
- verifier 名稱、版本、檔案 SHA-256 與來源 commit。
- 只含 Python、OS、release、architecture 的低敏環境輪廓。
- 每個 fixture 的 expected、observed、match。
- 5/5 摘要、verdict 與 `eligible_for_l1`。

即使五個 oracle 全部 match，只要 suite／verifier 沒有固定在乾淨 commit，`eligible_for_l1` 仍須為 false。這區分「本機原型邏輯正確」與「可作為 L1 依據」。L0 無權直接放行 live 專案；只有 L1 report 可設定 `eligible_for_project_runs`。

## L1 live canary

L1 必須使用 SmallGreen 自有最小專案，不使用第三方專案當砝碼。至少驗證：

1. 預設使用平台 CLI 既有 OAuth；只有要求帳號級 snapshot 的 Judge run 才使用最小權限 API token。
2. CLI、runtime、DNS 與平台 API 可用。
3. deploy effect identity 與 health target 都綁定同一個明確確認的 canary 名稱。
4. HTTP health 與一個 functional assertion 通過。
5. teardown 後契約擁有資源回到部署前狀態；若 report 宣稱帳號級驗證，完整帳號資源清單也必須等於部署前 snapshot。

Agent／模型、harness、verifier、Spec、Wrangler／runtime、平台、帳號或權限任一變更，都使舊 L1 失效。

L1 report schema：[live-canary-report.schema.json](live-canary-report.schema.json)。只有 live mode 六個 checkpoint 全部通過，且 report 所宣稱 observation scope 的部署前／teardown 後集合完全一致，才能設定 `eligible_for_project_runs: true`。

### 架構與副作用邊界

```text
L0 report（eligible_for_l1=true）
  → 以目前 checkout 重算 L0 穩定欄位
  → validate local canary source／Wrangler exact pin／可實際執行該 Wrangler 的 Node
  → 選擇 observation scope
      ├─ Public 預設：Wrangler OAuth＋owned Worker observation
      └─ Judge 選配：API token＋account Workers snapshot
  → auth probe＋collision check
  → wrangler deploy --strict（唯一建立副作用）
  → claimed scope effect assertion＋identity fingerprint
  → health＋functional HTTP oracle
  → wrangler delete（補償動作）
  → bounded settle
  → claimed scope zero-diff assertion
  → L1 report（eligible_for_project_runs）
```

Public 預設路徑使用 `wrangler whoami` 驗證既有 OAuth session，以 `wrangler versions list --name <confirmed-name> --json` 觀察該 Worker 是否存在及最新 version identity；deploy 輸出的 workers.dev URL 只在記憶體解析，hostname 必須逐字綁定已確認名稱，帳號 subdomain 也必須是單一合法 DNS label。OAuth 模式沒有 account-wide API 視野，因此該 label 的所有權信任已認證 Wrangler deploy output，不能獨立證明該帳號的完整資源所有權。此路徑不要求 Agent 額外取得 API token，也不宣稱看見帳號內其他資源。

Judge 選配路徑才使用官方 `GET /accounts/{account_id}/workers/scripts` 取得帳號級 snapshot，並以 `GET /accounts/{account_id}/workers/subdomain` 組合 acceptance target。Token 與 account ID 只從環境取得，禁止成為 CLI 參數、report、log 或 journal 欄位。兩條路徑都必須在 report 寫入機械導出的 `auth_mode`、`observation_scope` 與 `zero_diff_level`；合法組合只有：

- `wrangler_oauth`＋`owned_resources`＋`owned_resource_zero_diff`
- `api_token`＋`account`＋`account_snapshot_zero_diff`

前者是部署標準的必要證明；後者是 Judge／研究環境的加強證據。聚合成功率時必須依 observation scope 分層，不得把 owned-resource 證據升級成 account snapshot 宣稱。

Canary 只建立一個無 binding 的 Worker。固定提供：

- `GET /healthz`：HTTP 200＋固定 `fixture`／`version` sentinel。
- `GET /echo?value=smallgreen-canary`：HTTP 200＋逐字回傳固定測試值，證明不是只回健康頁。
- 其餘路徑：HTTP 404。

### Journal 與恢復

Live runner 在 deploy 前建立去識別化 journal，記錄 canary name hash、部署前 observation hash、認證模式、觀察範圍與狀態；部署 effect 確認後，另記不可逆 identity fingerprint。帳號模式以 Worker `tag`＋`etag` 導出 identity；OAuth 模式只取 Wrangler JSON 中最新 version ID 導出 identity，不保存 author email、message 或 raw output。L1 report 同時記錄 live runner 與 Cloudflare adapter 的合併 SHA-256 及 source revision；dirty scope 必須涵蓋 canary、live runner、adapter、L0 verifier 與 W0–W4 fixtures。若 deploy timeout／程序中斷，下一次只能用 journal 記載的同一 observation scope 進 recovery：目前同名 Worker 的 identity fingerprint 必須與 journal 相同才可刪除，再驗證該 scope 的 zero-diff；HEAD 改變本身不阻止 recovery。Scope／fingerprint 不符、缺失或查詢失敗時不得靠名稱猜 ownership，轉人工仲裁。Journal 採 fsync＋atomic rename，且不含 Token、帳號 ID、URL、既有 Worker 名稱或命令輸出。

L1 canary 為純 API Worker，不產生截圖。真實 Web 專案可在 acceptance 通過後、teardown 前收集網站／服務卡／簡報用畫面；該素材不屬於 L1 oracle，也不進 calibration 或部署成功率判定。

### 錯誤契約

| Error code | 可重試 | 語意 |
|---|---|---|
| `L1_INPUT_INVALID` | 否 | run ID、JSON、輸出路徑或明確名稱確認無效；進 API 前拒絕 |
| `L0_NOT_ELIGIBLE` | 否 | L0 缺失、dirty、hash 不符或未放行 L1 |
| `AUTH_MISSING` | 否 | 明確選擇 account scope，但必要 API token／account ID 環境變數不存在；不得輸出其值 |
| `AUTH_UNAVAILABLE` | 否 | 選定的認證模式不可用；OAuth 路徑應提示先完成 `wrangler login` |
| `WRANGLER_UNSUPPORTED` | 否 | Wrangler 缺失或 major <4 |
| `CANARY_SOURCE_UNPINNED` | 否 | Canary source 無乾淨 commit 或內容 hash 不可追溯 |
| `SNAPSHOT_FAILED` | 是，最多 3 次 | Workers list／subdomain 唯讀 API timeout 或錯誤 |
| `CANARY_NAME_COLLISION` | 否 | 部署前已有同名 Worker；不得覆蓋或刪除 |
| `DEPLOY_FAILED` | 否，本 run 轉補償 | deploy 非零退出或 timeout；仍須 snapshot 判定是否已有副作用 |
| `DEPLOY_EFFECT_MISSING` | 否 | deploy 回成功但 snapshot 無 canary |
| `DEPLOY_URL_MISSING` | 否，本 run 轉補償 | deploy effect 已存在，但無法取得逐字綁定 confirmed name 的 workers.dev URL；不得向其他 hostname 發送 acceptance probe |
| `SNAPSHOT_CONTAMINATED` | 否 | 量測窗出現非本 canary 的新增／移除資源 |
| `HEALTH_TIMEOUT` | 是，bounded settle | workers.dev 尚未可用或 health sentinel 不符 |
| `FUNCTIONAL_FAILED` | 否 | health 可達但 echo 功能不符 |
| `TEARDOWN_FAILED` | 是，最多 1 次補償 | delete 非零／timeout |
| `RESIDUAL_RESOURCE` | 否 | delete exit 0 但 snapshot 仍含 canary |
| `RECOVERY_REQUIRED` | 否 | 找到未結束 journal，須先執行 recovery |

### 邊界條件

1. run ID 含非法字元、過長或造成 Worker 名稱超過 63 字元時，進 API 前拒絕。
2. L0 report 缺失、`eligible_for_l1=false`、source revision 不同、suite／verifier hash 不符或結構不合法時不得 deploy；L1 必以目前 checkout 的 W0–W4 與 verifier 重算穩定欄位，不採信輸入 report 自述。
3. 預設 owned-resource 路徑不得因缺少 API token／account ID 而阻擋；Wrangler OAuth 不可用時只回 `AUTH_UNAVAILABLE`。只有操作者明確選擇 account scope 且環境變數缺失時回 `AUTH_MISSING`，兩者都不得印出 credential 或 auth command output。
4. Wrangler major <4、無法解析版本、執行 Wrangler 的 Node 架構與主機不相容，或 canary dry-run 失敗時不得 deploy；report 必記錄 Node 版本與 `node_arch`。
5. 部署前已有同名 Worker 時 fail-closed，且不得執行 delete。
6. observation timeout 採 bounded retry；OAuth 模式只有 Cloudflare Worker-not-found error code `10007` 加上 Worker-not-found 語意可判定為空集合，其他非零、空 JSON、malformed JSON 或 auth error 全部 fail-closed。帳號 snapshot 同樣不能把未知當空集合。
7. deploy timeout 仍可能已有副作用；必須重新 snapshot 並進補償。
8. HTTP 200 但 sentinel／echo 錯誤仍為 fail。
9. DNS／TLS／edge propagation 只能依 bounded settle 重試，不能無限等候。
10. delete exit 0 但 Worker 仍存在，必須回 `RESIDUAL_RESOURCE`。
11. account scope 量測窗有其他 Worker 增刪時標 `SNAPSHOT_CONTAMINATED`，不得歸因 canary；owned-resource scope 看不見其他 Worker，report 與研究資料必明示此限制，不能宣稱 account-wide clean。
12. teardown 失敗時 report 必為 fail，並保留不含敏感資訊的 recovery journal。
13. 執行中斷後不得靠名稱猜 ownership；只有 deploy 前 journal 加上部署後 identity fingerprint 可授權自動 recovery。Fingerprint 不符或缺失時不得 delete；source revision 改變不應阻止安全 recovery。
14. 既有 report／journal 不得靜默覆寫。
15. dry-run 只能證明 bundle／config 可編譯，不能產生 L1 pass report。
16. `auth_mode`、`observation_scope`、`zero_diff_level` 任一缺失或組合不合法時，schema 與 runner 都必須拒絕。
17. OAuth deploy output 中若只有其他 Worker 的 URL、非 HTTPS、帶 credential 或非 workers.dev hostname，acceptance 不得執行，但可能已建立的 owned Worker 仍須 teardown。

### 驗收用例

- **Given** 合格 L0、有效 Wrangler OAuth 與乾淨 confirmed name，**When** deploy、兩個 HTTP oracle、delete、owned-resource zero-diff 全通過，**Then** L1 report 為 pass、`eligible_for_project_runs=true`，但只能宣稱 `owned_resource_zero_diff`。
- **Given** 操作者明確選擇 account scope 且提供最小權限 API token，**When**完整 lifecycle 與帳號 snapshot zero-diff 全通過，**Then** 才能宣稱 `account_snapshot_zero_diff`。
- **Given** health HTTP 200 但 fixture sentinel 錯誤，**When** acceptance 執行，**Then** verdict fail 且 teardown 仍必執行。
- **Given** delete exit 0 但 snapshot 仍含 canary，**When** teardown effect assertion 執行，**Then** 回 `RESIDUAL_RESOURCE`，不得放行。
- **Given** deploy timeout 但 snapshot 已出現 canary，**When** runner 進補償，**Then** 必刪除 owned canary 並以 `DEPLOY_FAILED` 結案。
- **Given** 部署前同名 Worker 已存在，**When** collision check 執行，**Then** 不 deploy、不 delete、不宣稱 ownership。
- **Given** 量測窗出現其他 Worker 變更，**When** snapshot diff 執行，**Then** 標為 contaminated，不把差異算成 canary 效果。
- **Given** 中斷後同名 Worker 的 identity fingerprint 已改變，**When** recovery 執行，**Then** 不 delete 並轉人工仲裁。
- **Given** journal 記錄 account scope，**When** recovery 改用 owned-resource runtime，**Then** 不 delete 並要求使用原 scope 或人工仲裁。

## Requirements

| ID | 可判定條款 | 判定方式 | 來源風險 |
|---|---|---|---|
| CAL-1 | L0 suite 恰含 W0–W4 各一次；缺少、重複或新增未知 fixture 一律拒絕 | fixture set validator | 少測一個 fail mode 卻仍宣稱校正通過 |
| CAL-2 | observed verdict 只能由結構化 observation 機械導出，不讀取 Agent 自述 verdict | oracle API 不接受 verdict input | 執行者同時當裁判 |
| CAL-3 | suite 與 verifier 均記錄 SHA-256、來源 commit 與 dirty 狀態 | Calibration Report schema＋runner | 換了砝碼或秤卻無法追溯 |
| CAL-4 | 五 fixture 5/5 match 且乾淨 commit 才可令 `eligible_for_l1=true` | report invariant | fail-open 或未提交程式充當 L1 依據 |
| CAL-5 | 相同版本 L0 連跑三次的 suite hash、observed、match 與 verdict 必須一致 | repetition test | 非決定性 oracle |
| CAL-6 | calibration report 使用 `run_type=calibration`，不得進 project success rate 分母 | schema const＋資料聚合過濾 | 校正成功灌入部署成功率 |
| CAL-7 | 報告不得含 raw log、Token、帳號 ID、部署 URL、本機路徑或自由文字 | additionalProperties false＋欄位審查 | 校正產物外洩敏感資料 |
| CAL-8 | L1 失敗後啟動的 project run 標為 invalid-run，不歸責專案 | batch controller invariant（L1 實作時） | 環境故障被算成專案失敗 |
| CAL-9 | 任一校正 fixture misclassification 必使 process 非零退出 | CLI truth-table | 報告寫 fail 但 pipeline 繼續 |
| CAL-10 | L1 只有所宣稱 observation scope 的部署前後 zero-diff、功能 oracle 與 teardown effect assertion 全通過才能放行 project run | live canary runner＋report invariant | exit 0 被誤當效果證據 |
| CAL-11 | L1 無論 acceptance／deploy 結果如何，只要可能建立 canary 就必進 teardown／recovery | fault injection | 失敗 run 留下資源 |
| CAL-12 | L1 report／journal 不含 Token、account ID、URL、Worker 名稱、既有資源名稱或 raw command output | additionalProperties false＋secret scan | 校正本身變成資料外洩面 |
| CAL-13 | Public 預設使用平台 CLI OAuth＋owned-resource observation；不得因 API token 缺失阻擋已有可用平台登入的 Agent | runtime factory＋CLI default test | 驗證器比部署本身更難用，破壞一次成功目標 |
| CAL-14 | `auth_mode`、`observation_scope`、`zero_diff_level` 只能使用兩組合法組合，統計依 scope 分層且不得升級宣稱 | report schema oneOf＋aggregator invariant | owned-resource 結果被誤報為帳號級零差異 |

## test_matrix

| REQ | 驗證方式 | 測試類型 | 落點 |
|---|---|---|---|
| CAL-1 | exact set、缺一、重複 ID、未知 ID fixtures | fixture truth-table | conformance unit tests |
| CAL-2 | HTTP 200＋功能 fail、command success＋residual resource | oracle unit tests | conformance unit tests |
| CAL-3 | fixture mutation 改變 suite hash；report 含 verifier hash／revision | invariant | conformance unit tests＋schema fixtures |
| CAL-4 | dirty／unpinned source 即使 5/5 也不得 eligible | invariant | conformance unit tests＋schema condition |
| CAL-5 | 同一 suite 連跑三次比對穩定欄位 | repetition | conformance unit tests |
| CAL-6 | `run_type` 非 calibration 的 report fixture 必被拒 | schema fixture | spec self-check |
| CAL-7 | 未知敏感欄位必被 `additionalProperties: false` 拒絕 | schema fixture | spec self-check |
| CAL-8 | L1 fail 後 project executor 不啟動 | integration | batch controller（L1） |
| CAL-9 | mutation 後 CLI exit 1 | CLI unit test | conformance unit tests／CI |
| CAL-10 | success、HTTP 200 semantic fail、delete exit 0 residual | orchestrator truth-table | conformance unit tests＋sandbox |
| CAL-11 | deploy timeout-after-side-effect、identity lookup exception、跨 commit recovery、identity mismatch 不刪 | fault injection | conformance unit tests＋sandbox |
| CAL-12 | report 帶 URL／worker_name／raw_log／account_id 必被 schema 拒絕；journal 未知欄位必被 exact-key validator 拒絕 | schema＋mutation | spec self-check＋conformance unit tests |
| CAL-13 | 無 API env 仍建立 OAuth runtime；`whoami` failure 在 snapshot 前拒絕；account scope 缺 env 回 `AUTH_MISSING` | boundary＋CLI | conformance unit tests＋OAuth read-only probe |
| CAL-14 | 合法 owned/account examples 通過且 profile 必須不同；交叉組合 fixture 必被拒；recovery scope mismatch 不 delete | schema＋fault injection | spec self-check＋conformance unit tests |
| CAL-15 | snapshot transient failure 依 1s／2s 退避後成功；journal identity 缺失時，即使同名 Worker 存在也不 delete；v0.1 journal recovery 後升級且可再次 recovery | retry＋recovery boundary | conformance unit tests |
| CAL-16 | Rosetta／混合架構下不可只採信目前 Python 回報的 host arch；逐一驗證候選 Node 能實際執行固定 Wrangler，選中者的版本與架構必須進 report | compatibility boundary＋real dry-run | conformance unit tests＋local preflight |
| CAL-17 | OAuth deploy output 與 account API 回傳的 subdomain 只接受單一合法 DNS label；多餘 hostname label 不得成為 acceptance target | boundary mutation | conformance unit tests |

## 已知限制

L0 只校正「結構化判定器」；它不證明 Cloudflare 帳號、網路、CLI 或 live teardown 可用。完成 L0 只能宣稱 L0 verifier calibration。Public owned-resource L1 能放行一般 project batch，但不能推論帳號其他資源未變；其 acceptance URL 的帳號 subdomain 也只由已認證 Wrangler output 提供，未經 account-wide API 交叉驗證。需要帳號級證據強度的研究結論時，必須另跑 Judge account-snapshot L1。
