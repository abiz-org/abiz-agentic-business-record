# Menjadi Bisnis Agentik dengan ABIZ di Indonesia

*Panduan untuk ABIZ 1.1 (spesifikasi yang diterbitkan). [Spesifikasi (SPEC.md, bahasa Inggris)](../../../SPEC.md) adalah acuan utama: jika panduan ini berbeda dengan spesifikasi, yang berlaku adalah spesifikasi.*

## 1. Artinya bagi pelaku usaha di Indonesia

Asisten AI kini sering mendapat pertanyaan seperti “mana situs web resmi perusahaan ini?” atau “siapa yang mengelola toko ini?”. ABIZ (Agentic Business Record) adalah standar terbuka yang memungkinkan pelaku usaha di Indonesia menerbitkan informasi publiknya cukup sekali, dalam bentuk yang dapat dibaca alat-alat tersebut: catatan DNS TXT singkat pada domain yang dikendalikan usaha itu, yang menunjuk ke catatan usaha berformat JSON yang disajikan melalui HTTPS. Karena penunjuk itu berada di DNS milik usaha sendiri, alat dapat memastikan bahwa catatan diterbitkan oleh pihak yang mengendalikan domain tersebut, alih-alih mengandalkan direktori tidak resmi atau tebakan.

## 2. Cara menerbitkan catatan ABIZ

### Kolom wajib

Setiap catatan usaha memerlukan lima kolom berikut (SPEC bagian 4.1):

| Kolom | Contoh dan aturan |
|---|---|
| `record_version` | `abiz1` |
| `business_name` | nama publik yang dikenal pelanggan, misalnya `Kopi Gayo Nusantara` |
| `country` | `id`, kode ISO 3166-1 alpha-2 dalam huruf kecil |
| `identity_host` | `kopigayo.id.to.co`, harus sama persis dengan `h` di DNS |
| `domains` | `["kopigayo.example"]`, harus memuat domain tempat `_abiz` berada |

### Kunci usaha opsional `k`

`k` bersifat opsional bagi semua usaha, baik terdaftar maupun tidak. Jika diterbitkan, nilainya harus sama dengan `business_key` di catatan, dan catatan itu juga harus memuat `registration_number`. Untuk Indonesia, bentuknya:

```text
id-<registration-number>
```

Indonesia tidak memakai kode wilayah: jangan menambahkan kode provinsi atau kota. SPEC bagian 4.2.2 hanya mewajibkan kode wilayah untuk Amerika Serikat, korporasi provinsi Kanada, dan Uni Emirat Arab, serta melarangnya di negara lain.

**Nomor yang dipakai:** Nomor Induk Berusaha (NIB) 13 digit yang diterbitkan melalui OSS.

**Normalisasi (SPEC bagian 4.2.3):** mulai dari nomor persis seperti yang diterbitkan instansi pendaftar, terapkan normalisasi Unicode NFKC, hapus spasi, `-`, `.`, `/`, dan tanda pisah, lalu ubah huruf menjadi huruf besar. Pertahankan angka nol di depan dan awalan huruf. Hasilnya hanya boleh berisi huruf dan angka ASCII; jika tidak, kunci usaha tidak dapat diterbitkan sehingga `k`, `business_key`, dan `registration_number` dihilangkan.

**Contoh (fiktif):** `1234567890123` menjadi `1234567890123`, sehingga `k=id-1234567890123`. Di catatan: `"business_key": "id-1234567890123"` dan `"registration_number": "1234567890123"`. Kunci dibandingkan tanpa membedakan huruf besar dan kecil; bentuk kanoniknya kode negara huruf kecil dan nomor huruf besar.

**Usaha perseorangan:** jika satu-satunya nomor yang Anda miliki adalah nomor pribadi, seperti NIK atau NPWP pribadi, jangan terbitkan `k`. Hilangkan `k`, `business_key`, dan `registration_number`; catatan tetap sah.

### Catatan DNS TXT

Terbitkan tepat satu catatan TXT bernama `_abiz` di bawah domain Anda, dalam bentuk ringkas tanpa spasi, dengan `v=abiz1` di depan:

```dns
_abiz.kopigayo.example. 300 IN TXT "v=abiz1;k=id-1234567890123;h=kopigayo.id.to.co;p=dtDHyDPR7tnZCIou3cFwQxGO47BW/2esmInQa/cx+8w="
```

Nilai `p` di atas adalah kunci contoh sekali pakai yang dibuat untuk halaman ini. Jangan pernah menyalinnya: terbitkan kunci Anda sendiri. Pernyataan ABIZ 1.1 wajib memuat `p`. Semua nama, nomor, dan domain di halaman ini fiktif.

Tanpa tag opsional `k`, catatan ini juga sah:

```dns
_abiz.kopigayo.example. 300 IN TXT "v=abiz1;h=kopigayo.id.to.co;p=dtDHyDPR7tnZCIou3cFwQxGO47BW/2esmInQa/cx+8w="
```

Catatan usaha yang disajikan sebagai `application/json` di `https://kopigayo.id.to.co`:

```json
{
  "record_version": "abiz1",
  "business_name": "Kopi Gayo Nusantara",
  "country": "id",
  "business_key": "id-1234567890123",
  "registration_number": "1234567890123",
  "identity_host": "kopigayo.id.to.co",
  "domains": [
    "kopigayo.example"
  ],
  "public_key": "dtDHyDPR7tnZCIou3cFwQxGO47BW/2esmInQa/cx+8w=",
  "signature": "M+wv42BVAy9MTfXecSj5ojwBgtniZuaQbof26lkKTZu418pt9mrzTp+/LK5y6lo2NmEtGP0j7uY+hXNxB5SlDQ=="
}
```

Untuk memeriksa catatan sebelum diterbitkan, jalankan validator rujukan dari salinan repositori ini:

```sh
python scripts/validate.py record.json --domain kopigayo.example --dns-value 'v=abiz1;k=id-1234567890123;h=kopigayo.id.to.co;p=dtDHyDPR7tnZCIou3cFwQxGO47BW/2esmInQa/cx+8w='
```

Anda dapat meng-host catatan JSON sendiri di server HTTPS mana pun, atau memakai penyedia mana pun yang kompatibel. ABIZ tidak mewajibkan penyedia tertentu.

## 3. Memakai penyedia dan MCP

Model Context Protocol (MCP) adalah protokol terbuka yang memungkinkan asisten AI memanggil alat dan membaca data dari server luar dengan cara yang baku. Catatan usaha dapat memuat kolom opsional `mcp_server_url`, yaitu alamat HTTPS server MCP milik usaha, misalnya untuk pemesanan atau informasi produk. ABIZ tidak menjamin server itu; alat harus menerapkan kontrol aksesnya sendiri (SPEC bagian 4.2.6).

Penyedia dapat meng-host catatan dan menerbitkan penunjuk DNS untuk Anda. Misalnya, perusahaan terdaftar di Indonesia yang catatannya di-host oleh to.co dapat memakai host `kopigayo.id.to.co`, sehingga nilai DNS-nya `v=abiz1;k=id-1234567890123;h=kopigayo.id.to.co;p=dtDHyDPR7tnZCIou3cFwQxGO47BW/2esmInQa/cx+8w=`. Usaha yang tidak terdaftar dapat memakai host berbasis nama kota seperti `kopigayo-bandung.biz.to.co`. Penyedia kompatibel lain, atau server Anda sendiri, bekerja dengan cara yang sama.

## 4. Kunci dan tanda tangan (ABIZ 1.1)

ABIZ 1.1 mewajibkan kunci penandatanganan. Tag DNS `p` memuat kunci publik Ed25519: 32 byte mentah, base64 standar, 44 karakter, satu `=` di akhir (SPEC bagian 3.3.2). Base64url tidak diterima. Usaha, atau penyedia yang bertindak atas namanya, menyimpan kunci privat pasangannya dan menandatangani catatan usaha dengannya. Kunci privat selalu milik usaha, dan penyedia hosting wajib mengizinkan usaha mengekspornya.

- `v` dan `h` wajib. `p` bersifat wajib. `k` bersifat opsional. `p` harus kunci yang sah: nilai lain, seperti token heksadesimal lama ABIZ 1.0 atau kunci base64url, membuat seluruh pernyataan tidak sah.
- Hanya kunci yang berlaku yang diterbitkan. Untuk rotasi, buat pasangan kunci Ed25519 baru, terbitkan kunci publik baru pada pernyataan DNS atau well-known, tanda tangani ulang catatan dengan kunci privat baru, dan setel `public_key` ke `p` yang sama. Perhitungkan cache DNS. Menghapus hanya `p` bukan pencabutan yang sah selama pernyataan ABIZ 1.1 tetap ada: untuk menariknya, hapus seluruh pernyataan DNS atau well-known. Di ABIZ 1.1, kunci yang sudah dipensiunkan tidak diterbitkan, baik di DNS maupun di catatan usaha.
- Kunci menunjukkan siapa yang mengendalikan DNS domain. Kunci tidak membuktikan identitas hukum.

## 5. Apa yang akan dilihat alat AI

Alat kompatibel yang membaca catatan Anda dapat menjawab pertanyaan seperti:

1. Apa situs web resmi Kopi Gayo Nusantara?
2. Domain mana saja milik usaha ini?
3. Nomor pendaftaran apa yang dicantumkan usaha ini, dan di negara mana?
4. Apa yang ditawarkan, dan kapan buka?

**Batasan:** ABIZ menunjukkan apa yang diterbitkan pengendali sebuah domain. ABIZ tidak membuktikan bahwa usaha terdaftar secara sah, bahwa nomornya asli, atau bahwa layanan AI, instansi pemerintah, atau penyedia mana pun mendukungnya. Bila penting, alat dan orang sebaiknya memeriksa daftar resmi.

## 6. Catatan praktis setempat

- **Pendaftaran:** Online Single Submission (OSS) yang dikelola Kementerian Investasi dan Hilirisasi/BKPM; pengesahan badan hukum dilakukan Kementerian Hukum (AHU). Situs resmi: <https://oss.go.id>.
- **Menambahkan catatan TXT:** di pengaturan DNS registrar atau penyedia DNS Anda, tambahkan catatan TXT bernama `_abiz` (sebagian panel meminta nama lengkap, `_abiz.domainanda.co.id`), dengan nilai di atas dan TTL 300 detik. Domain `.co.id` bekerja sama seperti `.com` atau domain lain. Sebisa mungkin jangan memecah nilai, dan jangan pernah memecah `p`.
- **Data pribadi:** Undang-Undang Nomor 27 Tahun 2022 tentang Pelindungan Data Pribadi. Catatan ABIZ bersifat publik. Terbitkan hanya informasi usaha yang Anda rela bagikan, dan jangan cantumkan alamat rumah pribadi atau nomor telepon pribadi (SPEC bagian 4.3).

## 7. Bacaan lanjutan

- [Spesifikasi ABIZ (SPEC.md, bahasa Inggris)](../../../SPEC.md)
- [Skema JSON catatan usaha](../../../schemas/abiz-business-record-v1.1.schema.json)
- [Validator rujukan](../../../scripts/validate.py)
- [Panduan ABIZ per negara: Asia](index.md)
