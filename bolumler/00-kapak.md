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

<!-- ICINDEKILER -->
