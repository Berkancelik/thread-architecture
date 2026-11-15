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

## HTML sürümünü görüntüleme

Depoyu indirip `Thread-Mimarisi.html` dosyasını tarayıcıda açmanız yeterlidir. Diyagramlar (Mermaid) ve yazı tipleri CDN'den yüklendiği için ilk açılışta internet bağlantısı gerekir; bağlantı yoksa diyagramların kaynak metni gösterilir.

GitHub Pages etkinleştirilirse doküman doğrudan web sayfası olarak da yayınlanabilir (Settings → Pages → Branch: `main`).

## Yeniden derleme

```bash
pip install markdown
python tools/build.py
```

Windows'ta `python` yerine `py` kullanılabilir. Betik `bolumler/*.md` dosyalarını ad sırasıyla birleştirir, GitHub uyumlu içindekiler tablosunu oluşturur ve HTML'i üretir.
