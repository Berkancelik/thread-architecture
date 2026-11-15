## 25. Donanım, Çipler ve RF Tasarımı

### 25.1 Thread Destekli Popüler Çipler

> [!NOTE]
> Aşağıdaki değerler yaklaşık ve özet niteliğindedir; ürün varyantına, paketine, besleme gerilimine ve yazılım sürümüne göre değişir. Tasarım kararları için ilgili veri sayfasını (datasheet) esas alın.

| Üretici | Çip / aile | Çekirdek | Bellek (flash / RAM) | Radyolar | Azami TX | Not |
|---|---|---|---|---|---|---|
| Nordic | **nRF52840** | Cortex-M4F 64 MHz | 1 MB / 256 KB | 802.15.4, BLE | +8 dBm | Çok yaygın; USB; dongle'ı sniffer/RCP olarak popüler |
| Nordic | nRF5340 | 2 × Cortex-M33 | 1 MB+256 KB / 512 KB+64 KB | 802.15.4, BLE | +3 dBm | Uygulama ve ağ çekirdeği ayrı |
| Nordic | nRF54L serisi | Cortex-M33 128 MHz | ≈ 1.5 MB / 256 KB (L15) | 802.15.4, BLE | +8 dBm | Yeni nesil, düşük güç |
| Silicon Labs | **EFR32MG21** | Cortex-M33 80 MHz | ≤ 1 MB / ≤ 96 KB | 802.15.4, BLE | +20 dBm | Yüksek çıkış gücü; BR radyosu olarak yaygın |
| Silicon Labs | **EFR32MG24** | Cortex-M33 78 MHz | ≤ 1.5 MB / ≤ 256 KB | 802.15.4, BLE | +20 dBm | Matter için popüler; AI/ML hızlandırıcı |
| Texas Instruments | CC2652R7 / CC2674 ailesi | Cortex-M4F / M33 48 MHz | ≈ 704 KB–1 MB / 144–256 KB | 802.15.4, BLE | +5 dBm (P varyantları +20 dBm) | Çok protokollü |
| NXP | K32W0x1, MCX W7x | Cortex-M4 / M33 | ≈ 0.5–1 MB / 128–152 KB | 802.15.4, BLE | ≈ +10 dBm | Düşük güç |
| NXP | **RW612** | Cortex-M33 | harici flash | **Wi-Fi 6 + BLE + 802.15.4** | — | Tek çipte Border Router için üçlü radyo |
| Espressif | **ESP32-H2** | RISC-V 96 MHz | 2–4 MB (pakette) / 320 KB | 802.15.4, BLE | +20 dBm | Uygun maliyetli Thread/Zigbee |
| Espressif | **ESP32-C6** | RISC-V 160 MHz | harici / 512 KB | **Wi-Fi 6 + BLE + 802.15.4** | +20 dBm | Wi-Fi ve Thread tek çipte (zaman paylaşımlı radyo) |
| Qorvo, Telink, Realtek, Infineon vb. | çeşitli | — | — | 802.15.4 (+BLE) | — | Belirli ürün segmentleri |

### 25.2 Çip Seçerken Dikkat Edilecekler

| Kriter | Neden önemli? |
|---|---|
| **Flash/RAM** | Matter + Thread FTD + OTA için genellikle ≥ 1 MB flash (OTA'da çift imaj için daha fazla) ve ≥ 128–256 KB RAM gerekir |
| **Uyku akımı** | SED ömrünü belirler (RAM korumalı uyku ≈ 1–3 µA) |
| **RX/TX akımı** | Poll ve rapor başına enerji |
| **Hassasiyet ve TX gücü** | Bağlantı bütçesi → menzil ve güvenilirlik |
| **Kripto hızlandırıcı / güvenli depolama** | AES-CCM, ECC (CASE/EC-JPAKE) hızları; anahtar koruması |
| **Zamanlı gönderim ve hassas zamanlayıcı** | CSL (SSED ve CSL ebeveyni) için gerekli |
| **Çoklu protokol** | Thread + BLE (Matter devreye alma için BLE şart) |
| **SDK ve sertifika** | Sertifikalı Thread/Matter yığını, uzun süreli destek |

### 25.3 RF Ön Uç (Front-End)

- **FEM (Front-End Module)**: PA (güç yükselteci) + LNA (düşük gürültülü alıcı yükselteci) + anahtarlar. Border Router ve router'larda menzili belirgin şekilde artırır.
- **Yasal sınırlar**: Avrupa'da (ETSI EN 300 328) 2.4 GHz geniş bant sistemleri için azami EIRP 20 dBm (100 mW); ABD'de (FCC Part 15.247) daha yüksek iletim gücü mümkündür ama **kanal 26** gibi bant kenarına yakın kanallarda bant dışı emisyon sınırları nedeniyle güç düşürülmesi gerekebilir.
- **Simetri**: Yalnızca TX gücünü artırmak asimetrik bağlantılar yaratır (A, B'yi duyar ama B, A'yı duyamaz). LNA ile alım hassasiyetini de iyileştirmek ve çift yönlü link kalitesini dengelemek gerekir — Thread'in yönlendirmesi zaten çift yönlü kaliteye bakar.

### 25.4 Anten Tasarımı

| Anten tipi | Avantaj | Dezavantaj |
|---|---|---|
| PCB anten (ters-F, menderes) | Maliyetsiz | Kart alanı ister; ayara (tuning) duyarlı |
| Çip anten | Küçük | Toprak düzlemine ve yerleşime çok duyarlı; verim daha düşük |
| Harici (dipol, U.FL) | En iyi performans | Maliyet, mekanik tasarım |

**Yerleşim ipuçları:**

- Antenin altında ve çevresinde **bakır içermeyen (keep-out) bölge** bırakın; üretici referans tasarımına birebir uyun.
- Anteni pil, metal kasa, ekran ve yüksek akımlı hatlardan uzak tutun.
- **Empedans uyumlama (matching) ağı** için yer bırakın; nihai kasa içinde ölçüm yaparak ayarlayın (kasa ve el yakınlığı rezonansı kaydırır).
- Wi-Fi ve Thread antenleri aynı cihazdaysa (BR) aralarında mümkün olduğunca fazla **izolasyon** (mesafe, polarizasyon farkı) sağlayın.

### 25.5 Saat Kaynakları

| Saat | Gereksinim | Neden? |
|---|---|---|
| Yüksek frekans kristali (ör. 32 MHz) | ±40 ppm (802.15.4 şartı) | Taşıyıcı frekans doğruluğu, sembol zamanlaması |
| Düşük frekans kristali (32.768 kHz) | ±20–50 ppm (CSL için önemli) | Uyku zamanlayıcısı; CSL senkronizasyon penceresi |
| RC osilatör (kristal yerine) | Periyodik kalibrasyon | Maliyet tasarrufu, ama CSL ve uzun uyku aralıklarında ek pencere payı gerekir |

### 25.6 Border Router Donanım Seçenekleri

| Seçenek | Açıklama |
|---|---|
| **Tümleşik ürünler** | Akıllı hoparlörler, TV kutuları, hub'lar, Thread destekli Wi-Fi router'lar (Matter 1.4 HRAP) |
| **Linux + USB RCP** | Raspberry Pi / mini PC + nRF52840, EFR32MG21/MG24, ESP32-H2 gibi bir RCP dongle; OTBR veya Home Assistant OTBR eklentisi |
| **Tek çipli BR** | Wi-Fi + 802.15.4 içeren SoC'ler (ESP32-C6, RW612) ile gömülü BR'ler (aynı radyoyu zaman paylaşımlı kullanan çözümlerde performans kısıtlarına dikkat) |

### 25.7 Geliştirme Kitleri

- nRF52840 DK / Dongle, nRF5340 DK, nRF54L15 DK (Nordic)
- EFR32xG24 / xG21 geliştirme kitleri (Silicon Labs)
- CC2652R7 / CC2674 LaunchPad (TI)
- ESP32-H2-DevKitM, ESP32-C6-DevKitC (Espressif)
- NXP FRDM / K32W kitleri

### 25.8 Bölüm Özeti

- Thread çipleri çoğunlukla Cortex-M veya RISC-V tabanlı, 802.15.4 + BLE içeren SoC'lerdir; Matter için ≥ 1 MB flash yaygındır.
- FEM'ler menzili artırır ama yasal sınırlar ve çift yönlü link dengesi gözetilmelidir.
- Anten yerleşimi ve kasa etkisi pratik menzilin en büyük belirleyicilerindendir.
- CSL ve uzun uyku için düşük frekans saatinin doğruluğu önemlidir.
- Border Router'lar tümleşik ürünler, Linux + RCP veya tek çipli çözümlerle kurulabilir.
