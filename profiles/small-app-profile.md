# Small App Profile v0.1（判定規則）

> 六件套 #1a。判定小型個人服務的宣告式部署邊界。既有 Cloudflare 免費層與明確選擇的 ChatGPT Sites-only 分開判定。
> 形式＝判定腳本：輸入 repo → pass / fail ＋逐條原因。本文件是該腳本的規格；**沒有 validator 的條款不進本檔**。

## 適用範圍

- 未宣告 Sites：沿用 Cloudflare 免費層規則（[free-tier-allowlist.yaml](free-tier-allowlist.yaml)）。
- 存在 `.smallgreen/install.yaml` 或 `.openai/hosting.json`：進入 [Sites-only 靜態規則](sites-only.md)，必須同時驗證兩份宣告；壞宣告不得回退 Wrangler。Sites 資格及費用依使用者方案，不套用 Cloudflare 免費層承諾。
- 目標使用者：1–10 人私人服務
- 超出範圍時判定輸出固定措辭：「不符合 Small App Profile」＋逐條 fail 原因，不延伸評估其他平台

## 條款（Requirements）

每條可判定、有唯一 ID。「來源故障」欄對應真實發生過的事故（防呆規則：沒有真實故障對應的條款不收）。

| ID | 條款（可判定句） | 判定方式 | 來源故障 |
|---|---|---|---|
| SAP-1 | Wrangler 路徑：至少一份可解析設定，根或子目錄深度 ≤3，所有找到的設定均可解析。Sites-only 路徑：install 與 hosting manifest 同時存在，分別通過 install.schema.json 與 sites-hosting.schema.json | 依明確宣告分流；缺檔、壞格式、錯誤 target/schema 均 fail | 2026-11-22 PetMCP 已原生部署卻被無 Wrangler 判失敗；保留既有 monorepo 規則 |
| SAP-2 | Wrangler 路徑：全部設定資源落在 free-tier-allowlist，條件式資源符合條件。Sites-only 路徑：僅 Site 與 manifest 所列 D1/R2，安裝契約資源集合完全相符、external_infrastructure 為空、無獨立 Wrangler 來源設定或 alt_deployment | 依託管模式驗資源；Sites 不以額外 Cloudflare／BYOC 補通過 | 保留免費層邊界，避免將 Sites 受管資源誤認為使用者自架資源 |
| SAP-3 | runtime 所需 secrets 全數列於 `.smallgreen/profile.yaml` 的 secrets manifest，且 repo 內零真實 secret | manifest 存在性＋secret 掃描（gitleaks 規則集）零命中 | RedAccess 掃描 400 組外洩金鑰；自有 pre-commit hook 踩雷史 |
| SAP-4 | v0.2（issue #4）：常駐程序基礎設施檔（Dockerfile、docker-compose.yml、Procfile）**存在時必須在 profile.yaml `alt_deployment` 揭露**且 CF 免費層路徑（wrangler）獨立完整；存在且未揭露＝fail。適配 repo 亦可以 patch 移除 | 檔案掃描 × alt_deployment 欄位交叉比對 | 範圍紀律：VPS/容器不支援；一刀切誤傷選配替代路徑（S2 UptimeFlare Dockerfile 實測，v0.2 精修） |
| SAP-5 | 程式碼 outbound 網路目標全數被 profile.yaml `external_services` 宣告涵蓋。v0.2（issue #1）：宣告分三類（kind）——fixed 直接 diff 比對；user-directed（目標由使用者輸入決定，如連結預覽）驗「不夾帶服務憑證、不打宣告外固定 domain」；user-configured（webhook 類）驗「預設關閉」。非 fixed 類需人工裁決背書。範圍限自動發出的請求，HTML 內 `<a href>` 點擊連結不屬之（S2 Counterscale verifier 口徑假陽性教訓） | 行為分析器（靜態掃描＋沙盒動態攔截）diff；kind 分類驗證 | Smithery 抽查 22/100 有安全問題；Sink 連結預覽（域名不可枚舉）實測 |
| SAP-6 | repo 具 OSI-approved license（GitHub API license 欄位非空且非 NOASSERTION） | gh api 查詢 | registry batch-01：9 項無 license 專案無法安全複製 |
| SAP-7 | 照 AGENTS.md 標準流程部署，使用者確認次數 ≤ 3 | agent matrix 驗證紀錄 human_interventions ≤ 3 | 原計畫成功條件「主要確認不超過三次」 |
| SAP-8 | maintenance.yaml 定義完整 uninstall；Wrangler 路徑驗 CF 資源歸零，Sites-only 驗該 Site 的平台受管資源歸零，不能改走獨立 CF | 依原生託管模式取得 teardown 前後清單；不可觀測則 blocked，不以靜態通過替代 | Audacity 式信任危機的反面：退得乾淨才敢裝 |

Wrangler 路徑的低碳屬性（scale_to_zero / no_idle_infra）由 SAP-2 允許清單推導，規則見 [service-card.md](../schemas/service-card.md)。Sites 靜態通過不代表免費額度、低碳屬性、平台實測或 SmallGreen Ready；其資格與 teardown 依 Sites 證據分別判定。

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
| SAP-1 | Wrangler 三向 fixture；Sites 有效／缺檔／壞格式／錯 target／舊 Spec 必須正確判定 | fixture truth-table | conformance CI |
| SAP-2 | 既有 allowlist 正負樣本；Sites 資源不符、未知 key、重複 binding、BYOC、深層 Wrangler、alt_deployment 必拒；生成物不當作獨立來源 | fixture truth-table | conformance CI |
| SAP-3 | 含假 token 的 fixture 必 fail；乾淨 repo 必 pass | fixture truth-table | conformance CI |
| SAP-4 | 含 Dockerfile 的 fixture 必 fail | fixture truth-table | conformance CI |
| SAP-5 | 沙盒跑 acceptance suite，實測外連 vs 宣告 diff＝0 | invariant（宣告外 domain＝紅燈 fail-closed） | conformance CI＋每輪驗證 |
| SAP-6 | gh api license 欄位斷言 | integration | conformance CI＋registry 季度巡邏 detector（license 可能被移除） |
| SAP-7 | agent matrix 每輪記錄 human_interventions，>3＝fail | invariant | 驗證 harness（每輪驗證即測試執行） |
| SAP-8 | teardown 後資源清單 diff 斷言為空；殘留＝fail＋列名 | invariant（真值源往返：裝→拆→歸零） | 驗證 harness 每輪必跑 |

外部世界依賴（Cloudflare 免費額度變動、GitHub API 行為）落點為 registry 季度巡邏＋allowlist `verified_at` 過期告警，不假設「會一直正常」。
