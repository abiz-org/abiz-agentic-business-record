# 透過 ABIZ 在臺灣成為代理就緒企業

*已發布的 ABIZ 1.1 規範指南。[規範（SPEC.md，英文）](../../../SPEC.md)為權威文本：本指南與規範不一致時，以規範為準。*

## 1. 這對臺灣的企業代表什麼

現在，人們常常向 AI 助理提問：「這家公司真正的官網是哪一個？」「這家店由誰經營？」ABIZ（Agentic Business Record）是一項開放標準，讓臺灣的企業只需發布一次公開資訊，就能以這些工具可讀取的形式提供：在企業自己控制的網域上新增一筆簡短的 DNS TXT 紀錄，指向透過 HTTPS 提供的 JSON 企業紀錄。由於這個指標位於企業自己的 DNS 中，工具可以確認紀錄是由該網域的控制者發布，而不必仰賴非官方目錄或猜測。

## 2. 如何發布 ABIZ 紀錄

### 必填欄位

每筆企業紀錄都需要以下五個欄位（SPEC 第 4.1 節）：

| 欄位 | 範例與規則 |
|---|---|
| `record_version` | `abiz1` |
| `business_name` | 客戶熟悉的公開名稱，例如 `臺南木作工坊有限公司` |
| `country` | `tw`，ISO 3166-1 alpha-2 代碼，小寫 |
| `identity_host` | `tainanwoodwork.tw.to.co`，必須與 DNS 中的 `h` 完全一致 |
| `domains` | `["tainanwoodwork.example"]`，必須包含放置 `_abiz` 的網域 |

### 選用的企業鍵 `k`

不論是否已登記，`k` 對所有企業都是選用的。若要發布，必須與紀錄中的 `business_key` 相同，且紀錄中也必須包含 `registration_number`。臺灣的格式為：

```text
tw-<registration-number>
```

臺灣不使用行政區代碼：請勿加入縣市等代碼。SPEC 第 4.2.2 節只要求美國、加拿大省級公司與阿拉伯聯合大公國使用行政區代碼，其他國家和地區一律禁止。

**使用哪個號碼：** 公司登記資料上的 8 位數統一編號。

**正規化（SPEC 第 4.2.3 節）：** 以登記機關核發的號碼為準，先進行 Unicode NFKC 正規化，移除空格、`-`、`.`、`/` 及各種連字號，再將字母轉為大寫。保留開頭的零與字母前綴。結果只能包含 ASCII 字母與數字；否則無法發布企業鍵，應省略 `k`、`business_key` 與 `registration_number`。

**範例（虛構）：** `12345678` 正規化後為 `12345678`，因此 `k=tw-12345678`。紀錄中寫作 `"business_key": "tw-12345678"` 與 `"registration_number": "12345678"`。比較企業鍵時不分大小寫；標準形式為國家代碼小寫、號碼大寫。

**個人經營者：** 若您只有個人號碼（例如國民身分證統一編號），請不要發布 `k`。省略 `k`、`business_key` 與 `registration_number` 後，紀錄仍然有效。

### DNS TXT 紀錄

在網域下的 `_abiz` 只發布一筆 TXT 紀錄，採用不含空格的精簡格式，並以 `v=abiz1` 開頭：

```dns
_abiz.tainanwoodwork.example. 300 IN TXT "v=abiz1;k=tw-12345678;h=tainanwoodwork.tw.to.co;p=CJhIlcaL5YorelEniC2Mf1oUFANMtNXORlxxEapcfmI="
```

上方的 `p` 值是為本頁產生的一次性範例金鑰。切勿複製：請發布您自己的金鑰。ABIZ 1.1 声明必须包含 `p`。本頁所有名稱、號碼與網域皆為虛構。

省略選用的 `k` 標籤時，以下寫法同樣有效：

```dns
_abiz.tainanwoodwork.example. 300 IN TXT "v=abiz1;h=tainanwoodwork.tw.to.co;p=CJhIlcaL5YorelEniC2Mf1oUFANMtNXORlxxEapcfmI="
```

以 `application/json` 形式在 `https://tainanwoodwork.tw.to.co` 提供的企業紀錄：

```json
{
  "record_version": "abiz1",
  "business_name": "\u81fa\u5357\u6728\u4f5c\u5de5\u574a\u6709\u9650\u516c\u53f8",
  "country": {
    "code": "TW",
    "name": "Taiwan"
  },
  "business_key": "tw-12345678",
  "registration_number": "12345678",
  "identity_host": "tainanwoodwork.tw.to.co",
  "domains": [
    "tainanwoodwork.example"
  ],
  "public_key": "CJhIlcaL5YorelEniC2Mf1oUFANMtNXORlxxEapcfmI=",
  "signature": "jktHerFdQHkeiLP+jPXPURZTyVQMIPJQAtTGaBJhot/wtl3JB3CHLQUiy1iWedfbwm5o2dUng+faLp1nwVwpBQ=="
}
```

發布前若要檢查紀錄，可在本儲存庫的副本中執行參考驗證器：

```sh
python scripts/validate.py record.json --domain tainanwoodwork.example --dns-value 'v=abiz1;k=tw-12345678;h=tainanwoodwork.tw.to.co;p=CJhIlcaL5YorelEniC2Mf1oUFANMtNXORlxxEapcfmI='
```

您可以在任何 HTTPS 伺服器上自行託管 JSON 紀錄，也可以使用任何相容的服務商。ABIZ 不要求特定服務商。

## 3. 使用服務商與 MCP

模型情境協定（Model Context Protocol，MCP）是一項開放協定，讓 AI 助理以標準方式呼叫外部伺服器上的工具並讀取資料。企業紀錄可包含選用欄位 `mcp_server_url`，也就是企業 MCP 伺服器的 HTTPS 網址，例如用於預約或產品資訊。ABIZ 不為該伺服器擔保，工具必須自行實施存取控制（SPEC 第 4.2.6 節）。

服務商可以代您託管紀錄並發布 DNS 指標。例如，一家在臺灣登記、由 to.co 託管紀錄的公司可以使用主機名稱 `tainanwoodwork.tw.to.co`，對應的 DNS 值為 `v=abiz1;k=tw-12345678;h=tainanwoodwork.tw.to.co;p=CJhIlcaL5YorelEniC2Mf1oUFANMtNXORlxxEapcfmI=`。未登記的商家可以使用含地名的主機名稱，例如 `tainanwoodwork-tainan.biz.to.co`。任何相容的服務商或您自己的伺服器都以相同方式運作。

## 4. 金鑰與簽章（ABIZ 1.1）

ABIZ 1.1 要求簽章金鑰。DNS 中的 `p` 標籤存放 Ed25519 公鑰：32 個原始位元組，標準 base64，44 個字元，結尾一個 `=`（SPEC 第 3.3.2 節）。不接受 base64url。企業或代表企業的服務商保管對應的私鑰，並用它簽署企業紀錄。私鑰始終屬於企業，託管服務商必須允許企業匯出私鑰。

- `v` 與 `h` 為必填。`p` 為必填。`k` 為選用。`p` 必須是有效金鑰；其他任何值，例如十六進位字串或 base64url 金鑰，都會使整筆聲明無效。
- 只發布目前的金鑰。輪換時，產生新的 Ed25519 金鑰對，在 DNS 或 well-known 聲明中發布新公鑰，用新私鑰重新簽署企業紀錄，並使 `public_key` 與該 `p` 相同。請考慮 DNS 快取與傳播。在 ABIZ 1.1 聲明仍然存在時，僅刪除 `p` 不是有效撤銷：要撤回聲明，須刪除完整的 DNS 或 well-known 聲明。在 ABIZ 1.1 中，已停用的金鑰既不在 DNS 中發布，也不在企業紀錄中發布。
- 金鑰顯示誰控制該網域的 DNS，並不證明法律身分。

## 5. AI 工具會看到什麼

讀取您紀錄的相容工具可以回答以下問題：

1. 臺南木作工坊有限公司的官方網站是哪一個？
2. 哪些網域屬於這家企業？
3. 企業提供的登記號碼是什麼？屬於哪個國家或地區？
4. 提供哪些服務？營業時間為何？

**限制：** ABIZ 呈現的是網域控制者發布的內容。它無法證明企業已依法登記、號碼真實，也不代表任何 AI 服務、政府機關或服務商的背書。在重要情況下，工具與使用者都應查詢官方登記資料。

## 6. 在地實務說明

- **登記機關：** 經濟部商業發展署（公司登記）；登記資料可在商工行政資料開放平臺查詢。 官方網站：<https://gcis.nat.gov.tw>.
- **新增 TXT 紀錄：** 在網域註冊商或 DNS 服務商的 DNS 設定中，新增名稱為 `_abiz` 的 TXT 紀錄（部分控制台需要完整名稱，例如 `_abiz.yourdomain.com.tw`），填入上方的值，TTL 設為 300 秒。`.com.tw` 網域與 `.com` 等其他網域用法相同。盡量不要拆分該值，`p` 絕不能拆分。
- **個人資料保護：** 《個人資料保護法》。 ABIZ 紀錄是公開的。只發布您願意公開的企業資訊，不要發布私人住址或個人電話號碼（SPEC 第 4.3 節）。

## 7. 延伸閱讀

- [ABIZ 規格（SPEC.md，英文）](../../../SPEC.md)
- [企業紀錄 JSON Schema](../../../schemas/abiz-business-record-v1.1.schema.json)
- [參考驗證器](../../../scripts/validate.py)
- [ABIZ 國家和地區指南：亞洲](index.md)
