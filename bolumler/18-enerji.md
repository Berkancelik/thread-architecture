## 18. Uyuyan Cihazlar, Enerji Yönetimi ve CSL

### 18.1 Enerji Tüketiminin Kaynakları

Pille çalışan bir Thread cihazında enerjinin büyük kısmı radyoya gider. Tipik akım değerleri (çipe ve gerilime göre değişir):

| Durum | Tipik akım | Not |
|---|---|---|
| Derin uyku (RAM korumalı, RTC çalışıyor) | ≈ 1–3 µA | Cihaz zamanının > %99'unu burada geçirir |
| MCU aktif | ≈ 2–6 mA | Çip ve saat frekansına bağlı |
| Radyo alma (RX) | ≈ 4–10 mA | DC/DC dönüştürücü ile daha düşük |
| Radyo gönderme (TX, 0 dBm) | ≈ 5–10 mA | +8…+10 dBm'de 10–20 mA; FEM ile çok daha fazla |
| Kristal/radyo başlatma | kısa süreli tepe | Her uyanmada ek maliyet |

Enerji = akım × süre olduğu için tasarımın amacı, radyonun **açık kalma süresini** en aza indirmektir.

### 18.2 SED Çalışma Modeli

**Sleepy End Device (SED)** radyosunu kapalı tutar ve iki durumda uyanır:

1. **Uygulama olayı**: Sensör değeri değişti, düğmeye basıldı → veri gönderir.
2. **Poll zamanlayıcısı**: Belirli aralıklarla (**poll period**) ebeveynine **MAC Data Request** gönderip bekleyen veri olup olmadığını sorar (Bölüm 4.7).

| Parametre | Açıklama | Etkisi |
|---|---|---|
| **Poll period** | İki sorgu arasındaki süre | Kısa → düşük gecikme, yüksek tüketim; uzun → yüksek gecikme, düşük tüketim |
| **Child timeout** | Ebeveynin, sessiz kalan çocuğu silmeden önce beklediği süre (Timeout TLV) | Poll period'dan belirgin şekilde uzun olmalı |
| **Fast poll** | Bir istek gönderdikten sonra cevabı hızlı almak için geçici olarak sık poll | Cevap gecikmesini düşürür |

**Gecikme ilişkisi:** Bir SED'e giden mesaj, en kötü durumda bir poll period kadar ebeveynde bekler. 30 saniyelik poll period'lu bir kapı kilidine gönderilen "kilitle" komutu 30 saniye gecikebilir — bu yüzden etkileşimli cihazlarda kısa poll period, CSL veya Matter ICD'nin "aktif mod" mekanizmaları kullanılır.

### 18.3 Enerji Bütçesi Örneği

Kaba bir hesap (değerler örnek amaçlıdır):

```text
Uyku akımı              : 2 µA
Bir poll'un yükü        : ≈ 3 ms boyunca ortalama ≈ 10 mA   →  ≈ 30 µC
                          (kristal başlatma + CSMA + TX Data Request + ACK bekleme)

Poll period = 30 s      : 30 µC / 30 s = 1.0 µA
Ortalama                : 2 + 1.0 = 3.0 µA

Pil: CR2032 ≈ 220 mAh   : 220 mAh / 3.0 µA ≈ 73 000 saat ≈ 8 yıl (yalnızca poll + uyku)
```

Gerçek ömür; sensör ölçümleri, raporlar (ör. her 5 dakikada bir Matter raporu), yeniden iletimler, pilin kendi kendine boşalması ve sıcaklık etkileriyle bunun altında kalır. Yine de hesap, **poll period'un ve uyanma maliyetinin** ömrü belirleyen ana etkenler olduğunu gösterir:

| Poll period | Ortalama poll akımı (30 µC/poll) | Toplam (2 µA uyku ile) |
|---|---|---|
| 0.25 s | 120 µA | 122 µA (≈ 2.5 ay) |
| 1 s | 30 µA | 32 µA (≈ 9 ay) |
| 5 s | 6 µA | 8 µA (≈ 3 yıl) |
| 30 s | 1 µA | 3 µA (≈ 8 yıl) |
| 300 s | 0.1 µA | 2.1 µA (≈ 12 yıl) |

### 18.4 Child Timeout ve Canlı Tutma

- Çocuk, **Timeout TLV** ile ebeveynine bir zaman aşımı değeri bildirir (OpenThread varsayılanı 240 s).
- Ebeveyn bu süre boyunca çocuktan **hiçbir şey** duymazsa onu çocuk tablosundan siler ve onun için kuyruktaki paketleri atar.
- SED'in **poll'ları** etkinlik sayılır; ayrıca bir şey göndermesi gerekmez.
- Çocuk, kendi tarafında da zaman aşımından önce mutlaka bir mesaj (poll veya Child Update Request) gönderecek şekilde zamanlama yapar.
- Thread 1.2+ **Enhanced Keep-Alive**: Ebeveyne giden herhangi bir MAC veri çerçevesi canlılık göstergesi sayılır; MLE Child Update'e duyulan ihtiyaç azalır.

### 18.5 Child Supervision (Çocuk Denetimi)

Sorun: Ebeveyn kapanırsa, seyrek poll eden (veya hiç poll etmeyip yalnızca olay olduğunda veri gönderen) bir SED bunu uzun süre fark etmeyebilir; bu sürede ona gönderilen her şey kaybolur.

Çözüm — **Child Supervision**:

- Ebeveyn, bir çocuğa **supervision interval** süresince hiç çerçeve göndermediyse ona boş bir "denetim" çerçevesi kuyruğa koyar (çocuk poll edince alır).
- Çocuk, **supervision check timeout** süresince ebeveyninden hiçbir çerçeve almazsa ebeveynin kaybolduğunu varsayar ve yeniden bağlanma sürecini başlatır.
- Thread 1.3 ile denetim aralığı **Supervision Interval TLV** (MLE) ile çocuk tarafından ebeveyne bildirilir.

| Parametre | OpenThread varsayılanı |
|---|---|
| Supervision interval (ebeveyn) | 129 s |
| Supervision check timeout (çocuk) | 190 s |

### 18.6 Enhanced Frame Pending (Thread 1.2+)

Klasik 802.15.4'te Frame Pending biti yalnızca **Data Request**'e verilen ACK'de anlamlıdır. Thread 1.2 ile ebeveyn, SED'in gönderdiği **herhangi bir veri çerçevesinin** (Enhanced) ACK'inde Frame Pending = 1 ayarlayarak "senin için veri var" diyebilir. SED böylece ayrı bir Data Request göndermeden alıcısını açık tutar → bir uyanma ve bir TX tasarruf edilir. Özellikle istek-cevap trafiğinde (SED soru sorar, cevap hemen gelir) etkilidir.

### 18.7 CSL — Coordinated Sampled Listening (Thread 1.2+)

**CSL**, uyuyan cihazlara **düşük gecikmeyle ve düşük enerjiyle** veri ulaştırmak için tasarlanmış bir mekanizmadır. CSL kullanan uç cihaza **SSED (Synchronized Sleepy End Device)** denir.

#### Fikir

- SSED, **düzenli aralıklarla** (CSL period) çok kısa bir süre (birkaç milisaniye) kanalı **dinler** (sample). Gönderme yapmaz.
- Ebeveyn, SSED'in bir sonraki dinleme anını **bilir** ve göndereceği çerçeveyi tam o ana **zamanlar** (timed transmission).
- Poll'daki "TX Data Request + CSMA + ACK bekleme" maliyeti ortadan kalkar; her döngüde yalnızca kısa bir RX penceresi açılır.

```text
SSED radyosu:   ▁▁▁█▁▁▁▁▁▁▁▁▁█▁▁▁▁▁▁▁▁▁█▁▁▁▁▁▁▁▁▁█▁▁▁▁▁▁   (█ = kısa dinleme penceresi)
                   |<-- CSL period -->|
Ebeveyn TX:                           ▓                       (çerçeve, pencereye denk gelecek şekilde)
```

#### Senkronizasyon

| Bilgi | Taşıyıcı | Açıklama |
|---|---|---|
| **CSL Period** | MAC **CSL IE** (SSED'den ebeveyne giden çerçevelerde) | Dinleme periyodu, 10 sembol (160 µs) biriminde |
| **CSL Phase** | MAC **CSL IE** | Çerçevenin gönderildiği andan bir sonraki dinleme anına kalan süre (160 µs biriminde) |
| **CSL Channel** | MLE **CSL Channel TLV** | Dinlemenin yapılacağı kanal (genellikle ağ kanalı) |
| **CSL Synchronized Timeout** | MLE TLV | SSED'in en geç ne kadar sürede yeniden senkronizasyon sağlayacağı |
| **CSL Clock Accuracy** | MLE TLV | Saat doğruluğu (ppm) ve belirsizlik |

- SSED'in ebeveynine gönderdiği her çerçeve (veri veya ACK'li çerçeveler) CSL IE taşıdığı için ebeveyn zamanlamayı sürekli tazeler.
- SSED, **CSL Synchronized Timeout** süresi içinde hiçbir şey göndermezse ebeveyn senkronu kaybolmuş sayar; SSED bu süreden önce en az bir çerçeve (ör. boş veri veya poll) gönderir.

#### Saat kayması (drift) ve pencere genişliği

İki cihazın saatleri farklı hızlarda çalışır. Son senkrondan bu yana geçen süre arttıkça belirsizlik büyür:

```text
Belirsizlik ≈ geçen_süre × (ppm_ebeveyn + ppm_SSED) × 10⁻⁶ + sabit belirsizlik

Örnek: son senkrondan 60 s sonra, ±20 ppm + ±20 ppm saatler
       60 s × 40 × 10⁻⁶ = 2.4 ms  →  pencere her iki yönde ≈ 2.4 ms genişletilmeli
```

Bu yüzden CSL; doğru düşük frekans kristalleri (32.768 kHz, ±20–50 ppm) ve sık senkronizasyon ister. Ebeveyn, gönderimi pencerenin ortasına denk getirmek için kendi hesabını yapar.

#### SED (poll) ile SSED (CSL) karşılaştırması

| Özellik | SED (poll) | SSED (CSL) |
|---|---|---|
| Aşağı yön veri alma | Cihaz sorar (TX + RX) | Ebeveyn zamanlar, cihaz sadece dinler (RX) |
| Her döngünün maliyeti | ≈ birkaç ms TX/RX + CSMA | ≈ 1–2 ms RX penceresi |
| Tipik gecikme | Poll period (saniyeler–dakikalar) | CSL period (yüz milisaniyeler) |
| Ebeveyn gereksinimi | Her Thread router | Thread 1.2+ ebeveyn, zamanlı gönderim destekli radyo |
| Saat gereksinimi | Gevşek | Hassas (ppm), senkronizasyon |

**Örnek karşılaştırma (500 ms gecikme hedefi):**

```text
SED, poll = 500 ms   : 30 µC × 2 Hz            ≈ 60 µA
SSED, CSL = 500 ms   : ≈ 1.5 ms × 6 mA × 2 Hz  ≈ 18 µA   (+ periyodik senkron çerçeveleri)
```

### 18.8 Matter ICD (Intermittently Connected Device)

Matter, Thread uyuyan cihazlarının davranışını uygulama seviyesinde **ICD** (Intermittently Connected Device) kavramıyla standartlaştırır:

| Kavram | Açıklama | Thread karşılığı |
|---|---|---|
| **Idle Mode** | Cihaz çoğu zaman bu moddadır; seyrek uyanır | Uzun poll period (yavaş poll) |
| **Active Mode** | Etkileşim sırasında; hızlı cevap verir | Kısa poll period (hızlı poll) |
| **Idle Mode Duration** | Idle moddaki uyanma aralığı | Slow poll interval |
| **Active Mode Duration / Threshold** | Etkileşimden sonra aktif kalma süresi | Fast poll süresi |
| **SIT ICD** (Short Idle Time) | Yavaş poll aralığı kısa (≤ 15 s mertebesinde); denetleyici her an ulaşabilir | Klasik SED |
| **LIT ICD** (Long Idle Time) | Çok uzun uyku; denetleyiciye **Check-In** mesajlarıyla haber verir | Çok uzun poll period |

Matter'ın **MRP** (Message Reliability Protocol) yeniden iletim zamanlamaları da cihazın uyku/aktif aralıklarına göre ayarlanır; bu aralıklar DNS-SD kayıtlarında (`SII`, `SAI` anahtarları) ilan edilir. Ayrıntılar Bölüm 23.

### 18.9 Enerji Tasarımı İpuçları

1. **Mümkün olan en uzun poll period**'u seçin; etkileşim gerektiğinde fast poll / ICD aktif modunu kullanın.
2. **Ağ verisinden yalnızca stable kısmı** isteyin (Mode N = 0); gereksiz uyanmaları azaltır.
3. **Çoklu yayından kaçının**; SED'e ulaşan her çoklu yayın ayrı bir dolaylı iletimdir.
4. **İyi bir ebeveyn** seçimini sağlayın: Zayıf bağlantı = yeniden iletimler = boşa enerji. Kurulumda en az bir iyi router'ın yakında olduğundan emin olun.
5. **TX gücünü** ihtiyaca göre ayarlayın; gereğinden yüksek güç pil tüketir, gereğinden düşük güç yeniden iletim artırır.
6. **Raporları toplu gönderin**: Birden çok ölçümü tek mesajda birleştirin; her mesajın sabit bir uyanma maliyeti vardır.
7. **Uygulama yükünü küçük tutun**: Parçalanan paketler birden çok TX demektir.
8. **CSL** gerektiren cihazlarda düşük frekans kristalinin doğruluğuna dikkat edin.
9. **Matter abonelik (subscription) aralıklarını** (min/max interval) cihazın uyku profiline uygun seçin.

### 18.10 Bölüm Özeti

- Pilli cihazlarda enerjinin çoğu radyoya gider; hedef, radyonun açık kalma süresini en aza indirmektir.
- SED, poll period ile gecikme/enerji dengesi kurar; child timeout ve child supervision bağlantının sağlığını korur.
- Thread 1.2 Enhanced Frame Pending ve Enhanced Keep-Alive gereksiz uyanmaları azaltır.
- CSL, ebeveynin zamanlanmış gönderimiyle SSED'lere düşük gecikmeli ve verimli veri ulaştırır; hassas saat gerektirir.
- Matter ICD; aktif/boşta modları ve Check-In ile uyuyan cihaz davranışını uygulama seviyesinde standartlaştırır.
