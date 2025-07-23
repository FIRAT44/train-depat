import streamlit as st
from utils.db import db_baglanti

def arsiv_sorular():
    st.subheader("🗂️ Arşivlenmiş Sorular")
    if "arsiv_goster" not in st.session_state:
        st.session_state["arsiv_goster"] = None  # Hangi sorunun detayına bakıldığını tutar

    conn = db_baglanti()
    arsiv = conn.execute(
        "SELECT id, konu, zorluk, soru_metni, secenek_a, secenek_b, secenek_c, secenek_d, dogru_cevap, resim_yolu, arsiv_tarihi FROM arsiv_sorular ORDER BY arsiv_tarihi DESC"
    ).fetchall()
    conn.close()

    if not arsiv:
        st.info("Hiç arşivlenmiş soru yok.")
    else:
        for sid, konu, zorluk, metin, a, b, c, d, dogru, resim, tarih in arsiv:
            cols = st.columns([7, 2, 2, 2])
            with cols[0]:
                st.write(f"**({tarih[:16]}) {konu}** - {metin[:60]}{'...' if len(metin)>60 else ''}")
            with cols[1]:
                if st.button("Detaylı Gör", key=f"detayli_gor_{sid}"):
                    st.session_state["arsiv_goster"] = sid
            with cols[2]:
                if st.button("Geri Yükle", key=f"geri_yukle_{sid}"):
                    # Soru tekrar aktif sorulara taşınır
                    conn = db_baglanti()
                    conn.execute("""
                        INSERT INTO questions (id, konu, zorluk, soru_metni, secenek_a, secenek_b, secenek_c, secenek_d, dogru_cevap, resim_yolu)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (sid, konu, zorluk, metin, a, b, c, d, dogru, resim))
                    conn.execute("DELETE FROM arsiv_sorular WHERE id = ?", (sid,))
                    conn.commit()
                    conn.close()
                    st.success("Soru tekrar aktif sorulara taşındı!")
                    st.rerun()
            with cols[3]:
                if st.button("Kalıcı Sil", key=f"arsiv_kalici_sil_{sid}"):
                    conn = db_baglanti()
                    conn.execute("DELETE FROM arsiv_sorular WHERE id = ?", (sid,))
                    conn.commit()
                    conn.close()
                    st.warning("Soru tamamen silindi!")
                    st.rerun()

            # Detay gösterimi
            if st.session_state.get("arsiv_goster") == sid:
                with st.expander("Soru Detayı", expanded=True):
                    st.markdown(f"**Konu:** {konu}  \n"
                                f"**Zorluk:** {zorluk}  \n"
                                f"**Arşivlenme Tarihi:** {tarih[:19]}")
                    st.markdown(f"**Soru:** {metin}")
                    if resim:
                        try:
                            st.image(resim, width=350)
                        except Exception:
                            st.warning(f"Görsel yüklenemedi: {resim}")
                    st.markdown(f"""
                        - **A:** {a}
                        - **B:** {b}
                        - **C:** {c}
                        - **D:** {d}
                        - **Doğru Cevap:** {dogru}
                    """)
                    if st.button("Kapat", key=f"arsiv_detay_kapat_{sid}"):
                        st.session_state["arsiv_goster"] = None

