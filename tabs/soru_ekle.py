import streamlit as st
import os
from utils.db import db_baglanti, konu_listele, soru_sil

IMAGE_DIR = "images"

def soru_ekle():
    st.subheader("📝 Yeni Soru Ekle")
    konu_liste = konu_listele()
    konu = st.selectbox("Konu", konu_liste)
    zorluk = st.selectbox("Zorluk", ["Kolay", "Orta", "Zor"])
    soru_metni = st.text_area("Soru Metni")
    sec_a = st.text_input("A Şıkkı")
    sec_b = st.text_input("B Şıkkı")
    sec_c = st.text_input("C Şıkkı")
    sec_d = st.text_input("D Şıkkı")
    dogru = st.selectbox("Doğru Cevap", ["A", "B", "C", "D"])
    resim = st.file_uploader("📷 Soruya ait görsel (isteğe bağlı)", type=["jpg", "png", "jpeg"])
    if st.button("➕ Soruyu Ekle"):
        resim_yolu = ""
        if resim:
            os.makedirs(IMAGE_DIR, exist_ok=True)
            resim_yolu = os.path.join(IMAGE_DIR, resim.name)
            with open(resim_yolu, "wb") as f:
                f.write(resim.getbuffer())
        conn = db_baglanti()
        conn.execute("""
            INSERT INTO questions (konu, zorluk, soru_metni, secenek_a, secenek_b, secenek_c, secenek_d, dogru_cevap, resim_yolu)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (konu, zorluk, soru_metni, sec_a, sec_b, sec_c, sec_d, dogru, resim_yolu))
        conn.commit()
        conn.close()
        st.success("✅ Soru başarıyla eklendi!")

