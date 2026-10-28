# Gold veri gerçekte ne zaman hazır sayılacak? (v0.7)

Bu pakette **756 sentetik cümle**, **100 adet gerçek SGD konuşmasından alınmış ama insan etiketlemesi tamamlanmamış pilot örnek** ve **100 örneğe ait iki AI etiket önerisi** var. Bu sayılar **956 farklı gold örnek** anlamına gelmez: iki AI dosyası ve iki etiketsiz dosya aynı 100 konuşmayı tekrar eder. Gerçek insan onaylı gold örnek sayısı: **0**.

## Nasıl kullanacağız?
Başlangıçta 504 sentetik train örneğiyle yalnızca ön eğitim veya kodun çalıştığına dair teknik deney yapılabilir. 126 sentetik dev, mühendislik kontrolü içindir. 126 sentetik challenge aynı üreticinin farklı şablonlarıdır; gerçek hayatta modelin başarılı olduğunu kanıtlamaz.

Elimizdeki 100 SGD konuşması için önce **gerçekten iki ayrı kişinin** birbirinden bağımsız etiketleri gerekiyor. Etiketleme bitince anlaşmazlıkların gerekçeli çözülmesi, nadir sınıflar için yeni gerçek SGD örnekleri toplanması ve ayrı bir insan doğrulamalı test kümesinin dondurulması zorunlu. İki AI'ya farklı rol vermek bunu karşılamıyor.

## Ne zaman "başarılı" deriz?
Veri kaynağı, lisansı ve hash'leri belli; her sınıf için yeterli gerçek örnek ve sayılar açık; iki bağımsız insanın ham kararları + uzlaşma kaydı korunmuş; veri sızıntısı yok; gerçek test verisi hiç eğitimde kullanılmamış; CRF ve Transformer sonuçları aynı testte raporlanmış; başarısız sınıflar saklanmamışsa çalışma akademik açıdan savunulabilir hale gelir. O noktada bile "kesin yüksek not" veya "kusursuz etiket" sözü verilemez.

**Şu an tek ZIP'i agent'a verebilirsin; D3 insan adımını boş geçmesini isteme.**
