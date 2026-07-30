# 資料治理與版本政策 v0.1

> 反遙測條款是標準明文（normative），不是附錄。信任是本計畫唯一的資本：站方刻意不在金流上、統計刻意不在使用者身上。

## 反遙測條款（normative）

| ID | 條款（可判定句） | 判定方式 |
|---|---|---|
| GOV-1 | small-service-template 與所有 SmallGreen Ready 專案不得包含 phone-home／遙測程式碼；判定＝行為分析器宣告外連清單中不得出現任何統計／分析／回報用途 domain（含站方自身 domain） | 行為分析器（SAP-5）＋external_services 用途欄審查 |
| GOV-2 | 所有統計僅來自三種來源：(a) 公開 repo、(b) CI 紀錄、(c) 自願提交的 Evidence Pack。此外的資料收集管道一律不存在 | Evidence Pack schema 為唯一統計入口（EP-3 機械保證） |
| GOV-3 | **統計對象是專案，永遠不是使用者**：任何 schema、任何工具、任何報表不得含使用者識別欄位 | schema `additionalProperties: false` 全面掃描 |

前例：Debian popcon（自願制跑二十年）。反例：Audacity 2021 遙測風暴、Go 遙測改 opt-in。走前例的路。

## 資料集政策

| ID | 條款 | 判定方式 |
|---|---|---|
| GOV-4 | SmallGreen Evidence Dataset（Evidence Pack 彙總）以 CC-BY-4.0 公開＝社群公共財，任何人可查可研究 | dataset 發布物 LICENSE 檔 |
| GOV-5 | 碳計算 pipeline 與論文資料處理留計畫自有 repo——它們是資料的消費者，不是標準的一部分；spec 與 dataset 不依賴它們 | spec repo 零碳計算程式碼（目錄掃描） |
| GOV-6 | 測量欄位凍結：Evidence Pack schema 欄位刪除或語意變更＝major 版；新增欄位＝minor 版且必過欄位正當性判準（EP-4）。**數據不可回填**——舊 Pack 永不依新 schema 重寫 | semver 政策＋EP-2 append-only |

## 欄位正當性判準（收欄位的門檻）

**不做研究，社群自己也需要的欄位才進標準；純研究用途欄位不准進。** 每個欄位在 [evidence-pack.md](verification/evidence-pack.md) 的正當性表格必有「社群自身用途」一欄，缺者 PR 不可 merge。

## 版本政策（spec 全體）

- spec repo 採 semver，v0.1.x＝draft（本版）；v1.0.0＝S4 凍結
- 服務卡與 Evidence Pack 皆記錄驗證當時 spec_version；minor 落後標 stale、major 落後降級（VER-D.1）
- 條款進入標準的三防呆：每條規則對應真實發生過的故障（各檔「來源故障」欄）；契約檔由 publish agent 自動生成防官僚化；**閘太嚴要從產出端拿證據才准放寬**（非收斂預設不是閘的錯）

## test_matrix

| REQ | 驗證方式 | 測試類型 | 落點 |
|---|---|---|---|
| GOV-1 | template repo 行為分析零外連斷言（conformance 自掃，dogfooding） | invariant | template CI |
| GOV-2 | 站方基礎設施審計：目錄站無任何 analytics 收集端點 | integration | 目錄站 CI（S4） |
| GOV-3 | 全 schema 掃描：識別類欄位名清單（email／ip／device／install_id）零命中 | invariant | spec CI |
| GOV-4 | dataset LICENSE 存在性 | integration | dataset 發布 CI |
| GOV-5 | spec repo 目錄掃描零碳計算程式碼 | invariant | spec CI |
| GOV-6 | schema diff 檢查器：欄位刪除／型別變更的 PR 未升 major 必 fail | invariant | spec CI |
