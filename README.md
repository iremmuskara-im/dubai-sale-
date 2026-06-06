# 🏠 Dubai Home Sale — Kurulum Rehberi

Merhaba! Bu repo GitHub Pages üzerinde satılık eşyalar siteni barındırır.
Envanteri Google Sheets'ten yönetirsin — değişiklik yaptığında site otomatik güncellenir.

---

## ⚡ Hızlı Kurulum (yaklaşık 30 dakika)

### 1️⃣ GitHub Hesabı Aç
1. [github.com/signup](https://github.com/signup) adresine git
2. Ücretsiz hesap oluştur
3. E-postanı doğrula

---

### 2️⃣ Bu Repo'yu GitHub'a Yükle
1. GitHub'da sağ üstte **+** → **New repository** tıkla
2. İsim: `dubai-sale` (veya istediğin bir şey)
3. **Public** seç (GitHub Pages için gerekli)
4. **Create repository** tıkla
5. Tüm bu dosyaları yükle:
   - Yeşil **Code** butonu → **Upload files**
   - Tüm klasörleri sürükle bırak
   - **Commit changes** tıkla

---

### 3️⃣ Google Sheets Envanterini Hazırla

1. [Google Sheets](https://sheets.google.com) aç → Yeni spreadsheet
2. **Birinci satıra** (başlık satırı) şu kolonları yaz:

```
name | description | price | category | status | emoji | photo
```

3. Kategoriler (küçük harf kullan):
   - `living` — Oturma odası
   - `bedroom` — Yatak odası
   - `kitchen` — Mutfak & yemek
   - `decor` — Dekor & aydınlatma
   - `outdoor` — Dış mekan
   - `other` — Diğer

4. Durum değerleri:
   - `available` — Satışta
   - `sold` — Satıldı
   - `reserved` — Rezerve

5. Örnek satır:
```
Koltuk | 3 kişilik, gri kumaş, 2 yaşında | 1200 | living | available | 🛋️ | koltuk.jpg
```

6. **Public CSV linki al:**
   - **File** → **Share** → **Publish to web**
   - **Sheet1** seç, format olarak **Comma-separated values (.csv)** seç
   - **Publish** tıkla
   - Çıkan linki kopyala (şuna benzer: `https://docs.google.com/spreadsheets/d/.../pub?...output=csv`)

---

### 4️⃣ GitHub Secrets Ekle (güvenli bilgiler)

Repo sayfasında: **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Eklemen gereken 3 secret:

| Secret Adı | Değer |
|---|---|
| `SHEET_CSV_URL` | Google Sheets CSV linkin |
| `WHATSAPP_NUMBER` | Ülke kodu ile birlikte (örn: `971501234567`) |
| `CONTACT_EMAIL` | E-posta adresin |

---

### 5️⃣ GitHub Pages'i Aktifleştir

1. Repo → **Settings** → **Pages**
2. **Source**: `gh-pages` branch seç
3. **Save** tıkla
4. Birkaç dakika bekle → Sitenin adresi görünecek: `https://[kullanıcı-adin].github.io/dubai-sale`

---

### 6️⃣ İlk Build'i Başlat

1. Repo → **Actions** sekmesi
2. **Build & Deploy Dubai Sale Site** workflow'u seç
3. **Run workflow** → **Run workflow** tıkla
4. Yeşil tik görününce sitenin hazır!

---

## 📸 Fotoğraf Ekleme

1. Fotoğrafı düzenle (önerilen: 800x600 px, `.jpg` formatı)
2. Dosya adını not et (örn: `koltuk.jpg`)
3. GitHub'da `photos/` klasörüne yükle
4. Google Sheets'te ilgili ürünün `photo` kolonuna dosya adını yaz (örn: `koltuk.jpg`)
5. Actions otomatik çalışır → site güncellenir

---

## 🔄 Günlük Kullanım

**Ürün satıldığında:**
1. Google Sheets'te `status` kolonunu `sold` yap
2. Repo → Actions → **Run workflow** tıkla
3. ~1 dakikada site güncellenir ✅

**Otomatik güncelleme:** Her gün sabah 09:00 Dubai saatinde kendiliğinden çalışır.

---

## 🆘 Sorun Giderme

**Actions başarısız oluyor:**
- Secrets doğru girildi mi kontrol et
- CSV URL'nin "Anyone with the link" ile paylaşıldığından emin ol

**Site görünmüyor:**
- Pages ayarında `gh-pages` branch seçildi mi?
- İlk deploy 5-10 dakika sürebilir

**Fotoğraflar yüklenmiyor:**
- Dosya adlarında boşluk ve Türkçe karakter kullanma
- Sadece `.jpg`, `.jpeg`, `.png`, `.webp` desteklenir
