## 21. Ağ Teşhisi, İzleme ve Paket Analizi

### 21.1 Network Diagnostics (Ağ Teşhis) Protokolü

Thread, bir cihazın başka bir cihazın iç durumunu uzaktan sorgulayabilmesi için TMF tabanlı bir teşhis mekanizması tanımlar:

| URI | Kullanım |
|---|---|
| `d/dg` | **Diagnostic Get**: Belirli bir cihazdan (RLOC/ML-EID) istenen TLV'leri ister; cevap aynı CoAP alışverişinde döner |
| `d/dq` + `d/da` | **Diagnostic Get Query / Answer**: Çoklu yayın (ör. `ff03::1`) ile birçok cihaza sorgu; her cihaz ayrı bir Answer mesajıyla cevap verir |
| `d/dr` | **Diagnostic Reset**: Belirli sayaçları sıfırlar |

#### Teşhis TLV'leri

| Tür | TLV | İçerik |
|---|---|---|
| 0 | Extended MAC Address | Cihazın Extended Address'i |
| 1 | Address16 | RLOC16 |
| 2 | Mode | R/D/N bitleri |
| 3 | Timeout | Child timeout (çocuklar için) |
| 4 | Connectivity | Connectivity TLV (Bölüm 9.6) |
| 5 | Route64 | Yönlendirme bilgisi |
| 6 | Leader Data | Partition, Leader, sürümler |
| 7 | Network Data | Cihazın gördüğü Network Data |
| 8 | IPv6 Address List | Cihazın IPv6 adresleri |
| 9 | MAC Counters | MAC katmanı sayaçları |
| 14 | Battery Level | Pil seviyesi (%) |
| 15 | Supply Voltage | Besleme gerilimi (mV) |
| 16 | Child Table | Çocuk tablosu (router'lar için) |
| 17 | Channel Pages | Desteklenen kanal sayfaları |
| 18 | Type List | (İstekte) istenen TLV türlerinin listesi |
| 19 | Max Child Timeout | Çocuklardan en büyük timeout |
| 23 | EUI-64 | Fabrika EUI-64'ü |
| 24 | Version | Thread sürümü |
| 25 / 26 / 27 | Vendor Name / Model / SW Version | Üretici bilgileri |
| 28 | Thread Stack Version | Yığın sürüm dizesi |
| 29 | Child | (1.4) Ayrıntılı çocuk bilgisi |
| 30 | Child IPv6 Address List | (1.4) Çocuğun adresleri |
| 31 | Router Neighbor | (1.4) Router komşu bilgisi |
| 32 / 33 | Answer / Query ID | (1.4) Çok parçalı cevap yönetimi |
| 34 | MLE Counters | (1.4) MLE rol/attach sayaçları |
| 35 | Vendor App URL | Üretici uygulama adresi |

#### Örnek

```text
> networkdiagnostic get fdde:ad00:beef:0:0:ff:fe00:9400 0 1 5 6 9 16
DIAG_GET.rsp/ans from fdde:ad00:beef:0:0:ff:fe00:9400:
Ext Address: 8e1f00ab23cd45ef
Rloc16: 0x9400
Route: …
Leader Data: PartitionId:0x3f8a12c4 Weighting:64 DataVersion:118 StableDataVersion:74 LeaderRouterId:23
MAC Counters: …
Child Table: …
```

OpenThread'in `meshdiag topology` gibi komutları, bu mekanizmayı kullanarak tüm ağın router/çocuk topolojisini tek komutla çıkarabilir.

### 21.2 Teşhis İçin OpenThread CLI Komutları

| Komut | Ne gösterir? | Neye bakılır? |
|---|---|---|
| `state` | Rol (disabled/detached/child/router/leader) | Cihaz beklenen rolde mi? |
| `rloc16`, `extaddr` | Adresler | Kimlik |
| `leaderdata` | Partition ID, weighting, sürümler, Leader Router ID | Ağda birden çok partition var mı? (farklı cihazlarda farklı Partition ID) |
| `router table` | Router'lar, LQ In/Out, yol maliyeti, sonraki atlama | Zayıf (LQ 1) bağlantılar, uzak router'lar |
| `child table` | Çocuklar, timeout, yaş, mod, sürüm, CSL | Çocuk sayısı, kopan çocuklar |
| `neighbor table` | Tüm komşular (router + çocuk) ve RSSI | Sinyal seviyeleri |
| `parent` | Ebeveyn ve link kalitesi (çocuklar için) | Ebeveyn bağlantısı iyi mi? |
| `counters mac` / `counters mle` | MAC ve MLE sayaçları | Yeniden iletim, CCA hatası, attach/rol değişim sayıları |
| `netdata show` | Network Data | Önekler, rotalar, SRP/BBR servisleri |
| `ipaddr`, `ipmaddr` | Adresler ve abonelikler | OMR adresi var mı? |
| `channel`, `panid`, `extpanid`, `networkname` | Ağ parametreleri | Doğru ağda mı? |
| `dataset active` | Active Dataset | Zaman damgası, kanal |
| `ping <adres>` | Erişilebilirlik ve gecikme | Uçtan uca bağlantı |
| `scan`, `discover`, `scan energy` | Çevredeki ağlar ve kanal gürültüsü | Kanal seçimi, yabancı ağlar |
| `channel monitor` | Kanal doluluk örneklemesi | Wi-Fi girişimi |
| `pollperiod`, `childtimeout`, `csl` | Uyuyan cihaz ayarları | Enerji/gecikme dengesi |
| `br state`, `br omrprefix`, `br nat64prefix` | Border Router durumu | BR çalışıyor mu, önek ne? |
| `srp server host`, `srp server service` | SRP kayıtları | Cihazlar servis kaydı yapmış mı? |
| `linkmetrics …` | Link Metrics sorguları | 1.2+ bağlantı ölçümleri |

#### Örnek çıktılar

```text
> router table
| ID | RLOC16 | Next Hop | Path Cost | LQ In | LQ Out | Age | Extended MAC     | Link |
+----+--------+----------+-----------+-------+--------+-----+------------------+------+
|  5 | 0x1400 |       12 |         4 |     0 |      0 |   0 | 1e2c7a0f5a3f2a11 |    0 |
| 12 | 0x3000 |       63 |         0 |     3 |      3 |   4 | 6a77d1c2b0e94f20 |    1 |
| 23 | 0x5c00 |       63 |         0 |     0 |      0 |   0 | 1a2b3c4d5e6f7081 |    0 |
| 37 | 0x9400 |       12 |         3 |     0 |      0 |   0 | 8e1f00ab23cd45ef |    0 |
```

- `Link = 1`: Doğrudan komşu (LQ In/Out değerleri anlamlı). Burada Router 12 ile LQ 3/3 mükemmel bağlantı var.
- `Next Hop`: Komşu olmayan router'lara giden yolun ilk atlaması (63 = doğrudan/yok).
- `Path Cost`: Hedef router'a toplam maliyet.
- `Age`: Komşudan son duyulan mesajdan beri geçen süre (s).

```text
> child table
| ID  | RLOC16 | Timeout    | Age        | LQ In | C_VN |R|D|N|Ver|CSL|QMsgCnt| Extended MAC     |
+-----+--------+------------+------------+-------+------+-+-+-+---+---+-------+------------------+
|   1 | 0x5c01 |        240 |         17 |     3 |  118 |0|0|0|  4| 0 |     0 | 4ecede68435358ac |
|   2 | 0x5c02 |        240 |          3 |     2 |  118 |1|0|1|  4| 0 |     0 | b2f0c1d2e3a4b5c6 |
```

- Çocuk 1: SED (R=0, D=0, N=0), 17 s önce duyuldu, kuyrukta mesajı yok.
- Çocuk 2: MED (R=1, N=1), LQ 2.

```text
> counters mac
TxTotal: 10560
    TxAckRequested: 6380
    TxAcked: 6201
    TxNoAckRequested: 4180
    TxDataPoll: 0
    TxRetry: 912
    TxErrCca: 37
    TxErrAbort: 0
RxTotal: 24311
    RxDuplicated: 214
    RxErrNoFrame: 0
    RxErrSec: 3
    RxErrFcs: 418
```

Yorum: ACK başarı oranı 6201 / 6380 ≈ %97.2; yeniden iletim oranı 912 / 6380 ≈ %14 (biraz yüksek — bazı bağlantılar zayıf olabilir); CCA hatası düşük (kanal çok meşgul değil); FCS hataları ortamdaki girişimin veya zayıf sinyallerin göstergesi olabilir.

### 21.3 İzlenmesi Gereken Göstergeler

| Gösterge | Sağlıklı | Dikkat | Olası anlam |
|---|---|---|---|
| Partition sayısı | 1 | > 1 | Ağ bölünmüş; bölgeler arası bağlantı zayıf |
| Router sayısı | 16–32 arasında, cihaz sayısına uygun | Çok az router ve çok sayıda çocuk | Kapsama zayıf, tek hata noktaları oluşabilir |
| Router komşu LQ'ları | Çoğunlukla 3 | Çok sayıda LQ 1 | Zayıf bağlantılar, yüksek yeniden iletim |
| MAC yeniden iletim oranı | < %5–10 | > %20 | Girişim, zayıf link, gizli düğüm |
| CCA hata oranı | Çok düşük | Yükselen | Kanal meşgul (Wi-Fi), kanal değiştirmeyi düşünün |
| Attach / parent change sayaçları | Nadiren artar | Sürekli artar | Kararsız ebeveyn bağlantıları, ebeveyn kopmaları |
| Leader / router rol değişimleri | Nadiren | Sık | Ağ kararsızlığı, partition birleşmeleri |
| SED poll başarısı | Yüksek | Poll'lara cevap gelmiyor | Ebeveyn kaybı, aşırı yüklü ebeveyn |
| Address Query başarısızlıkları | Nadir | Sık | Cihazlar ağdan düşüyor veya önbellek sorunları |

### 21.4 Paket Yakalama (Sniffing)

Radyo trafiğini görmek, Thread sorunlarını çözmenin en güçlü yoludur.

**Donanım seçenekleri:**

- **nRF52840 Dongle** + Nordic'in 802.15.4 sniffer yazılımı (Wireshark eklentisi ile canlı yakalama),
- **Silicon Labs** geliştirme kitleri + Network Analyzer (Simplicity Studio),
- **TI** CC26xx/CC13xx LaunchPad + paket sniffer yazılımı,
- **Espressif** ESP32-H2/C6 tabanlı sniffer uygulamaları,
- OpenThread RCP + **pyspinel** sniffer aracı (`sniffer.py`) ile Wireshark'a akış.

Sniffer, ağın **kanalına** ayarlanmalıdır (yakalama tek kanalda yapılır).

**Wireshark yapılandırması:**

1. **IEEE 802.15.4 → Decryption Keys**: Anahtar olarak **Network Key**'i girin, anahtar indeksini (Key Sequence 0 için 1) belirtin ve **Key Hash** olarak **"Thread hash"** seçin. Wireshark MAC ve MLE anahtarlarını Network Key'den kendisi türetir.
2. **IEEE 802.15.4 FCS formatı**: Sniffer'ın çıktı biçimine göre (TI meta verili veya ITU-T CRC-16) ayarlayın; yanlışsa tüm çerçeveler "bad FCS" görünür.
3. **6LoWPAN → Context 0**: Mesh-local öneki girin (`fdde:ad00:beef:0::/64`); adreslerin doğru açılması için gereklidir. Diğer bağlamlar için OMR önekini de ekleyebilirsiniz.
4. **CoAP**: UDP 61631'in CoAP olarak çözümlendiğinden emin olun (TMF mesajları için).
5. Key Sequence ilerlediyse (anahtar rotasyonu) Thread protokol ayarlarındaki sıra numarasını güncelleyin veya ilgili indeksleri ekleyin.

**Kullanışlı Wireshark filtreleri:**

| Filtre | Gösterir |
|---|---|
| `wpan` | Tüm 802.15.4 çerçeveleri |
| `wpan.frame_type == 0x3` | MAC komutları (ör. Data Request poll'ları) |
| `mle` | MLE mesajları |
| `mle.cmd == 9` | Parent Request |
| `coap` | TMF ve uygulama CoAP mesajları |
| `udp.port == 61631` | TMF |
| `udp.port == 5540` | Matter |
| `thread_address` | Thread adres TLV'li TMF mesajları (Address Query/Notification/Solicit) |
| `thread_nwd` | Network Data içeren mesajlar |
| `thread_meshcop` | Devreye alma (MeshCoP) mesajları |
| `wpan.src64 == 1a:2b:3c:4d:5e:6f:70:81` | Belirli bir cihazın çerçeveleri |

### 21.5 Matter Üzerinden Thread Teşhisi

Matter, Thread cihazlarının ağ durumunu **Thread Network Diagnostics** kümesi (cluster ID `0x0035`) ile sunar. Önemli öznitelikler:

| Grup | Öznitelikler |
|---|---|
| Ağ | Channel, RoutingRole, NetworkName, PanId, ExtendedPanId, MeshLocalPrefix |
| Partition | PartitionId, Weighting, DataVersion, StableDataVersion, LeaderRouterId |
| Tablolar | NeighborTable (RSSI, LQI, yaş, frame error rate…), RouteTable |
| Rol sayaçları | DetachedRoleCount, ChildRoleCount, RouterRoleCount, LeaderRoleCount, AttachAttemptCount, PartitionIdChangeCount, ParentChangeCount |
| Trafik sayaçları | TxTotalCount, TxRetryCount, TxErrCcaCount, RxTotalCount, RxErrFcsCount … |
| Dataset | ActiveTimestamp, PendingTimestamp, Delay, SecurityPolicy, ChannelPage0Mask |
| Hatalar | ActiveNetworkFaults (ör. bağlantı kaybı) |

Ekosistem uygulamaları ve Home Assistant gibi platformlar bu verileri kullanarak ağ topolojisini ve cihaz bağlantı kalitesini görselleştirir.

### 21.6 Diğer Araçlar

| Araç | Amaç |
|---|---|
| **OTNS** (OpenThread Network Simulator) | Sanal Thread ağlarını görsel olarak simüle etme, senaryo testi |
| **OpenThread POSIX simülasyonu** | Bilgisayarda çok sayıda sanal düğüm (`ot-cli-ftd` simülasyon) |
| **Thread Topology Monitor** (Nordic) | Ağ topolojisinin canlı görselleştirilmesi |
| **Network Analyzer** (Silicon Labs) | Çok kanallı yakalama, enerji profili ile birlikte analiz |
| **OTBR Web arayüzü / REST API** | BR üzerinden ağ durumu, topoloji, dataset |
| **Ekosistem uygulamaları** | Bazı üçüncü taraf uygulamalar Thread topolojisini ve rolleri gösterebilir |

### 21.7 Bölüm Özeti

- Thread'in TMF tabanlı teşhis protokolü (`d/dg`, `d/dq`) ile cihazların iç durumu uzaktan okunabilir; 1.4 ile kapsam genişledi.
- `router table`, `child table`, `leaderdata`, `counters mac` gibi komutlar ağ sağlığının temel göstergeleridir.
- Yeniden iletim oranı, CCA hataları, partition ve parent değişim sayaçları en kritik metriklerdir.
- Wireshark'ta Network Key + "Thread hash", 6LoWPAN bağlam 0 ve doğru FCS formatı ile tüm trafik çözülebilir.
- Matter'ın Thread Network Diagnostics kümesi bu bilgileri uygulama seviyesine taşır.
