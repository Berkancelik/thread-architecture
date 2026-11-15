## 3. Fiziksel Katman (IEEE 802.15.4 PHY)

### 3.1 Genel Bakış

Thread, IEEE 802.15.4 standardının **2.4 GHz O-QPSK** fiziksel katmanını kullanır. Bu bant dünya genelinde lisanssız (ISM) olduğu için aynı ürün her ülkede satılabilir. 802.15.4'ün sub-GHz (868/915 MHz) PHY'leri Thread şartnamesinde yer almaz.

| Parametre | Değer |
|---|---|
| Frekans bandı | 2400–2483.5 MHz (ISM) |
| Kanal sayfası (channel page) | 0 |
| Kanallar | 11–26 (16 kanal) |
| Kanal aralığı | 5 MHz |
| Kapladığı bant genişliği | ≈ 2 MHz |
| Modülasyon | O-QPSK, yarım-sinüs darbe şekillendirme |
| Yayılma (spreading) | DSSS: 4 bit → 32 chip |
| Chip hızı | 2 Mchip/s |
| Sembol hızı | 62.5 ksembol/s (1 sembol = 16 µs) |
| Bit hızı | **250 kbit/s** (1 bayt = 32 µs) |
| Maksimum PSDU (MAC çerçevesi) | **127 bayt** (`aMaxPHYPacketSize`) |
| Asgari alıcı hassasiyeti (standart) | −85 dBm (%1 PER, 20 baytlık PSDU) |
| Tipik çip hassasiyeti | −98 … −106 dBm |
| Tipik çıkış gücü | 0 … +10 dBm (FEM ile +20 dBm'e kadar) |

### 3.2 Kanallar ve Frekanslar

Kanal merkez frekansı şu formülle bulunur:

```text
Fc(k) = 2405 + 5 × (k − 11)  MHz      k = 11, 12, …, 26
```

| Kanal | Merkez (MHz) | Kanal | Merkez (MHz) | Kanal | Merkez (MHz) | Kanal | Merkez (MHz) |
|---|---|---|---|---|---|---|---|
| 11 | 2405 | 15 | 2425 | 19 | 2445 | 23 | 2465 |
| 12 | 2410 | 16 | 2430 | 20 | 2450 | 24 | 2470 |
| 13 | 2415 | 17 | 2435 | 21 | 2455 | 25 | 2475 |
| 14 | 2420 | 18 | 2440 | 22 | 2460 | 26 | 2480 |

Bir Thread ağı **tek bir kanalda** çalışır. Kanal, Operational Dataset'in parçasıdır (Bölüm 17) ve ağın tüm cihazları aynı kanalı kullanır. Kanal değişikliği, "Pending Dataset" mekanizmasıyla tüm ağda eşzamanlı yapılır.

> [!NOTE]
> Thread **frekans atlamalı (frequency hopping)** değildir. Bu, tasarımı basitleştirir ve uyuyan cihazların ağı bulmasını kolaylaştırır; karşılığında girişime karşı direnç, iyi kanal seçimi ve gerektiğinde ağ genelinde kanal değiştirme ile sağlanır.

### 3.3 Modülasyon ve Yayılma Spektrumu

802.15.4 2.4 GHz PHY'sinde veri şu adımlarla radyo sinyaline dönüşür:

1. **Bit → Sembol**: Her bayt iki adet 4 bitlik sembole bölünür (önce düşük dörtlü / LSB nibble).
2. **Sembol → Chip (DSSS)**: Her 4 bitlik sembol, 16 adet yarı-ortogonal 32 chip'lik PN dizisinden birine eşlenir. Böylece 4 bit, 32 chip ile temsil edilir (yayılma oranı 8).
3. **Chip → O-QPSK**: Çift numaralı chip'ler I (in-phase) koluna, tek numaralı chip'ler Q (quadrature) koluna yerleştirilir. Q kolu yarım chip süresi (0.5 µs) geciktirilir (Offset-QPSK).
4. **Yarım-sinüs darbe şekillendirme**: Her chip yarım sinüs darbesiyle şekillendirilir. Sonuç, MSK'ye benzeyen **sabit zarflı** bir sinyaldir; bu da verimli (doğrusal olmayan) güç yükselteçleri kullanılmasına izin verir — pil ömrü için önemlidir.

```text
 Bayt 0xA7  →  sembol 0x7, sembol 0xA  (önce düşük nibble)
 sembol 0x7 →  32 chip'lik PN dizisi #7
 32 chip    →  16 chip I kolunda + 16 chip Q kolunda (Q, Tc/2 kaydırılmış)
 1 sembol   =  32 chip / 2 Mchip/s = 16 µs
 250 kbit/s =  4 bit / 16 µs
```

**İşlem kazancı (processing gain)**: 32 chip / 4 bit → 10·log10(8) ≈ **9 dB**. Alıcı korelasyon yaparak gürültü ve dar bantlı girişime karşı bu kadar ek dayanıklılık kazanır. Bu nedenle 802.15.4 sinyalleri gürültü tabanına yakın seviyelerde bile çözülebilir.

### 3.4 PPDU (Fiziksel Paket) Yapısı

```text
+------------------+---------+-----------------+-----------------------------+
| Preamble         |   SFD   |      PHR        |           PSDU              |
| 4 bayt (0x00×4)  | 1 bayt  | 1 bayt          |   0–127 bayt                |
| 8 sembol         | 0xA7    | bit0-6: uzunluk |   (MAC çerçevesi = MPDU)    |
|                  |         | bit7: ayrılmış  |                             |
+------------------+---------+-----------------+-----------------------------+
|<------- SHR (5 bayt, 160 µs) ------>|<- 32 µs ->|<---- uzunluk × 32 µs ---->|
```

| Alan | Boyut | Açıklama |
|---|---|---|
| **Preamble** | 4 bayt | Tümü sıfır; alıcının bit/chip senkronizasyonu için |
| **SFD** (Start of Frame Delimiter) | 1 bayt | `0xA7`; çerçevenin başladığını işaretler |
| **PHR** (PHY Header) | 1 bayt | 7 bit çerçeve uzunluğu (0–127), 1 bit ayrılmış |
| **PSDU** | ≤127 bayt | MAC çerçevesi (MHR + yük + 2 bayt FCS) |

**Yayın süresi (airtime) hesabı:**

```text
Airtime = (5 + 1 + PSDU_uzunluğu) × 32 µs

127 baytlık en büyük çerçeve : (6 + 127) × 32 µs = 4256 µs ≈ 4.26 ms
5 baytlık Imm-ACK çerçevesi   : (6 + 5)   × 32 µs =  352 µs
```

### 3.5 Önemli PHY/MAC Zaman Sabitleri

| Sabit | Değer | Süre | Anlamı |
|---|---|---|---|
| Sembol süresi | 1 sembol | 16 µs | Temel zaman birimi |
| `aTurnaroundTime` | 12 sembol | 192 µs | RX↔TX geçiş süresi; ACK bu süre sonra gönderilir |
| `aUnitBackoffPeriod` | 20 sembol | 320 µs | CSMA-CA geri çekilme birimi |
| `aCCATime` | 8 sembol | 128 µs | Kanal boşluk değerlendirme (CCA) süresi |
| `macAckWaitDuration` | 54 sembol | 864 µs | ACK bekleme süresi |
| `aMaxSIFSFrameSize` | 18 bayt | — | Bu boyuta kadar çerçevelerden sonra kısa aralık |
| `macSIFSPeriod` | 12 sembol | 192 µs | Kısa çerçeveler arası boşluk (SIFS) |
| `macLIFSPeriod` | 40 sembol | 640 µs | Uzun çerçeveler arası boşluk (LIFS) |

### 3.6 Alıcı Ölçümleri: RSSI, LQI, ED ve Gürültü Tabanı

| Terim | Açıklama | Thread'de kullanımı |
|---|---|---|
| **RSSI** (Received Signal Strength Indicator) | Alınan çerçevenin sinyal gücü (dBm) | Link margin hesabı |
| **Gürültü tabanı (noise floor)** | Kanal boşken ölçülen arka plan gücü (tipik −95…−100 dBm) | Link margin hesabı |
| **Link Margin** | RSSI − gürültü tabanı (dB) | Link Quality (0–3) seviyesine dönüştürülür |
| **LQI** (Link Quality Indicator) | Alınan sinyalin kalitesi, 0–255; üreticiye özgü hesaplanır | Teşhis, Link Metrics |
| **ED** (Energy Detection) | Kanaldaki toplam enerji ölçümü | Energy Scan, CCA, kanal seçimi |

Thread, **Link Margin**'i şöyle bir **Link Quality (LQ)** seviyesine çevirir (ayrıntılar Bölüm 10):

| Link Margin | Link Quality | Bağlantı maliyeti (link cost) |
|---|---|---|
| > 20 dB | 3 (çok iyi) | 1 |
| > 10 dB | 2 (iyi) | 2 |
| > 2 dB | 1 (zayıf) | 4 |
| ≤ 2 dB | 0 (kullanılamaz) | ∞ (16) |

Eşikler arasında yaklaşık 2 dB'lik **histerezis** uygulanır; böylece sınırdaki bağlantılar seviyeler arasında sürekli zıplamaz.

### 3.7 CCA (Clear Channel Assessment)

Göndermeden önce kanalın boş olup olmadığına bakılır. 802.15.4 üç mod tanımlar:

| Mod | Ölçüt |
|---|---|
| **Mod 1** | Enerji eşiğin (ED threshold) üzerindeyse meşgul |
| **Mod 2** | 802.15.4 uyumlu bir sinyal (carrier) algılanırsa meşgul |
| **Mod 3** | Mod 1 ve/veya Mod 2 birlikte (AND / OR) |

Tipik CCA enerji eşiği yaklaşık **−75 dBm** civarındadır (platforma göre değişir). Eşik çok düşük seçilirse Wi-Fi gürültüsü yüzünden sürekli "kanal meşgul" hatası (CCA failure) alınır; çok yüksek seçilirse çakışmalar artar.

### 3.8 Wi-Fi ve Bluetooth ile Bir Arada Yaşama

Thread, Wi-Fi ve Bluetooth ile aynı 2.4 GHz bandını paylaşır. 20 MHz genişliğindeki Wi-Fi kanalları birçok Thread kanalını örter:

```text
MHz:   2400   2410   2420   2430   2440   2450   2460   2470   2480
        |------|------|------|------|------|------|------|------|
Wi-Fi1  [==== 2402–2422 ====]
Wi-Fi6                   [==== 2427–2447 ====]
Wi-Fi11                                   [==== 2452–2472 ====]
Wi-Fi13 (AB)                                        [==== 2462–2482 ====]
Thread   11  12  13  14 [15] 16  17  18  19 [20] 21  22  23  24 [25] 26
```

| Thread kanalı | Merkez | Wi-Fi 1/6/11 ile örtüşme | Not |
|---|---|---|---|
| **15** | 2425 MHz | Wi-Fi 1 ile 6 arasındaki boşlukta | Wi-Fi 1/6/11 planında iyi seçenek; BLE reklam kanalı 38'e (2426 MHz) yakın |
| **20** | 2450 MHz | Wi-Fi 6 ile 11 arasındaki boşlukta | İyi seçenek |
| **25** | 2475 MHz | Wi-Fi 11'in üstünde | Avrupa'da Wi-Fi 12/13 kullanılıyorsa örtüşür |
| **26** | 2480 MHz | Wi-Fi 11'in üstünde | ABD'de bant kenarı (2483.5 MHz) nedeniyle bazı ürünlerde düşük güç; BLE reklam kanalı 39 ile aynı frekans |
| 11–14, 16–19, 21–24 | — | Bir Wi-Fi kanalının içinde | Wi-Fi yoğunsa CCA hataları ve kayıplar artar |

**Bir arada yaşama (coexistence) yöntemleri:**

- **Kanal planlama**: Ortamın Wi-Fi kanallarını ölçüp (Energy Scan) en az örtüşen Thread kanalını seçmek.
- **PTA (Packet Traffic Arbitration)**: Aynı cihazda Wi-Fi ve 802.15.4 radyosu varsa (ör. Border Router, ESP32-C6, tri-radio çipler) radyolar 2/3 telli bir hakemlik arayüzüyle hangisinin göndereceğini koordine eder.
- **Anten izolasyonu**: Aynı kutudaki Wi-Fi ve Thread antenleri arasında fiziksel mesafe ve polarizasyon farkı.
- **Dinamik kanal yönetimi**: OpenThread'in *Channel Monitor* ve *Channel Manager* özellikleri kanalları periyodik örnekleyip gerekirse ağın kanalını değiştirebilir.

### 3.9 Bağlantı Bütçesi ve Menzil

**Bağlantı bütçesi (link budget)** = verici gücü + anten kazançları − alıcı hassasiyeti.

```text
Örnek: TX = +8 dBm, hassasiyet = −100 dBm, anten kazançları ≈ 0 dBi
Bütçe = 8 − (−100) = 108 dB
```

2.44 GHz'te serbest uzay yol kaybı (FSPL):

```text
FSPL(dB) ≈ 40.2 + 20·log10(d / 1 m)

d =  1 m  →  40 dB          d = 10 m  →  60 dB
d = 30 m  →  70 dB          d = 100 m →  80 dB
```

İç mekânda her duvar/kat için ek kayıplar eklenir (alçıpan ≈ 3–5 dB, tuğla ≈ 6–12 dB, betonarme ≈ 10–20 dB, metal yüzeyler çok daha fazla). Ayrıca çok yollu sönümlenme (multipath fading) için 10–20 dB pay bırakmak gerekir.

| Ortam | Tipik tek atlama menzili |
|---|---|
| İç mekân, birkaç duvar | 10–30 m |
| Açık alan, görüş hattı | 50–100+ m (FEM ile daha fazla) |

Mesh yapısı sayesinde tek atlama menzili sınırlı olsa da ağ, router ekledikçe kapsama alanını genişletir.

### 3.10 Etkin Veri Hızı (Throughput)

250 kbit/s ham hızdır; gerçek uygulama verimi çok daha düşüktür. Tek atlamada en büyük çerçeve için kaba bir hesap:

| Bileşen | Süre |
|---|---|
| Ortalama CSMA geri çekilme (BE = 3 → ortalama 3.5 × 320 µs) | ≈ 1120 µs |
| CCA + RX→TX geçişi | 128 + 192 = 320 µs |
| 127 baytlık çerçeve | 4256 µs |
| ACK öncesi geçiş + ACK çerçevesi | 192 + 352 = 544 µs |
| **Toplam** | **≈ 6.24 ms / çerçeve** |

127 baytlık çerçevenin içinde MAC başlığı, güvenlik başlığı, MIC, FCS, 6LoWPAN parçalama/sıkıştırma ve UDP başlıkları çıktıktan sonra yaklaşık **80–90 bayt** uygulama verisi kalır:

```text
Tek atlama, en iyi durum : 85 bayt × 8 / 6.24 ms ≈ 109 kbit/s
Çok atlama (aynı kanal)  : her atlama aynı kanalı paylaştığı için verim
                           kabaca atlama sayısıyla bölünür
3 atlama                 : ≈ 30–40 kbit/s
```

Gerçek ağlarda yeniden iletimler, Wi-Fi girişimi ve kontrol trafiği nedeniyle tipik uygulama verimi **onlarca kbit/s** düzeyindedir. Bu, sensör/aktüatör trafiği için fazlasıyla yeterlidir; ancak OTA yazılım güncellemeleri gibi büyük aktarımlar dakikalar sürebilir (Bölüm 26).

### 3.11 Bölüm Özeti

- Thread yalnızca 2.4 GHz, 16 kanallı, 250 kbit/s O-QPSK PHY kullanır; ağ tek kanalda çalışır.
- DSSS ≈ 9 dB işlem kazancı ve sabit zarflı modülasyon, düşük güç ve gürültüye dayanıklılık sağlar.
- En büyük çerçeve 127 bayttır ve ≈ 4.26 ms sürer; bu sınır üst katmanlarda sıkıştırma ve parçalamayı zorunlu kılar.
- Link margin → Link Quality (0–3) → link cost dönüşümü, yönlendirmenin temelidir.
- Wi-Fi ile çakışmayı azaltmak için 15, 20, 25 (ve bölgeye göre 26) numaralı kanallar genelde daha temizdir.
