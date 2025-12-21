import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from sklearn.linear_model import LinearRegression 
import os

# -----------------------------------------------------------------------------
# 1. PROJE AYARLARI
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Su Kalitesi Analiz Sistemi",
    page_icon="💧",
    layout="wide"
)

st.title("💧 Su Kalitesi Karar Destek Sistemi")
st.markdown("""
**Proje Özeti:** Bu uygulama, su kalitesi verilerini analiz ederek içme ve havuz suyu uygunluğunu denetler.
**Veri Mühendisliği Notu:** Veri setindeki TDS (Solids) değerlerinde tespit edilen birim anomalisi (Scaling Error), 
ön işleme katmanında 1/100 oranında normalize edilerek gerçek dünya standartlarına (WHO) uyarlanmıştır.
""")

# -----------------------------------------------------------------------------
# 2. SABİT VERİLER (HAVUZ STANDARTLARI)
# -----------------------------------------------------------------------------
HAVUZ_REFERANS_DEGERLERI = {
    'ph': {'min': 7.2, 'max': 7.8, 'birim': '', 'oneri': 'pH dengeleyici kullanın.'},
    'Hardness': {'min': 150, 'max': 400, 'birim': 'mg/L', 'oneri': 'Kalsiyum seviyesini ayarlayın.'},
    'Solids': {'min': 0, 'max': 2500, 'birim': 'ppm', 'oneri': 'TDS yüksek, taze su ekleyin.'}, # 2500 ppm gerçekçi bir havuz sınırı
    'Chloramines': {'min': 0.0, 'max': 3.0, 'birim': 'ppm', 'oneri': 'Klor seviyesini ayarlayın.'},
    'Sulfate': {'min': 0, 'max': 360, 'birim': 'mg/L', 'oneri': 'Sülfat yüksek, korozyon riski.'},
    'Conductivity': {'min': 0, 'max': 1000, 'birim': 'μS/cm', 'oneri': 'İletkenlik yüksek.'},
    'Trihalomethanes': {'min': 0, 'max': 80, 'birim': 'μg/L', 'oneri': 'Zararlı yan ürünler var.'},
    'Turbidity': {'min': 0, 'max': 1.0, 'birim': 'NTU', 'oneri': 'Filtrasyon gerekli.'},
    'Organic_carbon': {'min': 0, 'max': 15, 'birim': 'ppm', 'oneri': 'Organik kirlilik var.'}
}

# -----------------------------------------------------------------------------
# 3. VERİ İŞLEME VE DÜZELTME
# -----------------------------------------------------------------------------
@st.cache_data
def veri_yukle_ve_duzelt():
    """
    CSV dosyasını yükler, temizler ve TDS birim hatasını düzeltir.
    """
    if not os.path.exists("water_potability.csv"):
        st.error("Veri seti dosyası (water_potability.csv) bulunamadı!")
        return None
    
    df = pd.read_csv("water_potability.csv")
    df = df.dropna() # Eksik verileri sil
    
    # --- KRİTİK DÜZELTME (DATA PREPROCESSING) ---
    # Veri setindeki Solids (TDS) değerleri ortalama 22.000 ppm (Tuzlu Su).
    # Gerçek dünya içme suyu ortalaması 200-300 ppm.
    # Bu yüzden veriyi 100'e bölerek normalize ediyoruz.
    df['Solids'] = df['Solids'] / 100 
    
    return df

@st.cache_data
def icme_suyu_limitlerini_hesapla(df):
    """
    Düzeltilmiş veri setinden dinamik içme suyu aralıklarını hesaplar.
    """
    icilebilir_df = df[df["Potability"] == 1]
    
    parametreler = list(HAVUZ_REFERANS_DEGERLERI.keys())
    hesaplanan_sinirlar = {}
    
    for kol in parametreler:
        # İdeal aralık için %10 ve %90 dilimlerini alıyoruz
        alt_sinir = icilebilir_df[kol].quantile(0.10)
        ust_sinir = icilebilir_df[kol].quantile(0.90)
        
        hesaplanan_sinirlar[kol] = {
            'min': round(alt_sinir, 2),
            'max': round(ust_sinir, 2),
            'birim': HAVUZ_REFERANS_DEGERLERI[kol]['birim'],
            'oneri': 'İçme suyu referans aralığı dışında.'
        }
    return hesaplanan_sinirlar

def uygunluk_kontrolu(girilen_degerler, standartlar):
    sorunlar = []
    for param, limit in standartlar.items():
        deger = girilen_degerler[param]
        if not (limit["min"] <= deger <= limit["max"]):
            durum = "Yüksek" if deger > limit["max"] else "Düşük"
            sorunlar.append(f"❌ {param}: {deger} ({durum}) -> {limit['oneri']}")
    return sorunlar

# -----------------------------------------------------------------------------
# 4. ANA PROGRAM AKIŞI
# -----------------------------------------------------------------------------

# Veriyi yükle ve düzelt
df = veri_yukle_ve_duzelt()
if df is None:
    st.stop()

# Standartları hesapla (Düzeltilmiş veri üzerinden)
ICME_REFERANS_DEGERLERI = icme_suyu_limitlerini_hesapla(df)

# --- Yan Panel (Sidebar) ---
st.sidebar.header("🧪 Numune Değerleri")

# Slider aralıklarını gerçek dünya değerlerine çektik
ph = st.sidebar.slider("pH Değeri", 0.0, 14.0, 7.4)
chlor = st.sidebar.slider("Kloramin (ppm)", 0.0, 12.0, 0.4)
turb = st.sidebar.slider("Bulanıklık (NTU)", 0.0, 10.0, 0.3)

with st.sidebar.expander("Diğer Parametreler"):
    hard = st.number_input("Sertlik", 0, 500, 200)
    # TDS girdisini artık 0-500 arası bekliyoruz (önceden 20000 idi)
    solid = st.number_input("TDS (Solids - ppm)", 0, 2000, 220) 
    sulf = st.number_input("Sülfat", 0, 600, 300)
    cond = st.number_input("İletkenlik", 0, 1000, 400)
    trih = st.number_input("Trihalometanlar", 0, 150, 60)
    carb = st.number_input("Organik Karbon", 0, 50, 15)

kullanici_girisi = {
    'ph': ph, 'Chloramines': chlor, 'Turbidity': turb, 'Hardness': hard, 
    'Solids': solid, 'Sulfate': sulf, 'Conductivity': cond, 
    'Trihalomethanes': trih, 'Organic_carbon': carb
}

# --- Ana Ekran ---
tab1, tab2 = st.tabs(["📊 Analiz Raporu", "📈 Veri Analitiği"])

with tab1:
    st.subheader("Kalite Analiz Sonucu")
    
    if st.button("Analizi Başlat", type="primary", use_container_width=True):
        
        icme_hatalari = uygunluk_kontrolu(kullanici_girisi, ICME_REFERANS_DEGERLERI)
        havuz_hatalari = uygunluk_kontrolu(kullanici_girisi, HAVUZ_REFERANS_DEGERLERI)
        
        # Karar Mantığı
        if len(icme_hatalari) == 0:
            st.success("✅ **SONUÇ: İÇİLEBİLİR SU**")
            st.write("Numune, WHO standartlarına uygun hale getirilmiş veri seti profiliyle tam uyumlu.")
        
        elif len(havuz_hatalari) == 0:
            st.info("🏊 **SONUÇ: YÜZMEYE UYGUN (HAVUZ SUYU)**")
            st.write("Numune içme kalitesinde değil ancak güvenli havuz suyu standartlarını karşılıyor.")
            with st.expander("Neden İçilemez?"):
                for hata in icme_hatalari: st.write(hata)
        
        else:
            st.error("⛔ **SONUÇ: RİSKLİ / ATIK SU**")
            st.write("Numune hiçbir güvenlik standardını karşılamıyor.")
            col1, col2 = st.columns(2)
            with col1:
                st.warning("İçme Kriteri Hataları:")
                for hata in icme_hatalari: st.write(hata)
            with col2:
                st.warning("Havuz Kriteri Hataları:")
                for hata in havuz_hatalari: st.write(hata)

    # Görselleştirme
    st.divider()
    st.write("### Kritik Göstergeler")
    g1, g2, g3 = st.columns(3)
    
    def gosterge_ciz(deger, baslik, min_v, max_v, ideal_min, ideal_max):
        renk = "#10b981" if (ideal_min <= deger <= ideal_max) else "#ef4444"
        return go.Figure(go.Indicator(
            mode="gauge+number", value=deger, title={'text': baslik},
            gauge={
                'axis': {'range': [min_v, max_v]}, 'bar': {'color': renk},
                'steps': [{'range': [ideal_min, ideal_max], 'color': "rgba(16, 185, 129, 0.2)"}]
            }
        ))

    # Referans olarak Düzeltilmiş İçme Suyu aralıklarını kullan
    ref = ICME_REFERANS_DEGERLERI
    with g1: st.plotly_chart(gosterge_ciz(ph, "pH", 0, 14, ref['ph']['min'], ref['ph']['max']), use_container_width=True)
    with g2: st.plotly_chart(gosterge_ciz(solid, "TDS (ppm)", 0, 1000, ref['Solids']['min'], ref['Solids']['max']), use_container_width=True)
    with g3: st.plotly_chart(gosterge_ciz(turb, "Bulanıklık", 0, 10, ref['Turbidity']['min'], ref['Turbidity']['max']), use_container_width=True)

with tab2:
    st.subheader("Veri İlişki Analizi")
    st.info("Not: Bu grafikler, TDS birim hatası düzeltilmiş veri seti üzerinden oluşturulmuştur.")
    
    secenekler = {
        "İletkenlik vs TDS (Düzeltilmiş)": ("Conductivity", "Solids"),
        "pH vs Kloramin": ("ph", "Chloramines")
    }
    
    secim = st.selectbox("İlişki Seç:", list(secenekler.keys()))
    x_ekseni, y_ekseni = secenekler[secim]
    
    orneklem = df.sample(min(1000, len(df)), random_state=42)
    X_reg = orneklem[[x_ekseni]].values
    y_reg = orneklem[y_ekseni].values
    model = LinearRegression().fit(X_reg, y_reg)
    y_tahmin = model.predict(X_reg)
    
    fig = px.scatter(orneklem, x=x_ekseni, y=y_ekseni, opacity=0.4, title=f"{x_ekseni} ve {y_ekseni}")
    fig.add_traces(go.Scatter(x=orneklem[x_ekseni], y=y_tahmin.flatten(), mode='lines', name='Trend', line=dict(color='red')))
    st.plotly_chart(fig, use_container_width=True)

st.sidebar.divider()
st.sidebar.caption("Yazılım Müh. Projesi | vFinal Corrected")