# ABIZ ile Türkiye’de yapay zekâ ajanlarına hazır bir işletme olmak

*ABIZ 1.1 (yayımlanmış belirtim) için bir rehberdir. Esas metin [spesifikasyondur (SPEC.md, İngilizce)](../../../SPEC.md): bu rehber ile spesifikasyon farklıysa spesifikasyon geçerlidir.*

## 1. Türkiye’de bir işletme için ne anlama geliyor

Yapay zekâ asistanlarına artık sık sık “Bu şirketin gerçek web sitesi hangisi?” ya da “Bu dükkânı kim işletiyor?” gibi sorular soruluyor. ABIZ (Agentic Business Record), Türkiye’de bir işletmenin kamuya açık bilgilerini bir kez, bu araçların okuyabileceği biçimde yayımlamasını sağlayan açık bir standarttır: İşletmenin denetlediği bir alan adına kısa bir DNS TXT kaydı eklenir ve bu kayıt HTTPS üzerinden sunulan JSON biçimindeki işletme kaydını gösterir. İşaretçi işletmenin kendi DNS’inde bulunduğu için bir araç, resmî olmayan bir rehbere ya da tahmine güvenmek yerine kaydın o alan adını denetleyen kişi tarafından yayımlandığını görebilir.

## 2. ABIZ kaydı nasıl yayımlanır

### Zorunlu alanlar

Her işletme kaydında şu beş alan bulunur (SPEC bölüm 4.1):

| Alan | Örnek ve kural |
|---|---|
| `record_version` | `abiz1` |
| `business_name` | müşterilerin bildiği kamuya açık ad, örneğin `Kapadokya Seramik` |
| `country` | `tr`, küçük harfle ISO 3166-1 alpha-2 kodu |
| `identity_host` | `kapadokyaseramik.tr.to.co`; DNS’teki `h` ile tam olarak aynı olmalıdır |
| `domains` | `["kapadokyaseramik.example"]`; `_abiz` kaydını taşıyan alan adını içermelidir |

### İsteğe bağlı işletme anahtarı `k`

`k`, tescilli olsun olmasın her işletme için isteğe bağlıdır. Yayımlarsanız kayıttaki `business_key` ile aynı olmalı ve kayıtta `registration_number` da bulunmalıdır. Türkiye için biçim şöyledir:

```text
tr-<registration-number>
```

Türkiye’de alt bölge kodu kullanılmaz: il veya ilçe kodu eklemeyin. SPEC bölüm 4.2.2 alt bölgeyi yalnızca ABD, Kanada’nın eyalet şirketleri ve Birleşik Arap Emirlikleri için zorunlu tutar, diğer tüm ülkelerde yasaklar.

**Hangi numara:** 16 haneli MERSİS numarası. Ticaret sicil numarası her sicil müdürlüğünce ayrı verildiği için ulusal düzeyde benzersiz değildir; bu yüzden ulusal MERSİS numarasını öneriyoruz. SPEC Türkiye’yi açıkça anmadığından bu bizim yorumumuzdur.

**Normalleştirme (SPEC bölüm 4.2.3):** Numarayı sicilin verdiği hâliyle alın, Unicode NFKC normalleştirmesi uygulayın, boşlukları, `-`, `.`, `/` ve tire karakterlerini silin, harfleri büyük harfe çevirin. Baştaki sıfırları ve harf öneklerini koruyun. Sonuçta yalnızca ASCII harf ve rakam kalmalıdır; aksi hâlde işletme anahtarı yayımlanamaz ve `k`, `business_key` ile `registration_number` çıkarılır.

**Örnek (kurgusal):** `0123456789000015` değeri `0123456789000015` olur; dolayısıyla `k=tr-0123456789000015`. Kayıtta: `"business_key": "tr-0123456789000015"` ve `"registration_number": "0123456789000015"`. Anahtarlar büyük/küçük harf ayrımı yapılmadan karşılaştırılır; kanonik biçimde ülke kodu küçük, numara büyük harfle yazılır.

**Lütfen kontrol edin:** Bu numaranın tam biçimini resmî bir kaynaktan doğrulayamadık; örnek yalnızca açıklama amaçlıdır.

**Şahıs işletmeleri:** Elinizdeki tek numara T.C. kimlik numarası gibi kişisel bir numaraysa `k` yayımlamayın. `k`, `business_key` ve `registration_number` alanlarını çıkarın; kayıt yine geçerlidir.

### DNS TXT kaydı

Alan adınızın altında `_abiz` adıyla yalnızca bir TXT kaydı yayımlayın; boşluksuz kısa biçimde ve en başta `v=abiz1` olacak şekilde:

```dns
_abiz.kapadokyaseramik.example. 300 IN TXT "v=abiz1;k=tr-0123456789000015;h=kapadokyaseramik.tr.to.co;p=4ibVnq387H/uJZ4qf/0Sbtb6VHzSdKyNmEqUdg+K450="
```

Yukarıdaki `p` değeri bu sayfa için üretilmiş, tek kullanımlık bir örnek anahtardır. Asla kopyalamayın: kendi anahtarınızı yayımlayın. Bir ABIZ 1.1 beyanı `p` içermelidir. Bu sayfadaki tüm adlar, numaralar ve alan adları hayalîdir.

İsteğe bağlı `k` etiketi olmadan da şu kayıt geçerlidir:

```dns
_abiz.kapadokyaseramik.example. 300 IN TXT "v=abiz1;h=kapadokyaseramik.tr.to.co;p=4ibVnq387H/uJZ4qf/0Sbtb6VHzSdKyNmEqUdg+K450="
```

`https://kapadokyaseramik.tr.to.co` adresinde `application/json` olarak sunulan işletme kaydı:

```json
{
  "record_version": "abiz1",
  "business_name": "Kapadokya Seramik",
  "country": "tr",
  "business_key": "tr-0123456789000015",
  "registration_number": "0123456789000015",
  "identity_host": "kapadokyaseramik.tr.to.co",
  "domains": [
    "kapadokyaseramik.example"
  ],
  "public_key": "4ibVnq387H/uJZ4qf/0Sbtb6VHzSdKyNmEqUdg+K450=",
  "signature": "VyIt4A+bWY6PBttC3gJ+BRGT/Li1ZfZ7mgdHNusrBwo9h5SeuVSyb6D2D56jRV2W0lam2Olo/hd6chyhthFrCg=="
}
```

Bir kaydı yayımlamadan önce denetlemek için bu deponun bir kopyasında başvuru doğrulayıcısını çalıştırın:

```sh
python scripts/validate.py record.json --domain kapadokyaseramik.example --dns-value 'v=abiz1;k=tr-0123456789000015;h=kapadokyaseramik.tr.to.co;p=4ibVnq387H/uJZ4qf/0Sbtb6VHzSdKyNmEqUdg+K450='
```

JSON kaydını herhangi bir HTTPS sunucusunda kendiniz barındırabilir ya da uyumlu herhangi bir sağlayıcıyı kullanabilirsiniz. ABIZ belirli bir sağlayıcı şart koşmaz.

## 3. Sağlayıcı ve MCP kullanımı

Model Context Protocol (MCP), yapay zekâ asistanlarının dış sunuculardaki araçları standart bir yolla çağırmasını ve veri okumasını sağlayan açık bir protokoldür. İşletme kaydı isteğe bağlı `mcp_server_url` alanını, yani işletmenin MCP sunucusunun HTTPS adresini içerebilir; örneğin rezervasyon ya da ürün bilgisi için. ABIZ bu sunucuya kefil olmaz; araçlar kendi erişim denetimlerini uygulamalıdır (SPEC bölüm 4.2.6).

Bir sağlayıcı kaydı barındırıp DNS işaretçisini sizin adınıza yayımlayabilir. Örneğin kaydı to.co’da barındırılan, Türkiye’de tescilli bir şirket `kapadokyaseramik.tr.to.co` adresini kullanabilir; DNS değeri `v=abiz1;k=tr-0123456789000015;h=kapadokyaseramik.tr.to.co;p=4ibVnq387H/uJZ4qf/0Sbtb6VHzSdKyNmEqUdg+K450=` olur. Tescilsiz bir işletme ise `kapadokyaseramik-nevsehir.biz.to.co` gibi şehir adı içeren bir adres kullanabilir. Uyumlu her sağlayıcı ya da kendi sunucunuz aynı şekilde çalışır.

## 4. Anahtarlar ve imzalar (ABIZ 1.1)

ABIZ 1.1 bir imza anahtarı gerektirir. DNS’teki `p` etiketi bir Ed25519 açık anahtarı taşır: 32 ham bayt, standart base64, 44 karakter, sonda tek bir `=` (SPEC bölüm 3.3.2). Base64url kabul edilmez. İşletme ya da onun adına çalışan bir sağlayıcı ilgili özel anahtarı saklar ve işletme kaydını onunla imzalar. Özel anahtar her zaman işletmenindir; barındırma sağlayıcısı işletmenin anahtarı dışa aktarmasına izin vermelidir.

- `v` ve `h` zorunludur. `p` zorunludur. `k` isteğe bağlıdır. `p` geçerli bir anahtar olmalıdır: eski bir ABIZ 1.0 onaltılık belirteci ya da base64url anahtarı gibi başka bir değer, tüm beyanı geçersiz kılar.
- Yalnızca güncel anahtar yayımlanır. Döndürmek için yeni bir Ed25519 anahtar çifti üretin, yeni açık anahtarı DNS veya well-known beyanında yayımlayın, kaydı yeni özel anahtarla yeniden imzalayın ve `public_key` değerini aynı `p` yapın. DNS önbelleğini hesaba katın. ABIZ 1.1 beyanı dururken yalnızca `p`’yi kaldırmak geçerli bir iptal değildir: geri çekmek için DNS veya well-known beyanının tamamını kaldırın. ABIZ 1.1’de emekliye ayrılan anahtarlar ne DNS’te ne de işletme kaydında yayımlanır.
- Anahtar, alan adının DNS’ini kimin denetlediğini gösterir; hukuki kimliği kanıtlamaz.

## 5. Yapay zekâ araçları neyi görecek

Kaydınızı okuyan uyumlu bir araç şu gibi sorulara yanıt verebilir:

1. Kapadokya Seramik işletmesinin resmî web sitesi hangisi?
2. Bu işletmeye hangi alan adları ait?
3. İşletme hangi sicil numarasını, hangi ülkede bildiriyor?
4. Ne sunuyor ve ne zaman açık?

**Sınırlar:** ABIZ, bir alan adını denetleyen kişinin yayımladığını gösterir. İşletmenin yasal olarak tescilli olduğunu, numarasının gerçek olduğunu ya da herhangi bir yapay zekâ hizmetinin, kamu kurumunun veya sağlayıcının onu onayladığını kanıtlamaz. Önemli durumlarda araçlar ve kişiler resmî sicile bakmalıdır.

## 6. Yerel pratik notlar

- **Sicil:** Ticaret Bakanlığı Merkezi Sicil Kayıt Sistemi (MERSİS) ve ticaret sicili müdürlükleri. Resmî web sitesi: <https://mersis.ticaret.gov.tr>.
- **TXT kaydı ekleme:** Alan adı kayıt kuruluşunuzun ya da DNS sağlayıcınızın DNS ayarlarında `_abiz` adlı (bazı paneller `_abiz.alanadiniz.com.tr` gibi tam adı ister), yukarıdaki değere ve 300 saniyelik TTL’ye sahip bir TXT kaydı ekleyin. `.com.tr` alan adları `.com` ya da diğer alan adlarıyla aynı şekilde çalışır. Değeri mümkün olduğunca bölmeyin, `p`’yi ise asla bölmeyin.
- **Kişisel veriler:** 6698 sayılı Kişisel Verilerin Korunması Kanunu (KVKK). ABIZ kaydı herkese açıktır. Yalnızca paylaşmaktan memnun olduğunuz işletme bilgilerini yayımlayın; ev adresi ve kişisel telefon numarası koymayın (SPEC bölüm 4.3).

## 7. Ek okumalar

- [ABIZ spesifikasyonu (SPEC.md, İngilizce)](../../../SPEC.md)
- [İşletme kaydı JSON şeması](../../../schemas/abiz-business-record-v1.1.schema.json)
- [Başvuru doğrulayıcısı](../../../scripts/validate.py)
- [Ülkelere göre ABIZ rehberleri: Asya](index.md)
