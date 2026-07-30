# 契約檔規格 v0.1（.smallgreen/ 三件）

> 六件套 #2。契約檔位於 repo（或適配 repo）的 `.smallgreen/` 目錄，共三份 YAML，各配一份 JSON Schema。
> 目錄名沿革：原計畫為 `.smallapp/`，隨品牌定名改為 `.smallgreen/`（2026-07-30 定案，v0.1 起唯一有效名）。

## 設計原則

1. **wrangler 設定仍是資源宣告的唯一真相源**。契約檔不重複宣告 Workers / D1 / KV / R2——schema 刻意不提供資源宣告欄位（提供了就會有人填，就會分岔）。契約檔只補 wrangler 管不到的三層：**判定（profile）、驗收（acceptance）、維護（maintenance）**，外加 secrets manifest 與外連宣告。
2. **由 publish agent 自動生成，防官僚化**。Path B（retrofit）的契約檔由 agent 掃 repo 生成 PR，人只審不填表。
3. 欄位語意對齊既有標準（`.agent` manifest、Score spec 的 dev/ops 分離哲學），不重造已有輪子；驗收格式無既有標準可借，自創（護城河候選）。

## 三份檔案

| 檔 | 回答的問題 | Schema |
|---|---|---|
| `.smallgreen/profile.yaml` | 這是什麼、屬哪個 profile、資料流向哪、要哪些 key | [profile.schema.json](profile.schema.json) |
| `.smallgreen/acceptance.yaml` | 怎樣算部署成功（機械 smoke＋使用者驗收＋移除驗證） | [acceptance.schema.json](acceptance.schema.json) |
| `.smallgreen/maintenance.yaml` | 怎麼更新、備份、回復、監控額度、完整移除 | [maintenance.schema.json](maintenance.schema.json) |

## 條款（Requirements）

| ID | 條款（可判定句） | 判定方式 | 來源故障 |
|---|---|---|---|
| CON-1 | 三份契約檔存在且各自通過對應 JSON Schema 驗證 | YAML parse → schema validate | 無契約＝agent 只能語意推測（RedAccess 事故根源） |
| CON-2 | profile.yaml 不含資源宣告欄位（schema `additionalProperties: false` 機械保證） | schema 驗證即涵蓋 | 雙真相源分岔（自有 SecondBrain 兩路寫入撞車史） |
| CON-3 | secrets manifest 與程式碼實際引用一致：**runtime 程式碼**引用的 env/secret 名 ⊆ manifest ∪ wrangler vars（掃描範圍排除 tests/、build 工具腳本、生成的型別宣告檔；平台標準變數 NODE_ENV/CI/VITEST 等不計）。**v0.2 收斂決策（issue #2）**：framework 隱式 env 映射（Nuxt runtimeConfig 的 NUXT_* 等）維持「已知限制＋補償控制」——由 publish agent／適配者人工補列 manifest（Sink 實證可行），framework-aware 自動掃描（需 per-framework 映射表、regex 解析脆弱）列 v0.3 檢查器路線圖，不阻擋 v0.2 | 靜態掃描 env 引用 × manifest diff，宣告外引用＝fail | 「部署成功但跑不動」：缺 key 在 runtime 才爆；範圍教訓來自 S2 Sink 實測（18 個假陽性收斂到 2 個真項） |
| CON-4 | acceptance.yaml 至少含：1 個 health check、1 個 smoke test、1 個 user acceptance task、uninstall 驗證區塊 | schema required 欄位 | 「Build 成功＝部署完成」謬誤（原計畫明文反對） |
| CON-5 | maintenance.yaml 至少含：update、backup、restore、uninstall 四流程＋quota watchdog 宣告 | schema required 欄位 | Heroku 難民無遷移路徑；D1 免費層 Time Travel 有限 |
| CON-6 | 適配 repo（Path C）必含 `UPSTREAM.md` 鎖定上游 commit hash，且 profile.yaml `upstream` 欄位與之一致 | 檔案存在＋hash 格式＋兩處一致性 diff | fork 與上游差異累積失控（原計畫風險清單） |
| CON-7 | repo 內零真實 secret（契約檔本身亦受掃描） | gitleaks 規則集零命中 | 同 SAP-3 |

## test_matrix

| REQ | 驗證方式 | 測試類型 | 落點 |
|---|---|---|---|
| CON-1 | 合法／缺檔／壞 YAML／schema 違規四類 fixture | fixture truth-table | conformance CI |
| CON-2 | 帶 `d1_databases` 欄位的 profile.yaml fixture 必被 schema 拒絕 | fixture truth-table | conformance CI |
| CON-3 | fixture：程式碼引用 `env.FOO` 而 manifest 未列 → fail | fixture truth-table | conformance CI |
| CON-4 | 缺 uninstall 區塊的 acceptance fixture 必 fail | fixture truth-table | conformance CI |
| CON-5 | 缺 quota watchdog 的 maintenance fixture 必 fail | fixture truth-table | conformance CI |
| CON-6 | UPSTREAM.md hash 與 profile.yaml 不一致 fixture 必 fail | invariant（雙處一致性） | conformance CI |
| CON-7 | 同 SAP-3 | fixture truth-table | conformance CI |

三份 schema 本身的回歸測試：`schemas/examples/` 內每份 schema 至少一個 valid＋一個 invalid 範例，CI 對跑（schema 改壞會立刻紅）。
