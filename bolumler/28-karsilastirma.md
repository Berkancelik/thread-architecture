## 28. Diğer IoT Protokolleriyle Karşılaştırma

### 28.1 Genel Karşılaştırma Tablosu

| Özellik | **Thread** | Zigbee | Z-Wave | BLE Mesh | Wi-Fi (2.4 GHz) | Wi-SUN FAN | LoRaWAN |
|---|---|---|---|---|---|---|---|
| Standart kuruluşu | Thread Group (+IEEE, IETF) | CSA | Z-Wave Alliance (ITU G.9959 tabanlı) | Bluetooth SIG | IEEE / Wi-Fi Alliance | Wi-SUN Alliance (+IEEE, IETF) | LoRa Alliance |
| Fiziksel katman | 802.15.4, 2.4 GHz | 802.15.4, 2.4 GHz (+ sub-GHz) | Sub-GHz (868/908 MHz vb.) | BLE 2.4 GHz | 802.11 | 802.15.4g sub-GHz | LoRa (sub-GHz) |
| Ham veri hızı | 250 kbit/s | 250 kbit/s | 9.6–100 kbit/s | 1 Mbit/s (PHY) | 10'larca–100'lerce Mbit/s | 50–300 kbit/s | 0.3–50 kbit/s |
| Topoloji | Mesh (router omurgası + uç cihazlar) | Mesh (coordinator + router'lar) | Mesh (kaynak yönlendirmeli) | Yönetilen taşma (flooding) | Yıldız | Mesh (RPL) | Yıldızların yıldızı |
| IP tabanlı mı? | **Evet (IPv6)** | Hayır | Hayır | Hayır | Evet | Evet (IPv6) | Hayır |
| Uygulama katmanı | Tanımlamaz (Matter vb.) | ZCL (Zigbee Cluster Library) | Z-Wave komut sınıfları | Mesh modelleri | Tanımlamaz | Tanımlamaz | Tanımlamaz |
| Tek hata noktası | Yok (Leader ve BR yedekli) | Coordinator (Trust Center) | Birincil denetleyici | Yok (sağlayıcı bağımlı) | Erişim noktası | Border router | Ağ sunucusu/gateway |
| Güvenlik | AES-128-CCM, EC-JPAKE / bant dışı | AES-128, install code | S2 (ECDH + AES) | AES-CCM, iki katmanlı anahtar | WPA2/WPA3 | IEEE 802.1X/EAP-TLS | AES-128 (oturum anahtarları) |
| Güç | Çok düşük (SED/SSED) | Çok düşük | Çok düşük | Düşük–orta | Yüksek | Düşük (sub-GHz) | Çok düşük |
| Tipik menzil (tek atlama) | 10–30 m iç mekân | 10–30 m | 30–100 m (sub-GHz) | 10–30 m | 30–50 m | 100'lerce m | km'ler |
| Matter desteği | **Yerel taşıma** | Köprü (bridge) ile | Köprü ile | Yalnızca devreye alma için BLE | **Yerel taşıma** | — | — |
| Tipik kullanım | Akıllı ev, bina | Akıllı ev, aydınlatma | Akıllı ev güvenlik | Aydınlatma, beacon | Kameralar, yüksek veri | Akıllı şehir, sayaçlar | Geniş alan sensörleri |

### 28.2 Thread ve Zigbee: Aynı Radyo, Farklı Mimari

Thread ve Zigbee aynı 802.15.4 radyosunu kullandığı için en sık karşılaştırılan ikilidir:

| Konu | Thread | Zigbee |
|---|---|---|
| Ağ katmanı | IPv6 + 6LoWPAN + Thread yönlendirmesi | Zigbee NWK (16 bit adresler, AODV benzeri / ağaç yönlendirme) |
| İnternet/telefon erişimi | Border Router ile doğrudan IP yönlendirme | Gateway ile protokol çevirisi |
| Merkezi düğüm | Yok; Leader herhangi bir router olabilir | Coordinator (genellikle Trust Center) |
| Çoklu sağlayıcı ağ geçidi | Birden çok BR aynı ağda | Genellikle tek coordinator |
| Uygulama katmanı | Matter (ayrı standart) | ZCL (yığına gömülü) |
| Olgunluk ve cihaz yelpazesi | Hızla büyüyor | Çok olgun, çok geniş cihaz yelpazesi |
| Birlikte çalışma | Aynı çipte farklı zamanlarda/eşzamanlı (çoklu protokol) çalışabilir | — |

**Pratik sonuç:** Zigbee'nin geniş cihaz tabanı köprülerle Matter'a bağlanabilirken, yeni ürünlerde Thread + Matter, "gateway'siz IP" ve çok üreticili Border Router avantajları nedeniyle öne çıkmaktadır.

### 28.3 Thread ve Wi-Fi (Matter Açısından)

| Konu | Thread | Wi-Fi |
|---|---|---|
| Güç tüketimi | Pille yıllar | Genellikle şebeke; pilli cihazlarda sınırlı |
| Veri hızı | Düşük (sensör/kontrol için yeterli) | Yüksek (kamera, ses, video) |
| Erişim noktası yükü | Wi-Fi AP'yi yormaz | Her cihaz AP'ye bağlanır; çok cihazda AP sınırları |
| Kapsama | Mesh ile kendiliğinden genişler | AP/mesh Wi-Fi sistemine bağlı |
| Altyapı gereksinimi | Border Router | Wi-Fi AP |
| Uygun cihazlar | Sensörler, kilitler, prizler, ampuller, düğmeler | Kameralar, hoparlörler, büyük beyaz eşyalar |

### 28.4 Thread ve BLE Mesh

- BLE Mesh, IP tabanlı değildir; mesajlar "yönetilen taşma" ile birçok düğüm tarafından yeniden yayınlanır. Basit ve kurulumu kolaydır ama büyük ağlarda kanal verimi düşebilir.
- Thread, yönlendirme tablolarıyla hedefe yönelik iletim yapar; IPv6 sayesinde internet ve diğer IP ağlarıyla doğal entegrasyon sunar.
- Matter, BLE'yi yalnızca **devreye alma** için kullanır; operasyonel iletişim Thread veya Wi-Fi üzerindendir.

### 28.5 Thread ve Wi-SUN

Her ikisi de 802.15.4 + 6LoWPAN + IPv6 kullanır; ancak:

- **Wi-SUN FAN** sub-GHz (802.15.4g), frekans atlamalı, **RPL** yönlendirmeli ve kilometrelerce alana yayılan şehir/altyapı ağları içindir.
- **Thread** 2.4 GHz, tek kanallı, mesafe-vektör yönlendirmeli ve ev/bina ölçeği içindir.

### 28.6 Bölüm Özeti

- Thread'in ayırt edici özellikleri: IPv6'nın uç cihaza kadar gitmesi, tek hata noktasının olmaması, düşük güç ve Matter'ın yerel taşıması olması.
- Zigbee aynı radyoyu kullanır ama IP tabanlı değildir ve coordinator'a bağımlıdır.
- Wi-Fi yüksek veri gerektiren cihazlar, Thread düşük güçlü kontrol/sensör cihazları için uygundur; Matter ikisini birlikte kullanır.
