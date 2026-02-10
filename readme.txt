1. Sistem Mimarisi
Sistemini bir "NLU (Doğal Dil Anlama) Boru Hattı" üzerine kuracağız.

Arayüz (Frontend): React veya Next.js (Manuel girişler ve chat ekranı burada olur).

API Katmanı (Backend): Python FastAPI. (Hafif ve asenkrondur, AI modelleriyle çok hızlı çalışır).

Zeka (NLU): Hugging Face üzerinden çalışan hafifletilmiş Türkçe modeller.

Veritabanı: SQLite. (Dosya tabanlıdır, kurulum gerektirmez ama tam SQL desteği sunar. VM üzerinde yönetmesi çok kolaydır).


2. Hafif Ama Güçlü: Model Seçimi
7/24 çalışacak bir sistemde RAM kullanımını düşük tutmak için "Distilled" (damıtılmış) modelleri tercih etmeliyiz.

Öneri: dbmdz/distilbert-base-turkish-cased

Neden: Standart BERT modellerinden yaklaşık %40 daha küçüktür ve %60 daha hızlıdır, ancak performansı ona çok yakındır. 4GB RAM'li bir VM'de çok rahat çalışır.


3. Türkçe Kelime ve Cümleleri Anlamak İçin Strateji
Türkçe, eklemeli bir dil olduğu için "kalem", "kalemler", "kalemi" kelimelerinin aynı şeyi ifade ettiğini sisteme öğretmen gerekir. Bunun için şu 3 adımı uygulamalıyız:

A. Niyet Algılama (Intent Detection)
Kullanıcının ne yapmak istediğini anlamalıyız.

Örnek: "X ürününü ekle" -> Intent: add_item

Örnek: "X nerede?" -> Intent: query_location

B. Varlık İsmi Tanıma (NER - Named Entity Recognition)
Cümle içindeki "özne"yi ve "yer"i cımbızla çekmeliyiz.

Model: akdeniz27/bert-base-turkish-cased-ner

Girdi: "Mavi dosyayı üst rafa koy."

Çıktı: { "ürün": "Mavi dosya", "konum": "üst raf" }

C. Normalizasyon ve Zemberek
Türkçe karakterleri ve ekleri yönetmek için Zemberek (veya Python için zeyrek) kullanabilirsin. Kullanıcı "kalemler nerede" dediğinde, sistem "kalemler" kelimesini "kalem" köküne indirger ve SQL'de arama yaparken hata payını düşürür.




Dil ModeliDistilBERT (Turkish)Cümleyi anlar ve vektöre çevirir.VeritabanıSQLiteEnvanter bilgilerini (ad, miktar, konum) saklar.BackendFastAPIAI modeli ile Veritabanı arasındaki köprü.Kütüphanelertransformers, torch, spacyNLP işlemleri için temel araçlar.





CREATE TABLE inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name TEXT NOT NULL,
    location TEXT NOT NULL,
    quantity INTEGER DEFAULT 1,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
);
