<!-- Bu dosya tools/build.py tarafından bolumler/ klasöründen otomatik üretilir. Düzenlemeleri bolumler/ altında yapıp betiği yeniden çalıştırın. -->

# Thread Ağ Mimarisi ve Haberleşme Yapısı — Kapsamlı Teknik Rehber

> IEEE 802.15.4 radyosu üzerinde IPv6 konuşan, düşük güçlü, kendi kendini onaran mesh ağ protokolü **Thread**'in fiziksel katmandan uygulama katmanına (Matter) kadar tüm mimarisi, mesaj akışları, adresleme ve yönlendirme mantığı, güvenlik modeli, Border Router işlevleri ve pratik kullanımı.

| Özellik | Değer |
|---|---|
| **Kapsam** | Thread 1.1 → 1.4, OpenThread, Thread Border Router, Matter over Thread |
| **Dil** | Türkçe (teknik terimler orijinal İngilizce adlarıyla birlikte verilmiştir) |
| **Seviye** | Temelden uzmanlığa: her bölüm önce kavramı, sonra bit/bayt seviyesindeki ayrıntıyı anlatır |
| **Biçim** | Tek parça Markdown + aynı içeriğin kenar menülü HTML sürümü |
| **Doküman sürümü** | 1.0 — Kasım 2026 |

## 0. Bu Doküman Hakkında

### 0.1 Kimler İçin?

Bu rehber şu okuyucular düşünülerek hazırlanmıştır:

- **Gömülü yazılım geliştiricileri** — OpenThread veya üretici SDK'ları (Nordic, Silicon Labs, TI, NXP, Espressif) ile Thread cihazı geliştirenler.
- **IoT / akıllı ev mimarları** — Matter tabanlı ürün ve ağ tasarlayanlar, Border Router seçimi ve ağ planlaması yapanlar.
- **Ağ mühendisleri** — IPv6, 6LoWPAN, mesh yönlendirme ve güvenlik konularını Thread özelinde derinlemesine öğrenmek isteyenler.
- **Test / saha ekipleri** — Sniffer ile paket analizi yapan, kopma, gecikme, pil tüketimi gibi sorunları teşhis edenler.
- **Meraklı öğrenciler** — "Akıllı ampulüm telefonumla nasıl konuşuyor?" sorusunun her katmandaki cevabını bilmek isteyenler.

### 0.2 Nasıl Okunmalı?

Doküman katmanlı bir sırayla ilerler: önce büyük resim (Bölüm 1–2), sonra radyodan yukarıya doğru katmanlar (Bölüm 3–6), ardından Thread'in kendine özgü kontrol düzlemi (Bölüm 7–14), güvenlik ve devreye alma (Bölüm 15–17), enerji ve Border Router (Bölüm 18–19), sürüm özellikleri ve teşhis (Bölüm 20–21), uçtan uca senaryolar ve Matter (Bölüm 22–23), yazılım/donanım/tasarım (Bölüm 24–27), karşılaştırma ve ekler (Bölüm 28–29).

- Hızlı bir genel bakış için: **Bölüm 1, 2, 7, 8, 22**.
- Paket seviyesinde derinlik için: **Bölüm 4, 5, 9, 10, 13**.
- Güvenlik odaklı okuma için: **Bölüm 15, 16, 17**.
- Ürün geliştirme için: **Bölüm 18, 19, 23, 24, 26, 27**.

### 0.3 Gösterim Kuralları

| Gösterim | Anlamı |
|---|---|
| `0x1A` | Onaltılık (hex) değer |
| `0b0110` | İkili (binary) değer |
| `fd00::/8` | IPv6 öneki (prefix) ve uzunluğu |
| **RLOC16** | İlk geçtiği yerde kalın yazılan teknik terim; sözlükte (Ek E) açıklaması vardır |
| `a/aq` | Thread yönetim mesajı (CoAP URI yolu) |
| bit 7 … bit 0 | Bayt içindeki bitler en anlamlıdan (MSB) en anlamsıza (LSB) doğru numaralanır |
| LE / BE | Little-endian / Big-endian bayt sırası |
| ≈ | Yaklaşık değer; donanıma, yapılandırmaya veya yazılım sürümüne göre değişir |

> [!NOTE]
> Thread şartnamesi (Thread Specification) Thread Group tarafından yayımlanır. Bu dokümandaki sabitler ve varsayılan değerler şartname ile yaygın açık kaynak uygulama OpenThread'deki karşılıkları esas alınarak verilmiştir. "OpenThread varsayılanı" ifadesi geçen değerler derleme zamanında veya çalışma anında değiştirilebilir; kesin ürün davranışı için kullandığınız SDK sürümünün belgelerine bakın.

## İçindekiler

- [0. Bu Doküman Hakkında](#0-bu-doküman-hakkında)
  - [0.1 Kimler İçin?](#01-kimler-i̇çin)
  - [0.2 Nasıl Okunmalı?](#02-nasıl-okunmalı)
  - [0.3 Gösterim Kuralları](#03-gösterim-kuralları)
- [1. Thread'e Giriş](#1-threade-giriş)
  - [1.1 Thread Nedir?](#11-thread-nedir)
  - [1.2 Neden Thread? Çözdüğü Problemler](#12-neden-thread-çözdüğü-problemler)
  - [1.3 Tarihçe](#13-tarihçe)
  - [1.4 Sürümlerin Özeti](#14-sürümlerin-özeti)
  - [1.5 Thread Group ve Sertifikasyon](#15-thread-group-ve-sertifikasyon)
  - [1.6 OpenThread](#16-openthread)
  - [1.7 Thread ve Matter İlişkisi](#17-thread-ve-matter-i̇lişkisi)
  - [1.8 Büyük Resim](#18-büyük-resim)
  - [1.9 Thread'in Tanımlamadıkları](#19-threadin-tanımlamadıkları)
  - [1.10 Bölüm Özeti](#110-bölüm-özeti)
- [2. Protokol Yığını ve Genel Mimari](#2-protokol-yığını-ve-genel-mimari)
  - [2.1 Katmanlar](#21-katmanlar)
  - [2.2 OSI Modeliyle Eşleme](#22-osi-modeliyle-eşleme)
  - [2.3 Thread'in Kullandığı ve Tanımladığı Bileşenler](#23-threadin-kullandığı-ve-tanımladığı-bileşenler)
  - [2.4 Kontrol Düzlemi ve Veri Düzlemi](#24-kontrol-düzlemi-ve-veri-düzlemi)
  - [2.5 Bir Paketin Yolculuğu (Genel Bakış)](#25-bir-paketin-yolculuğu-genel-bakış)
  - [2.6 Önemli UDP Portları](#26-önemli-udp-portları)
  - [2.7 Bölüm Özeti](#27-bölüm-özeti)
- [3. Fiziksel Katman (IEEE 802.15.4 PHY)](#3-fiziksel-katman-ieee-802154-phy)
  - [3.1 Genel Bakış](#31-genel-bakış)
  - [3.2 Kanallar ve Frekanslar](#32-kanallar-ve-frekanslar)
  - [3.3 Modülasyon ve Yayılma Spektrumu](#33-modülasyon-ve-yayılma-spektrumu)
  - [3.4 PPDU (Fiziksel Paket) Yapısı](#34-ppdu-fiziksel-paket-yapısı)
  - [3.5 Önemli PHY/MAC Zaman Sabitleri](#35-önemli-phymac-zaman-sabitleri)
  - [3.6 Alıcı Ölçümleri: RSSI, LQI, ED ve Gürültü Tabanı](#36-alıcı-ölçümleri-rssi-lqi-ed-ve-gürültü-tabanı)
  - [3.7 CCA (Clear Channel Assessment)](#37-cca-clear-channel-assessment)
  - [3.8 Wi-Fi ve Bluetooth ile Bir Arada Yaşama](#38-wi-fi-ve-bluetooth-ile-bir-arada-yaşama)
  - [3.9 Bağlantı Bütçesi ve Menzil](#39-bağlantı-bütçesi-ve-menzil)
  - [3.10 Etkin Veri Hızı (Throughput)](#310-etkin-veri-hızı-throughput)
  - [3.11 Bölüm Özeti](#311-bölüm-özeti)
- [4. MAC Katmanı (IEEE 802.15.4 MAC)](#4-mac-katmanı-ieee-802154-mac)
  - [4.1 Görevler](#41-görevler)
  - [4.2 Thread'in 802.15.4 MAC'i Kullanma Biçimi](#42-threadin-802154-maci-kullanma-biçimi)
  - [4.3 MAC Çerçeve Formatı](#43-mac-çerçeve-formatı)
  - [4.4 Adresler](#44-adresler)
  - [4.5 CSMA-CA (Slotsuz)](#45-csma-ca-slotsuz)
  - [4.6 Onay (ACK) ve Yeniden İletim](#46-onay-ack-ve-yeniden-i̇letim)
  - [4.7 Dolaylı İletim (Indirect Transmission) ve Veri Sorgulama (Data Poll)](#47-dolaylı-i̇letim-indirect-transmission-ve-veri-sorgulama-data-poll)
  - [4.8 MAC Komutları](#48-mac-komutları)
  - [4.9 MAC Güvenliği](#49-mac-güvenliği)
  - [4.10 Bilgi Elemanları (Information Elements — IE)](#410-bilgi-elemanları-information-elements--ie)
  - [4.11 Taramalar](#411-taramalar)
  - [4.12 MAC Seviyesinde Alım Filtreleri](#412-mac-seviyesinde-alım-filtreleri)
  - [4.13 Bölüm Özeti](#413-bölüm-özeti)

## 1. Thread'e Giriş

### 1.1 Thread Nedir?

**Thread**, nesnelerin interneti (IoT) için tasarlanmış; **IPv6 tabanlı**, **düşük güçlü**, **kablosuz mesh (ağ örgüsü)** ağ protokolüdür. Özellikle akıllı ev ve bina otomasyonu cihazlarının (lambalar, prizler, sensörler, kilitler, termostatlar, perdeler vb.) birbirleriyle ve internetle güvenli, güvenilir ve pil dostu şekilde haberleşmesi için geliştirilmiştir.

Tek cümleyle: **Thread = IEEE 802.15.4 radyosu + 6LoWPAN + IPv6 + Thread'e özgü ağ yönetimi (MLE, yönlendirme, güvenlik, devreye alma).**

Thread'in temel karakteristikleri:

| Özellik | Açıklama |
|---|---|
| **IP tabanlı** | Ağdaki her cihazın kendi IPv6 adresi vardır. Cihaza ulaşmak için protokol çeviren bir "gateway" gerekmez; sadece bir yönlendirici (**Border Router**) yeterlidir. |
| **Mesh topoloji** | Cihazlar birbirlerinin mesajlarını taşır. Kapsama alanı cihaz eklendikçe büyür. |
| **Kendi kendini onarma** | Bir yönlendirici bozulursa trafik otomatik olarak başka yollardan akar; yeni bir **Leader** seçilir. |
| **Tek hata noktası yok** | Zigbee'deki "coordinator" gibi vazgeçilmez merkezi bir düğüm yoktur. Leader rolünü herhangi bir router devralabilir; birden fazla Border Router bulunabilir. |
| **Düşük güç** | Pille çalışan "uyuyan" cihazlar (Sleepy End Device) radyolarını çoğu zaman kapalı tutarak yıllarca çalışabilir. |
| **Güvenlik** | Tüm bağlantı katmanı trafiği AES-128-CCM ile şifrelenir ve doğrulanır. Ağa katılım, parola doğrulamalı anahtar değişimi (EC-JPAKE) veya bant dışı (Matter) devreye alma ile yapılır. |
| **Ölçeklenebilirlik** | Tek ağda 32 aktif router ve her router'a bağlı çok sayıda çocuk cihaz: pratikte 250+ cihaz. |
| **Açık standartlar** | IEEE 802.15.4, IETF RFC'leri (6LoWPAN, IPv6, CoAP, DTLS, MPL, Trickle) üzerine kuruludur. |

> [!IMPORTANT]
> Thread bir **ağ katmanı** protokolüdür; **uygulama katmanını tanımlamaz**. Bir lambanın "aç/kapat" komutunun nasıl kodlanacağı Thread'in değil, üzerinde çalışan uygulama protokolünün (bugün çoğunlukla **Matter**) işidir. Thread'i "Wi-Fi'ın düşük güçlü, mesh'li kuzeni", Matter'ı ise "bu ağların üzerinde konuşulan ortak dil" olarak düşünebilirsiniz.

### 1.2 Neden Thread? Çözdüğü Problemler

Thread öncesinde akıllı ev dünyası birkaç temel sorunla boğuşuyordu:

1. **Dikey, kapalı yığınlar.** Zigbee ve Z-Wave gibi teknolojiler radyodan uygulamaya kadar kendi protokol yığınlarını tanımlıyordu. İnternete veya telefona bağlanmak için mesajları IP dünyasına **çeviren** üreticiye özel hub/gateway'ler gerekiyordu.
2. **Wi-Fi'ın güç tüketimi.** Wi-Fi yüksek veri hızı sunar ama sürekli dinleme ve ilişkilendirme (association) maliyeti, düğme pilli bir kapı sensörü için uygun değildir. Ayrıca Wi-Fi erişim noktalarının bağlı istemci sayısı sınırlıdır.
3. **Bluetooth'un menzil ve topoloji kısıtları.** Klasik BLE noktadan noktaya çalışır; BLE Mesh ise IP tabanlı değildir ve "managed flooding" yaklaşımı büyük ağlarda verimsizleşebilir.
4. **Tek hata noktası.** Coordinator/hub'a bağımlı ağlarda o cihaz bozulduğunda bütün ağ etkilenir.

Thread bu sorunlara şu yaklaşımla cevap verir:

- Radyo olarak düşük güçlü ve olgun **IEEE 802.15.4**'ü kullanır (Zigbee ile aynı radyo).
- Üzerine **IPv6**'yı taşır (6LoWPAN ile sıkıştırarak). Böylece "çeviri" değil, sadece "yönlendirme" gerekir.
- Uygulama katmanını serbest bırakır; bugün bu boşluğu **Matter** doldurur.
- Yönetimi dağıtık yapar: Leader, router'lar ve Border Router'lar yedeklidir.

### 1.3 Tarihçe

| Yıl | Olay |
|---|---|
| **2014 (Temmuz)** | **Thread Group** kuruldu. Kurucular arasında Nest Labs (Google), Samsung, ARM, Freescale (bugün NXP), Silicon Labs, Big Ass Fans ve Yale Security vardı. |
| **2015** | Thread 1.0 şartnamesi yayımlandı; ilk sertifikalı ürünler (Nest ürünleri) pazara çıktı. |
| **2016 (Mayıs)** | Google/Nest, Thread'in açık kaynak uygulaması **OpenThread**'i BSD-3 lisansıyla yayımladı. |
| **2017** | **Thread 1.1**: devreye alma (commissioning) ve ağ yönetimi iyileştirmeleri, MLE tabanlı keşif, anahtar yönetimi düzenlemeleri. |
| **2019** | **Thread 1.2**: büyük/kurumsal ağlar için **Thread Domain**, **Backbone Router**, **DUA**, çoklu yayın kaydı (MLR), **CSL** (senkronize uyuyan cihazlar), **Link Metrics**, Enhanced ACK, ticari devreye alma (CCM). |
| **2019 (Aralık)** | Apple, Google, Amazon ve Zigbee Alliance **Project CHIP**'i duyurdu; Thread düşük güçlü taşıma katmanı olarak seçildi. |
| **2020** | Apple HomePod mini gibi tüketici ürünleriyle Thread Border Router'lar evlere yayılmaya başladı. |
| **2021** | Zigbee Alliance adını **Connectivity Standards Alliance (CSA)** olarak değiştirdi; Project CHIP'in adı **Matter** oldu. |
| **2022–2023** | **Matter 1.0** (Ekim 2022) yayımlandı. **Thread 1.3** ile Border Router işlevleri (SRP, DNS-SD proxy, NAT64, OMR yönlendirme) ve TREL standartlaştırıldı. |
| **2024 (Eylül)** | **Thread 1.4** duyuruldu: zorunlu ve birlikte çalışabilir Border Router özellikleri, ekosistemler arası kimlik bilgisi paylaşımı (ePSKc), gelişmiş internet bağlantısı (DHCPv6-PD), gelişmiş ağ teşhisi, TCAT. |

### 1.4 Sürümlerin Özeti

| Sürüm | Öne çıkan özellikler | Uyumluluk |
|---|---|---|
| **1.0** | Temel mesh, MLE, 6LoWPAN, güvenlik, MAC beacon tabanlı keşif | Tarihsel |
| **1.1** | MLE Discovery, iyileştirilmiş MeshCoP, harici commissioner, network key rotasyonu | 1.2+ ile birlikte çalışır |
| **1.2** | CSL / SSED, Enhanced Frame Pending, Enhanced Keep-Alive, Link Metrics, 802.15.4-2015 çerçeveleri, Thread Domain, Backbone Router, DUA, MLR, CCM | 1.1 ile geriye uyumlu |
| **1.3** | Thread Border Router (TBR) şartnamesi: OMR prefix, RA/RIO, SRP sunucusu, Advertising/Discovery Proxy, NAT64; TREL (Thread over Wi-Fi/Ethernet) | Matter için temel gereksinim |
| **1.4** | Zorunlu BR yetenekleri, ePSKc ile kimlik paylaşımı, DHCPv6-PD ile global IPv6, gelişmiş teşhis TLV'leri, TCAT (TLS tabanlı devreye alma) | 1.3 ile geriye uyumlu |

> [!TIP]
> Bir Thread ağında farklı sürümlerden cihazlar bir arada çalışabilir. Yeni özellikler (ör. CSL) yalnızca bu özelliği destekleyen eşler arasında kullanılır; eski cihazlar bunları görmezden gelir. Sürüm bilgisi MLE mesajlarındaki **Version TLV** ile taşınır (1.1 = 2, 1.2 = 3, 1.3 = 4, 1.4 = 5).

### 1.5 Thread Group ve Sertifikasyon

**Thread Group**, şartnameyi geliştiren, sertifikasyon programını yürüten ve birlikte çalışabilirlik etkinlikleri düzenleyen kar amacı gütmeyen endüstri birliğidir.

- **Şartname**: Thread Specification (çekirdek ağ katmanı), Thread Border Router özellikleri, test şartnameleri.
- **Sertifikasyon**: Ürünler yetkili test laboratuvarlarında sertifika test senaryolarından geçer. Sertifikalı yığınlar ("Thread Certified Component") üzerine ürün geliştiren üreticiler süreci kısaltabilir.
- **Logo**: "Built on Thread" logosu sertifikalı ürünlerde kullanılır.
- **Test araçları**: Thread Test Harness ve referans cihaz setleri ile otomatik birlikte çalışabilirlik testleri yapılır.

### 1.6 OpenThread

**OpenThread**, Google tarafından başlatılan, Thread şartnamesini uygulayan açık kaynak (BSD-3-Clause) bir yığındır.

- C++ ile yazılmıştır, C API sunar; mikrodenetleyiciden Linux'a kadar taşınabilir.
- **Platform soyutlama katmanı** (radyo, zamanlayıcı, kalıcı bellek, rastgele sayı, kripto) sayesinde birçok çip üreticisi tarafından desteklenir: Nordic, Silicon Labs, NXP, Texas Instruments, Espressif, Qorvo, Telink ve diğerleri.
- **OpenThread Border Router (OTBR)** projesi Linux tabanlı Border Router'lar için referans uygulamadır (Home Assistant OTBR eklentisi de buna dayanır).
- Thread sürümleriyle paralel güncellenir; Thread sertifikası almış sürümleri vardır.

Ayrıntılar için Bölüm 24'e bakın.

### 1.7 Thread ve Matter İlişkisi

| Konu | Thread | Matter |
|---|---|---|
| **Katman** | Ağ (bağlantı + IPv6 ağ yönetimi) | Uygulama (veri modeli, etkileşim modeli, güvenlik oturumları) |
| **Sorumlu kuruluş** | Thread Group | Connectivity Standards Alliance (CSA) |
| **Neyi tanımlar?** | Paketlerin cihazdan cihaza nasıl taşınacağını | "Lambayı aç" komutunun anlamını ve formatını |
| **Taşıma** | IEEE 802.15.4 | Thread, Wi-Fi, Ethernet (IPv6 üzerinden) |

Matter cihazı, Thread ağında sıradan bir IPv6/UDP uygulaması gibi çalışır (UDP port 5540). Matter, Thread ağının kimlik bilgilerini (Operational Dataset) cihaza devreye alma sırasında BLE üzerinden aktarır. Ayrıntılar Bölüm 23'te.

### 1.8 Büyük Resim

Tipik bir akıllı evde Thread ağı şöyle görünür:

```mermaid
flowchart LR
    INET(("İnternet"))
    subgraph EV["Ev Ağı (Wi-Fi / Ethernet, IPv6)"]
        RTR["Wi-Fi Router"]
        PHONE["Telefon / Tablet<br/>(Matter Controller)"]
        BR1["Border Router 1<br/>(ör. akıllı hoparlör)"]
        BR2["Border Router 2<br/>(ör. TV kutusu)"]
    end
    subgraph THREAD["Thread Mesh Ağı (IEEE 802.15.4, 2.4 GHz)"]
        L["Leader<br/>(Router)"]
        R1["Router<br/>(akıllı priz)"]
        R2["Router<br/>(ampul)"]
        REED["REED<br/>(ampul)"]
        SED1["SED<br/>(kapı sensörü)"]
        SED2["SED<br/>(sıcaklık sensörü)"]
        MED["MED<br/>(perde motoru)"]
    end
    INET --- RTR
    RTR --- PHONE
    RTR --- BR1
    RTR --- BR2
    BR1 -.-|"802.15.4"| L
    BR2 -.-|"802.15.4"| R1
    L --- R1
    L --- R2
    R1 --- R2
    R2 --- REED
    R1 --- SED1
    R2 --- SED2
    L --- MED
```

- **Border Router**'lar Thread mesh'i ile Wi-Fi/Ethernet ev ağını IP seviyesinde birbirine bağlar.
- **Router**'lar (genelde şebekeden beslenen cihazlar) mesh omurgasını oluşturur ve paketleri yönlendirir.
- **Leader**, router'lardan biridir; router kimliklerini dağıtır ve ağ verisini yönetir.
- **REED** (Router Eligible End Device), gerektiğinde router'a terfi edebilen cihazdır.
- **SED/MED** gibi uç cihazlar yalnızca **ebeveyn (parent)** router'larıyla konuşur.

### 1.9 Thread'in Tanımlamadıkları

Thread'in kapsamını doğru anlamak için neleri **tanımlamadığını** bilmek önemlidir:

- **Uygulama protokolü / veri modeli** → Matter, LwM2M, özel CoAP uygulamaları vb.
- **Bulut bağlantısı ve uzaktan erişim** → Ekosistem hub'ları/bulut servisleri.
- **Kullanıcı arayüzü ve cihaz eşleştirme deneyimi** → Ekosistem uygulamaları (Apple Home, Google Home, Home Assistant vb.).
- **Uçtan uca (end-to-end) uygulama güvenliği** → Thread bağlantı katmanında hop-by-hop güvenlik sağlar; uçtan uca güvenlik Matter (CASE/PASE oturumları) veya DTLS gibi üst katmanların işidir.
- **Wi-Fi ağının yapılandırılması** → Border Router'ın altyapı ağıyla etkileşimi Thread BR şartnamesinde tanımlanır ama ev ağı Thread'in kontrolünde değildir.

### 1.10 Bölüm Özeti

- Thread, 802.15.4 radyo üzerinde IPv6 taşıyan, düşük güçlü ve kendi kendini onaran bir mesh ağıdır.
- Uygulama katmanından bağımsızdır; bugün en yaygın üst katman Matter'dır.
- Merkezi tek hata noktası yoktur: Leader ve Border Router işlevleri yedeklidir.
- Sürümler geriye uyumludur; 1.2 enerji ve ölçek, 1.3 Border Router, 1.4 birlikte çalışabilirlik ve kimlik paylaşımı odaklıdır.

## 2. Protokol Yığını ve Genel Mimari

### 2.1 Katmanlar

Thread, mevcut standartları bir araya getirip eksik parçaları kendisi tanımlayan bir "sistem şartnamesi"dir. Yığın aşağıdan yukarıya şöyledir:

```text
+-----------------------------------------------------------------------+
|  UYGULAMA        Matter  |  CoAP uygulamaları  |  LwM2M  |  özel UDP  |
+-----------------------------------------------------------------------+
|  OTURUM/GÜVENLİK         (Matter CASE/PASE, DTLS — uygulamaya bağlı)  |
+-----------------------------------------------------------------------+
|  TAŞIMA          UDP   (TCP isteğe bağlı; Thread 1.3+ TCP desteği)    |
+--------------------------+--------------------------------------------+
|                          |  Thread Kontrol Düzlemi:                   |
|  AĞ  IPv6 + ICMPv6       |   MLE   (UDP 19788)  komşuluk / bağlanma   |
|      Thread yönlendirme  |   TMF   (CoAP, UDP 61631) ağ yönetimi      |
|                          |   MeshCoP (DTLS)  devreye alma             |
+--------------------------+--------------------------------------------+
|  UYARLAMA        6LoWPAN: başlık sıkıştırma, parçalama, mesh başlığı  |
+-----------------------------------------------------------------------+
|  BAĞLANTI (MAC)  IEEE 802.15.4-2006 (+2015 özellikleri): CSMA-CA,     |
|                  ACK, AES-CCM* güvenlik, dolaylı iletim, IE'ler       |
+-----------------------------------------------------------------------+
|  FİZİKSEL (PHY)  IEEE 802.15.4  2.4 GHz  O-QPSK  250 kbit/s  k11-26   |
+-----------------------------------------------------------------------+
```

```mermaid
flowchart TB
    APP["Uygulama<br/>Matter / CoAP / LwM2M"]
    UDP["UDP (+ DTLS / Matter güvenliği)"]
    IP["IPv6 + ICMPv6"]
    MLE["MLE<br/>UDP 19788"]
    TMF["TMF (CoAP)<br/>UDP 61631"]
    MESHCOP["MeshCoP<br/>DTLS / EC-JPAKE"]
    LOWPAN["6LoWPAN<br/>IPHC · Fragment · Mesh Header"]
    MAC["IEEE 802.15.4 MAC<br/>CSMA-CA · ACK · AES-CCM*"]
    PHY["IEEE 802.15.4 PHY<br/>2.4 GHz O-QPSK 250 kbit/s"]
    APP --> UDP --> IP
    MLE --> UDP
    TMF --> UDP
    MESHCOP --> UDP
    IP --> LOWPAN --> MAC --> PHY
```

### 2.2 OSI Modeliyle Eşleme

| OSI katmanı | Thread'deki karşılığı | Standart / kaynak |
|---|---|---|
| 7 Uygulama | Matter, CoAP uygulamaları | CSA Matter, RFC 7252 |
| 6 Sunum | (Uygulamaya ait — TLV, CBOR vb.) | — |
| 5 Oturum | Matter CASE/PASE, DTLS 1.2 | RFC 6347 |
| 4 Taşıma | UDP (ağırlıklı), TCP | RFC 768, RFC 9293 |
| 3 Ağ | IPv6, ICMPv6, Thread yönlendirme, MLE, TMF, MPL | RFC 8200, RFC 4443, RFC 7731, Thread Spec |
| 2.5 Uyarlama | 6LoWPAN | RFC 4944, RFC 6282 |
| 2 Veri bağlantısı | IEEE 802.15.4 MAC | IEEE 802.15.4-2006 / -2015 |
| 1 Fiziksel | IEEE 802.15.4 O-QPSK PHY (2.4 GHz) | IEEE 802.15.4 |

### 2.3 Thread'in Kullandığı ve Tanımladığı Bileşenler

**Kullandığı (başkalarının tanımladığı) standartlar:**

| Bileşen | Kaynak | Thread'deki rolü |
|---|---|---|
| IEEE 802.15.4 PHY/MAC | IEEE | Radyo ve çerçeve erişimi |
| 6LoWPAN çerçeveleme ve parçalama | RFC 4944 | IPv6'yı 127 baytlık çerçevelere sığdırma |
| IPHC / NHC sıkıştırma | RFC 6282 | IPv6/UDP başlıklarını sıkıştırma |
| IPv6 adresleme | RFC 4291, RFC 4193 (ULA), RFC 4862 (SLAAC) | Adres yapısı |
| ICMPv6 | RFC 4443 | Ping, hata mesajları |
| CoAP | RFC 7252 | TMF yönetim mesajları |
| DTLS 1.2 | RFC 6347 | Devreye alma oturumları |
| EC-JPAKE | RFC 8236 (J-PAKE) temelli TLS uzantısı | Parola doğrulamalı anahtar değişimi |
| Trickle | RFC 6206 | Advertisement zamanlaması |
| MPL | RFC 7731 | Mesh içi çoklu yayın (multicast) iletimi |
| mDNS / DNS-SD / SRP | RFC 6762, RFC 6763, RFC 9665 | Servis keşfi (Border Router) |
| NAT64 / DNS64 | RFC 6146, RFC 6147, RFC 6052 | IPv4 erişimi (Border Router) |

**Thread'in kendi tanımladıkları:**

| Bileşen | Görevi |
|---|---|
| **MLE** (Mesh Link Establishment) | Komşu keşfi, bağlanma (attach), ebeveyn seçimi, bağlantı kalitesi ölçümü, yönlendirme bilgisinin yayılması, ağ parametrelerinin dağıtımı |
| **Thread yönlendirme protokolü** | Router'lar arası mesafe-vektör (distance-vector) yönlendirme (Route64 TLV) |
| **TMF** (Thread Management Framework) | CoAP tabanlı yönetim: adres sorgulama, router ID atama, ağ verisi kaydı, teşhis |
| **Network Data** | Ağ genelinde önekler, rotalar, servisler, sıkıştırma bağlamları |
| **MeshCoP** (Mesh Commissioning Protocol) | Commissioner, Border Agent, Joiner süreçleri; Operational Dataset yönetimi |
| **Adres mimarisi** | RLOC, ALOC, ML-EID, RLOC16 yapısı, adres sorgulama |
| **Güvenlik mimarisi** | Network Key'den MAC/MLE anahtarı türetme, anahtar rotasyonu, PSKc/PSKd |
| **Border Router davranışları** | OMR prefix, RA/RIO, SRP, NAT64, TREL (1.3+) |

### 2.4 Kontrol Düzlemi ve Veri Düzlemi

Thread'deki trafiği iki gruba ayırmak mimariyi anlamayı kolaylaştırır:

**Veri düzlemi (data plane)** — Uygulamanın asıl yükü: Matter komutları, sensör verileri, CoAP istekleri. IPv6/UDP paketleri olarak taşınır, 6LoWPAN ile sıkıştırılır, MAC katmanında şifrelenir.

**Kontrol düzlemi (control plane)** — Ağın kendisini ayakta tutan trafik:

| Protokol | Kapsam | Örnek işler |
|---|---|---|
| **MLE** | Tek atlama (link-local) | Parent Request/Response, Child ID Request/Response, Link Request/Accept, Advertisement, Data Response |
| **TMF** | Mesh geneli (RLOC/ALOC adresleri) | Address Query/Notification, Address Solicit/Release, Server Data, Diagnostic Get |
| **MeshCoP** | Mesh + Border Agent + harici commissioner | Commissioner Petition, Joiner DTLS, Joiner Entrust, Active/Pending Set |

```mermaid
flowchart LR
    subgraph KONTROL["Kontrol düzlemi"]
        MLE2["MLE<br/>komşuluk, attach, rota ilanı"]
        TMF2["TMF / CoAP<br/>adres, router ID, ağ verisi"]
        MC["MeshCoP<br/>devreye alma, dataset"]
    end
    subgraph VERI["Veri düzlemi"]
        APPD["Uygulama trafiği<br/>(Matter, CoAP, UDP)"]
    end
    KONTROL --> FWD["Yönlendirme tabloları<br/>EID→RLOC önbelleği<br/>Network Data"]
    FWD --> VERI
```

### 2.5 Bir Paketin Yolculuğu (Genel Bakış)

Bir uygulamanın Thread ağındaki başka bir cihaza UDP mesajı gönderdiğini düşünelim. Ayrıntılar ilgili bölümlerde verilecek; burada akışı kuşbakışı görüyoruz:

1. **Uygulama** veriyi UDP soketine yazar (ör. hedef: `fd4f:…:1234` port 5540).
2. **IPv6 katmanı** kaynak adresini seçer ve hedefin mesh içinde mi (on-mesh) yoksa dışarıda mı olduğuna bakar.
3. **Thread yönlendirme**: Hedef bir EID ise (ML-EID veya OMR adresi) **EID→RLOC** önbelleğine bakılır. Kayıt yoksa ağa **Address Query** gönderilir ve paket bekletilir. Hedef ağ dışındaysa Network Data'dan uygun **Border Router**'ın RLOC16'sı seçilir.
4. **Sonraki atlama (next hop)** yönlendirme tablosundan bulunur.
5. **6LoWPAN**: IPv6 ve UDP başlıkları sıkıştırılır; paket birden fazla atlama gidecekse **Mesh Header** (kaynak ve nihai hedef RLOC16) eklenir; paket 127 bayta sığmıyorsa **parçalanır** (FRAG1/FRAGN).
6. **MAC**: Her parça, hedef MAC adresi = sonraki atlama olacak şekilde çerçevelenir, **AES-CCM*** ile şifrelenip doğrulanır, **CSMA-CA** ile kanala erişilip gönderilir, **ACK** beklenir; gelmezse yeniden denenir.
7. **Ara router'lar** her çerçeveyi alır, MAC güvenliğini doğrular, Mesh Header'daki nihai hedefe bakar, *Hops Left* değerini azaltır ve sonraki atlamaya — paketi IPv6 seviyesinde birleştirmeden — iletir.
8. **Hedef router** paketi doğrudan veya (uyuyan çocuk cihaz ise) **dolaylı iletim** ile teslim eder.
9. **Hedef cihaz** parçaları birleştirir, başlıkları açar ve UDP yükünü uygulamaya verir.

```mermaid
sequenceDiagram
    participant A as Kaynak (SED)
    participant P as Ebeveyn Router
    participant R as Ara Router
    participant H as Hedef Router
    participant B as Hedef (Çocuk)
    A->>P: MAC unicast (şifreli) — tüm trafik ebeveyne
    Note over P: EID→RLOC çöz, next hop bul,<br/>Mesh Header ekle
    P->>R: 802.15.4 çerçeve + Mesh Header
    Note over R: Hops Left bir azaltılır, sonraki atlamaya iletilir<br/>(IPv6 birleştirme yok)
    R->>H: 802.15.4 çerçeve + Mesh Header
    Note over H: Hedef benim çocuğum
    H->>B: Doğrudan (rx-on) veya dolaylı (poll sonrası) teslim
```

### 2.6 Önemli UDP Portları

| Port | Protokol | Açıklama |
|---|---|---|
| **19788** | MLE | Mesh Link Establishment (link-local) |
| **61631** | TMF (CoAP) | Thread yönetim mesajları (`0xF0BF`; 6LoWPAN ile 4 bite sıkıştırılabilir) |
| **1000** | MeshCoP Joiner | Joiner UDP portu (varsayılan; Discovery Response içinde ilan edilir) |
| **49191** | MeshCoP Border Agent | OTBR varsayılanı; gerçek port mDNS `_meshcop._udp` SRV kaydıyla ilan edilir |
| **5540** | Matter | Matter operasyonel mesajları (UDP/TCP) |
| **5353** | mDNS | Altyapı ağında (Wi-Fi/Ethernet) servis keşfi |
| **53** | DNS | Discovery Proxy / DNS sorguları (Border Router) |
| **53535–53554** | SRP | OpenThread SRP sunucusunun kullandığı aralık (Network Data'da ilan edilir) |

### 2.7 Bölüm Özeti

- Thread yığını: 802.15.4 PHY/MAC → 6LoWPAN → IPv6 → UDP → uygulama.
- Thread'e özgü kontrol protokolleri: MLE (link yönetimi), TMF (CoAP tabanlı ağ yönetimi), MeshCoP (devreye alma).
- Mesh içinde paketler IPv6 seviyesinde değil, 6LoWPAN **Mesh Header** ile RLOC16'lara göre iletilir; ara düğümler parçaları birleştirmez.
- Her atlamada MAC katmanı şifreleme/doğrulama yapar (hop-by-hop güvenlik).

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

## 4. MAC Katmanı (IEEE 802.15.4 MAC)

### 4.1 Görevler

802.15.4 MAC katmanının Thread'deki sorumlulukları:

| Görev | Açıklama |
|---|---|
| **Kanal erişimi** | Slotsuz (unslotted) CSMA-CA ile çakışmaları azaltmak |
| **Çerçeveleme** | Başlık (MHR), yük ve FCS (CRC-16) oluşturmak |
| **Adresleme** | PAN ID, 16 bit kısa adres, 64 bit genişletilmiş adres |
| **Güvenilirlik** | Onay (ACK) ve yeniden iletim (retry) |
| **Güvenlik** | AES-128-CCM* ile şifreleme + bütünlük (MIC), tekrar (replay) koruması |
| **Dolaylı iletim** | Uyuyan cihazlar için ebeveynde kuyruklama ve "poll" ile teslim |
| **Tarama** | Active scan, energy scan |
| **Bilgi elemanları (IE)** | Thread 1.2+: CSL, Link Metrics gibi bilgilerin başlıkta taşınması |

### 4.2 Thread'in 802.15.4 MAC'i Kullanma Biçimi

802.15.4 çok geniş bir standarttır; Thread bunun yalnızca belirli bir alt kümesini kullanır:

- **Beacon'sız (non-beacon) mod**: Süper çerçeve (superframe), GTS (garantili zaman dilimi) yoktur. Kanal erişimi tamamen **slotsuz CSMA-CA** ile yapılır.
- **802.15.4 "association" kullanılmaz**: Bir cihazın ağa bağlanması MAC Association komutlarıyla değil, **MLE** (Bölüm 9) ile yapılır. Bu sayede bağlanma süreci güvenli ve IP tabanlıdır.
- **PAN Coordinator kavramı yoktur**: Thread'de "coordinator" rolü bulunmaz; Leader bir MAC kavramı değil, Thread ağ katmanı rolüdür.
- **Çerçeve sürümleri**: Thread 1.1 güvenli çerçeveler için 802.15.4-**2006** sürümünü kullanır. Thread 1.2 ve sonrası, IE (Information Element) ve Enhanced ACK gerektiren durumlarda 802.15.4-**2015** çerçeve sürümünü kullanır (ör. CSL, Link Metrics).
- **Genişletilmiş adres rastgeledir**: Thread cihazları ağda fabrika EUI-64'ünü değil, rastgele üretilmiş bir 64 bit **Extended Address** kullanır (gizlilik). Fabrika EUI-64'ü yalnızca devreye almada Joiner ID türetmek için kullanılır.

### 4.3 MAC Çerçeve Formatı

```text
           MHR (MAC Header)                                          MAC Payload      MFR
+-------+-----+-------+-------+-------+-------+-----------+-------+--------------+--------+
| Frame | Seq | Dest  | Dest  |  Src  |  Src  | Auxiliary | Header|   Payload    |  FCS   |
|Control| Num | PAN ID| Addr  | PAN ID| Addr  | Security  |  IEs  | (+Payload IE)| CRC-16 |
|   2   | 0/1 | 0/2   |0/2/8  | 0/2   | 0/2/8 | 0/5/6/10/14| değ. |   değişken   |   2    |
+-------+-----+-------+-------+-------+-------+-----------+-------+--------------+--------+
```

Tüm çok baytlı alanlar havada **little-endian** sırayla gönderilir.

#### Frame Control (2 bayt)

```text
 bit: 15 14 | 13 12 | 11 10 |  9  |  8  |  7  |  6  |  5  |  4  |  3  | 2 1 0
      SrcAM | Sürüm | DstAM | IEP | SNS | ayr.| PIC | AR  | FP  | Sec | Tür
```

| Bit(ler) | Alan | Değerler |
|---|---|---|
| 0–2 | **Frame Type** | `000` Beacon, `001` Data, `010` Ack, `011` MAC Command (diğerleri Thread'de kullanılmaz) |
| 3 | **Security Enabled** | 1 = Aux Security Header var, yük şifreli/doğrulanmış |
| 4 | **Frame Pending** | 1 = gönderende bu alıcı için bekleyen veri var (uyuyan cihazlar için kritik) |
| 5 | **AR** (Ack Request) | 1 = alıcı ACK göndermeli (unicast çerçeveler); yayın (broadcast) çerçevelerde 0 |
| 6 | **PAN ID Compression** | 1 = kaynak PAN ID atlanır (hedef PAN ID ile aynı kabul edilir) |
| 8 | **Sequence Number Suppression** | (2015) 1 = sıra numarası alanı yok |
| 9 | **IE Present** | (2015) 1 = başlıkta Information Element var |
| 10–11 | **Dest Addr Mode** | `00` yok, `10` kısa (16 bit), `11` genişletilmiş (64 bit) |
| 12–13 | **Frame Version** | `00` 2003, `01` 2006, `10` 2015 |
| 14–15 | **Src Addr Mode** | `00` yok, `10` kısa, `11` genişletilmiş |

#### Çözümlenmiş örnekler

| Havadaki baytlar | FCF değeri | Anlamı |
|---|---|---|
| `41 D8` | `0xD841` | Data, güvenliksiz, ACK yok, PAN sıkıştırma; hedef kısa (yayın `0xFFFF`), kaynak genişletilmiş, sürüm 2006 → tipik **MLE yayın** çerçevesi (ör. Parent Request) |
| `61 DC` | `0xDC61` | Data, güvenliksiz, ACK istekli, PAN sıkıştırma; hedef ve kaynak genişletilmiş, sürüm 2006 → tipik **MLE unicast** çerçevesi |
| `69 98` | `0x9869` | Data, **güvenli**, ACK istekli, PAN sıkıştırma; hedef ve kaynak kısa, sürüm 2006 → tipik **komşular arası veri** çerçevesi |
| `69 D8` | `0xD869` | Aynısı, kaynak genişletilmiş |
| `02 00` | `0x0002` | Imm-Ack (Frame Pending = 0) |
| `12 00` | `0x0012` | Imm-Ack (Frame Pending = 1) — "sende bekleyen veri var" |

#### Tam bir veri çerçevesi örneği

```text
69 98                 Frame Control: Data, Sec=1, AR=1, PIC=1, kısa→kısa, 2006
5A                    Sıra numarası = 90
34 12                 Hedef PAN ID = 0x1234
00 5C                 Hedef kısa adres = 0x5C00  (Router ID 23)
01 5C                 Kaynak kısa adres = 0x5C01 (Router 23'ün 1 numaralı çocuğu)
0D                    Security Control: seviye 5 (ENC-MIC-32), Key ID Mode 1
3A 00 00 00           Frame Counter = 58
01                    Key Index = 1  (Key Sequence 0)
.. .. .. ..           Şifreli yük (6LoWPAN: Mesh/Frag/IPHC + UDP + uygulama)
xx xx xx xx           MIC (32 bit)
yy yy                 FCS (CRC-16/ITU-T)
```

MAC ek yükü: başlık 9 bayt + güvenlik başlığı 6 bayt + MIC 4 bayt + FCS 2 bayt = **21 bayt**. Yani kısa adreslerle MAC yükü için en fazla **106 bayt** kalır (kaynak genişletilmiş adres ise ≈ 100 bayt).

### 4.4 Adresler

| Adres | Boyut | Thread'deki anlamı |
|---|---|---|
| **PAN ID** | 16 bit | Ağın MAC seviyesindeki kimliği; Operational Dataset'te bulunur. `0xFFFF` yayın PAN ID'sidir. |
| **Kısa adres (Short Address)** | 16 bit | Thread'de doğrudan **RLOC16** değeridir (Router ID + Child ID). `0xFFFF` yayın, `0xFFFE` "kısa adres yok" anlamına gelir. |
| **Genişletilmiş adres (Extended Address)** | 64 bit | Cihazın ağdaki rastgele 64 bitlik kimliği. Link-local IPv6 adresinin arayüz kimliği (IID) bundan türetilir. Ayrıca MAC güvenlik **nonce**'unda kullanılır. |

**Hangi adres ne zaman kullanılır?**

- Cihaz henüz RLOC16 almamışken (bağlanma sırasında) **genişletilmiş** adres kullanılır.
- MLE mesajları link-local IPv6 adresleriyle gönderildiği için MAC kaynağı genellikle **genişletilmiş** adrestir.
- Bağlanmış komşular arasındaki veri trafiğinde çerçeveyi küçültmek için **kısa** adresler tercih edilir.
- IPv6 çoklu yayın (multicast) paketleri MAC seviyesinde **`0xFFFF`** yayın adresine gönderilir ve ACK istenmez.

### 4.5 CSMA-CA (Slotsuz)

Thread cihazları göndermeden önce rastgele süre bekleyip kanalı dinler:

```mermaid
flowchart TD
    S(["Gönderim isteği"]) --> I["NB = 0<br/>BE = macMinBE (3)"]
    I --> D["Rastgele bekle:<br/>0 … 2^BE − 1 birim × 320 µs"]
    D --> C{"CCA: kanal boş mu?"}
    C -- Evet --> T["Çerçeveyi gönder"]
    C -- Hayır --> U["NB = NB + 1<br/>BE = min(BE + 1, macMaxBE = 5)"]
    U --> Q{"NB > macMaxCSMABackoffs (4)?"}
    Q -- Hayır --> D
    Q -- Evet --> F(["Kanal erişim hatası<br/>(CCA failure)"])
    T --> A{"ACK istendi mi?"}
    A -- Hayır --> OK(["Tamam"])
    A -- Evet --> W{"864 µs içinde ACK geldi mi?"}
    W -- Evet --> OK
    W -- Hayır --> R{"Yeniden deneme hakkı var mı?"}
    R -- Evet --> I
    R -- Hayır --> NA(["Hata: No ACK"])
```

| Parametre | Varsayılan | Açıklama |
|---|---|---|
| `macMinBE` | 3 | İlk geri çekilme üssü (0–7 birim) |
| `macMaxBE` | 5 | En büyük geri çekilme üssü (0–31 birim) |
| `macMaxCSMABackoffs` | 4 | Vazgeçmeden önce en fazla CCA denemesi (toplam 5 CCA) |
| `macMaxFrameRetries` | 3 | ACK gelmezse yeniden iletim sayısı (OpenThread doğrudan iletim varsayılanı 3) |

> [!TIP]
> MAC sayaçlarında **TxErrCca** (kanal erişim hatası) oranı yüksekse kanal çok meşguldür (genellikle Wi-Fi); **TxRetry** oranı yüksekse bağlantı kalitesi zayıftır veya gizli düğüm (hidden node) problemi vardır. Bkz. Bölüm 21.

### 4.6 Onay (ACK) ve Yeniden İletim

- Unicast çerçevelerde AR = 1 olur. Alıcı çerçeveyi doğru aldıysa (FCS geçerli ve adres kendisine) **`aTurnaroundTime` = 192 µs** sonra ACK gönderir; CSMA uygulanmaz.
- **Imm-Ack** (2006): 5 baytlık MPDU (FCF 2 + Seq 1 + FCS 2). Güvenlik içermez; yalnızca sıra numarası eşleşmesi kontrol edilir.
- **Enhanced ACK** (2015, Thread 1.2+): IE taşıyabilen, güvenli olabilen ACK. CSL bilgisi (CSL IE) veya Link Metrics verisi taşımak için kullanılır.
- Yayın (broadcast) çerçeveler ACK'lenmez. Bu yüzden MLE/MPL gibi üst katmanlar kendi tekrar mekanizmalarını kullanır.
- Gönderen ACK gelmezse çerçeveyi **aynı sıra numarasıyla** yeniden gönderir; alıcı, yinelenen çerçeveleri sıra numarası + kaynak adres ile ayıklar (RxDuplicated sayacı).

### 4.7 Dolaylı İletim (Indirect Transmission) ve Veri Sorgulama (Data Poll)

Uyuyan cihazlar (SED) radyolarını çoğu zaman kapalı tutar; ebeveyn onlara istediği an veri gönderemez. Çözüm **dolaylı iletim**dir:

1. Ebeveyn, SED'e giden paketi **kuyrukta** tutar.
2. SED periyodik olarak uyanıp ebeveynine **MAC Data Request** komutu (komut kimliği `0x04`) gönderir — buna **poll** (sorgulama) denir.
3. Ebeveyn ACK'deki **Frame Pending** bitini 1 yaparak "senin için veri var" der.
4. SED alıcısını açık tutar; ebeveyn veriyi gönderir.
5. Kuyrukta başka çerçeve varsa veri çerçevesindeki Frame Pending biti 1 olur; SED dinlemeye devam eder veya tekrar poll eder.

```mermaid
sequenceDiagram
    participant SED as SED (çocuk)
    participant P as Ebeveyn Router
    Note over P: SED için paket geldi, kuyruğa alındı
    Note over SED: Radyo kapalı (uyku)
    SED->>P: MAC Data Request (poll)
    P-->>SED: ACK (Frame Pending = 1)
    Note over SED: Alıcı açık kalır
    P->>SED: Data çerçevesi (Frame Pending = 0)
    SED-->>P: ACK
    Note over SED: Radyo kapanır, uykuya döner
```

**Ebeveynin tampon yükümlülüğü:** Thread, ebeveynin her uyuyan çocuğu için en az bir tam IPv6 datagramını (1280 bayt) tutabilmesini ister. Thread 1.2+ ebeveynler bu kapasiteyi **Connectivity TLV** içindeki *SED Buffer Size* ve *SED Datagram Count* alanlarıyla ilan eder.

**Poll yanıtı gecikmesi:** Data Request ile veri çerçevesi arasındaki süre kısa olmalıdır; SED bu süre boyunca alıcısını açık tutar. Bu yüzden ebeveyn yazılımları poll'a hızlı cevap verecek şekilde optimize edilir.

### 4.8 MAC Komutları

Thread yalnızca birkaç MAC komutu kullanır:

| Kimlik | Komut | Thread'de kullanımı |
|---|---|---|
| `0x04` | **Data Request** | SED'in ebeveynini sorgulaması (poll) |
| `0x07` | **Beacon Request** | Active scan (çevredeki 802.15.4 ağlarını bulma) |
| `0x01`–`0x03`, `0x05`, `0x06`, `0x08`, `0x09` | Association, Disassociation, Orphan, Coordinator Realignment, GTS vb. | **Kullanılmaz** (MLE ile değiştirilmiştir) |

**Thread Beacon (tarihsel):** Thread 1.0'da ağlar, Beacon Request'e MAC beacon ile cevap verip beacon yükünde *Protocol ID (3)*, sürüm, "Joining Permitted" ve "Native Commissioning" bayrakları, *Network Name*, *Extended PAN ID* ve *Steering Data* taşırdı. Thread 1.1 ve sonrası ağ keşfi için **MLE Discovery Request/Response** kullanır (Bölüm 9.13); beacon yükü geriye uyumluluk için isteğe bağlıdır.

### 4.9 MAC Güvenliği

Thread'de ağ trafiği **her atlamada** MAC katmanında şifrelenir ve doğrulanır.

#### Güvenlik seviyeleri

| Seviye | Ad | Şifreleme | MIC |
|---|---|---|---|
| 0 | None | Hayır | — |
| 1 / 2 / 3 | MIC-32 / 64 / 128 | Hayır | 4 / 8 / 16 bayt |
| 4 | ENC | Evet | — |
| **5** | **ENC-MIC-32** | **Evet** | **4 bayt** ← Thread bunu kullanır |
| 6 / 7 | ENC-MIC-64 / 128 | Evet | 8 / 16 bayt |

#### Auxiliary Security Header

```text
+------------------+----------------+--------------------------------------+
| Security Control | Frame Counter  | Key Identifier                       |
|     1 bayt       |  4 bayt (LE)   | Mode 0: yok                          |
|                  |                | Mode 1: Key Index (1)                |
|                  |                | Mode 2: Key Source (4) + Index (1)   |
|                  |                | Mode 3: Key Source (8) + Index (1)   |
+------------------+----------------+--------------------------------------+

Security Control:
 bit:   7      6           5              4  3          2 1 0
      ayr.  ASN-in-Nonce  FC Suppression  Key ID Mode   Security Level
```

| Kullanım | Key ID Mode | Anahtar | Security Control | Başlık boyutu |
|---|---|---|---|---|
| Normal veri çerçeveleri | **1** | MAC Key (Network Key'den türetilmiş) | `0x0D` | 6 bayt |
| Joiner Entrust (devreye almada) | **0** | **KEK** (DTLS oturumundan türetilmiş) | `0x05` | 5 bayt |
| MLE mesajları | MAC'te güvenliksiz; güvenlik **MLE katmanında** (Bölüm 9.4) | MLE Key | — | — |

**Key Index** değeri, mevcut **Key Sequence**'ten türetilir:

```text
Key Index = (Key Sequence mod 128) + 1        → 1 … 128
```

Alıcı, Key Index'e bakarak çerçevenin mevcut, önceki veya sonraki anahtar dizisiyle şifrelendiğini anlar ve ilgili anahtarı kullanır (anahtar rotasyonu, Bölüm 15).

#### AES-CCM* nonce'u (13 bayt)

```text
+-----------------------------------+--------------------+----------------+
| Kaynak Extended Address (8 bayt)  | Frame Counter (4)  | Sec. Level (1) |
+-----------------------------------+--------------------+----------------+
```

> [!IMPORTANT]
> Nonce her zaman gönderenin **64 bitlik Extended Address**'ini içerir — çerçeve kısa adresle gönderilse bile. Bu yüzden bir cihaz, bir komşudan gelen kısa adresli güvenli çerçeveyi çözebilmek için o komşunun Extended Address'ini önceden (MLE ile) öğrenmiş olmalıdır. Bu, MLE bağlantı kurulumunun neden zorunlu olduğunun bir sebebidir.

**Şifrelenen ve doğrulanan kısımlar:**

- **Doğrulanır (AAD)**: MHR (Frame Control, adresler, Aux Security Header, IE'ler).
- **Şifrelenir + doğrulanır**: MAC yükü (6LoWPAN ile sıkıştırılmış IPv6 paketi).
- **MIC** (4 bayt) yükün sonuna, FCS'den önce eklenir.

#### Frame Counter ve tekrar (replay) koruması

- Her cihaz, gönderdiği her güvenli çerçeve için 32 bitlik **Frame Counter**'ı bir artırır.
- Alıcı, her komşu için en son kabul ettiği frame counter'ı saklar ve **daha küçük veya eşit** değerli çerçeveleri reddeder.
- Komşuların başlangıç sayaçları MLE ile değiş tokuş edilir (*Link-layer Frame Counter TLV*).
- Key Sequence değiştiğinde (yeni anahtar) sayaçlar sıfırlanır; çünkü (anahtar, nonce) çifti benzersiz kalmaya devam eder.
- Cihazlar yeniden başlatmada sayacın geri gitmemesi için değeri kalıcı belleğe **ileriye dönük bir payla** yazar (OpenThread birkaç yüz/bin değer ileriyi saklar); aksi hâlde yeniden başlatma sonrası gönderilen çerçeveler komşular tarafından reddedilirdi.

### 4.10 Bilgi Elemanları (Information Elements — IE)

802.15.4-2015 çerçevelerinde, başlığa esnek alanlar eklemek için IE'ler kullanılır. Thread 1.2+ bunları şu amaçlarla kullanır:

| IE | Element ID | İçerik | Kullanım |
|---|---|---|---|
| **CSL IE** | `0x1A` | CSL Phase (2 bayt), CSL Period (2 bayt) — 10 sembol (160 µs) biriminde | SSED'in örnekleme zamanlamasını ebeveynine bildirmesi (Bölüm 18) |
| **Vendor Specific Header IE** | `0x00` | Thread Group OUI'si + içerik | Enhanced-ACK tabanlı Link Metrics raporları |
| **Header Termination 1** | `0x7E` | — | Header IE'lerin bittiğini ve Payload IE'lerin başladığını gösterir |
| **Header Termination 2** | `0x7F` | — | Header IE'lerin bittiğini ve doğrudan yükün başladığını gösterir |

Header IE tanımlayıcısı 2 bayttır: 7 bit uzunluk, 8 bit Element ID, 1 bit tür (0 = header IE).

### 4.11 Taramalar

| Tarama | Nasıl? | Thread'de amacı |
|---|---|---|
| **Energy Scan** | Her kanalda belirli süre ED ölçümü | En sessiz kanalı seçmek; commissioner'ın uzaktan Energy Scan istemesi (`c/es`) |
| **Active Scan** | Her kanalda Beacon Request yayını, beacon dinleme | Çevredeki 802.15.4 ağlarını listelemek (`scan` komutu) |
| **MLE Discovery Scan** | Her kanalda MLE Discovery Request yayını | Thread ağlarını ve devreye almaya açık ağları bulmak (`discover` komutu, Joiner) |

### 4.12 MAC Seviyesinde Alım Filtreleri

Bir çerçeve kabul edilmeden önce sırasıyla şu kontrollerden geçer:

1. **FCS** doğru mu? (Değilse: RxErrFcs)
2. **Hedef PAN ID** kendi PAN ID'm veya `0xFFFF` mi?
3. **Hedef adres** kendi kısa/genişletilmiş adresim veya `0xFFFF` mi? (Değilse: RxDestAddrFiltered)
4. **Kaynak adres** geçerli mi, (filtre etkinse) izin listesinde mi?
5. Güvenli çerçeveyse: **anahtar** bulunuyor mu, **frame counter** yeni mi, **MIC** doğru mu? (Değilse: RxErrSec)
6. **Yinelenen çerçeve** mi? (sıra numarası + kaynak; RxDuplicated)
7. Gönderen bilinen bir **komşu** mu? Değilse ve çerçeve güvenliyse genellikle reddedilir (RxErrUnknownNeighbor) — istisna: MLE ve devreye alma mesajları.

### 4.13 Bölüm Özeti

- Thread, 802.15.4 MAC'in beacon'sız, slotsuz CSMA-CA modunu kullanır; association yerine MLE vardır.
- Kısa MAC adresi = RLOC16; genişletilmiş adres rastgeledir ve güvenlik nonce'unun parçasıdır.
- Veri çerçeveleri seviye 5 (AES-CCM*, 4 baytlık MIC), Key ID Mode 1 ile korunur; MAC ek yükü ≈ 21 bayttır.
- Uyuyan cihazlara veri dolaylı iletimle (poll + Frame Pending) ulaştırılır.
- Thread 1.2+ Enhanced ACK ve Header IE'leri ile CSL ve Link Metrics gibi gelişmiş özellikleri taşır.
