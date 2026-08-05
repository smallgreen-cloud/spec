# 三方審查請求：一份「部署 agent 系統優化」設計提案

你是獨立審查者。**不要讀取檔案系統、不要探索目錄**——只根據下面的內容作答。**請盡量反駁，不要護航。**

## 背景（你需要知道的前情）

一個定義「AI agent 如何把開源專案部署到使用者自己的 Cloudflare 免費帳號」的規格，已跑了 37 次真實部署（11 個第三方專案）。前一輪三方審查判定：該規格**沒有**提高部署成功率（有契約 11/12、無契約 12/12），也沒縮短耗時（中位 14 vs 16 分）；唯一有證據的效果是「第三方能重現移除程序」。規格定位已下修為「候選 conformance profile」。

主持人的要求是：**不要再做治理面的事，要真正優化這個部署 agent 系統與標準，讓部署能更完整地成功。**

下面這份提案是對該要求的回應。它宣稱找到了「為什麼契約沒有提高成功率」的機制性原因，並提出四個機制。

## 你要審查的提案全文

# 提案：環境層——契約瞄錯層次，40% 的卡點宣告不掉

> 狀態：設計提案（未進 spec）｜依據：86 筆卡點事件（E01-E86）逐筆分類｜2026-08-05
> 背景：三方審查判定「契約沒有提高部署成功率」（11/12 vs 12/12）。本提案回答**為什麼**，以及**要加什麼才會有**。

## 一、問題：契約宣告 repo，但失敗來自環境

86 筆卡點事件逐筆讀完後的分類：

| 類別（失敗分類法） | 事件數 | 標準現況 |
|---|---:|---|
| TOOL（工具鏈行為） | 21 | 契約無條款 |
| PLATACCT（平台帳號狀態） | 19 | 契約無條款 |
| REPO（上游 repo 缺陷） | 19 | **adapter patch＋AGENTS.md 已處理** |
| 其餘（AGENTRES／UX／ASSET／BUILD／CFCOMPAT…） | 27 | 部分 |

契約三檔（profile／acceptance／maintenance）＋AGENTS.md 的作用對象是**上游 repo**：它把 README 沒寫的部署知識補齊、把上游的缺陷用 patch 補上。這對 REPO 類 19 筆有效，也確實是 adapter 存在的理由。

**但 TOOL＋PLATACCT 合計 38 筆（44%）不在 repo 上。** 它們是：這個帳號有沒有開 R2、這把 token 有沒有 Vectorize 權限、今天的 AI 額度還剩多少、本機這版 wrangler 的 `subdomain` 子命令還在不在、`pnpm 10` 會不會攔截 `deploy`。**沒有任何一份放在 repo 裡的契約能宣告掉這些**，因為它們每次執行都不一樣。

這就是「為什麼把幾個標準拼湊起來，卻沒辦法讓部署更完整地成功」的機制性答案：**拼湊起來的那幾個標準，全都是描述 artifact 的；沒有一個描述執行環境。**

## 二、四個機制（依覆蓋事件數×跨專案廣度排序）

逐筆歸因後，34 筆可被四個機制涵蓋（另 2 筆為 agent harness 自身限制，非標準可管）。

### 機制 A：環境前置探針｜11 筆事件，橫跨 7 個專案

**問題形態**：部署跑到一半（或跑完）才發現環境根本不具備。
實例：AE 未啟用（E01）／workers.dev 子網域未註冊（E02）／R2 未啟用（E21、E31、E55）／token 無 Vectorize 權限（E43）／PAT 缺 Actions Secrets 權限（E27）／本機無 terraform（E28）／AI 額度已耗盡（E84）／`compatibility_date` 超過本機 wrangler runtime 上限（E06）。

**代價不對稱**：探針 30 秒；白跑一輪部署＋驗收是 8-30 分鐘，而且像 E84 那種當日額度耗盡是**不可重試**的。

**設計**：契約增設 `environment.probes[]`，在 clone／build **之前**執行。

```yaml
environment:
  probes:
    - id: r2-enabled
      run: |
        curl -sf -X POST "$CF_API/accounts/$CF_ACCOUNT_ID/r2/buckets" \
          -H "Authorization: Bearer $CF_TOKEN" -d '{"name":"sg-probe"}'
      expect: success == true          # 或 error_code not_in [10042]
      on_fail: degrade                 # block | degrade | warn
      degrade_to: kv-only              # 對應 profile 宣告的降級模式
      attribution: environment         # 不歸因為專案缺陷
      reason: "帳號未啟用 R2（10042），僅 dashboard 可開"
```

**三個設計要點**（每一個都來自實測）：

1. **`on_fail` 三態是核心**，不是 pass/fail。R2 未啟用打到四個專案（imgbed／microfeed／r2-explorer／second-brain 的 Vectorize 同型），其中 E42 是 agent **自行想出**乾淨降級、E52 是上游 `r2BucketExists` 前置檢查直接中止全流程。**降級路徑該由專案事先宣告，不該由 agent 臨場發明**——臨場發明的結果不可重現，也就無法驗收。
2. **`attribution: environment` 把歸因寫進資料**。目前 PLATACCT 造成的失敗會被記成該專案的失敗，服務卡因此懲罰了專案。帳號沒開 R2 不是專案的缺陷。
3. **探針必須無副作用**（`validate-before-scale` 已有此紀律）：驗生效看回應欄位，不要送真實形狀的請求賭它會被擋掉。

### 機制 E：工具行為知識庫｜8 筆事件，橫跨 6 個專案

**問題形態**：某個工具的某個版本有某個怪行為，每個 adapter 各自重新踩、各自寫進自己的 AGENTS.md。

實例（全部來自實測）：

| 工具×版本 | 行為 | 事件 |
|---|---|---|
| wrangler ≥4.54 | `subdomain` 子命令已移除；API 動詞 POST 回 10405 | E13 |
| wrangler 4.114 ＋ `secrets.required` | 對不存在的 worker 拒絕「先 deploy 再 secret put」順序 | E66 |
| wrangler pages deploy | detached HEAD 下失敗 | E11 |
| wrangler 4.71／REST | queue endpoint 無 backlog 欄位（契約假設的證據路徑不存在） | E65 |
| pnpm ≥10 | 內建 `deploy` 指令攔截同名 script | E40 |
| npm 11 | `prepare` hook 未留產物 | E63 |
| Rosetta x64 node | lockfile 選中 darwin-64 binary，workerd optional 套件不完整 | E72 |
| 上游 `pre.sh` | 硬依賴 wget（macOS 預設無）；cfstore 對 python UA 回 403 | E34 |

**設計**：conformance repo 維護 `tool-traps.yaml`，以 `(tool, version_range, command)` 為鍵，preflight 時比對本機實際版本後把命中的條目注入 agent context。

```yaml
- tool: pnpm
  version_range: ">=10"
  trigger: "package.json scripts 含 deploy"
  trap: "pnpm 10 的內建 deploy 指令會攔截同名 script（ERR_PNPM_CANNOT_DEPLOY）"
  workaround: "改用 pnpm run deploy"
  evidence: E40（pastebin-worker）
```

**這是唯一會複利的機制**：每個 run 踩到的新陷阱變成一條記錄，之後每個 run 免費受益。目前這些知識散在 10 份 AGENTS.md 的前置段落裡，跨專案不流通——`serverless-dns` 學到的 wget 陷阱，`microfeed` 用不到。

這正是 `agentic-systems` 的「交付迴圈不是補丁」在**工具鏈層**的落地：現在的做法是每案寫補丁，該做的是讓系統把補丁蒸餾成共用知識。

### 機制 C：效果斷言｜5 筆事件，橫跨 4 個專案

**問題形態**：**指令回 exit 0，但根本沒做到。**

| 事件 | 指令 | 實際 |
|---|---|---|
| E05 | `wrangler d1 delete` | 非互動下靜默失敗，D1 仍在 |
| E38 | `wrangler delete`（worker＋queue） | 雙雙靜默失敗；真因是 Worker 為 Queue consumer 需先刪 consumer（10064） |
| E36 | `bun install` | exit 0 但靜默漏裝 1 套件（CDN 404 重試後）→ 首次部署才 TS2307 |
| E45 | wrangler auto-provision | 中途失敗不把資源 ID 寫回 wrangler.jsonc → 重跑撞 already exists（10014） |
| E78 | `r2 bucket delete` | 桶內有物件時回 10008，SOP 缺清桶步驟 |

E05 與 E38 **只被 teardown 的歸零 diff 碰巧抓到**；E36 與 E45 是到下一步才爆。**exit code 不是效果的證據。**

**設計**：任何改變狀態的生命週期指令，契約必須宣告它應產生的可觀察後置條件，由 harness 斷言。

```yaml
uninstall:
  steps:
    - cmd: npx wrangler d1 delete <name> --yes
      assert: { probe: "d1 list", not_contains: "<name>" }
```

這條同時是 `automation.md`「沉默失敗＝設計缺陷」的契約層版本。

### 機制 D＋B：非互動不變量與 settle 語意｜8 筆，已部分在 #14／#16

**D 的關鍵修正**：非互動不是「加 `--yes`」。E54 實測 CLI 的 `--yes` **不涵蓋資源名稱與 admin path 的互動提示**，stdin `/dev/null` 即中止；E70 是測試 fail 後程序不退出撞工具上限。可判定的寫法是——**以 stdin `</dev/null` 執行，斷言不 hang 且輸出無提示字串**，而不是檢查旗標存在。

**B**：`settle: {max_wait_s, retry_interval_s, transient_codes[]}`（E03 TLS 3-5 分、E14 CDN 快取 500、E15 edge 1042、E25 secret 傳播 401）。不形式化，agent 就把暫態記成失敗。

## 三、誠實的效果邊界

四個機制涵蓋 32 筆（37%）。**它們不保證部署成功率上升**——A 類的多數情況（帳號沒開 R2）本來就不可能成功，探針只是讓失敗**快 20 分鐘、原因具體、且歸因正確**。真正可能提高成功率的只有 E（工具陷阱不再重踩）與 C（錯誤狀態當場抓到而非累積）。

**應該宣稱的**：把「跑很久之後失敗、原因模糊、歸因給專案」變成「30 秒內拒絕、原因具體、歸因給環境」，以及讓工具層的教訓跨專案複利。

**不應該宣稱的**：讓部署更常成功。現有資料不支持，加了這四層也不會自動支持——要宣稱就得再跑一輪對照。

## 四、與現有條款的關係

- **不新增平行機制**：A 與 D 擴充 v0.3.0 已建立的 `build_requirements`＋CON-8／CON-9（前置宣告＋乾淨環境閘＋宣告完整性對帳），語義從「本機建置」擴到「執行環境」
- **C 擴充 `maintenance.yaml` 的 `uninstall.steps`**（現只有 cmd，增 assert）
- **E 是新元件**，落點在 conformance repo 而非 spec（它是資料不是條款；spec 只需一條「preflight 必須比對工具行為知識庫」）
- 每條新欄位**必須同批附檢查器**——CON-9 的教訓是「宣告了但沒人驗」等於沒宣告

## 五、實作順序

1. **A 的最小版**：`environment.probes[]` schema ＋ preflight 執行器 ＋ 三個真實探針（R2／Vectorize／Workers AI 額度，皆已有可用指令）。這三個涵蓋 A 類 11 筆中的 7 筆
2. **C**：`uninstall.steps[].assert` ＋ teardown 時逐步斷言（現有歸零 diff 保留為最後一道）
3. **E**：`tool-traps.yaml` 起手式，先把上表 8 條入庫；preflight 比對本機 `wrangler --version`／`pnpm --version`／`node -v`
4. **D／B**：併入 #14／#16 導入

## 六、資料出處

全部事件見 smallgreen-research `datasets/stuck-events.csv`（E01-E86）；分類與跨專案統計的重生指令記於本提案 commit message。分類本身是人工判讀，**未經第三方複核**——若要用於對外宣稱，需比照驗收出處核實的做法外派複分類。

---

## 請你回答（各 150-350 字，直接下判斷，不要鋪陳）

1. **診斷是否成立？** 「契約宣告 repo，但 44% 的失敗來自環境，所以契約對那些無效」——這個因果推論有沒有漏洞？特別是：分類本身是人工判讀（未經第三方複核），有沒有可能是把「其實 repo 契約能處理的東西」誤分到環境類，來讓結論成立？
2. **四個機制的優先序對嗎？** 提案用「事件數×跨專案廣度」排序。這個排序準則本身有沒有問題？如果你來排，順序會不同嗎？為什麼？
3. **機制 A 的設計有沒有致命缺陷？** 特別是 `on_fail: degrade` ＋ `degrade_to`——讓專案事先宣告降級路徑，聽起來合理，但實際上會不會產生新問題（例如：宣告的降級路徑本身沒被驗證過、降級模式的組合爆炸、或者把「應該失敗」的部署變成「假成功」）？
3b. **`attribution: environment` 會不會被濫用？** 專案可以把自己的缺陷宣告成環境問題來逃避歸因嗎？要怎麼防？
4. **提案漏了什麼？** 請指出至少一個提案沒提到、但你認為對「讓部署更完整地成功」更重要的機制。不要重複提案已列的四項。
5. **誠實邊界畫得對嗎？** 提案說「四機制涵蓋 37%，但不保證成功率上升，真正可能提高成功率的只有 E 與 C」。這個自我設限是恰當、過度保守、還是仍然過度樂觀？
