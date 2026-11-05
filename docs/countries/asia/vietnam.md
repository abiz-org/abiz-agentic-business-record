# Trở thành doanh nghiệp sẵn sàng cho tác tử AI với ABIZ tại Việt Nam

*Hướng dẫn cho ABIZ 1.1 (đặc tả đã công bố). [Đặc tả (SPEC.md, tiếng Anh)](../../../SPEC.md) là văn bản có giá trị quyết định: nếu hướng dẫn này khác với đặc tả, áp dụng đặc tả.*

## 1. Ý nghĩa đối với doanh nghiệp tại Việt Nam

Ngày nay, trợ lý AI thường được hỏi “trang web thật của công ty này là trang nào?” hay “ai đang điều hành cửa hàng này?”. ABIZ (Agentic Business Record) là một tiêu chuẩn mở cho phép doanh nghiệp tại Việt Nam công bố thông tin công khai của mình một lần, theo dạng mà các công cụ đó đọc được: một bản ghi DNS TXT ngắn trên tên miền do doanh nghiệp kiểm soát, trỏ tới hồ sơ doanh nghiệp định dạng JSON được cung cấp qua HTTPS. Vì con trỏ nằm trong DNS của chính doanh nghiệp, công cụ có thể xác định hồ sơ do người kiểm soát tên miền công bố, thay vì dựa vào danh bạ không chính thức hay phỏng đoán.

## 2. Cách công bố bản ghi ABIZ

### Các trường bắt buộc

Mọi hồ sơ doanh nghiệp đều cần năm trường sau (SPEC mục 4.1):

| Trường | Ví dụ và quy tắc |
|---|---|
| `record_version` | `abiz1` |
| `business_name` | tên công khai mà khách hàng biết, ví dụ `Công ty TNHH Gốm Bát Tràng` |
| `country` | `vn`, mã ISO 3166-1 alpha-2, viết thường |
| `identity_host` | `gombattrang.vn.to.co`, phải trùng khớp hoàn toàn với `h` trong DNS |
| `domains` | `["gombattrang.example"]`, phải gồm tên miền chứa `_abiz` |

### Khóa doanh nghiệp tùy chọn `k`

`k` là tùy chọn với mọi doanh nghiệp, dù đã đăng ký hay chưa. Nếu công bố, giá trị phải bằng `business_key` trong hồ sơ, và khi đó hồ sơ cũng phải có `registration_number`. Với Việt Nam, dạng thức là:

```text
vn-<registration-number>
```

Việt Nam không dùng mã đơn vị hành chính: không thêm mã tỉnh hay thành phố. SPEC mục 4.2.2 chỉ yêu cầu mã đơn vị con với Hoa Kỳ, các công ty cấp tỉnh của Canada và Các Tiểu vương quốc Ả Rập Thống nhất, và cấm dùng ở mọi quốc gia khác.

**Dùng số nào:** mã số doanh nghiệp gồm 10 chữ số, đồng thời là mã số thuế của doanh nghiệp.

**Chuẩn hóa (SPEC mục 4.2.3):** bắt đầu từ số đúng như cơ quan đăng ký cấp, áp dụng chuẩn hóa Unicode NFKC, bỏ khoảng trắng, `-`, `.`, `/` và các dấu gạch, rồi chuyển chữ cái sang chữ hoa. Giữ nguyên số 0 ở đầu và tiền tố chữ. Kết quả chỉ được chứa chữ cái và chữ số ASCII; nếu không, không thể công bố khóa doanh nghiệp và phải bỏ `k`, `business_key` và `registration_number`.

**Ví dụ (giả định):** `0123456789` trở thành `0123456789`, vậy `k=vn-0123456789`. Trong hồ sơ: `"business_key": "vn-0123456789"` và `"registration_number": "0123456789"`. Khóa được so sánh không phân biệt chữ hoa, chữ thường; dạng chuẩn là mã quốc gia viết thường và số viết hoa.

**Hộ kinh doanh và cá nhân kinh doanh:** nếu số duy nhất bạn có là số cá nhân, như số định danh cá nhân hoặc mã số thuế cá nhân, đừng công bố `k`. Bỏ `k`, `business_key` và `registration_number`; hồ sơ vẫn hợp lệ.

### Bản ghi DNS TXT

Công bố đúng một bản ghi TXT tên `_abiz` dưới tên miền của bạn, ở dạng gọn không có khoảng trắng, với `v=abiz1` đứng đầu:

```dns
_abiz.gombattrang.example. 300 IN TXT "v=abiz1;k=vn-0123456789;h=gombattrang.vn.to.co;p=fMQgbgcrGsnI8EysdkbKP8G6nluwm6Y124UYPNKGSMk="
```

Giá trị `p` ở trên là khóa ví dụ dùng một lần được tạo cho trang này. Tuyệt đối không sao chép: hãy công bố khóa của riêng bạn. Khai báo ABIZ 1.1 phải có `p`. Mọi tên, số và tên miền trên trang này đều là giả định.

Không có thẻ tùy chọn `k`, bản ghi này cũng hợp lệ:

```dns
_abiz.gombattrang.example. 300 IN TXT "v=abiz1;h=gombattrang.vn.to.co;p=fMQgbgcrGsnI8EysdkbKP8G6nluwm6Y124UYPNKGSMk="
```

Hồ sơ doanh nghiệp được cung cấp dưới dạng `application/json` tại `https://gombattrang.vn.to.co`:

```json
{
  "record_version": "abiz1",
  "business_name": "C\u00f4ng ty TNHH G\u1ed1m B\u00e1t Tr\u00e0ng",
  "country": {
    "code": "VN",
    "name": "Vietnam"
  },
  "business_key": "vn-0123456789",
  "registration_number": "0123456789",
  "identity_host": "gombattrang.vn.to.co",
  "domains": [
    "gombattrang.example"
  ],
  "public_key": "fMQgbgcrGsnI8EysdkbKP8G6nluwm6Y124UYPNKGSMk=",
  "signature": "3pNnqnuf/YuB8f7pYYCfq2olKfRSOAQssBx/YJo4C1P8ZQ1fNFCxtmCVVBLprFQkpJGKW/OUwML/vE5pOPT9CQ=="
}
```

Để kiểm tra hồ sơ trước khi công bố, hãy chạy trình xác thực tham chiếu từ một bản sao của kho mã này:

```sh
python scripts/validate.py record.json --domain gombattrang.example --dns-value 'v=abiz1;k=vn-0123456789;h=gombattrang.vn.to.co;p=fMQgbgcrGsnI8EysdkbKP8G6nluwm6Y124UYPNKGSMk='
```

Bạn có thể tự lưu trữ hồ sơ JSON trên bất kỳ máy chủ HTTPS nào, hoặc dùng bất kỳ nhà cung cấp tương thích nào. ABIZ không bắt buộc một nhà cung cấp cụ thể.

## 3. Dùng nhà cung cấp và MCP

Model Context Protocol (MCP) là giao thức mở cho phép trợ lý AI gọi công cụ và đọc dữ liệu từ máy chủ bên ngoài theo cách chuẩn hóa. Hồ sơ doanh nghiệp có thể có trường tùy chọn `mcp_server_url`, là địa chỉ HTTPS của máy chủ MCP của doanh nghiệp, ví dụ để đặt chỗ hoặc xem thông tin sản phẩm. ABIZ không bảo đảm cho máy chủ đó; công cụ phải tự áp dụng kiểm soát truy cập (SPEC mục 4.2.6).

Nhà cung cấp có thể lưu trữ hồ sơ và công bố con trỏ DNS thay bạn. Ví dụ, một công ty đã đăng ký tại Việt Nam có hồ sơ lưu trên to.co có thể dùng máy chủ `gombattrang.vn.to.co`, cho giá trị DNS `v=abiz1;k=vn-0123456789;h=gombattrang.vn.to.co;p=fMQgbgcrGsnI8EysdkbKP8G6nluwm6Y124UYPNKGSMk=`. Hộ kinh doanh chưa đăng ký có thể dùng máy chủ theo tên thành phố như `gombattrang-hanoi.biz.to.co`. Mọi nhà cung cấp tương thích, hoặc máy chủ của riêng bạn, đều hoạt động theo cùng một cách.

## 4. Khóa và chữ ký (ABIZ 1.1)

ABIZ 1.1 yêu cầu khóa ký. Thẻ DNS `p` mang khóa công khai Ed25519: 32 byte thô, base64 chuẩn, 44 ký tự, một dấu `=` ở cuối (SPEC mục 3.3.2). Không chấp nhận base64url. Doanh nghiệp, hoặc nhà cung cấp thay mặt doanh nghiệp, giữ khóa bí mật tương ứng và ký hồ sơ doanh nghiệp bằng khóa đó. Khóa bí mật luôn thuộc về doanh nghiệp, và nhà cung cấp lưu trữ phải cho phép doanh nghiệp xuất khóa.

- `v` và `h` là bắt buộc. `p` là bắt buộc. `k` là tùy chọn. `p` phải là một khóa hợp lệ: mọi giá trị khác, như một chuỗi thập lục phân hay khóa base64url, đều làm toàn bộ khai báo mất hiệu lực.
- Chỉ công bố khóa hiện hành. Để xoay khóa, tạo cặp khóa Ed25519 mới, công bố khóa công khai mới trong khai báo DNS hoặc well-known, ký lại hồ sơ bằng khóa bí mật mới, và đặt `public_key` trùng `p` đó. Hãy tính đến bộ nhớ đệm DNS. Xóa riêng `p` không phải là thu hồi hợp lệ khi khai báo ABIZ 1.1 vẫn còn: để rút khai báo, hãy xóa toàn bộ khai báo DNS hoặc well-known. Trong ABIZ 1.1, khóa đã ngừng dùng không được công bố, cả trong DNS lẫn trong hồ sơ doanh nghiệp.
- Khóa cho biết ai kiểm soát DNS của tên miền. Khóa không chứng minh danh tính pháp lý.

## 5. Công cụ AI sẽ thấy gì

Một công cụ tương thích đọc hồ sơ của bạn có thể trả lời những câu hỏi như:

1. Trang web chính thức của Công ty TNHH Gốm Bát Tràng là gì?
2. Những tên miền nào thuộc doanh nghiệp này?
3. Doanh nghiệp ghi mã số đăng ký nào, ở quốc gia nào?
4. Doanh nghiệp cung cấp gì và mở cửa khi nào?

**Giới hạn:** ABIZ cho thấy những gì người kiểm soát tên miền đã công bố. Nó không chứng minh doanh nghiệp được đăng ký hợp pháp, mã số là thật, hay bất kỳ dịch vụ AI, cơ quan nhà nước hoặc nhà cung cấp nào xác nhận doanh nghiệp đó. Khi cần thiết, công cụ và người dùng nên tra cứu cơ sở dữ liệu đăng ký chính thức.

## 6. Ghi chú thực tế tại địa phương

- **Cơ quan đăng ký:** Cổng thông tin quốc gia về đăng ký doanh nghiệp. Trang chính thức: <https://dangkykinhdoanh.gov.vn>.
- **Thêm bản ghi TXT:** trong phần cài đặt DNS của nhà đăng ký tên miền hoặc nhà cung cấp DNS, thêm một bản ghi TXT tên `_abiz` (một số bảng điều khiển yêu cầu tên đầy đủ, `_abiz.tenmien.vn`), với giá trị ở trên và TTL 300 giây. Tên miền `.vn` hoạt động giống `.com` hay bất kỳ tên miền nào khác. Cố gắng không tách giá trị, và tuyệt đối không tách `p`.
- **Dữ liệu cá nhân:** Nghị định 13/2023/NĐ-CP về bảo vệ dữ liệu cá nhân và Luật Bảo vệ dữ liệu cá nhân năm 2025. Hồ sơ ABIZ là công khai. Chỉ công bố thông tin doanh nghiệp mà bạn sẵn lòng chia sẻ, và không đưa địa chỉ nhà riêng hay số điện thoại cá nhân (SPEC mục 4.3).

## 7. Tài liệu tham khảo

- [Đặc tả ABIZ (SPEC.md, tiếng Anh)](../../../SPEC.md)
- [JSON Schema của hồ sơ doanh nghiệp](../../../schemas/abiz-business-record-v1.1.schema.json)
- [Trình xác thực tham chiếu](../../../scripts/validate.py)
- [Hướng dẫn ABIZ theo quốc gia: Châu Á](index.md)
