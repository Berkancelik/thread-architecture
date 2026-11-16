## 29. Ekler

### Ek A — Sabitler ve Zamanlayıcılar

| Sabit / parametre | Değer | Açıklama | Bölüm |
|---|---|---|---|
| `aMaxPHYPacketSize` | 127 bayt | En büyük 802.15.4 çerçevesi | 3 |
| Sembol süresi / bayt süresi | 16 µs / 32 µs | 250 kbit/s O-QPSK | 3 |
| `aTurnaroundTime` | 192 µs | RX↔TX geçişi, ACK gecikmesi | 3, 4 |
| `aUnitBackoffPeriod` | 320 µs | CSMA backoff birimi | 4 |
| `macAckWaitDuration` | 864 µs | ACK bekleme süresi | 4 |
| `macMinBE` / `macMaxBE` | 3 / 5 | CSMA backoff üsleri | 4 |
| `macMaxCSMABackoffs` | 4 | CCA deneme sınırı | 4 |
| `macMaxFrameRetries` | 3 | ACK'siz yeniden iletim (OpenThread doğrudan iletim) | 4 |
| IPv6 asgari MTU | 1280 bayt | 6LoWPAN parçalamayı zorunlu kılar | 5 |
| Bağlam ID yeniden kullanım gecikmesi | 48 saat | Kaldırılan 6LoWPAN bağlamı | 5, 12 |
| `MAX_ROUTERS` | 32 | Partition başına aktif router | 7, 8 |
| Router ID aralığı | 0–62 | 63 geçersiz (ALOC alanı) | 6 |
| Child ID aralığı | 1–511 | 9 bit | 6 |
| `ROUTER_UPGRADE_THRESHOLD` | 16 | Altındaysa REED'ler terfi eder | 7 |
| `ROUTER_DOWNGRADE_THRESHOLD` | 23 | Üstündeyse gereksiz router'lar düşer | 7 |
| `ROUTER_SELECTION_JITTER` | 120 s | Terfi öncesi rastgele bekleme üst sınırı | 7 |
| `ADVERTISEMENT_I_MIN` / `I_MAX` | 1 s / 32 s | Trickle aralıkları | 9 |
| `MAX_NEIGHBOR_AGE` | 100 s | Router komşu yaşlanması | 9, 10 |
| `PARENT_REQUEST_ROUTER_TIMEOUT` | 750 ms | Router'lara Parent Request bekleme | 9 |
| `PARENT_REQUEST_REED_TIMEOUT` | 1250 ms | Router + REED Parent Request bekleme | 9 |
| REED Advertisement aralığı | ≈ 570–630 s | REED varlık ilanı | 9 |
| `MAX_ROUTE_COST` | 16 | Ulaşılamaz (sonsuz) maliyet | 10 |
| Link cost (LQ 3/2/1/0) | 1 / 2 / 4 / ∞ | Bağlantı maliyeti | 10 |
| `NETWORK_ID_TIMEOUT` | 120 s | Leader'dan haber alınamazsa partition kaybı | 11 |
| `MAX_LEADER_TO_ROUTER_TIMEOUT` | 90 s | Leader'ın ulaşılamayan router ID'sini bırakması | 11 |
| `ID_REUSE_DELAY` | 100 s | Serbest bırakılan Router ID'nin bekletilmesi | 11 |
| Varsayılan partition weighting | 64 | Leader Data | 11 |
| Network Data azami boyutu | 254 bayt | | 12 |
| Thread Enterprise Number | 44970 | Service TLV | 12 |
| CoAP `ACK_TIMEOUT` / `MAX_RETRANSMIT` | 2 s / 4 | TMF güvenilirliği | 13 |
| Key Rotation Time (varsayılan) | 672 saat (28 gün) | Security Policy | 15 |
| PSKc PBKDF2 tur sayısı | 16384 | AES-CMAC-PRF-128 | 15 |
| PSKd uzunluğu | 6–32 karakter | `I`, `O`, `Q`, `Z` hariç büyük harf/rakam | 15 |
| Commissioner oturum zaman aşımı | ≈ 50 s | Keep-alive gelmezse | 16 |
| Pending Dataset varsayılan gecikmesi | 300 s | Delay Timer | 17 |
| Varsayılan child timeout | 240 s | OpenThread | 18 |
| Supervision interval / check timeout | 129 s / 190 s | OpenThread varsayılanları | 18 |
| Address Query zaman aşımı | 3 s | OpenThread | 6 |
| Address Query ilk yeniden deneme gecikmesi | 15 s | OpenThread | 6 |

### Ek B — Portlar, Adresler ve Kimlikler

| Öğe | Değer |
|---|---|
| MLE | UDP 19788 |
| TMF (CoAP) | UDP 61631 (`0xF0BF`) |
| MeshCoP Joiner (varsayılan) | UDP 1000 |
| Border Agent (OTBR varsayılanı) | UDP 49191 (mDNS SRV ile ilan) |
| Matter | UDP/TCP 5540 |
| mDNS | UDP 5353 |
| SRP sunucusu (OpenThread) | UDP 53535–53554 aralığı (Network Data ile ilan) |
| Leader ALOC16 | `0xFC00` |
| DHCPv6 Agent ALOC16 | `0xFC01`–`0xFC0F` |
| Service ALOC16 | `0xFC10`–`0xFC2F` |
| Commissioner ALOC16 | `0xFC30`–`0xFC37` |
| Primary BBR ALOC16 | `0xFC38` |
| ND Agent ALOC16 | `0xFC40`–`0xFC4E` |
| Link-Local All Thread Nodes | `ff32:40:<mesh-local önek>::1` |
| Realm-Local All Thread Nodes | `ff33:40:<mesh-local önek>::1` |
| Realm-Local All MPL Forwarders | `ff03::fc` |
| mDNS servisleri | `_meshcop._udp` (Border Agent), `_meshcop-e._udp` (ePSKc), `_trel._udp` (TREL), `_matter._tcp`, `_matterc._udp`, `_matterd._udp` |
| Thread sürüm numaraları (Version TLV) | 1.1 = 2, 1.2 = 3, 1.3 = 4, 1.4 = 5 |

### Ek C — Mesaj ve TLV Referans Dizini

| Konu | Bulunduğu yer |
|---|---|
| 802.15.4 Frame Control bitleri | Bölüm 4.3 |
| Auxiliary Security Header, nonce | Bölüm 4.9 |
| Header IE'ler (CSL IE vb.) | Bölüm 4.10 |
| 6LoWPAN dispatch, IPHC, NHC | Bölüm 5.2–5.5 |
| Mesh Header, FRAG1/FRAGN | Bölüm 5.7–5.8 |
| RLOC16 ve ALOC tablosu | Bölüm 6.4–6.5 |
| MLE komutları ve TLV'leri | Bölüm 9.4–9.6 |
| Route64 TLV | Bölüm 10.3 |
| Leader Data TLV | Bölüm 9.6, 11.3 |
| Network Data TLV'leri | Bölüm 12.4–12.10 |
| TMF URI'leri ve TLV'leri | Bölüm 13.3–13.4 |
| MeshCoP / Dataset TLV'leri | Bölüm 17.2–17.7 |
| Security Policy bayrakları | Bölüm 15.9 |
| Teşhis TLV'leri | Bölüm 21.1 |
| Spinel komutları | Bölüm 24.5 |

### Ek D — İlgili Standartlar ve RFC'ler

| Standart | Konu |
|---|---|
| IEEE 802.15.4-2006 / -2015 / -2020 | Düşük hızlı kablosuz kişisel alan ağları (PHY/MAC) |
| RFC 4944 | IPv6 over IEEE 802.15.4 (6LoWPAN çerçeveleme, Mesh Header, parçalama) |
| RFC 6282 | 6LoWPAN başlık sıkıştırma (IPHC, NHC) |
| RFC 6775 | 6LoWPAN Neighbor Discovery optimizasyonu (arka plan) |
| RFC 8200 / RFC 4291 | IPv6 ve IPv6 adresleme mimarisi |
| RFC 4193 | Unique Local Addresses (ULA) |
| RFC 4862 / RFC 7217 | SLAAC / kararlı-gizli arayüz kimlikleri |
| RFC 6724 | IPv6 varsayılan adres seçimi |
| RFC 3306 | Önek tabanlı multicast adresleri |
| RFC 4443 | ICMPv6 |
| RFC 4191 | Router Advertisement Route Information Option (RIO) |
| RFC 7252 | CoAP |
| RFC 6347 | DTLS 1.2 |
| RFC 8236 | J-PAKE (EC-JPAKE'nin temeli) |
| RFC 2104 / RFC 4493 / RFC 4615 | HMAC / AES-CMAC / AES-CMAC-PRF-128 |
| RFC 8018 | PBKDF2 (PKCS #5 v2.1) |
| RFC 6206 | Trickle algoritması |
| RFC 7731 | MPL (Multicast Protocol for Low-Power and Lossy Networks) |
| RFC 6762 / RFC 6763 | mDNS / DNS-SD |
| RFC 9665 | SRP (Service Registration Protocol) |
| RFC 8766 | DNS-SD Discovery Proxy |
| RFC 6146 / RFC 6147 / RFC 6052 | NAT64 / DNS64 / IPv4-gömülü IPv6 adresleri |
| RFC 7050 / RFC 8781 | NAT64 önek keşfi / RA PREF64 seçeneği |
| RFC 8415 | DHCPv6 (önek delegasyonu dahil) |
| Thread Specification (Thread Group) | Thread 1.1 / 1.2 / 1.3 / 1.4 çekirdek ve Border Router şartnameleri |
| Matter Specification (CSA) | Matter çekirdek, cihaz kütüphanesi ve cluster şartnameleri |

### Ek E — Sözlük

| Terim | Açıklama |
|---|---|
| **6LoWPAN** | IPv6'yı 802.15.4 gibi kısıtlı bağlantılara uyarlayan sıkıştırma/parçalama katmanı |
| **ACK** | Onay çerçevesi; Imm-Ack (5 bayt) veya Enhanced ACK (IE taşıyabilir) |
| **Active Dataset** | Ağın şu an kullandığı Operational Dataset |
| **Active Timestamp** | Dataset sürüm damgası; büyük olan kazanır |
| **Address Query / Notification** | EID'nin RLOC16'sını bulma sorgusu ve cevabı (`a/aq`, `a/an`) |
| **Advertisement** | Router'ların Trickle ile gönderdiği, Route64 içeren MLE mesajı |
| **AES-CCM\*** | 802.15.4'te kullanılan, şifreleme + doğrulama sağlayan blok şifre modu |
| **ALOC** | Anycast Locator; Leader, commissioner, servis gibi rollere ulaşma adresi (`0xFCxx`) |
| **Announce** | Ağın kanal/PAN bilgisini diğer kanallarda duyuran MLE mesajı |
| **BBR (Backbone Router)** | Thread ağını omurgaya bağlayan, DUA ve MLR'yi yöneten işlev (1.2+) |
| **BDX** | Matter Bulk Data Exchange; OTA gibi büyük aktarımlar |
| **Bloom filtresi** | Steering Data'nın kullandığı olasılıksal küme yapısı |
| **Border Agent** | Harici commissioner'ın ağa güvenli erişim noktası (`_meshcop._udp`) |
| **Border Router (BR)** | Thread ile diğer IP ağları arasında yönlendirme yapan cihaz |
| **CASE / PASE** | Matter'ın sertifika tabanlı / parola tabanlı güvenli oturum kurma protokolleri |
| **CCA** | Clear Channel Assessment; göndermeden önce kanal boşluk kontrolü |
| **CCM** | Commercial Commissioning Mode; sertifika tabanlı ticari devreye alma (1.2) |
| **Child** | Bir parent'a bağlı uç cihaz (REED, FED, MED, SED, SSED) |
| **Child Supervision** | Parent'ın uyuyan child'a periyodik denetim çerçevesi göndermesi |
| **CoAP** | Kısıtlı cihazlar için UDP tabanlı REST protokolü (RFC 7252) |
| **Commissioner** | Yeni cihazların ağa katılmasını yetkilendiren rol |
| **Connectivity TLV** | Parent adayının bağlantı durumu bilgisi |
| **Context** | 6LoWPAN sıkıştırmasında paylaşılan önek (bağlam 0 = mesh-local önek) |
| **CSL** | Coordinated Sampled Listening; parent'ın zamanlanmış gönderimiyle SSED'e veri ulaştırma |
| **CSMA-CA** | Taşıyıcı dinlemeli çoklu erişim / çakışmadan kaçınma |
| **Data Poll** | SED'in MAC Data Request ile parent'ını sorgulaması |
| **Delay Timer** | Pending Dataset'in Active olmasına kalan süre |
| **Discovery Request/Response** | Güvenliksiz MLE ağ keşif mesajları |
| **DNS-SD** | DNS tabanlı servis keşfi |
| **DTLS** | UDP üzerinde TLS; MeshCoP oturumlarında kullanılır |
| **DUA** | Domain Unicast Address; Thread Domain genelinde sabit adres (1.2+) |
| **EC-JPAKE** | Eliptik eğri tabanlı parola doğrulamalı anahtar değişimi |
| **ED (Energy Detection)** | Kanal enerjisi ölçümü |
| **EID** | Endpoint Identifier; topolojiden bağımsız cihaz adresi (ML-EID, OMR, DUA) |
| **ePSKc** | Ephemeral PSKc; Border Agent'ın ürettiği kısa ömürlü commissioner anahtarı (1.4) |
| **EUI-64** | Fabrika tarafından atanmış 64 bitlik benzersiz donanım kimliği |
| **Extended Address** | Cihazın ağdaki rastgele 64 bitlik MAC adresi |
| **Extended PAN ID** | Thread ağının 8 baytlık benzersiz kimliği |
| **FED** | Full End Device; router olmayan FTD |
| **FEM** | Front-End Module; PA + LNA RF ön ucu |
| **Frame Counter** | Tekrar korumasında kullanılan, her mesajda artan 32 bitlik sayaç |
| **Frame Pending** | Parent'ta bekleyen veri olduğunu bildiren MAC biti |
| **FTD / MTD** | Full / Minimal Thread Device |
| **HDLC-lite** | Spinel'in UART üzerindeki çerçeveleme biçimi |
| **ICD** | Intermittently Connected Device; Matter'ın uyuyan cihaz modeli (SIT/LIT) |
| **IE** | Information Element; 802.15.4-2015 başlık/yük uzantıları |
| **IPHC / NHC** | 6LoWPAN IPv6 başlık ve sonraki başlık (UDP) sıkıştırması |
| **Joiner / Joiner Router** | Ağa katılan yeni cihaz / onun DTLS trafiğini aktaran komşu router |
| **Joiner ID** | SHA-256(EUI-64)'ten türetilen 64 bitlik katılım kimliği |
| **KEK** | Key Encryption Key; Joiner Entrust'ı şifreleyen anahtar |
| **Key Sequence** | Anahtar rotasyon sayacı; MAC/MLE anahtarları bundan türetilir |
| **Leader** | Router ID'leri ve Network Data'yı yöneten router |
| **Leader Data** | Partition ID, weighting, veri sürümleri ve Leader Router ID |
| **Link Margin** | RSSI − gürültü tabanı (dB) |
| **Link Metrics** | Komşudan bağlantı ölçümleri isteme mekanizması (1.2+) |
| **Link Quality (LQ)** | Link margin'den türetilen 0–3 arası kalite seviyesi |
| **LQI** | Link Quality Indicator; alınan sinyal kalitesi göstergesi (0–255) |
| **MED / SED / SSED** | Minimal / Sleepy / Synchronized Sleepy End Device |
| **Mesh Header** | 6LoWPAN'da uçtan uca kaynak/hedef RLOC16'ları taşıyan başlık |
| **Mesh-Local Prefix** | Mesh-local adreslerin ULA /64 öneki |
| **MeshCoP** | Mesh Commissioning Protocol; Thread devreye alma protokolü |
| **MIC** | Message Integrity Code; bütünlük doğrulama kodu |
| **ML-EID** | Mesh-Local EID; rastgele IID'li sabit mesh-local adres |
| **MLE** | Mesh Link Establishment; Thread'in link seviyesi kontrol protokolü |
| **MLR** | Multicast Listener Registration; multicast aboneliğini BBR'ye kaydetme |
| **MPL** | Multicast Protocol for LLNs; mesh içi multicast yayma protokolü |
| **MRP** | Matter Message Reliability Protocol |
| **NAT64** | IPv6 ↔ IPv4 adres/protokol çevirisi |
| **NCP / RCP** | Network / Radio Co-Processor mimarileri |
| **Network Data** | Ağ geneli önek, rota, servis ve devreye alma bilgisi |
| **Network Key** | Ağın 128 bitlik kök anahtarı |
| **OMR Prefix** | Off-Mesh Routable önek; Thread cihazlarına dışarıdan erişilebilir adres sağlar |
| **OpenThread / OTBR** | Açık kaynak Thread yığını / Border Router uygulaması |
| **Operational Dataset** | Ağın kimlik bilgileri ve parametreleri |
| **PAN ID** | 802.15.4 ağ kimliği (16 bit) |
| **Parent** | Bir uç cihazın bağlı olduğu router |
| **Partition** | Aynı Leader'ı paylaşan, birbirine ulaşabilen cihaz kümesi |
| **Pending Dataset** | Gelecekte devreye girecek dataset |
| **PSKc / PSKd** | Commissioner anahtarı / Joiner parolası |
| **REED** | Router Eligible End Device; router olabilecek uç cihaz |
| **RIO** | Route Information Option; RA içinde rota ilanı |
| **RLOC / RLOC16** | Routing Locator adresi / 16 bitlik konum değeri (Router ID + Child ID) |
| **Route64 TLV** | Router'ların yönlendirme bilgisini taşıyan MLE TLV'si |
| **Router ID** | Leader'ın atadığı 0–62 arası router kimliği |
| **RSSI** | Alınan sinyal gücü |
| **Security Policy** | Anahtar rotasyon süresi ve güvenlik bayrakları |
| **SLAAC** | Durumsuz IPv6 adres otomatik yapılandırması |
| **Spinel** | Host ile NCP/RCP arasındaki protokol |
| **SRP** | Service Registration Protocol; unicast DNS-SD kaydı |
| **Steering Data** | Katılmasına izin verilen joiner'ları gösteren Bloom filtresi |
| **TCAT** | Thread Commissioning over Authenticated TLS (1.4) |
| **TMF** | Thread Management Framework; CoAP tabanlı yönetim mesajları |
| **TREL** | Thread Radio Encapsulation Link; Thread'i Wi-Fi/Ethernet üzerinden taşıma (1.3+) |
| **Trickle** | Ağ kararlıyken mesaj sıklığını azaltan zamanlama algoritması |
| **ULA** | Unique Local Address (`fd00::/8`) |

### Ek F — Kaynaklar ve İleri Okuma

| Kaynak | Adres |
|---|---|
| Thread Group (şartnameler, sertifikasyon, teknik belgeler) | https://www.threadgroup.org |
| OpenThread belgeleri (kılavuzlar, CLI ve API referansı) | https://openthread.io |
| OpenThread kaynak kodu | https://github.com/openthread/openthread |
| OpenThread Border Router | https://github.com/openthread/ot-br-posix |
| Connectivity Standards Alliance (Matter) | https://csa-iot.org |
| Matter açık kaynak SDK | https://github.com/project-chip/connectedhomeip |
| IETF RFC'leri | https://www.rfc-editor.org |

### Ek G — Doküman Sürüm Geçmişi

| Sürüm | Tarih | Değişiklik |
|---|---|---|
| 1.0 | Kasım 2026 | İlk tam sürüm: 29 bölüm + ekler; Markdown ve HTML çıktıları |
