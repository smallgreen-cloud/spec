# SmallGreen Spec

> 小型雲端服務的部署標準 | The deployment standard for small, green, self-owned cloud services.

**Status: v0.1.0 — 六件套齊備；Evidence Pack schema 已凍結（2026-07-30 簽核）**

## 這是什麼

SmallGreen Spec 定義「一個小型開源專案如何被安全地部署成使用者自己帳號裡的 serverless 服務（GitHub＋Cloudflare 免費額度）」的完整標準：部署前判定、部署驗收、長期維護、以及可稽核的驗證證據。

核心原則：

1. **沒有 validator 的條款不進標準**——寫得出檢查器的才是規範，寫不出的是建議。每條 requirement 有唯一 ID 且可判定；每份 spec 文件必含 test_matrix 章節（requirement × 測試類型 × 落點），矩陣即 conformance 實作的 RED 清單
2. **Agent 是導遊不是裁判**——引導用跨 CLI 的 AGENTS.md，每一關的綠燈由機械驗證判定
3. **統計對象是專案，永遠不是使用者**——範本與已驗證專案不得包含任何遙測程式碼
4. **wrangler 設定仍是資源宣告的唯一真相源**——契約檔（`.smallgreen/`）只補判定、驗收、維護三層

## 六件套（Spec Stack v0.1）

| # | 元件 | 文件 | ID 前綴 |
|---|---|---|---|
| 1 | Profile 判定規則 | [profiles/small-app-profile.md](profiles/small-app-profile.md)／[profiles/pipeline-profile.md](profiles/pipeline-profile.md)＋[free-tier-allowlist.yaml](profiles/free-tier-allowlist.yaml) | SAP／PIP |
| 2 | 契約檔 schema（`.smallgreen/` 三件） | [schemas/contract.md](schemas/contract.md)＋[profile](schemas/profile.schema.json)／[acceptance](schemas/acceptance.schema.json)／[maintenance](schemas/maintenance.schema.json) | CON |
| 3 | 服務卡 schema（含低碳欄位組） | [schemas/service-card.md](schemas/service-card.md)＋[service-card.schema.json](schemas/service-card.schema.json) | SVC |
| 4 | 三級驗證＋Evidence Pack | [verification/levels.md](verification/levels.md)＋[evidence-pack.md](verification/evidence-pack.md)＋[evidence-pack.schema.json](verification/evidence-pack.schema.json) | VER／EP |
| 5 | 裁判層 MCP 介面規格（12 工具） | [judge/mcp-interface.md](judge/mcp-interface.md) | JDG |
| 6 | 部署狀態機 | [state-machine/deployment-state-machine.md](state-machine/deployment-state-machine.md) | SM |
| — | 資料治理與版本政策 | [GOVERNANCE.md](GOVERNANCE.md) | GOV |

三級驗證：**Discovered → Community Verified → SmallGreen Ready**

三條套用路徑：**A** 新專案用 [small-service-template](https://github.com/smallgreen-cloud/small-service-template)／**B** 既有專案由 publish agent 生成契約檔 PR／**C** 外部專案建適配 repo（UPSTREAM.md 鎖 commit，徽章掛 registry 不掛上游）。

## 可執行載體（S1 已上線）

- [`conformance`](https://github.com/smallgreen-cloud/conformance)——檢查腳本＋reusable GitHub Actions workflow：契約 schema、免費層允許清單、secrets 掃描、secrets manifest 一致性、migration 空庫重放、本地 smoke。各檔 test_matrix 的「conformance CI」落點由它實現
- [`small-service-template`](https://github.com/smallgreen-cloud/small-service-template)——起手式範本，用它建的專案天生合規（其 CI 即 conformance 的活體驗證）

## 相關 repo

- [`registry`](https://github.com/smallgreen-cloud/registry) — 已驗證服務目錄與服務卡
- [`conformance`](https://github.com/smallgreen-cloud/conformance) — conformance 檢查腳本與 reusable workflow
- [`small-service-template`](https://github.com/smallgreen-cloud/small-service-template) — 天生合規的起手式範本

## Green software

本標準將 GSF 三活動落為可檢核屬性：能源效率（scale-to-zero）、碳感知（Green Compute）、硬體效率（共享多租戶）；量測對齊 SCI（ISO/IEC 21031:2024）。驗證統計以 CC 授權公開為 SmallGreen Evidence Dataset（見 [GOVERNANCE.md](GOVERNANCE.md)）。

---

發起：Alan Chen（[cooperation.tw](https://cooperation.tw)）。License：規格文件 CC-BY-4.0／程式碼與機器可讀資產 Apache-2.0（見 [LICENSE.md](LICENSE.md)，2026-07-30 定案）。
