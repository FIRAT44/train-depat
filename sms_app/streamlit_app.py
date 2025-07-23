import streamlit as st
from sms_app.pages.Dashboard import dashboard
from sms_app.pages.Rapor_Yonetimi import rapor_yonetimi
from sms_app.pages.Hazard_Scheme import hazard_yonetimi

# st.set_page_config yalnızca EN ÜSTTE olmalı!
#st.set_page_config(page_title="Ayjet SMS Programı ✈️", layout="wide")

def sms_app():
    # ————— Login ve kullanıcı kontrolü kaldırıldı —————

    st.title("Ayjet Uçuş Okulu SMS Programı ✈️")
    st.sidebar.title("🔍 Menü")
    page = st.sidebar.selectbox("Sayfa Seçin", ["Dashborad", "Rapor Yönetimi", "Hazard Yönetimi", "Voluntary Yönetimi", "SPI Takibi"])

    if page == "Dashborad":
        dashboard()
        #st.write("🏠 Anasayfa içeriği...")
    elif page == "Rapor Yönetimi":
        rapor_yonetimi()
        #st.write("📄 Raporlar içeriği...")
    elif page == "Hazard Yönetimi":
        hazard_yonetimi()
    elif page == "Voluntary Yönetimi":
        from sms_app.pages.Voluntary_Scheme import voluntary_yonetimi
        voluntary_yonetimi()
    
    elif page == "SPI Takibi":
        from sms_app.pages.SPI_Takibi import spi_takibi
        spi_takibi()
    
    if st.sidebar.button("⬅️ Ana Menüye Dön", key="back_main_sinav_menu"):
        st.session_state["uygulama_modu"] = "ana"
        st.rerun()

