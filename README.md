💧 Su Kalitesi Karar Destek Sistemi (SafePool & DrinkGuard)
Bu proje, Yazılım Mühendisliği bitirme projesi kapsamında geliştirilmiş, su numunelerinin kimyasal özelliklerini analiz ederek kullanım amacına uygunluğunu (İçme Suyu veya Havuz Suyu) hiyerarşik olarak denetleyen bir karar destek sistemidir.
Proje, Kaggle Water Potability veri setini temel almakta olup, literatürden alınan havuz suyu standartları ile zenginleştirilmiştir.
🚀 Projenin Amacı
Su kalitesi analizlerinde sadece "İçilebilir/İçilemez" ayrımı yerine, kullanım senaryosuna göre (Örn: İçilemez ama yüzülebilir) esnek bir karar mekanizması oluşturmak ve hatalı veri setlerini tespit edip düzelten bir veri işleme hattı (pipeline) kurmaktır.
🛠️ Teknik Özellikler ve Mühendislik Yaklaşımı
1. Veri Anomalisi Tespiti ve Normalizasyon
Proje geliştirme sürecinde, kullanılan veri setindeki TDS (Solids) değerlerinin ortalamasının 22.000 ppm (Tuzlu Su seviyesi) olduğu tespit edilmiştir. Gerçek dünya içme suyu standartlarına (WHO) aykırı olan bu durumun bir ölçeklendirme hatası (Scaling Error) olduğu analiz edilmiş ve veri ön işleme katmanında 1/100 oranında normalizasyon uygulanarak düzeltilmiştir.
2. Dinamik Referans Aralığı (IQR Yöntemi)
Sabit if-else kuralları yerine, veri setindeki "İçilebilir" etiketli suların istatistiksel dağılımı (Quantile %10 - %90) hesaplanarak, sisteme veri odaklı (data-driven) dinamik sınırlar tanımlanmıştır.
3. Hiyerarşik Karar Algoritması
Sistem numuneyi doğrusal olmayan bir mantıkla değerlendirir:
Aşama: Numune, WHO standartlarına göre içilebilir mi? -> Evet ise "İçilebilir".
Aşama: Hayır ise, Havuz Suyu kimyasal dengesine uygun mu? -> Evet ise "Yüzülebilir".
Sonuç: Hiçbiri değilse -> "Riskli/Atık Su".
📊 Ekran Görüntüleri
Analiz Ekranı
Veri Grafikleri
(Buraya uygulamanın ekran görüntüsünü ekleyebilirsiniz)
(Buraya grafik ekran görüntüsünü ekleyebilirsiniz)

💻 Kurulum ve Çalıştırma
Projeyi yerel makinenizde çalıştırmak için aşağıdaki adımları izleyin:
Repoyu Klonlayın:
git clone [https://github.com/KULLANICI_ADINIZ/Water-Quality-Project.git](https://github.com/KULLANICI_ADINIZ/Water-Quality-Project.git)
cd Water-Quality-Project


Gerekli Kütüphaneleri Yükleyin:
pip install -r requirements.txt


Uygulamayı Başlatın:
streamlit run app.py


📂 Proje Yapısı
├── app.py                  # Ana uygulama ve algoritma kodları
├── water_potability.csv    # Ham veri seti (Kaggle)
├── requirements.txt        # Bağımlılıklar
└── README.md               # Proje dokümantasyonu
