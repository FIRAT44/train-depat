import streamlit as st
import os
from utils.db import db_baglanti, konu_listele

IMAGE_DIR = "images"

def soru_duzenle():
    st.subheader("📝 Eklenen Soruları Düzenle")
    conn = db_baglanti()
    sorular = conn.execute(
        "SELECT id, konu, zorluk, soru_metni, secenek_a, secenek_b, secenek_c, secenek_d, dogru_cevap, resim_yolu FROM questions ORDER BY id DESC"
    ).fetchall()
    conn.close()

    if not sorular:
        st.info("Sistemde hiç soru yok.")
        return

    for sid, konu, zorluk, metin, a, b, c, d, dogru, resim in sorular:
        with st.expander(f"{konu} | {metin[:50]}{'...' if len(metin)>50 else ''}", expanded=False):
            yeni_konu = st.selectbox("Konu", konu_listele(), index=konu_listele().index(konu), key=f"konu_{sid}")
            yeni_zorluk = st.selectbox("Zorluk", ["Kolay", "Orta", "Zor"], index=["Kolay", "Orta", "Zor"].index(zorluk), key=f"zorluk_{sid}")
            yeni_metin = st.text_area("Soru Metni", value=metin, key=f"metin_{sid}")
            yeni_a = st.text_input("A Şıkkı", value=a, key=f"a_{sid}")
            yeni_b = st.text_input("B Şıkkı", value=b, key=f"b_{sid}")
            yeni_c = st.text_input("C Şıkkı", value=c, key=f"c_{sid}")
            yeni_d = st.text_input("D Şıkkı", value=d, key=f"d_{sid}")
            yeni_dogru = st.selectbox("Doğru Cevap", ["A", "B", "C", "D"], index=["A","B","C","D"].index(dogru), key=f"dogru_{sid}")

            if resim:
                try:
                    st.image(resim, width=200)
                except Exception:
                    st.warning(f"Görsel yüklenemedi: {resim}")

            yeni_resim = st.file_uploader("Görsel Güncelle (isteğe bağlı)", type=["jpg", "png", "jpeg"], key=f"resim_{sid}")
            yeni_resim_yolu = resim
            if yeni_resim:
                os.makedirs(IMAGE_DIR, exist_ok=True)
                yeni_resim_yolu = os.path.join(IMAGE_DIR, yeni_resim.name)
                with open(yeni_resim_yolu, "wb") as f:
                    f.write(yeni_resim.getbuffer())

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Kaydet", key=f"guncelle_{sid}"):
                    conn = db_baglanti()
                    conn.execute("""
                        UPDATE questions
                        SET konu=?, zorluk=?, soru_metni=?, secenek_a=?, secenek_b=?, secenek_c=?, secenek_d=?, dogru_cevap=?, resim_yolu=?
                        WHERE id=?
                    """, (yeni_konu, yeni_zorluk, yeni_metin, yeni_a, yeni_b, yeni_c, yeni_d, yeni_dogru, yeni_resim_yolu, sid))
                    conn.commit()
                    conn.close()
                    st.success("Soru güncellendi!")
                    st.experimental_rerun()
            with col2:
                if st.button("Sil", key=f"sil_{sid}"):
                    conn = db_baglanti()
                    conn.execute("DELETE FROM questions WHERE id=?", (sid,))
                    conn.commit()
                    conn.close()
                    st.warning("Soru silindi!")
                    st.experimental_rerun()
