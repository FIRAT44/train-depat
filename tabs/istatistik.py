import streamlit as st
from utils.db import db_baglanti, konu_listele

def istatistik():
    st.subheader("📊 Sistem İstatistikleri")
    conn = db_baglanti()
    toplam_soru = conn.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
    konu_sayilari = conn.execute("SELECT konu, COUNT(*) FROM questions GROUP BY konu").fetchall()
    conn.close()
    st.write(f"**Toplam Soru:** {toplam_soru}")
    st.write("**Konuya Göre Soru Dağılımı:**")
    for konu, adet in konu_sayilari:
        st.write(f"- {konu}: {adet} soru")
    # İsteğe bağlı grafik/plotly de eklenebilir

