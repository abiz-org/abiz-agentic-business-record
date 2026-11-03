# ABIZで日本のエージェンティック・ビジネスになる

*ABIZ 1.1（提案）の解説です。正本は[仕様書（SPEC.md、英語）](../../../SPEC.md)であり、本ガイドと仕様書が異なる場合は仕様書が優先します。*

## 1. 日本の事業者にとっての意味

AIアシスタントには「この会社の本物のウェブサイトはどれか」「この店を運営しているのは誰か」といった質問が日常的に寄せられています。ABIZ（Agentic Business Record）は、日本の事業者が公開情報を一度だけ、こうしたツールが読める形で公開できるオープンな標準です。事業者が管理するドメインに短いDNS TXTレコードを置き、HTTPSで提供されるJSON形式の事業者レコードを指し示します。ポインタは事業者自身のDNSにあるため、ツールは非公式なディレクトリや推測に頼らず、そのドメインの管理者がレコードを公開したことを確認できます。

## 2. ABIZレコードの公開方法

### 必須項目

すべての事業者レコードには次の5項目が必要です（SPEC 4.1節）。

| 項目 | 例と規則 |
|---|---|
| `record_version` | `abiz1` |
| `business_name` | 顧客に知られている公開名。例：`株式会社山田製作所` |
| `country` | `jp`（ISO 3166-1 alpha-2コード、小文字） |
| `identity_host` | `yamadaseisakusho.jp.to.co`。DNSの`h`と完全に一致する必要があります |
| `domains` | `["yamadaseisakusho.example"]`。`_abiz`を置くドメインを含める必要があります |

### 任意のビジネスキー`k`

`k`は、登記の有無にかかわらず、すべての事業者にとって任意です。公開する場合は、レコードの`business_key`と一致させ、レコードに`registration_number`も含めます。日本での形式は次のとおりです。

```text
jp-<registration-number>
```

日本では下位区分を使いません。都道府県や市区町村のコードは付けないでください。SPEC 4.2.2節が下位区分を求めるのは米国、カナダの州法人、アラブ首長国連邦だけで、それ以外の国では禁止されています。

**使う番号：** 国税庁が指定する13桁の法人番号です。法務局の会社法人等番号や、漢数字で書かれた番号ではありません（SPEC 4.2.2節）。全角数字で書かれていても、NFKCで半角の0–9になります。

**正規化（SPEC 4.2.3節）：** 登録機関が発行したとおりの番号から始め、Unicode NFKC正規化を適用し、空白、`-`、`.`、`/`、各種ダッシュを取り除き、英字を大文字にします。先頭のゼロや英字の接頭辞は残します。結果はASCIIの英字と数字だけでなければなりません。そうでない場合はビジネスキーを公開できないため、`k`、`business_key`、`registration_number`を省略します。

**例（架空）：** `１２３４５６７８９０１２３`は`1234567890123`になり、`k=jp-1234567890123`です。レコードでは`"business_key": "jp-1234567890123"`、`"registration_number": "1234567890123"`とします。キーは大文字小文字を区別せずに比較され、正規形は国コードが小文字、番号が大文字です。

**個人事業主の方へ：** お持ちの番号がマイナンバー（個人番号）など個人の番号だけの場合は、`k`を公開しないでください。`k`、`business_key`、`registration_number`を省略しても、レコードは有効です。

### DNS TXTレコード

ドメインの`_abiz`に、TXTレコードを1件だけ、空白のない簡潔な形式で、`v=abiz1`を先頭にして公開します。

```dns
_abiz.yamadaseisakusho.example. 300 IN TXT "v=abiz1;k=jp-1234567890123;h=yamadaseisakusho.jp.to.co;p=VU6KejF2F+CJuIW2OcrK4opUygzruzVdY8gwysWAqSE="
```

上の`p`の値は、このページ用に生成した使い捨ての例示用鍵です。決してコピーしないでください。自分の鍵を公開してください。ABIZ 1.1のアサーションには`p`が必要です。このページの名称、番号、ドメインはすべて架空のものです。

任意の`k`を省いた次の形も有効です。

```dns
_abiz.yamadaseisakusho.example. 300 IN TXT "v=abiz1;h=yamadaseisakusho.jp.to.co;p=VU6KejF2F+CJuIW2OcrK4opUygzruzVdY8gwysWAqSE="
```

`https://yamadaseisakusho.jp.to.co`で`application/json`として提供する事業者レコード：

```json
{
  "record_version": "abiz1",
  "business_name": "株式会社山田製作所",
  "country": "jp",
  "business_key": "jp-1234567890123",
  "registration_number": "1234567890123",
  "identity_host": "yamadaseisakusho.jp.to.co",
  "domains": [
    "yamadaseisakusho.example"
  ],
  "public_key": "VU6KejF2F+CJuIW2OcrK4opUygzruzVdY8gwysWAqSE=",
  "signature": "ZAuaWYREub6XOo88Iqmqxyozitn4yZCeNY0mub467bCweNt8hX5UANfX33z1FJRVIRUA8vb5eKIRC0fhKC5yAw=="
}
```

公開前にレコードを確認するには、このリポジトリのコピーで参照用バリデーターを実行します。

```sh
python scripts/validate.py record.json --domain yamadaseisakusho.example --dns-value 'v=abiz1;k=jp-1234567890123;h=yamadaseisakusho.jp.to.co;p=VU6KejF2F+CJuIW2OcrK4opUygzruzVdY8gwysWAqSE='
```

JSONレコードは任意のHTTPSサーバーで自分でホストしても、互換性のある任意のプロバイダーを使っても構いません。ABIZは特定のプロバイダーを必要としません。

## 3. プロバイダーとMCPの利用

Model Context Protocol（MCP）は、AIアシスタントが外部サーバーのツールを呼び出したりデータを読んだりするための、標準化されたオープンなプロトコルです。事業者レコードには任意で`mcp_server_url`（事業者のMCPサーバーのHTTPS URL。予約や商品情報などに使います）を含められます。ABIZはそのサーバーを保証しません。ツール側で独自のアクセス制御を行う必要があります（SPEC 4.2.6節）。

プロバイダーにレコードのホスティングとDNSポインタの公開を任せることもできます。たとえば、to.coでレコードをホストする日本の登記済み法人なら、ホスト`yamadaseisakusho.jp.to.co`を使い、DNSの値は`v=abiz1;k=jp-1234567890123;h=yamadaseisakusho.jp.to.co;p=VU6KejF2F+CJuIW2OcrK4opUygzruzVdY8gwysWAqSE=`になります。未登記の事業者なら、`yamadaseisakusho-osaka.biz.to.co`のような地名を含むホストを使うこともできます。互換性のある他のプロバイダーや自社サーバーでも同じように機能します。

## 4. 鍵と署名（ABIZ 1.1）

ABIZ 1.1では署名鍵が必須です。DNSの`p`タグには、Ed25519公開鍵（32バイトの生データ、標準base64、44文字、末尾の`=`は1つ）を入れます（SPEC 3.3.2節）。base64urlは受け付けません。事業者、またはその代理のプロバイダーが対応する秘密鍵を保管し、その鍵で事業者レコードに署名します。秘密鍵は常に事業者のものであり、ホスティング事業者は事業者が鍵をエクスポートできるようにしなければなりません。

- `v`と`h`は必須です。`p`は必須です。`k`は任意です。`p`は有効な鍵でなければなりません。ABIZ 1.0の古い16進トークンやbase64urlの鍵など、それ以外の値があるとアサーション全体が無効になります。
- 公開するのは現在の鍵だけです。ローテーションでは、新しいEd25519鍵対を生成し、新しい公開鍵をDNSまたはwell-knownのアサーションに公開し、新しい秘密鍵で事業者レコードに再署名し、`public_key`をその`p`と一致させます。DNSキャッシュと伝播を見込んでください。ABIZ 1.1のアサーションを残したまま`p`だけを削除することは、有効な失効ではありません。撤回するには、DNSまたはwell-knownの宣言全体を削除します。ABIZ 1.1では、退役した鍵はDNSにも事業者レコードにも公開しません。
- 鍵が示すのはドメインのDNSを誰が管理しているかであり、法的な身元を証明するものではありません。

## 5. AIツールに見えること

レコードを読む互換ツールは、たとえば次のような質問に答えられます。

1. 株式会社山田製作所の公式ウェブサイトはどれですか？
2. この事業者のドメインはどれですか？
3. 事業者が示す登録番号は何で、どの国のものですか？
4. 何を提供していて、営業時間はいつですか？

**限界：** ABIZが示すのは、ドメインの管理者が公開した内容です。事業者が法的に登記されていること、番号が本物であること、AIサービスや行政機関、プロバイダーが推薦していることを証明するものではありません。重要な場面では、ツールも人も公式の登録情報を確認してください。

## 6. 国内での実務メモ

- **登録機関：** 国税庁の法人番号公表サイト（法人番号の指定・公表）。会社の登記は法務局が行います。 公式サイト：<https://www.houjin-bangou.nta.go.jp>.
- **TXTレコードの追加：** レジストラーまたはDNSホスティングのDNS設定で、名前`_abiz`（管理画面によっては`_abiz.yourdomain.jp`のような完全な名前）、上記の値、TTL 300秒のTXTレコードを追加します。`.jp`ドメインも`.com`など他のドメインと同じです。値はなるべく分割せず、`p`は決して分割しないでください。
- **個人情報：** 個人情報の保護に関する法律（個人情報保護法）。 ABIZレコードは公開情報です。共有してよい事業情報だけを載せ、自宅住所や個人の電話番号は載せないでください（SPEC 4.3節）。

## 7. 参考資料

- [ABIZ仕様書（SPEC.md、英語）](../../../SPEC.md)
- [事業者レコードのJSONスキーマ](../../../schemas/abiz-business-record-v1.1.schema.json)
- [参照用バリデーター](../../../scripts/validate.py)
- [ABIZ国別ガイド：アジア](index.md)
