import streamlit as st
from plan_new.tabs.firebase.firestoredan_tarih_sec_ve_veri_getir import firestoredan_tarih_sec_ve_veri_getir

def main():
    st.set_page_config(page_title="Firestore Tarih Aralığı Çekme", layout="centered")
    st.title("🗂️ Firestore'dan Tarih Aralığıyla Veri Çekme Demo")
    st.info(
        """
        - Tarih aralığını seç,  
        - "Verileri Getir" butonuna bas,  
        - Sonuçları tablo halinde ve istersen Excel olarak indir!
        """
    )
    df = firestoredan_tarih_sec_ve_veri_getir()
    if not df.empty:
        st.success(f"Çekilen veri {len(df)} satır içeriyor.")

