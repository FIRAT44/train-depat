import streamlit as st
from utils.db import db_baglanti, konu_ekle, konu_listele
from datetime import datetime

def konu_yonet():
    st.subheader("📚 Konu Yönetimi")

    # --- KONULARI LİSTELE, EKLE, SİL ---
    st.markdown("### ➕ Yeni Konu Ekle / Sil")
    yeni_konu = st.text_input("Yeni Konu Adı", "")
    if st.button("Konu Ekle"):
        if yeni_konu.strip():
            konu_ekle(yeni_konu.strip())
            st.success(f"'{yeni_konu}' konusu eklendi.")
        else:
            st.warning("Konu adı boş olamaz!")

    mevcut_konular = konu_listele()
    st.write("#### Konular:")
    for konu in mevcut_konular:
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"- {konu}")
        with col2:
            if st.button("Sil", key=f"sil_konu_{konu}"):
                conn = db_baglanti()
                conn.execute("DELETE FROM konular WHERE ad = ?", (konu,))
                conn.execute("DELETE FROM questions WHERE konu = ?", (konu,))
                conn.commit()
                conn.close()
                st.warning(f"'{konu}' silindi! (Tüm o konudaki sorular da silindi)")
                st.experimental_rerun()

    # --- SORU SİLME - KONULARA GÖRE GRUPLU ---
    st.markdown("### 🗑️ Soru Sil (Konuya Göre Gruplu)")
    conn = db_baglanti()
    sorular = conn.execute("SELECT id, konu, soru_metni FROM questions ORDER BY konu, id DESC").fetchall()
    conn.close()
    if not sorular:
        st.info("Hiç soru yok.")
    else:
        from collections import defaultdict
        gruplu = defaultdict(list)
        for sid, konu, metin in sorular:
            gruplu[konu].append((sid, metin))
        for konu, liste in gruplu.items():
            st.write(f"#### {konu} ({len(liste)} soru)")
            for sid, metin in liste:
                cols = st.columns([8, 1])
                with cols[0]:
                    st.write(f"- {metin[:80]}{'...' if len(metin) > 80 else ''}")
                with cols[1]:
                    if st.button("Sil", key=f"sil_soru_{sid}"):
                        conn = db_baglanti()
                        # 1. Soru detaylarını al
                        soru = conn.execute("SELECT * FROM questions WHERE id = ?", (sid,)).fetchone()
                        # 2. Arşiv tablosuna ekle
                        if soru:
                            conn.execute("""
                                INSERT INTO arsiv_sorular
                                (id, konu, zorluk, soru_metni, secenek_a, secenek_b, secenek_c, secenek_d, dogru_cevap, resim_yolu, arsiv_tarihi)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (*soru, datetime.now().isoformat(" ", "seconds")))
                        # 3. Orijinal soruyu sil
                        conn.execute("DELETE FROM questions WHERE id = ?", (sid,))
                        conn.commit()
                        conn.close()
                        st.warning("Soru arşive taşındı!")
                        st.rerun()