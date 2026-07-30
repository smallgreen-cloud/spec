# SmallGreen Spec

> 小型雲端服務的部署標準 | The deployment standard for small, green, self-owned cloud services.

**Status: v0.1 draft — under construction**

## 這是什麼

SmallGreen Spec 定義「一個小型開源專案如何被安全地部署成使用者自己帳號裡的 serverless 服務（GitHub＋Cloudflare 免費額度）」的完整標準：部署前判定、部署驗收、長期維護、以及可稽核的驗證證據。

核心原則：

1. **沒有 validator 的條款不進標準**——寫得出檢查器的才是規範，寫不出的是建議。每條 requirement 有唯一 ID 且可判定；每份 spec 文件必含 test_matrix 章節（requirement × 測試類型 × 落點），矩陣即 conformance 實作的 RED 清單
2. **Agent 是導遊不是裁判**——引導用跨 CLI 的 AGENTS.md，每一關的綠燈由機械驗證判定
3. **統計對象是專案，永遠不是使用者**——範本與已驗證專案不得包含任何遙測程式碼
4. **wrangler 設定仍是資源宣告的唯一真相源**——契約檔只補判定、驗收、維護三層

## 六件套（Spec Stack）

| # | 元件 | 目錄（規劃中） |
|---|---|---|
| 1 | Profile 判定規則（Small App / Pipeline 兩檔） | `profiles/` |
| 2 | 契約檔 schema（profile / acceptance / maintenance） | `schemas/` |
| 3 | 服務卡 schema（含低碳欄位組） | `schemas/` |
| 4 | 三級驗證與 Evidence Pack 格式 | `verification/` |
| 5 | 裁判層 MCP 介面規格 | `judge/` |
| 6 | 部署狀態機 | `state-machine/` |

三級驗證：**Discovered → Community Verified → SmallGreen Ready**

## 相關 repo

- [`registry`](https://github.com/smallgreen-cloud/registry) — 已驗證服務目錄與服務卡
- [`small-service-template`](https://github.com/smallgreen-cloud/small-service-template) — 天生合規的起手式範本

## Green software

本標準將 GSF 三活動落為可檢核屬性：能源效率（scale-to-zero）、碳感知（Green Compute）、硬體效率（共享多租戶）；量測對齊 SCI（ISO/IEC 21031:2024）。驗證統計以 CC 授權公開為 SmallGreen Evidence Dataset。

---

發起：Alan Chen（[cooperation.tw](https://cooperation.tw)）。License：待定（spec 文件傾向 CC-BY-4.0，程式碼傾向 Apache-2.0，v0.1 凍結前定案）。
