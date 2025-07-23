import streamlit as st
from utils.auth import login_required
login_required()
st.set_page_config(page_title="Continuous Improvement Tools", layout="wide")
st.title("📊 Continuous Improvement Tools")

# Tablar oluştur
sekme1, sekme2, sekme3, sekme4, sekme5, gelismis_tab = st.tabs([
    "Giriş & Temel Bilgiler",
    "Emniyet İstihbaratı",
    "Devlet SSP",
    "SMS Uygulaması",
    "Sürekli İyileştirme Araçları",
    "Gelişmiş Entegrasyon"
])

with sekme1:
    st.header("Giriş & Temel Bilgiler")
    st.markdown("""
**Part I – Introduction and background**: Emniyet yönetimi tanımı, temel kavramlar, emniyet kültürü. citeturn0file0
- 1.1 Emniyet yönetimi nedir?
- 1.2 Annex 19 tarihçesi
- 1.3 Uygulanabilirlik kriterleri
- 1.4 Uygulama adımları  
""")

with sekme2:
    st.header("Emniyet İstihbaratı Oluşturma")
    st.markdown("""
**Part II – Developing safety intelligence**: Verilerin korunması, performans yönetimi, veri odaklı karar alma. citeturn0file0
- 2.1 Koruma prensipleri
- 2.2 Emniyet performansı göstergeleri
- 2.3 Emniyet performansı hedefleri
- 2.4 Veri odaklı karar alma süreci
""")

with sekme3:
    st.header("Devlet Emniyet Programı (SSP)")
    st.markdown("""
**Part III-Ch1 – State Safety Program**: Politika, risk yönetimi, güvençe, promosyon bileşenleri. citeturn0file0
- SSP bileşenleri:
  1. Emniyet Politikası ve Kaynaklar
  2. Emniyet Riski Yönetimi
  3. Emniyet Güvencesi
  4. Emniyet Teşviki
- SSP uygulama adımları
""")

with sekme4:
    st.header("Hizmet Sağlayıcı SMS Uygulaması")
    st.markdown("""
**Part III-Ch2 – SMS**: SMS bileşenleri ve uygulama planlaması. citeturn0file0
- SMS bileşenleri:
  1. Emniyet Politikası ve Hedefler
  2. Emniyet Riski Yönetimi
  3. Emniyet Güvencesi
  4. Emniyet Teşviki
- Uygulama için GAP analizi ve takvim
""")

with sekme5:
    st.header("Sürekli İyileştirme Araçları")
    st.markdown("""
**Continuous Improvement Tools**: GAP Analizi, Maturity Assessment, Değişim Yönetimi, Ölçüm ve İzleme. citeturn0file0
- Performans Göstergeleri (SPI)
- Performans Hedefleri (SPT)
- Olgunluk değerlendirmesi
- Değişim yönetimi süreçleri
- Sürekli gelişim döngüsü (PDCA)
""")

with gelismis_tab:
    st.header("Gelişmiş Entegrasyon & IRM")
    st.markdown("""
**Integrated Risk Management**: Sistemik bakış, arayüz yönetimi, IRM yaklaşımları. citeturn0file0
- IRM kavramı ve önem
- Arayüz güvenliği değerlendirme
- Kanıtlanmış örnek uygulamalar
""")