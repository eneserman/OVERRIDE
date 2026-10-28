# İnsan etiketçiler için kısa başlangıç (OVERRIDE v0.7)

Bu çalışma bir konuşmada kullanıcının önceki talimatını düzelttiği, değiştirdiği, iptal ettiği veya eski değere döndüğü ifadeleri işaretleme çalışmasıdır. Metinler İngilizcedir. **Önceki konuşmaya bakın, sonraki mesajı görmeyin.** Lütfen bir başka etiketçiyle konuşmadan bağımsız karar verin.

- **NEW_VALUE**: Güncel mesajda belirtilen yeni/eklenen tercih (örn. "Paris").
- **OLD_VALUE**: Güncel mesajda açıkça geçen değiştirilen eski değer (örn. "Berlin instead of Paris" içindeki eski değer, geçmişe göre yönü kontrol ederek).
- **KEPT_VALUE**: Güncel mesajda açıkça tekrar edilen korunacak değer (örn. "keep Friday" içindeki Friday).
- **REFERENCE**: "my first choice" gibi önceki bir değere gönderme yapan ifade.
- **UPDATE_CUE**: "instead", "change", "make it" gibi düzeltme ifadesi.
- **CANCEL_CUE**: Asıl niyeti iptal eden ifade; ancak "don't cancel" gibi *olumsuzlanmış* iptal sözünü ayrı `NEGATED` olarak kaydetmek gerekir. Bir teklife "No" demek her zaman önceden verilmiş talimatı iptal etmek değildir.
- **KEEP_CUE**: "keep", "leave unchanged" gibi koruma ifadesi.
- **RESTORE_CUE**: "go back to", "restore" gibi eski tercihi yeniden isteme ifadesi.

**Aynı katmanda iki span üst üste gelmemeli.** 0'dan başlayan karakter ofsetleri kullanın; bitiş ofseti karakterin kendisini kapsamaz. Emin olmadığınız durumda not yazın. Hiçbir etiket yoksa bunu açıkça değerlendirilmiş negatif örnek olarak kaydedin.

## Zor ayrımlar
- "Go back to booking tickets" geçmiş *konuya* dönüş olabilir; eski *bir değeri* restore etmek zorunda değildir.
- "Also show vegetarian options" önceki tercihi değiştirmek değil **ADD** olabilir.
- "No thanks" sistemin teklifini reddedebilir ama aktif rezervasyonu iptal ettiğini kanıtlamaz.
- "the one we discussed" geçmişte birden fazla seçenek varsa **UNRESOLVED** olabilir.
- "six pm" ile "6 in the evening" aynı zaman olabilir; otomatik UPDATE yapmayın.
- Eski değer yalnızca geçmiş mesajda bulunuyorsa güncel mesaj üzerinde sahte `OLD_VALUE` span oluşturmayın.

Verilen `reviewer_A_BLIND.jsonl` veya `reviewer_B_BLIND.jsonl` dosyasında 100+ kayıt varsa hepsine bakın. AI taslaklarına ve gizli örnekleme manifestine ilk turda bakmayın. Özgün iki dosyayı saklayın; anlaşmazlıkların açıklamalı çözümü daha sonra yapılacak. Bu insan değerlendirmesini bir AI botuna yaptırıp **insan incelemesi** diye sunmayın.
