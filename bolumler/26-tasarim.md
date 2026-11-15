## 26. Ağ Tasarımı ve En İyi Uygulamalar

### 26.1 Planlama Adımları

1. **Envanter**: Kaç cihaz var? Hangileri şebekeden beslenecek (router adayı), hangileri pilli (SED/SSED)?
2. **Kapsama haritası**: Ev/bina planı üzerinde Border Router ve router adaylarının yerleri; duvar/kat malzemeleri.
3. **Router yoğunluğu**: Her pilli cihazın çevresinde en az **iki** iyi (LQ 3) ebeveyn adayı olmasını hedefleyin.
4. **Border Router sayısı ve konumu**: En az **iki** BR, merkezi ve farklı bölgelerde; aynı Thread ağında.
5. **Kanal seçimi**: Wi-Fi kanallarını ölçün; Thread'i en az örtüşen kanala koyun.
6. **IPv6 ve mDNS altyapısı**: Ev ağının IPv6 RA/RIO ve mDNS'i düzgün taşıdığından emin olun.
7. **Test**: Kurulum sonrası topolojiyi, link kalitelerini ve yeniden iletim oranlarını kontrol edin.

### 26.2 Router ve Border Router Yerleşimi

| Kural | Gerekçe |
|---|---|
| Şebekeden beslenen cihazları router/REED olarak bırakın | Mesh omurgasını güçlendirir |
| Router'lar arası tipik mesafe iç mekânda ≈ 5–15 m, en fazla 1–2 duvar | LQ 3 bağlantılar için pay |
| Katlar arası en az birkaç router bağlantısı | Tek noktadan bölünmeyi (partition) önler |
| Border Router'ları metal dolapların, TV arkalarının içine koymayın | Ciddi sinyal kaybı |
| BR'yi Wi-Fi router'ının hemen yanına koymayın (ayrı cihazlarsa) | Girişim; ancak ağ bağlantısı için Ethernet kullanılabiliyorsa daha iyi |
| Pilli cihazları router yapmayın | Pil günler içinde biter |

### 26.3 Kanal Planlama

- Tercih sırası (Wi-Fi 1/6/11 kullanan ortamlarda): **15, 20, 25** (ve bölgeye göre **26**).
- Wi-Fi 40 MHz kanal genişliği 2.4 GHz'te geniş bir bölgeyi kaplar; mümkünse 2.4 GHz Wi-Fi'ı 20 MHz'te çalıştırın.
- Kanal değişikliği tüm ağ için bir Pending Dataset işlemidir; sık sık yapılmamalı, gerekirse otomatik kanal yöneticisine bırakılmalıdır.
- Çevredeki diğer Thread/Zigbee ağlarını `scan` / `discover` ile görüp aynı kanalı paylaşmaktan kaçının.

### 26.4 Tek Ağ İlkesi

- Bir evde/binada **tek Thread ağı** hedefleyin; farklı ekosistemlerin BR'lerini kimlik paylaşımıyla (işletim sistemi API'leri, ePSKc) aynı ağa katın.
- İlk BR'yi kurduktan sonra eklenen BR'lerin **aynı Extended PAN ID**'yi kullandığını doğrulayın.
- Büyük binalarda birden fazla ağ gerekiyorsa bunları Thread Domain/BBR veya TREL ile planlı şekilde birleştirin.

### 26.5 Ev Ağı (Altyapı) Gereksinimleri

| Gereksinim | Açıklama |
|---|---|
| IPv6 bağlantı yerel (link-local) ve ULA iletişimine izin verilmeli | Thread erişimi IPv6 ile yapılır; ISS IPv6 vermese bile yerel IPv6 çalışır |
| RA'lar ve ICMPv6 engellenmemeli | RIO ile Thread rotaları öğrenilir |
| Denetleyiciler RIO'yu kabul etmeli | Linux'ta `accept_ra_rt_info_max_plen` vb. ayarlar |
| mDNS (5353) çalışmalı, VLAN'lar arasında gerekiyorsa yansıtılmalı | Matter keşfi ve Border Agent ilanı |
| Wi-Fi'da çoklu yayın filtreleme/IGMP-MLD snooping doğru yapılandırılmalı | Yanlış snooping mDNS ve RA'ları düşürebilir |
| Denetleyiciler ve BR'ler aynı L2 segmentte olmalı (veya doğru yönlendirme) | RIO yalnızca aynı bağlantıda geçerlidir |

### 26.6 Cihaz Davranışı Ayarları

| Parametre | Öneri |
|---|---|
| SED poll period | Etkileşimsiz sensörlerde uzun (15–60 s+); etkileşimli cihazlarda ICD aktif mod veya CSL |
| Child timeout | Poll period'un birkaç katı; çok kısa olursa gereksiz yeniden bağlanmalar olur |
| Rapor/abonelik aralıkları | İhtiyaca göre; çok sık rapor enerji ve kanal kapasitesi tüketir |
| Uygulama yükü | Tek çerçeveye sığacak boyutlar; büyük veriyi parçalamaktan kaçının |
| Çoklu yayın | Yalnızca gerektiğinde; periyodik yayın yerine abonelik |
| TX gücü | Router/BR'de yüksek (yasal sınırda), SED'de ihtiyaca göre |

### 26.7 Güvenlik Uygulamaları

- Rastgele ağ parametreleri (`dataset init new`), cihaz başına benzersiz PSKd, güçlü passphrase.
- Dataset'i (özellikle Network Key) günlüklere, destek çıktılarına, ekran görüntülerine sızdırmayın.
- Güvenli önyükleme, imzalı OTA, kapalı debug portları, güvenli anahtar depolama.
- Network Key sızıntısı şüphesinde Pending Dataset ile anahtar değişimi.
- Uygulama katmanında uçtan uca güvenlik (Matter CASE).

### 26.8 Yazılım Güncellemeleri (OTA) Üzerine

Thread'in verimi düşük olduğundan büyük imajların aktarımı zaman alır:

```text
Örnek: 600 KB imaj, etkin verim ≈ 20 kbit/s
       600 × 1024 × 8 / 20 000 ≈ 246 s ≈ 4 dakika (ideal, kesintisiz)
       Uyuyan cihazlarda, çok atlamada ve paylaşılan kanalda: onlarca dakika olabilir
```

- Matter OTA (BDX) blok boyutunu ve uyuyan cihazlarda aktif modu doğru ayarlayın.
- Aynı anda çok sayıda cihazı güncellemek kanalı doyurur; güncellemeleri kademelendirin.
- İmajı sıkıştırmak ve delta (fark) güncellemeleri kullanmak süreyi azaltır.

### 26.9 Kurulum Sonrası Kontrol Listesi

| Kontrol | Nasıl? | Hedef |
|---|---|---|
| Tek partition | Farklı cihazlarda `leaderdata` (Partition ID) | Hepsi aynı |
| Tek Thread ağı | BR'lerin Extended PAN ID'si, `_meshcop._udp` ilanları | Hepsi aynı |
| Router sayısı | `router table` | Cihaz sayısına uygun, 32'nin altında |
| Link kaliteleri | `router table` LQ In/Out, `neighbor table` RSSI | Çoğunlukla LQ 3 |
| Yeniden iletim oranı | `counters mac` | < %10 |
| OMR adresleri | Cihazlarda `ipaddr` | OMR önekli adres var |
| SRP kayıtları | BR'de `srp server service` | Tüm Matter cihazları kayıtlı |
| Dış erişim | Denetleyiciden cihaz OMR adresine ping | Başarılı |
| BR yedekliliği | Bir BR'yi kapatıp erişimi test edin | Erişim devam ediyor |

### 26.10 Bölüm Özeti

- Şebekeden beslenen cihazlarla güçlü bir router omurgası, en az iki BR ve tek Thread ağı temel ilkelerdir.
- Kanal seçimi Wi-Fi'a göre yapılmalı; ev ağının IPv6/RA/mDNS desteği doğrulanmalıdır.
- SED parametreleri, rapor aralıkları ve yük boyutları enerji ve güvenilirliği belirler.
- OTA güncellemeleri yavaştır; kademelendirme ve doğru blok boyutları gerekir.
- Kurulum sonrası topoloji, link kalitesi ve dış erişim mutlaka doğrulanmalıdır.
