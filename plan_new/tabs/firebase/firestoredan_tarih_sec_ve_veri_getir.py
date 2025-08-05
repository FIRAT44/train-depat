import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
from datetime import date

def firestoredan_tarih_sec_ve_veri_getir():
    st.header("📅 Firestore'dan Tarih Aralığında Kayıt Getir")
    
    # Varsayılan ayarlar
    firebase_key_path = "tabs/firebase/firebase-key.json"
    firestore_collection = "naeron_ucuslar"
    tarih_kolonu_firestore = "Ucus_Tarihi_2"

    # Tarih seçimi
    col1, col2 = st.columns(2)
    with col1:
        baslangic_tarihi = st.date_input("Başlangıç Tarihi", value=date.today().replace(day=1))
    with col2:
        bitis_tarihi = st.date_input("Bitiş Tarihi", value=date.today())
    if baslangic_tarihi > bitis_tarihi:
        st.warning("Başlangıç tarihi, bitiş tarihinden büyük olamaz.")
        return

    get_btn = st.button("Verileri Getir")
    df = pd.DataFrame()
    if get_btn:
        # Firebase başlatıldı mı kontrol et
        if not firebase_admin._apps:
            cred = credentials.Certificate(firebase_key_path)
            firebase_admin.initialize_app(cred)
        db = firestore.client()

        # Firestore sorgusu
        docs = db.collection(firestore_collection) \
            .where(tarih_kolonu_firestore, ">=", baslangic_tarihi.strftime("%Y-%m-%d")) \
            .where(tarih_kolonu_firestore, "<=", bitis_tarihi.strftime("%Y-%m-%d")) \
            .stream()
        kayitlar = []
        for doc in docs:
            veri = doc.to_dict()
            tarih_str = veri.get(tarih_kolonu_firestore)
            try:
                veri[tarih_kolonu_firestore] = pd.to_datetime(tarih_str)
            except Exception:
                veri[tarih_kolonu_firestore] = None
            kayitlar.append(veri)
        if not kayitlar:
            st.warning("Seçilen aralıkta kayıt bulunamadı.")
        else:
            df = pd.DataFrame(kayitlar)
            st.success(f"Toplam {len(df)} kayıt bulundu.")
            st.dataframe(df, use_container_width=True)
            
            # İndirme butonu (Excel)
            xls = pd.ExcelWriter('veri.xlsx')
            df.to_excel(xls, index=False)
            xls.close()
            with open('veri.xlsx', 'rb') as f:
                st.download_button(
                    label="📥 Excel Olarak İndir",
                    data=f,
                    file_name=f"firestore_kayitlari_{baslangic_tarihi}_{bitis_tarihi}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    return df

# Kendi sayfanda şöyle çağırabilirsin:
# firestoredan_tarih_sec_ve_veri_getir()
