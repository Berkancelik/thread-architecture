# Thread Ağ Mimarisi ve Haberleşme Yapısı

IoT ve akıllı ev dünyasında kullanılan **Thread** (IEEE 802.15.4 + 6LoWPAN + IPv6 tabanlı, düşük güçlü mesh ağ protokolü) hakkında kapsamlı, Türkçe teknik rehber.

Fiziksel katmandan (radyo, kanallar, modülasyon) başlayıp MAC, 6LoWPAN, IPv6 adresleme, MLE, yönlendirme, Leader/partition yönetimi, Network Data, TMF/CoAP, çoklu yayın, güvenlik, devreye alma (commissioning), Operational Dataset, uyuyan cihazlar ve CSL, Border Router, Thread 1.2–1.4 özellikleri, teşhis, uçtan uca senaryolar, Matter, OpenThread, donanım, ağ tasarımı ve sorun gidermeye kadar her konuyu bit/bayt seviyesinde ele alır.

## Dosyalar

| Dosya | Açıklama |
|---|---|
| [`Thread-Mimarisi.md`](Thread-Mimarisi.md) | Tek parça Markdown doküman (GitHub'da doğrudan okunabilir, Mermaid diyagramları otomatik çizilir) |
| [`Thread-Mimarisi.html`](Thread-Mimarisi.html) | Aynı içeriğin kenar menülü, aramalı, açık/koyu temalı HTML sürümü |
| [`bolumler/`](bolumler/) | Dokümanın kaynak bölümleri (düzenlemeler burada yapılır) |
| [`tools/build.py`](tools/build.py) | Bölümleri birleştirip MD ve HTML çıktılarını üreten betik |

## İçerik

| # | Bölüm | # | Bölüm |
|---|---|---|---|
| 0 | Bu doküman hakkında | 15 | Güvenlik mimarisi |
| 1 | Thread'e giriş, tarihçe, sürümler | 16 | Devreye alma (MeshCoP, Matter, TCAT, ePSKc) |
| 2 | Protokol yığını ve genel mimari | 17 | Operational Dataset |
| 3 | Fiziksel katman (IEEE 802.15.4 PHY) | 18 | Uyuyan cihazlar, enerji ve CSL |
| 4 | MAC katmanı | 19 | Border Router (OMR, RIO, NAT64, SRP, OTBR) |
| 5 | 6LoWPAN uyarlama katmanı | 20 | Thread 1.2 / 1.3 / 1.4 gelişmiş özellikleri |
| 6 | Thread'de IPv6 adresleme | 21 | Ağ teşhisi, izleme ve paket analizi |
| 7 | Cihaz türleri ve roller | 22 | Uçtan uca haberleşme senaryoları |
| 8 | Ağ topolojisi ve ölçek | 23 | Matter ve Thread |
| 9 | MLE (Mesh Link Establishment) | 24 | OpenThread ve yazılım mimarisi |
| 10 | Yönlendirme (routing) | 25 | Donanım, çipler ve RF tasarımı |
| 11 | Leader, partition ve Router ID yönetimi | 26 | Ağ tasarımı ve en iyi uygulamalar |
| 12 | Network Data | 27 | Sorun giderme rehberi |
| 13 | TMF ve CoAP | 28 | Diğer IoT protokolleriyle karşılaştırma |
| 14 | Çoklu yayın (multicast) ve MPL | 29 | Ekler: sabitler, portlar, RFC'ler, sözlük, kaynaklar |

Dokümanda 34 Mermaid diyagramı, 170'ten fazla tablo ve bayt seviyesinde çözümlenmiş çerçeve/TLV örnekleri bulunur. Anahtar türetme (HMAC-SHA256) ve PSKc (PBKDF2-AES-CMAC) örnekleri hesaplanarak doğrulanmıştır.

## HTML sürümünü görüntüleme

**Çevrimiçi:** https://berkancelik.github.io/thread-architecture/ (GitHub Pages, `main` dalından yayınlanır; her push sonrası birkaç dakika içinde güncellenir).

**Yerel:** Depoyu indirip `Thread-Mimarisi.html` dosyasını tarayıcıda açmanız yeterlidir. Diyagramlar (Mermaid) ve yazı tipleri CDN'den yüklendiği için ilk açılışta internet bağlantısı gerekir; bağlantı yoksa diyagramların kaynak metni gösterilir.

## Yeniden derleme

```bash
pip install markdown
python tools/build.py
```

Windows'ta `python` yerine `py` kullanılabilir. Betik `bolumler/*.md` dosyalarını ad sırasıyla birleştirir, GitHub uyumlu içindekiler tablosunu oluşturur ve HTML'i üretir.
