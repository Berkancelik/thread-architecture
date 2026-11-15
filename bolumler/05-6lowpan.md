## 5. 6LoWPAN Uyarlama Katmanı

### 5.1 Neden 6LoWPAN?

IPv6 ile 802.15.4 arasında ciddi bir boyut uyumsuzluğu vardır:

| Ölçü | Değer |
|---|---|
| IPv6 asgari MTU (her bağlantının taşıması gereken) | **1280 bayt** |
| 802.15.4 en büyük çerçeve | **127 bayt** |
| MAC ek yükü (güvenli, kısa adres) | ≈ 21 bayt |
| IPv6 başlığı | 40 bayt |
| UDP başlığı | 8 bayt |

Sıkıştırma olmadan 127 baytın 69'u başlıklara giderdi. **6LoWPAN** (IPv6 over Low-Power Wireless Personal Area Networks) bu sorunu üç araçla çözer:

1. **Başlık sıkıştırma** (IPHC/NHC — RFC 6282): 48 baytlık IPv6+UDP başlığını çoğu durumda 6–10 bayta indirir.
2. **Parçalama** (Fragmentation — RFC 4944): 1280 bayta kadar IPv6 paketlerini birden çok 802.15.4 çerçevesine böler.
3. **Mesh başlığı** (Mesh Header — RFC 4944): Paketin asıl kaynağını ve nihai hedefini taşıyarak çok atlamalı iletimi IPv6 katmanına çıkmadan yapmayı sağlar.

### 5.2 Dispatch (Gönderim Türü) Baytları

6LoWPAN yükünün ilk baytı(ları), hangi başlığın geldiğini belirtir:

| Bit deseni | Anlamı | Thread'de |
|---|---|---|
| `00xxxxxx` | NALP — 6LoWPAN çerçevesi değil | — |
| `01000001` (`0x41`) | Sıkıştırılmamış IPv6 başlığı | Nadiren |
| `011xxxxx` | **IPHC** — sıkıştırılmış IPv6 başlığı (RFC 6282) | Evet (her pakette) |
| `10xxxxxx` | **Mesh Header** | Evet (çok atlamalı iletimde) |
| `11000xxx` | **FRAG1** — ilk parça | Evet |
| `11100xxx` | **FRAGN** — sonraki parçalar | Evet |
| `01010000` | LOWPAN_BC0 (yayın başlığı) | Hayır (Thread MPL kullanır) |

Başlıkların sırası sabittir:

```text
[ Mesh Header ] [ Fragment Header ] [ IPHC (+ inline alanlar) ] [ NHC (UDP) ] [ yük ]
```

### 5.3 IPHC: IPv6 Başlık Sıkıştırma

IPHC'nin temel fikri: **alt katmanlardan veya paylaşılan bağlamdan (context) çıkarılabilen hiçbir bilgiyi gönderme.**

#### IPHC kodlaması (2 bayt temel)

```text
  Bayt 0                          Bayt 1
  0   1   1 | TF  | NH | HLIM     CID | SAC | SAM | M | DAC | DAM
 bit7     5 | 4 3 |  2 | 1 0      7   |  6  | 5 4 | 3 |  2  | 1 0
```

| Alan | Bit | Değerler |
|---|---|---|
| **TF** (Traffic Class + Flow Label) | 2 | `00` ECN+DSCP+FL inline (4 bayt) · `01` ECN+FL (3 bayt) · `10` ECN+DSCP (1 bayt) · `11` tamamen atlanmış (0 bayt) |
| **NH** (Next Header) | 1 | `0` Next Header inline (1 bayt) · `1` NHC ile sıkıştırılmış |
| **HLIM** (Hop Limit) | 2 | `00` inline · `01` = 1 · `10` = 64 · `11` = 255 |
| **CID** | 1 | `1` = ek bağlam kimliği baytı var (kaynak ve hedef için 4'er bit) |
| **SAC** | 1 | `0` durumsuz (stateless) · `1` bağlam tabanlı (stateful) kaynak |
| **SAM** | 2 | Kaynak adres modu (aşağıda) |
| **M** | 1 | `1` hedef çoklu yayın (multicast) |
| **DAC** | 1 | Hedef için durumsuz/bağlam tabanlı |
| **DAM** | 2 | Hedef adres modu |

#### Tekil (unicast) adres sıkıştırma modları

| SAC/DAC | SAM/DAM | Satır içi (inline) | Adres nasıl elde edilir? |
|---|---|---|---|
| 0 | `00` | 16 bayt | Tam adres |
| 0 | `01` | 8 bayt | `fe80::` + 64 bit IID |
| 0 | `10` | 2 bayt | `fe80::ff:fe00:XXXX` |
| 0 | `11` | 0 bayt | `fe80::` + IID MAC adresinden türetilir |
| 1 | `00` | 0 bayt | Belirtilmemiş adres `::` (yalnızca kaynak için) |
| 1 | `01` | 8 bayt | Bağlam öneki + 64 bit IID |
| 1 | `10` | 2 bayt | Bağlam öneki + `0000:00ff:fe00:XXXX` |
| 1 | `11` | 0 bayt | Bağlam öneki + IID MAC (veya Mesh Header) adresinden türetilir |

**IID'nin MAC adresinden türetilmesi:**

```text
Genişletilmiş MAC adresi : 1A:2B:3C:4D:5E:6F:70:81
IID                      : 182B:3C4D:5E6F:7081      (ilk bayttaki U/L biti, 0x02, ters çevrilir)

Kısa MAC adresi (RLOC16) : 0x5C01
IID                      : 0000:00FF:FE00:5C01
```

Mesh Header varsa, "MAC adresinden türetme" kuralında MAC çerçevesinin adresleri yerine Mesh Header'daki **asıl kaynak (originator)** ve **nihai hedef (final destination)** adresleri kullanılır. Bu sayede çok atlamalı paketlerde de RLOC adresleri 0 bayta sıkışır.

#### Çoklu yayın (multicast) hedef sıkıştırma (M = 1)

| DAC | DAM | Inline | Biçim |
|---|---|---|---|
| 0 | `00` | 16 bayt | Tam adres |
| 0 | `01` | 6 bayt | `ffXX::00XX:XXXX:XXXX` |
| 0 | `10` | 4 bayt | `ffXX::00XX:XXXX` |
| 0 | `11` | 1 bayt | `ff02::00XX` (ör. `ff02::1`, `ff02::2`) |
| 1 | `00` | 6 bayt | Önek tabanlı çoklu yayın (RFC 3306): `ffXX:XXLL:<bağlam öneki>:XXXX:XXXX` |

Örnek: Thread'in **Realm-Local All Thread Nodes** adresi `ff33:40:<mesh-local önek>::1`, bağlam 0 kullanılarak 6 bayta sıkıştırılabilir.

### 5.4 Bağlamlar (Contexts)

Bağlam tabanlı sıkıştırma, ağdaki tüm düğümlerin paylaştığı **önek tablosuna** dayanır:

| Bağlam ID | İçerik | Kaynağı |
|---|---|---|
| **0** | **Mesh-Local Prefix** (her zaman) | Operational Dataset |
| 1–15 | Diğer önekler (ör. OMR öneki, Domain öneki) | Network Data'daki **6LoWPAN Context** alt-TLV'leri (Bölüm 12) |

- Bağlam kimliklerini **Leader** atar ve Network Data ile dağıtır.
- Context alt-TLV'sindeki **C (Compress)** bayrağı, o bağlamın sıkıştırma için kullanılıp kullanılamayacağını belirtir. Bir önek kaldırılırken bağlam önce C=0 yapılır, kimlik bir süre (Thread'de 48 saat) yeniden kullanılmaz; böylece eski bağlamla sıkıştırılmış paketler yanlış açılmaz.
- CID = 0 olduğunda ek bayt gönderilmez ve varsayılan bağlam 0 (mesh-local) kullanılır.

### 5.5 NHC: UDP Başlık Sıkıştırma

UDP başlığı (8 bayt) da sıkıştırılır:

```text
  1 1 1 1 0 | C | P P
```

| Alan | Değer | Anlamı |
|---|---|---|
| **C** | 0 | Sağlama toplamı (checksum) inline (2 bayt) — **Thread'de checksum atlanmaz** |
| **P** | `00` | Her iki port inline (4 bayt) |
| | `01` | Kaynak inline (2), hedef `0xF0XX` → 1 bayt |
| | `10` | Kaynak `0xF0XX` → 1 bayt, hedef inline (2) |
| | `11` | Her iki port `0xF0BX` → 4'er bit (toplam 1 bayt) |

Uzunluk alanı her zaman atlanır (alt katmandan hesaplanır).

> [!TIP]
> TMF'nin portu **61631 = `0xF0BF`** özellikle bu yüzden seçilmiştir: `0xF0B0–0xF0BF` aralığında olduğu için iki uçta da TMF portu kullanıldığında portlar tek bayta sığar. MLE portu 19788 (`0x4D4C`, ASCII "ML") ise sıkıştırılamaz ve inline taşınır. Matter'ın 5540 portu da inline taşınır.

### 5.6 Sıkıştırma Örneği: Router'lar Arası TMF Mesajı

RLOC adresinden RLOC adresine, TMF portundan TMF portuna giden bir CoAP mesajı düşünelim (iki router komşu olsun):

```text
Sıkıştırılmamış:
  IPv6 başlığı 40 bayt  (kaynak fdde:ad00:beef:0:0:ff:fe00:5c00,
                          hedef  fdde:ad00:beef:0:0:ff:fe00:9400,
                          hop limit 64, next header UDP)
  UDP  başlığı  8 bayt  (61631 → 61631)
  Toplam       48 bayt

Sıkıştırılmış:
  7E          IPHC bayt 0: 011 | TF=11 | NH=1 | HLIM=10 (64)
  77          IPHC bayt 1: CID=0 | SAC=1 SAM=11 | M=0 | DAC=1 DAM=11
  F3          NHC UDP: 11110 | C=0 | P=11
  FF          Kaynak port 0xF0B[F], hedef port 0xF0B[F]
  xx xx       UDP checksum
  Toplam       6 bayt   (%87.5 tasarruf)
```

Burada kaynak/hedef adresler, bağlam 0'ın (mesh-local önek) ve MAC çerçevesindeki kısa adreslerin (RLOC16) birleşiminden tamamen türetilir.

### 5.7 Mesh Header

Bir paket kaynaktan hedefe **birden fazla radyo atlaması** ile gidecekse, 6LoWPAN Mesh Header eklenir. MAC başlığı yalnızca *o anki atlamanın* adreslerini (gönderen → sonraki atlama) taşırken, Mesh Header *uçtan uca* adresleri taşır:

```text
  1 0 | V | F | Hops Left (4 bit) | Originator Addr | Final Destination Addr
 bit7 6   5   4                 0 |   2 veya 8 bayt |   2 veya 8 bayt

  V = 1 → originator kısa (16 bit)    F = 1 → final kısa (16 bit)
```

Thread'de Mesh Header her zaman **RLOC16** (kısa) adresler kullanır → toplam **5 bayt**:

```text
B? 5C 01 94 02
│  │     └──── Final Destination = 0x9402  (Router 37'nin 2 numaralı çocuğu)
│  └────────── Originator        = 0x5C01  (Router 23'ün 1 numaralı çocuğu)
└───────────── 10 1 1 xxxx → V=1, F=1, Hops Left = xxxx
```

- **Hops Left**: Paketi başlatan router tarafından uygun bir değerle başlatılır, her atlamada 1 azaltılır; 0'a ulaşan paket atılır (döngü koruması). 4 bit yetmezse `0xF` değeri ve ek bir "deep hops left" baytı kullanılabilir.
- **Ara router'lar paketi IPv6 seviyesinde açmaz/birleştirmez**: Mesh Header'daki nihai hedefe göre sonraki atlamayı seçer ve çerçeveyi (parça olsa bile) iletir. Bu, bellek ve gecikme açısından büyük kazançtır.
- Komşuya giden (tek atlamalı) paketlerde Mesh Header eklenmez.

### 5.8 Parçalama (Fragmentation)

127 bayta sığmayan IPv6 paketleri parçalanır:

```text
FRAG1 (ilk parça) — 4 bayt:
  1 1 0 0 0 | datagram_size (11 bit) | datagram_tag (16 bit)

FRAGN (sonraki parçalar) — 5 bayt:
  1 1 1 0 0 | datagram_size (11 bit) | datagram_tag (16 bit) | datagram_offset (8 bit, 8 bayt birim)
```

| Alan | Açıklama |
|---|---|
| **datagram_size** | Sıkıştırılmamış IPv6 paketinin toplam boyutu (en fazla 2047) |
| **datagram_tag** | Aynı paketin parçalarını eşleştiren etiket (kaynak başına artan) |
| **datagram_offset** | Bu parçanın, sıkıştırılmamış paketteki konumu (8 baytlık birimlerle) |

Kurallar:

- İlk parça sıkıştırılmış IPHC başlığını içerir; sonrakiler yalnızca ham yük taşır.
- Son parça hariç parçaların taşıdığı (sıkıştırılmamış karşılık) veri 8'in katı olmalıdır.
- Alıcı tüm parçaları **yeniden birleştirme (reassembly)** tamponunda toplar; bir zaman aşımı içinde tamamlanmazsa (OpenThread varsayılanı birkaç saniye) paket atılır.
- **Tek bir parçanın kaybı bütün paketin kaybı demektir.** Parça sayısı arttıkça paket kaybı olasılığı katlanarak artar.

> [!WARNING]
> Uygulama tasarımında yükleri mümkün olduğunca **tek çerçeveye sığacak** şekilde küçük tutun (yaklaşık 60–80 bayt uygulama verisi). Matter'ın sertifika içeren CASE el sıkışması gibi büyük mesajlar kaçınılmaz olarak 10+ parçaya bölünür; bu mesajlar zayıf bağlantılarda en çok sorun yaşayan trafiktir.

### 5.9 Tam Bir Çerçevenin Anatomisi

Çok atlamalı, parçalanmamış, OMR adresinden OMR adresine giden bir Matter mesajı:

| Katman | Alan | Bayt |
|---|---|---|
| PHY | Preamble + SFD + PHR | 6 (PSDU'ya dahil değil) |
| MAC | Frame Control + Seq + PAN ID + Dest(kısa) + Src(kısa) | 9 |
| MAC | Aux Security Header (Key ID Mode 1) | 6 |
| 6LoWPAN | Mesh Header | 5 |
| 6LoWPAN | IPHC (2) + CID baytı (1) + kaynak IID (8) + hedef IID (8) | 19 |
| 6LoWPAN | NHC UDP (1) + portlar inline (4) + checksum (2) | 7 |
| Uygulama | Matter mesaj başlığı + şifreli yük + Matter MIC (16) | ≈ 30 + yük |
| MAC | MIC | 4 |
| MAC | FCS | 2 |
| **Toplam ek yük (yük hariç)** | | **≈ 82 bayt** → uygulama yükü için ≈ 45 bayt kalır |

OMR adreslerinin IID'leri MAC/Mesh adreslerinden türetilemediği için inline taşınır. Bu yüzden mesh-local RLOC trafiğine göre daha fazla yer kaplar.

### 5.10 Thread'de Yönlendirme Hangi Katmanda?

6LoWPAN literatüründe iki yaklaşım vardır:

- **Mesh-under**: Yönlendirme tamamen bağlantı katmanında yapılır; tüm mesh tek bir IP bağlantısı (link) gibi görünür.
- **Route-over**: Her atlama bir IP yönlendirmesidir; her radyo atlaması ayrı bir IP bağlantısıdır.

Thread ikisinin karışımıdır:

- IP semantiği açısından **link-local kapsam tek radyo atlamasıdır** (route-over benzeri). Mesh genelini kapsayan ayrı bir kapsam, **realm-local** (scope 3), tanımlanmıştır.
- Yönlendirme kararı Thread ağ katmanında RLOC16'ya göre verilir; ancak paketin atlamalar boyunca taşınması 6LoWPAN **Mesh Header** ile, IPv6 paketini her atlamada yeniden oluşturmadan yapılır (mesh-under benzeri verimlilik).

### 5.11 Bölüm Özeti

- 6LoWPAN, IPv6'yı 127 baytlık çerçevelere sıkıştırma, parçalama ve mesh başlığı ile uyarlar.
- IPHC, adresleri bağlam (context 0 = mesh-local önek) ve MAC adreslerinden türeterek 40 baytlık IPv6 başlığını 2 bayta kadar indirebilir.
- TMF portu 61631 bilerek `0xF0BX` aralığından seçilmiştir; UDP portları 4 bite sığar.
- Mesh Header (5 bayt) uçtan uca RLOC16'ları taşır; ara router'lar parçaları birleştirmeden iletir.
- Parça kaybı tüm paketi kaybettirir; uygulama yükleri küçük tutulmalıdır.
