# Motifo Mimarlık – Sosyal Medya Yöneticisi Talimatı

Bu depo, Motifo Mimarlık'ın (Instagram: @motifomimarlik) sosyal medya içeriklerinin üretim merkezidir.
Sahibi: Ahmet (ahmetyunuskonyalioglu). Dil: Türkçe. Ahmet'e her zaman sade, kısa Türkçe yaz.

## Değişmez kurallar
1. **Onaysız paylaşım yok.** Her içerik Ahmet'e gösterilir, "onay" gelmeden Metricool'a planlanmaz.
2. **Tekrar yok.** `kullanilan_gorseller.json` içindeki kaynak dosyalar (alan `kaynak`) bir daha kullanılmaz.
   Instagram'da son 1 yıl içinde paylaşılmış görseller (dhash kayıtları) de kullanılmaz.
   1 yıldan eski paylaşımların görselleri sadece YENİ bir formatta (derinlikli reels, gece/gündüz geçişi, editoryal karusel) kullanılabilir.
3. **Satış dili yok.** "DM", "bize ulaşın", hizmet listesi, fiyat yok. İşi göster. Kapanış = sadece logo / logo animasyonu.
4. **Kamera yavaş ve derinlikli** (araclar/parallax.py – Depth Anything V2). Düz 2D kaydırma yok. Sahne ≥3,4 sn.
5. **Müzik telifsiz ve kodla üretilir** (araclar/sesler.py, ses_reel.py). Reels'te müzik logo kapanışında da devam eder; logo kapanışına AYRI müzik/efekt konmaz.
6. Özel günlerde her yıl farklı konsept; mümkünse mimari dil (çizim, ölçü, plan, cephe).
7. **Logo:** Ahmet'in altın logosu (`marka/logo_altin.png`) renklerine ASLA dokunulmadan, olduğu gibi kullanılır. Kapanış = beyaz zemin + dağınık, farklı yönlere dönük çok silik kabartma amblemler + logo yavaşça belirir (soldan sağa açılma/harf harf kurulma YOK). Hazır kareler: `marka/logo_kapanis_kareleri/` (araclar/logo_anim_v4.py).

## Haftalık ritim
- 1 Reels (Salı 18:00), 1 Gönderi/karusel (Perşembe 10:00), 3–4 Story (hafta içi 11:00 civarı)
- Saat dilimi: Europe/Istanbul. Metricool brand/blogId: 7380617

## Kaynaklar
- `kaynak/PROJELER/<PROJE>/...` – küçültülmüş proje renderları (şablonlu olanlar `araclar/cropframe.py` ile kırpılır)
- `marka/` – logo_beyaz/siyah/altin, amblem; `fr_logo` gerekiyorsa `araclar/logo_anim.py` ile yeniden üret
- Proje konumları: Oyster Pırlanta = Kayseri İldem · Afrika = Gabon villa · Florya Mavikoru = İstanbul Florya ·
  Afra Park / Vogue / Bahçeşehir = İstanbul Bahçeşehir · YCR = Antalya Lara (Pesta Hotel) · Kıbrıs = KKTC
- Bilinmeyen konum yazılmaz.

## Araçlar
- Derinlik modeli: `curl -sL -o /home/claude/models/da2s.onnx https://github.com/fabio-sim/Depth-Anything-ONNX/releases/download/v2.0.0/depth_anything_v2_vits.onnx` (onnxruntime kurulu)
- `araclar/reel.py spec.json out` → kareler; `araclar/ses_reel.py` → müzik; ffmpeg ile birleştir (örnek: `araclar/ornek_reels_spec.json`)
- `araclar/karusel.py spec.json outdir` → 1080x1350 editoryal karusel (örnek: `araclar/ornek_karusel_spec.json`)
- Scratch yolları araç dosyalarında sabit olabilir; çalıştırmadan önce `S=` yolunu kendi ortamına göre düzelt.

## Paylaşım akışı
1. Bu haftanın içeriklerini üret → `paylasimlar/YYYY-MM-DD_konu/` içine koy → commit + push
2. Dosyaları SendUserFile ile gönder + PushNotification ("Motifo: bu haftanın içerikleri onayını bekliyor")
3. Onay gelince Metricool `createScheduledPost` ile planla; medya URL'si:
   `https://raw.githubusercontent.com/ahmetyunuskonyalioglu/motifo-medya/main/<yol>`
   (Instagram type: STORY / REEL / POST; story'de text gönderme)
4. Planlanan her kaynak görseli `kullanilan_gorseller.json` → `used` listesine ekle (`kaynak`, `tarih`, `paylasim`) → push
5. Ayrıntılı strateji: `STRATEJI.md`

## Takvim notları
- 2026-10-13 18:00 – Oyster reels v3 planlandı (uuid -3683940586244323580)
- 2026-10-29 09:00 – 29 Ekim story planlandı (Metricool uuid -5575539309169979481)
- Sıradaki özel günler: 8 Kasım Dünya Şehircilik Günü, 10 Kasım, Yılbaşı
