# Motifo Mimarlık – Sosyal Medya Yöneticisi Talimatı

Bu depo, Motifo Mimarlık'ın (Instagram: @motifomimarlik) sosyal medya içeriklerinin üretim merkezidir.
Sahibi: Ahmet (ahmetyunuskonyalioglu). Dil: Türkçe. Ahmet'e her zaman sade, kısa Türkçe yaz.

## Değişmez kurallar
1. **Onaysız paylaşım yok.** Her içerik Ahmet'e gösterilir, "onay" gelmeden Metricool'a planlanmaz.
2. **Tekrar yok.** `kullanilan_gorseller.json` içindeki kaynak dosyalar (alan `kaynak`) bir daha kullanılmaz.
   Instagram'da son 1 yıl içinde paylaşılmış görseller (dhash kayıtları) de kullanılmaz.
   1 yıldan eski paylaşımların görselleri sadece YENİ bir formatta (derinlikli reels, gece/gündüz geçişi, editoryal karusel) kullanılabilir.
3. **Satış dili yok.** "DM", "bize ulaşın", fiyat yok. İşi göster. Kapanış = sadece logo / logo animasyonu.
   İstisna: ara ara (ayda ~1–2) Motifo/BİM'i anlatan **bilgi gönderileri** olur ("BİM NOTLARI" serisi: araclar/izgara.py `bilgi_kapak`/`bilgi_sayfa`; örnek paylasimlar/taslak_bim_notlari/). Dil öğretici ve sakin; çağrı/fiyat yok, uydurma istatistik yok.
4. **Kamera yavaş ve derinlikli** (araclar/parallax.py – Depth Anything V2). Düz 2D kaydırma yok. Sahne ≥3,4 sn.
5. **Müzik telifsiz ve kodla üretilir** — `araclar/muzik.py` (tarzlar: keman, insaat, piyano, lofi, sinematik). Ahmet keman tarzını seviyor; sinematik (karanlık/korkutucu) KULLANMA. Her videoda yeni melodi (ton/tohum). **Aynı parça tekrar kullanılmaz:** keman tarzında her videoda ton/tempo/tohum değiştirilir (farklı melodi); diğer tarzlara geçilecekse `muzik.sonraki_stil()` kullanılır; `muzik.kaydet()` ile `muzik_kayit.json`a yazılır. Reels'te müzik logo kapanışında da devam eder; kapanışa AYRI müzik/efekt konmaz.
6. Özel günlerde her yıl farklı konsept; mümkünse mimari dil (çizim, ölçü, plan, cephe).
7. **Logo:** Ahmet'in altın logosu (`marka/logo_altin.png`) renklerine ASLA dokunulmadan, olduğu gibi kullanılır. Kapanış = beyaz zemin + dağınık, farklı yönlere dönük çok silik kabartma amblemler + logo yavaşça belirir (soldan sağa açılma/harf harf kurulma YOK). Hazır kareler: `marka/logo_kapanis_kareleri/` (araclar/logo_anim_v4.py).

8. **BİM videoları kareden kamera gezdirmeyle YAPILMAZ.** 3B motorla (`araclar/bim3d/`) bina aşama aşama inşa edilir: temel → taşıyıcı → duvar → tesisat (borular uzar) → şap → kaplama → cephe → çatı; çakışma anı röntgen moduyla gösterilir. `render.py scene.js out all <süre>` → `araclar/bim_yazi.py cfg.json` → logo kapanışı → müzik. "Aynı bina, iki katman" (render | BİM ayırıcı) için `split.py`. Gerçek proje için Archicad'den IFC/OBJ dışa aktarımı istenirse model doğrudan bu motora uyarlanabilir.

## Instagram ızgara (profil düzeni)
- **SEÇİLEN DÜZEN (Ahmet onayladı, 14.10.2026): 4'lü döngü** → render, render, KOYU çizim (koyu zemin + altın eskiz), KREM çizim. 3 sütunda çizimler kendiliğinden çapraz iner; "gelişigüzel ama planlı", dolu/boş dengesi. Referans: paylasimlar/izgara_tasarimi/florya_C_diyagonal.json (izgara.py `cizim(..., koyu=True/False)`).
  - Render karelerinde kapak şablonu dönüşümlü (cerceve / yok / alt_orta / dergi / kenar) — hepsi aynı olmasın.
  - **BİM eskiz** (izgara.py `bim_eskiz_detay` tercih: tam çözünürlük + yakın kadraj `kutu`, kesit pochesi taramalı, bina silueti net, dikey tesisat kümelerine kesikli şaft sınırı; eski: `bim_eskiz`): Arma BİM görselleri koyu zeminde; yapı altın çizgi, tesisat kendi renginde kalem eskizi. Koyu çizim slotuna (koyu=True) veya krem çizim slotuna (koyu=False) girer. Renk→sistem eşlemesi bilinmediği için lejant YAZILMAZ.
  - **BİM karuseli (siyah ve beyaz eskiz BİM postları) = 3 sayfa (Ahmet'in tarifi):** 1 manşetli eskiz kapak (`bim_manset`), 2 ORİJİNAL BİM görüntüsü (sadece siyah kesit → betonarme dolgu, `zenginlestir(sap=False)`) üzerinde mevcut borulara şematik oklar + etiketler (`bim_aciklamali`: pis su kolonu, ısıtma hattı, şebeke suyu, altyapı bağlantısı, tesisat şaftı…), 3 BİM animasyonu. Örnek: paylasimlar/taslak_bim_karusel/.
  - **SAHTE ELEMAN EKLEME YOK:** radyatör, kollektör, yerden ısıtma vb. çizilip eklenmez ('oyuncak gibi'). Sadece betonarme dolgu + açıklama okları.
  - **Tasarım karuseli:** kapak dönüşümlü şablon (eskiz/render…); kapak eskizse 2. sayfa aynı karede eskizden render'a yumuşak geçiş, sonra tam ekran renderlar (`sade_sayfa`, küçük etiket). Örnek: paylasimlar/taslak_tasarim_karusel/.
  - Ahmet reels kapaklarını, yazı boyutlarını ve sayfa dağılımını çok beğendi — koru.
  - **BİM görselleri yeniden oluşturulabilir** (Ahmet izni): `araclar/bim2d/zengin.py zenginlestir()` → siyah kesit = dokulu betonarme + donatı, döşeme üstü şap + yerden ısıtma boruları, kesikli şaft + kolonlar + vanalar, kollektör, radyatörler; mevcut borular doygunlaştırılır. Sonra `bim_manset(PIL_img, ...)` ile eskiz kapak. Örnek: kaynak/PROJELER/BAHADIR_ARMA/ZENGIN_BEKLI.jpg
  - **YAZI KURALI (Ahmet: 'yazılar fiyasko'):** paragraf YOK. Kapakta ızgaradan okunan TEK kısa, kurumsal manşet (ör. 'Süperpoze, üç boyutta.' / 'Bütçe, ilk çizgide belli.' / 'Tasarım ve uygulama, aynı modelde.'; liste: izgara.py `BIM_MANSETLER`). İç sayfalarda en fazla tek küçük etiket. Açıklama metni 1 cümle + etiketler. Her BİM gönderisinde farklı manşet. Örnek: paylasimlar/taslak_bim_karusel/. Animasyonda temsili (uydurma) tesisat lejantı olan Arma split videosu 'Arma' diye kullanılmaz.
  - BİM NOTLARI kapağı koyu çizim yerine, BİM şeffaf görsel krem çizim yerine geçebilir (döngü bozulmaz).
  - Her yeni paylaşımda döngüde sıradaki tip kullanılır; son tip `paylasimlar/izgara_sirasi.json` içinde tutulur.
- Ahmet sade, tam ekran görsel kapakları seviyor (araclar/izgara.py `sade`/`gorsel`); "fazla tasarım" kapakları (palet, paspartu, kemer vb.) beğenmedi.
- Aynı proje farklı görsellerle tekrar tekrar paylaşılabilir (daha çok proje varmış gibi durur); sadece aynı GÖRSEL tekrar edilmez.
- Kapaklar HER gönderide aynı olmaz: şablon ailesi dönüşümlü kullanılır (izgara.py `tile`/`sade`: cerceve, yok=yazısız, alt_orta, dergi, kenar, eskiz, yari=yarı eskiz, BİM). Yan yana aynı şablon gelmez; aynı proje tekrarında farklı şablon + farklı görsel + farklı künye (ör. 'Bar · Ataşehir'). Ortak dil: aynı yazı tipleri, krem/altın tonlar, açık kareler (eskiz/BİM) ~her 4 gönderide 1. Örnek: paylasimlar/izgara_tasarimi/karma_sablonlar.json
- Üstte 3'lü sabit panorama (şimdilik Florya); zamanla başka projeyle değişebilir. Düzeni kapak tasarımı değil, sıralama kurar (koyu/açık dönüşümlü).
- Önizleme: `araclar/profil_mock.py spec.json çıktı` (örnekler paylasimlar/izgara_tasarimi/).

## Deneme hesabı
- Instagram deneme hesabı: **@denemehesabi4212** (Ahmet'in Chrome'unda açık; Metricool'a bağlı değil). Yeni düzenler önce burada denenir.
- Paylaşım yolu: Claude in Chrome → instagram.com → Oluştur → gizli file input'a `file_upload` (yollar repo içinden) → kırp: Orijinal (3:4) → İleri → İleri → açıklama → Paylaş. Web'de arşivleme ve sabitleme yok (telefondan yapılır). Paket: `araclar/deneme_paket.py` → paylasimlar/deneme_hesap/ (sira.json: eskiden yeniye).

## Örnek havuzu ve bellek
- **HAVUZ OTURUMU (öncelikli):** Ahmet ayrı bir 'Motifo Havuz' oturumu açıp telefondan SADECE görsel atar, açıklama yazmaz. O oturumda gelen her açıklamasız görsel = havuz örneği: dosyayı `havuz/YYYY-MM-DD_NN.jpg` olarak kaydet, `havuz/README.md` tablosuna 'neyi öne çıkarıyor / Motifo'ya nasıl uyarlanır' satırı ekle, commit + push, Ahmet'e tek satır 'Havuza eklendi' yaz. (Kişisel IG hesabı/kaydedilenler KULLANILMAZ.) İçerik üretirken havuz/ tablosuna bak.
- **Yedek:** Ahmet örnekleri bilgisayarındaki `C:\Users\Win11\Desktop\MOTİFO\PAYLAŞIM ÖRNEKLERİ HAVUZU` klasörüne SADECE görsel olarak atar (not yazmaz).** Her çalışmada (bilgisayar bağlıysa) bu klasörü listele; yeni görselleri stage edip incele, depoya `havuz/` altına kopyala, tabloya 'neyi öne çıkarıyor / nasıl uyarlanır' satırı ekle, sıradaki içeriklere uyarla. İşlenenleri kayıt için tabloya yaz (klasörde silme/taşıma yapma).
- `havuz/`: Ahmet'in beğendiği başka sayfa örnekleri (ekran görüntüleri) + README tablosu. Yeni örnek gelince dosyayı buraya kaydet, tabloya satır ekle, Motifo diline uyarla.
- `havuz/MOTIFO_BELLEK.md`: claude.ai Projesi için özet bellek. Kural değişince bunu da güncelle.

## Haftalık ritim
- 1 Reels (Salı 18:00), 1 Gönderi/karusel (Perşembe 10:00), 3–4 Story (hafta içi 11:00 civarı)
- Saat dilimi: Europe/Istanbul. Metricool brand/blogId: 7380617

## Kaynaklar
- `kaynak/PROJELER/<PROJE>/...` – küçültülmüş proje renderları (şablonlu olanlar `araclar/cropframe.py` ile kırpılır)
- `marka/` – logo_beyaz/siyah/altin, amblem; `fr_logo` gerekiyorsa `araclar/logo_anim.py` ile yeniden üret
- Proje konumları: Oyster Pırlanta = Kayseri İldem · Afrika = Gabon villa · Florya Mavikoru = İstanbul Florya ·
  Afra Park / Vogue / Bahçeşehir = İstanbul Bahçeşehir · YCR = Antalya Lara (Pesta Hotel) · Kıbrıs = KKTC
- BAHADIR_ARMA = Arma, İstanbul Bahçeşehir (BİM modeli; şeffaf/kesit görselleri BİM reels için).
- Büyüme yol haritası dokümanı: https://claude.ai/code/artifact/2e47630d-bf04-48c7-ba73-b3df9684b1fb
- Bilinmeyen konum yazılmaz.
- **Müştemilat:** Tasarımı düşük olan müştemilat görselleri ana ev gibi sunulmaz; ya kullanılmaz ya da "müştemilat" diye belirtilir. Bilinen: AFRİKA/26.jpg (müştemilat salonu). Emin olunmayan iç mekânlar için Ahmet'e sor.

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
- 2026-10-15 10:00 – Gabon villa karuseli (8 kare) planlandı (uuid -216466890298798533)
- 2026-10-29 09:00 – 29 Ekim story planlandı (Metricool uuid -5575539309169979481)
- Sıradaki özel günler: 8 Kasım Dünya Şehircilik Günü, 10 Kasım, Yılbaşı
