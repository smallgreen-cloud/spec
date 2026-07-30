# 服務卡規格 v0.1

> 六件套 #3。服務卡是 registry 的原子單位：每個收錄專案一份 YAML（registry repo `cards/<id>.yaml`），目錄站只 render 不另存資料（**registry YAML＝真相源，站只是 render**）。Schema：[service-card.schema.json](service-card.schema.json)。

## 條款（Requirements）

| ID | 條款（可判定句） | 判定方式 | 來源故障 |
|---|---|---|---|
| SVC-1 | 每張服務卡通過 service-card.schema.json 驗證 | registry CI schema validate | 欄位漂移＝目錄站 render 崩壞 |
| SVC-2 | `verification.level` 晉級欄位齊備：Community Verified 需 ≥1 筆 evidence_packs＋≥1 位具名 verifier＋≥1 則 scenario_story；SmallGreen Ready 另需 agent_matrix 至少一列全自主通過＋network diff 零宣告外連＋teardown pass | registry CI 條件式 required（schema allOf） | 登錄 ≠ 審查（Smithery 事故）：等級不可宣告取得 |
| SVC-3 | `low_carbon` 欄位組由契約與 wrangler 機械推導，卡內值與推導值一致 | 推導腳本 re-derive → diff | 手填綠色宣稱＝greenwashing 風險（低碳主軸信用基石） |
| SVC-4 | `free_tier_grade` 依判定表機械判定（見下），卡內值與判定值一致 | 判定腳本 re-derive → diff | 「免費」承諾含糊＝使用者踩額度雷（FluxGate 標 D 案例） |
| SVC-5 | `verification.spec_version` 落後現行 spec minor 版以上時，卡自動標示 stale | registry 巡邏腳本比對 semver | 平台規則變動後舊驗證失效（Cloudflare 免費層變動風險） |
| SVC-6 | scenario_stories 每則標注作者與日期；AI 草稿須通過 ai-content-filter 掃描＋人工審後才可標 `reviewed: true`；未 reviewed 的故事不上目錄站 | 欄位存在性＋render 過濾 | AI 殘留字外洩（自有 quiz-quality-guard 失敗案例庫同型） |
| SVC-7 | 分類標籤 ⊆ registry `taxonomy.yaml` 現行鍵值；新類別需先滿足「滿 3 個專案才立新類」 | registry CI 引用完整性檢查 | 鬼城分類（分類是標籤不是資料夾） |
| SVC-8 | 主圖為真實截圖（Evidence Pack screenshot artifact 引用）；無 UI 服務副圖＝由 profile.yaml 自動生成的架構 SVG。禁止 mockup、禁止 AI 生圖 | 圖片來源欄位必須引用 Evidence Pack artifact 或生成器輸出 hash | demo 要真鐵律；AI 生圖傷驗證品牌可信度（目錄站設計定案） |

## free_tier_grade 判定表（SVC-4）

由 profile.yaml 機械判定，取符合條件的最低等級：

| 等級 | 條件（全部由契約欄位判定；v0.2 起 resource_usage 標 required: false 的資源不參與判級，改列 quota_note——issue #3） |
|---|---|
| A | required secrets 為空＋不需自有網域＋不必用 workers_ai |
| B | 僅缺 A 的「不需自有網域」（需綁自己的 domain） |
| C | secrets 含 required 外部 key 且該服務 free_tier: true |
| D | **必用**（required 或未標注）workers_ai 等共用額度緊資源，或任一 required key 無免費層——卡上必附 quota_watchdog 摘要 |

案例：Sink 的 AI slug 建議為選配（resource_usage: workers_ai required: false）→ v0.2 判 C 不判 D，AI 額度列 quota_note。

## low_carbon 推導規則（SVC-3）

| 欄位 | 推導 |
|---|---|
| scale_to_zero | wrangler 宣告資源全部落在 free-tier-allowlist `allowed`（全事件驅動）→ true |
| no_idle_infra | scale_to_zero 且無 always-on 外部依賴（external_services 全部為請求時呼叫）→ true |
| green_compute | wrangler cron worker 有 Green Compute 設定（帳號層屬性，Evidence Pack 回報）→ true |
| replaces_vps_estimated | 布林＋一句話情境（「此類服務傳統上需一台常開 VPS」），估算方法引用低碳方法學文件 v0.1，標明 estimated |

## test_matrix

| REQ | 驗證方式 | 測試類型 | 落點 |
|---|---|---|---|
| SVC-1 | valid／invalid 卡 fixture 對跑 | fixture truth-table | registry CI |
| SVC-2 | 三等級各一 fixture：欄位不齊必被 schema allOf 拒絕 | fixture truth-table | registry CI |
| SVC-3 | 推導腳本對 fixture 卡 re-derive，篡改 low_carbon 值必 fail | invariant（真值源往返） | registry CI |
| SVC-4 | 四等級判定表每格一個 fixture | fixture truth-table | registry CI |
| SVC-5 | 模擬 spec 升版，舊卡 stale 標示斷言 | cache/staleness（時間流逝路徑） | registry 巡邏 detector＋TG 告警 |
| SVC-6 | 未 reviewed 故事不出現在 render 輸出 | integration | registry CI |
| SVC-7 | 引用不存在 taxonomy 鍵的卡必 fail；2 個專案就立新類必 fail | invariant | registry CI |
| SVC-8 | 圖片欄位缺來源引用必 fail | fixture truth-table | registry CI |

上游活性（repo archived／license 變更／last_push 停滯）屬外部世界依賴：落點＝registry 季度巡邏 detector（per-card freshness，聚合綠燈不可掩蓋個體死亡）＋TG 告警。
