# 借助 ABIZ 在中国成为智能体就绪企业

*ABIZ 1.1（提案）指南。[规范（SPEC.md，英文）](../../../SPEC.md)为权威文本：本指南与规范不一致时，以规范为准。*

## 1. 这对中国的企业意味着什么

如今，人们常常向 AI 助手提问：“这家公司真正的官网是哪个？”“这家店由谁经营？”ABIZ（Agentic Business Record）是一项开放标准，让中国的企业只需发布一次公开信息，就能以这些工具可读的形式提供：在企业自己控制的域名上添加一条简短的 DNS TXT 记录，指向通过 HTTPS 提供的 JSON 企业记录。由于该指针位于企业自己的 DNS 中，工具可以确认记录是由该域名的控制者发布的，而不必依赖非官方目录或猜测。

## 2. 如何发布 ABIZ 记录

### 必填字段

每条企业记录都需要以下五个字段（SPEC 第 4.1 节）：

| 字段 | 示例与规则 |
|---|---|
| `record_version` | `abiz1` |
| `business_name` | 客户熟知的公开名称，例如 `杭州青山茶业有限公司` |
| `country` | `cn`，ISO 3166-1 alpha-2 代码，小写 |
| `identity_host` | `qingshantea.cn.to.co`，必须与 DNS 中的 `h` 完全一致 |
| `domains` | `["qingshantea.example"]`，必须包含放置 `_abiz` 的域名 |

### 可选的企业键 `k`

无论是否登记注册，`k` 对所有企业都是可选的。如发布，它必须与记录中的 `business_key` 相同，且记录中还必须包含 `registration_number`。中国的格式为：

```text
cn-<registration-number>
```

中国不使用行政区划代码：请勿添加省、市等代码。SPEC 第 4.2.2 节仅要求美国、加拿大省级公司和阿拉伯联合酋长国使用区划代码，其他国家和地区一律禁止。

**使用哪个号码：** 营业执照上的 18 位统一社会信用代码（GB 32100-2015）。它在全国唯一，不需要省份代码（SPEC 第 4.2.2 节）。

**规范化（SPEC 第 4.2.3 节）：** 以登记机关签发的号码为准，先做 Unicode NFKC 规范化，去掉空格、`-`、`.`、`/` 和各类连字符，再把字母转为大写。保留前导零和字母前缀。结果只能包含 ASCII 字母和数字；否则无法发布企业键，应省略 `k`、`business_key` 和 `registration_number`。

**示例（虚构）：** `91330100MA2ABCDE1X` 规范化后为 `91330100MA2ABCDE1X`，因此 `k=cn-91330100MA2ABCDE1X`。记录中写作 `"business_key": "cn-91330100MA2ABCDE1X"` 和 `"registration_number": "91330100MA2ABCDE1X"`。比较企业键时不区分大小写；规范形式为国家代码小写、号码大写。

**个体经营者：** 如果您只有个人号码（例如居民身份证号码），请不要发布 `k`。省略 `k`、`business_key` 和 `registration_number` 后，记录仍然有效。

### DNS TXT 记录

在域名下的 `_abiz` 处只发布一条 TXT 记录，采用不含空格的紧凑格式，并以 `v=abiz1` 开头：

```dns
_abiz.qingshantea.example. 300 IN TXT "v=abiz1;k=cn-91330100MA2ABCDE1X;h=qingshantea.cn.to.co;p=YZq8jSTakRCOmsX/AWZzKRXDi9TCHjrnkarDdiDQHoI="
```

上面的 `p` 值是为本页生成的一次性示例密钥。切勿复制：请发布您自己的密钥，或省略 `p`。本页中的所有名称、号码和域名均为虚构。

省略可选的 `k` 和 `p` 标签时，以下写法同样有效：

```dns
_abiz.qingshantea.example. 300 IN TXT "v=abiz1;h=qingshantea.cn.to.co;p=YZq8jSTakRCOmsX/AWZzKRXDi9TCHjrnkarDdiDQHoI="
```

以 `application/json` 形式在 `https://qingshantea.cn.to.co` 提供的企业记录：

```json
{
  "record_version": "abiz1",
  "business_name": "杭州青山茶业有限公司",
  "country": "cn",
  "business_key": "cn-91330100MA2ABCDE1X",
  "registration_number": "91330100MA2ABCDE1X",
  "identity_host": "qingshantea.cn.to.co",
  "domains": [
    "qingshantea.example"
  ],
  "public_key": "YZq8jSTakRCOmsX/AWZzKRXDi9TCHjrnkarDdiDQHoI=",
  "signature": "q7X5wXRHY1Pprasl9bCpK9oZWTPkDRZQJQPCgPhlkuJeMCMgSRqDPhOMcQge31uW3Q7buB5dA9ETUKif0NcWAg=="
}
```

发布前如需检查记录，可在本仓库的副本中运行参考验证器：

```sh
python scripts/validate.py record.json --domain qingshantea.example --dns-value 'v=abiz1;k=cn-91330100MA2ABCDE1X;h=qingshantea.cn.to.co;p=YZq8jSTakRCOmsX/AWZzKRXDi9TCHjrnkarDdiDQHoI='
```

您可以在任何 HTTPS 服务器上自行托管 JSON 记录，也可以使用任何兼容的服务商。ABIZ 不要求使用特定服务商。

## 3. 使用服务商与 MCP

模型上下文协议（Model Context Protocol，MCP）是一种开放协议，让 AI 助手以标准方式调用外部服务器上的工具并读取数据。企业记录可包含可选字段 `mcp_server_url`，即企业 MCP 服务器的 HTTPS 地址，例如用于预约或产品信息。ABIZ 不为该服务器作担保，工具必须自行实施访问控制（SPEC 第 4.2.6 节）。

服务商可以替您托管记录并发布 DNS 指针。例如，一家在中国登记、由 to.co 托管记录的公司可以使用主机名 `qingshantea.cn.to.co`，对应的 DNS 值为 `v=abiz1;k=cn-91330100MA2ABCDE1X;h=qingshantea.cn.to.co;p=YZq8jSTakRCOmsX/AWZzKRXDi9TCHjrnkarDdiDQHoI=`。未登记的商户可以使用含地名的主机名，例如 `qingshantea-hangzhou.biz.to.co`。任何兼容的服务商或您自己的服务器都以同样方式工作。

## 4. 密钥与签名（ABIZ 1.1）

ABIZ 1.1 新增了可选的签名密钥。DNS 中的 `p` 标签可以存放 Ed25519 公钥：标准 base64 编码的 44 个字符，以一个 `=` 结尾（SPEC 第 3.3.2 节）。企业或代表企业的服务商保管对应的私钥，可以签署他人用已发布公钥验证的内容。私钥始终归企业所有，托管服务商必须允许企业导出私钥。

- `p` 是可选的。一旦出现，必须是有效密钥；任何其他值，例如 ABIZ 1.0 旧的十六进制令牌或 base64url 密钥，都会使整条声明无效。
- 只发布当前密钥。更换时，在 `p` 中发布新密钥；撤销时，删除 `p`。在 ABIZ 1.1 中，已停用的密钥既不在 DNS 中发布，也不在企业记录中发布。
- 密钥表明谁控制该域名的 DNS，并不证明法律身份。

## 5. AI 工具会看到什么

读取您记录的兼容工具可以回答以下问题：

1. 杭州青山茶业有限公司的官方网站是哪个？
2. 哪些域名属于这家企业？
3. 企业提供的登记号码是什么？属于哪个国家或地区？
4. 提供哪些服务？营业时间如何？

**局限：** ABIZ 展示的是域名控制者发布的内容。它不能证明企业已依法登记、号码真实，也不代表任何 AI 服务、政府机构或服务商的认可。在重要场合，工具和用户都应查询官方登记信息。

## 6. 本地实用说明

- **登记机关：** 国家市场监督管理总局及各地市场监督管理部门（企业登记）；登记信息可在国家企业信用信息公示系统查询。 由于无法确认可正常访问的官方网址，此处未列出网站。
- **添加 TXT 记录：** 在域名注册商或 DNS 服务商的 DNS 设置中，添加一条名称为 `_abiz` 的 TXT 记录（部分控制面板需要填写完整名称，如 `_abiz.yourdomain.cn`），填入上面的值，TTL 设为 300 秒。`.cn` 域名与 `.com` 等其他域名用法相同。尽量不要拆分该值，`p` 绝不能拆分。
- **个人信息保护：** 《中华人民共和国个人信息保护法》。 ABIZ 记录是公开的。只发布您愿意公开的企业信息，不要发布私人住址或个人电话号码（SPEC 第 4.3 节）。

## 7. 延伸阅读

- [ABIZ 规范（SPEC.md，英文）](../../../SPEC.md)
- [企业记录 JSON Schema](../../../schemas/abiz-business-record-v1.schema.json)
- [参考验证器](../../../scripts/validate.py)
- [ABIZ 国家和地区指南：亚洲](index.md)
