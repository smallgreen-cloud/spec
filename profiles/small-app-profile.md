# Small App Profile v0.1（判定規則）

> 六件套 #1a。判定「一個 repo 是否為可在 Cloudflare 免費額度內、由使用者自己帳號一鍵部署的小型服務」。
> 形式＝判定腳本：輸入 repo → pass / fail ＋逐條原因。本文件是該腳本的規格；**沒有 validator 的條款不進本檔**。

## 適用範圍

- 執行環境：Cloudflare 免費層 only（資源允許清單見 [free-tier-allowlist.yaml](free-tier-allowlist.yaml)）
- 目標使用者：1–10 人私人服務
- 超出範圍時判定輸出固定措辭：「不符合 Small App Profile」＋逐條 fail 原因，不延伸評估其他平台

## 條款（Requirements）

每條可判定、有唯一 ID。「來源故障」欄對應真實發生過的事故（防呆規則：沒有真實故障對應的條款不收）。

| ID | 條款（可判定句） | 判定方式 | 來源故障 |
|---|---|---|---|
| SAP-1 | repo 根目錄存在可解析的 wrangler 設定（wrangler.jsonc / wrangler.toml / wrangler.json 其一） | 檔案存在＋parse 成功 | 無 wrangler＝無法宣告式部署（Deploy Button 前提） |
| SAP-2 | wrangler 宣告的全部資源落在 free-tier-allowlist.yaml `allowed` 清單內 | 解析 wrangler keys × 允許清單 diff，宣告外 key＝fail＋列名 | Heroku/Glitch 難民：付費資源綁定＝免費承諾破產 |
| SAP-3 | runtime 所需 secrets 全數列於 `.smallgreen/profile.yaml` 的 secrets manifest，且 repo 內零真實 secret | manifest 存在性＋secret 掃描（gitleaks 規則集）零命中 | RedAccess 掃描 400 組外洩金鑰；自有 pre-commit hook 踩雷史 |
| SAP-4 | repo 不含常駐程序基礎設施檔（Dockerfile、docker-compose.yml、Procfile、k8s manifest） | 檔案清單掃描零命中 | 範圍紀律：VPS/容器不支援（計畫核心定位） |
| SAP-5 | 程式碼 outbound 網路目標全數被 profile.yaml `external_services` 宣告涵蓋 | 行為分析器（靜態掃描＋沙盒動態攔截）diff 零宣告外 domain | Smithery 抽查 22/100 有安全問題；README 與實際行為不符 |
| SAP-6 | repo 具 OSI-approved license（GitHub API license 欄位非空且非 NOASSERTION） | gh api 查詢 | registry batch-01：9 項無 license 專案無法安全複製 |
| SAP-7 | 照 AGENTS.md 標準流程部署，使用者確認次數 ≤ 3 | agent matrix 驗證紀錄 human_interventions ≤ 3 | 原計畫成功條件「主要確認不超過三次」 |
| SAP-8 | 具備完整移除路徑：maintenance.yaml 定義 uninstall 步驟，執行後 CF 帳號資源歸零 | teardown 後 wrangler/API 資源清單與部署前 diff 為空 | Audacity 式信任危機的反面：退得乾淨才敢裝 |

低碳屬性（scale_to_zero / no_idle_infra）不是獨立條款：由 SAP-2 允許清單機械推導（清單內資源全部事件驅動），推導規則見 [service-card.md](../schemas/service-card.md)。

## 判定輸出格式

```json
{
  "profile": "small-app",
  "spec_version": "0.1.0",
  "result": "pass | fail",
  "checks": [
    {"id": "SAP-1", "result": "pass"},
    {"id": "SAP-2", "result": "fail", "reasons": ["queues 不在允許清單"]}
  ]
}
```

SAP-5、SAP-7 依賴部署期產物（行為分析器報告、agent matrix），靜態判定時標 `pending`，不阻擋 Discovered 收錄，但阻擋 SmallGreen Ready。

## test_matrix

| REQ | 驗證方式 | 測試類型 | 落點 |
|---|---|---|---|
| SAP-1 | fixture repo（有/無/壞格式 wrangler）三向判定正確 | fixture truth-table | conformance CI |
| SAP-2 | 每個 allowlist 成員一個正樣本＋每個 excluded 成員一個負樣本（加成員必加樣本） | fixture truth-table | conformance CI |
| SAP-3 | 含假 token 的 fixture 必 fail；乾淨 repo 必 pass | fixture truth-table | conformance CI |
| SAP-4 | 含 Dockerfile 的 fixture 必 fail | fixture truth-table | conformance CI |
| SAP-5 | 沙盒跑 acceptance suite，實測外連 vs 宣告 diff＝0 | invariant（宣告外 domain＝紅燈 fail-closed） | conformance CI＋每輪驗證 |
| SAP-6 | gh api license 欄位斷言 | integration | conformance CI＋registry 季度巡邏 detector（license 可能被移除） |
| SAP-7 | agent matrix 每輪記錄 human_interventions，>3＝fail | invariant | 驗證 harness（每輪驗證即測試執行） |
| SAP-8 | teardown 後資源清單 diff 斷言為空；殘留＝fail＋列名 | invariant（真值源往返：裝→拆→歸零） | 驗證 harness 每輪必跑 |

外部世界依賴（Cloudflare 免費額度變動、GitHub API 行為）落點為 registry 季度巡邏＋allowlist `verified_at` 過期告警，不假設「會一直正常」。
