# Menjadi Perniagaan Agentik dengan ABIZ di Brunei Darussalam

*Panduan untuk ABIZ 1.1 (spesifikasi yang diterbitkan). [Spesifikasi (SPEC.md, bahasa Inggeris)](../../../SPEC.md) ialah teks yang berwibawa: jika panduan ini dan spesifikasi berbeza, spesifikasi yang terpakai.* Bahasa Melayu ialah bahasa rasmi; bahasa Inggeris digunakan secara meluas dalam perniagaan.

## 1. Maksudnya bagi perniagaan di Brunei Darussalam

Pembantu AI kini kerap ditanya soalan seperti “yang mana laman web sebenar syarikat ini?” atau “siapa yang mengendalikan kedai ini?”. ABIZ (Agentic Business Record) ialah piawaian terbuka yang membolehkan perniagaan di Brunei Darussalam menerbitkan maklumat awamnya sekali sahaja, dalam bentuk yang boleh dibaca oleh alat-alat tersebut: rekod DNS TXT yang ringkas pada domain yang dikawal oleh perniagaan itu, yang menunjuk kepada rekod perniagaan dalam format JSON yang disediakan melalui HTTPS. Oleh sebab penunjuk itu berada dalam DNS perniagaan itu sendiri, alat boleh mengesahkan bahawa rekod diterbitkan oleh pihak yang mengawal domain tersebut, dan tidak perlu bergantung pada direktori tidak rasmi atau tekaan.

## 2. Cara menerbitkan rekod ABIZ

### Medan wajib

Setiap rekod perniagaan memerlukan lima medan berikut (SPEC bahagian 4.1):

| Medan | Contoh dan peraturan |
|---|---|
| `record_version` | `abiz1` |
| `business_name` | nama awam yang dikenali pelanggan, contohnya `Kedai Kopi Kampong Ayer` |
| `country` | `bn`, kod ISO 3166-1 alpha-2 dalam huruf kecil |
| `identity_host` | `kopikampongayer.bn.to.co`, mesti sama tepat dengan `h` dalam DNS |
| `domains` | `["kopikampongayer.example"]`, mesti mengandungi domain yang membawa `_abiz` |

### Kunci perniagaan pilihan `k`

`k` adalah pilihan bagi semua perniagaan, sama ada berdaftar atau tidak. Jika diterbitkan, nilainya mesti sama dengan `business_key` dalam rekod, dan rekod itu juga mesti mengandungi `registration_number`. Bagi Brunei Darussalam, bentuknya ialah:

```text
bn-<registration-number>
```

Brunei Darussalam tidak menggunakan kod subbahagian: jangan tambah kod negeri, daerah atau bandar. SPEC bahagian 4.2.2 hanya mewajibkan subbahagian bagi Amerika Syarikat, perbadanan wilayah Kanada dan Emiriah Arab Bersatu, dan melarangnya di negara lain.

**Nombor yang digunakan:** nombor pendaftaran syarikat atau nama perniagaan pada sijil pendaftaran anda, contohnya `RC/00012345` bagi syarikat.

**Penormalan (SPEC bahagian 4.2.3):** mulakan dengan nombor tepat seperti yang dikeluarkan oleh pendaftar, gunakan penormalan Unicode NFKC, buang ruang, `-`, `.`, `/` dan sempang, kemudian tukar huruf kepada huruf besar. Kekalkan sifar di hadapan dan awalan huruf. Hasilnya mesti mengandungi huruf dan digit ASCII sahaja; jika tidak, kunci perniagaan tidak boleh diterbitkan dan `k`, `business_key` serta `registration_number` ditinggalkan.

**Contoh (rekaan):** `RC/00012345` menjadi `RC00012345`, maka `k=bn-RC00012345`. Dalam rekod: `"business_key": "bn-RC00012345"` dan `"registration_number": "RC00012345"`. Kunci dibandingkan tanpa mengira huruf besar atau kecil; bentuk kanoniknya ialah kod negara dalam huruf kecil dan nombor dalam huruf besar.

**Sila semak:** kami tidak dapat mengesahkan format tepat nombor ini daripada sumber rasmi, jadi contoh ini sekadar gambaran. Gunakan nombor tepat seperti yang tertera pada dokumen pendaftaran rasmi anda. Jika tidak jelas nombor mana yang mengenal pasti perniagaan anda di peringkat negara, jangan terbitkan `k` sehingga anda pasti.

**Pemilik tunggal:** jika satu-satunya nombor yang anda ada ialah nombor peribadi, seperti nombor kad pengenalan, jangan terbitkan `k`. Tinggalkan `k`, `business_key` dan `registration_number`; rekod masih sah.

### Rekod DNS TXT

Terbitkan tepat satu rekod TXT bernama `_abiz` di bawah domain anda, dalam bentuk padat tanpa ruang, dengan `v=abiz1` di hadapan:

```dns
_abiz.kopikampongayer.example. 300 IN TXT "v=abiz1;k=bn-RC00012345;h=kopikampongayer.bn.to.co;p=sJZdvOixahHFykwTfY0QFVslpceY9Z/BLMyfO5X7240="
```

Nilai `p` di atas ialah kunci contoh pakai buang yang dijana untuk halaman ini. Jangan sekali-kali menyalinnya: terbitkan kunci anda sendiri. Pengisytiharan ABIZ 1.1 mesti mengandungi `p`. Semua nama, nombor dan domain di halaman ini adalah rekaan.

Tanpa tag pilihan `k`, rekod ini juga sah:

```dns
_abiz.kopikampongayer.example. 300 IN TXT "v=abiz1;h=kopikampongayer.bn.to.co;p=sJZdvOixahHFykwTfY0QFVslpceY9Z/BLMyfO5X7240="
```

Rekod perniagaan yang disediakan sebagai `application/json` di `https://kopikampongayer.bn.to.co`:

```json
{
  "record_version": "abiz1",
  "business_name": "Kedai Kopi Kampong Ayer",
  "country": "bn",
  "business_key": "bn-RC00012345",
  "registration_number": "RC00012345",
  "identity_host": "kopikampongayer.bn.to.co",
  "domains": [
    "kopikampongayer.example"
  ],
  "public_key": "sJZdvOixahHFykwTfY0QFVslpceY9Z/BLMyfO5X7240=",
  "signature": "DtVz+TPNp2HlJeACYDy3gitC2PBWnIhoDUBAN91H683OSKvm4LiMOCIhgL4nDgPFdYVWlS2PkqHELpmBAFgdBA=="
}
```

Untuk menyemak rekod sebelum diterbitkan, jalankan pengesah rujukan daripada salinan repositori ini:

```sh
python scripts/validate.py record.json --domain kopikampongayer.example --dns-value 'v=abiz1;k=bn-RC00012345;h=kopikampongayer.bn.to.co;p=sJZdvOixahHFykwTfY0QFVslpceY9Z/BLMyfO5X7240='
```

Anda boleh menempatkan sendiri rekod JSON pada mana-mana pelayan HTTPS, atau menggunakan mana-mana penyedia yang serasi. ABIZ tidak mewajibkan penyedia tertentu.

## 3. Menggunakan penyedia dan MCP

Model Context Protocol (MCP) ialah protokol terbuka yang membolehkan pembantu AI memanggil alat dan membaca data daripada pelayan luar dengan cara yang standard. Rekod perniagaan boleh mengandungi medan pilihan `mcp_server_url`, iaitu alamat HTTPS pelayan MCP perniagaan, contohnya untuk tempahan atau maklumat produk. ABIZ tidak menjamin pelayan itu; alat mesti menggunakan kawalan akses sendiri (SPEC bahagian 4.2.6).

Penyedia boleh menempatkan rekod dan menerbitkan penunjuk DNS bagi pihak anda. Contohnya, syarikat berdaftar di Brunei Darussalam yang rekodnya ditempatkan oleh to.co boleh menggunakan hos `kopikampongayer.bn.to.co`, dengan nilai DNS `v=abiz1;k=bn-RC00012345;h=kopikampongayer.bn.to.co;p=sJZdvOixahHFykwTfY0QFVslpceY9Z/BLMyfO5X7240=`. Perniagaan yang tidak berdaftar boleh menggunakan hos berasaskan nama bandar seperti `kopikampongayer-bandarseribegawan.biz.to.co`. Mana-mana penyedia serasi, atau pelayan anda sendiri, berfungsi dengan cara yang sama.

## 4. Kunci dan tandatangan (ABIZ 1.1)

ABIZ 1.1 mewajibkan kunci tandatangan. Tag DNS `p` membawa kunci awam Ed25519: 32 bait mentah, base64 standard, 44 aksara, satu `=` di hujung (SPEC bahagian 3.3.2). Base64url tidak diterima. Perniagaan, atau penyedia yang bertindak bagi pihaknya, menyimpan kunci peribadi yang sepadan dan menandatangani rekod perniagaan dengannya. Kunci peribadi sentiasa milik perniagaan, dan penyedia hos mesti membenarkan perniagaan mengeksportnya.

- `v` dan `h` wajib. `p` adalah wajib. `k` adalah pilihan. `p` mesti kunci yang sah: nilai lain, seperti rentetan heksadesimal atau kunci base64url, menjadikan keseluruhan pengisytiharan tidak sah.
- Hanya kunci semasa diterbitkan. Untuk memutar, jana pasangan kunci Ed25519 baharu, terbitkan kunci awam baharu dalam pengisytiharan DNS atau well-known, tandatangani semula rekod dengan kunci peribadi baharu, dan tetapkan `public_key` kepada `p` yang sama. Benarkan cache DNS. Membuang `p` sahaja bukan pembatalan yang sah selagi pengisytiharan ABIZ 1.1 kekal: untuk menariknya, buang keseluruhan pengisytiharan DNS atau well-known. Dalam ABIZ 1.1, kunci yang telah dipersarakan tidak diterbitkan, sama ada dalam DNS atau dalam rekod perniagaan.
- Kunci menunjukkan siapa yang mengawal DNS domain. Kunci tidak membuktikan identiti undang-undang.

## 5. Apa yang akan dilihat oleh alat AI

Alat serasi yang membaca rekod anda boleh menjawab soalan seperti:

1. Apakah laman web rasmi Kedai Kopi Kampong Ayer?
2. Domain manakah milik perniagaan ini?
3. Nombor pendaftaran apakah yang dinyatakan oleh perniagaan ini, dan di negara mana?
4. Apakah yang ditawarkan, dan bilakah waktu operasinya?

**Had:** ABIZ menunjukkan apa yang diterbitkan oleh pengawal sesuatu domain. Ia tidak membuktikan bahawa perniagaan itu berdaftar secara sah, bahawa nombornya tulen, atau bahawa mana-mana perkhidmatan AI, agensi kerajaan atau penyedia menyokongnya. Apabila perkara itu penting, alat dan orang ramai harus menyemak daftar rasmi.

## 6. Nota praktikal tempatan

- **Pendaftaran:** Pendaftar Syarikat dan Nama Perniagaan (ROCBN), Kementerian Kewangan dan Ekonomi. Laman rasmi: <https://www.ocp.mofe.gov.bn>.
- **Menambah rekod TXT:** dalam tetapan DNS pendaftar domain atau penyedia DNS anda, tambah rekod TXT bernama `_abiz` (sesetengah panel meminta nama penuh, `_abiz.domainanda.com.bn`), dengan nilai di atas dan TTL 300 saat. Domain `.com.bn` berfungsi sama seperti `.com` atau domain lain. Sedapat mungkin jangan pecahkan nilai itu, dan jangan sekali-kali memecahkan `p`.
- **Data peribadi:** Semak peraturan perlindungan data yang terpakai di Brunei Darussalam sebelum menerbitkan data peribadi. Rekod ABIZ adalah awam. Terbitkan hanya maklumat perniagaan yang anda sanggup kongsi, dan jangan sertakan alamat kediaman atau nombor telefon peribadi (SPEC bahagian 4.3).

## 7. Bacaan lanjut

- [Spesifikasi ABIZ (SPEC.md, bahasa Inggeris)](../../../SPEC.md)
- [Skema JSON rekod perniagaan](../../../schemas/abiz-business-record-v1.1.schema.json)
- [Pengesah rujukan](../../../scripts/validate.py)
- [Panduan ABIZ mengikut negara: Asia](index.md)
