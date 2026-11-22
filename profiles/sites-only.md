# Sites-only 靜態判定

2026-11-23 補充 SAP-1／SAP-2／CON-3。問題來源是 PetMCP runtime `ed20ee8f` 已由原生 Sites 部署，但 conformance `82600612` 只接受 Wrangler。此分支不變更既有 Cloudflare 專案的規則。

## 宣告與資源

1. repo 有 `.smallgreen/install.yaml` 或 `.openai/hosting.json` 就必須驗證 Sites 宣告，兩者缺一即 fail，不能退回 Wrangler。
2. install 必須通過 `schemas/install.schema.json`，包含鎖定來源、`chatgpt-work`／`sites`／`native-sites` 與空的 external_infrastructure。
3. hosting 必須通過 `schemas/sites-hosting.schema.json`。這是依 OpenAI Sites plugin 1.1.7 的官方 skill／storage／app-integrations 宣告整理的保守子集，不冒充完整平台 API schema；新增平台欄位需更新 Spec、測試及維護者核對。
4. 公開模板可省略 project_id；部署時由原生 Sites 回傳並保存。這個靜態檢查不查帳號、建立資源或證明發布成功。
5. 實際集合為 site，加上非 null 的 d1／r2；必須與 install.hosting.managed_resources 完全一致。綁定名稱可自訂，但不能重複。MCP 是 capability，不是額外託管資源。
6. 非生成物、非依賴目錄內任何深度的 Wrangler 設定都拒絕；alt_deployment 必須為空。Sites 編譯器產生的 dist/server/wrangler.json 是打包 metadata，不能當成自架來源，也不能拿來取代原生 manifest。
7. plugins／connectors 是 Sites 原生整合宣告，不等於另外建立基礎設施；靜態 schema 通過不證明插件資格、使用者同意或線上權限。

## Runtime 名稱與建置邊界

CON-3 的名稱來源是 profile.secrets、已驗證 Sites manifest 的 d1/r2 名稱，以及既有的標準平台變數。Sites 檢查必須提供 `--spec`，不在檢查器內猜一份寬鬆 manifest。

根目錄 vite.config.js／mjs／cjs／ts／mts／cts 是建置入口，不掃作 runtime；例如 app/vite.config.ts 不享有排除。這不驗證任意 import graph，建置工具的 runtime 重用仍需人工審查。既有 tests、scripts、生成型別與建置目錄排除保留。

Sites 1.1.7 的 worker/index.ts 使用可信 ctx.props.CONNECTORS；env.CONNECTORS 只出現在受 DEV 條件保護的預覽橋接。此版本的精確 SHA-256 為 `a0a10229cdda6f5fdb32234e3539007412233bb4938a671866c9295a44a3bdb6`。僅當路徑、整檔指紋及 Sites 宣告都匹配，才排除其中的 CONNECTORS 引用。更動 guard、增加程式或其他檔案引用同名 env 都不豁免。未知 starter 版本需審查，不能直接把 CONNECTORS 加入全域白名單。

此掃描沿用 literal env.NAME／process.env.NAME 的靜態範圍；動態索引、別名與 framework 隱式映射仍需人工補償審查，不能聲稱完整程式資料流分析。

## 證據界線

SAP-1／SAP-2／CON-3 通過只代表這些靜態要求通過，不代表免費方案可部署、完整 conformance、原生 Voice、手機、第二真實帳號或 teardown 已通過。Sites teardown 使用平台受管資源證據，不要求使用者登入 Cloudflare；平台若無法提供清單或移除證據，zero-diff 保持 blocked。
