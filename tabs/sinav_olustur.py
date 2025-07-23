import streamlit as st
import random
from utils.db import db_baglanti, konu_listele
from utils.pdf_utils import pdf_olustur

def sinav_olustur():
    st.subheader("🎲 Rastgele Sınav Oluştur")
    konu_liste = konu_listele()
    secenekler = ["Tümü"] + konu_liste
    secilen_konu = st.selectbox("Konu Seç (İsteğe Bağlı)", secenekler)
    toplam_soru = st.slider("Toplam Soru Sayısı", 5, 30, 10)
    
    # Zorluk dağılımını sor
    st.markdown("#### ➗ Zorluk Dağılımı")
    col1, col2, col3 = st.columns(3)
    with col1:
        kolay_sayi = st.number_input("Kolay", min_value=0, max_value=toplam_soru, value=int(toplam_soru//3))
    with col2:
        orta_sayi = st.number_input("Orta", min_value=0, max_value=toplam_soru, value=int(toplam_soru//3))
    with col3:
        zor_sayi = st.number_input("Zor", min_value=0, max_value=toplam_soru, value=toplam_soru - int(toplam_soru//3)*2)
    
    # Toplam kontrolü
    if kolay_sayi + orta_sayi + zor_sayi != toplam_soru:
        st.warning("Kolay + Orta + Zor toplamı seçtiğiniz soru sayısı ile aynı olmalı!")
        return
    
    conn = db_baglanti()
    cursor = conn.cursor()
    # Her zorluk için filtreli çek
    filtre = ""
    params = []
    if secilen_konu != "Tümü":
        filtre = "AND konu = ?"
        params = [secilen_konu]

    def get_sorular(zorluk, limit):
        cursor.execute(
            f"SELECT * FROM questions WHERE zorluk=? {filtre}",
            ([zorluk] + params)
        )
        return cursor.fetchall()

    kolaylar = get_sorular("Kolay", kolay_sayi)
    ortalar = get_sorular("Orta", orta_sayi)
    zorlar = get_sorular("Zor", zor_sayi)
    conn.close()

    # Yeterli soru var mı kontrolü
    if len(kolaylar) < kolay_sayi or len(ortalar) < orta_sayi or len(zorlar) < zor_sayi:
        st.error(
            f"Seçilen zorluklarda yeterli soru yok! (Kolay: {len(kolaylar)}/{kolay_sayi}, Orta: {len(ortalar)}/{orta_sayi}, Zor: {len(zorlar)}/{zor_sayi})"
        )
        return

    # Rastgele seç
    secilenler = []
    if kolay_sayi > 0: secilenler += random.sample(kolaylar, kolay_sayi)
    if orta_sayi > 0: secilenler += random.sample(ortalar, orta_sayi)
    if zor_sayi > 0: secilenler += random.sample(zorlar, zor_sayi)

    random.shuffle(secilenler)

    # Zorluklara göre renk
    zorluk_renk = {"Kolay": "#15d251", "Orta": "#f1c40f", "Zor": "#ff4848"}
    # Önizleme
    for idx, soru in enumerate(secilenler, start=1):
        zor = soru[2]
        renk = zorluk_renk.get(zor, "#999")
        st.markdown(f"""### {idx}. Soru <span style='font-size:0.98rem; color:{renk}; font-weight:700;'>&nbsp;({zor})</span>""", unsafe_allow_html=True)
        st.markdown(f"**{soru[3]}**")
        if soru[9]:
            try:
                st.image(soru[9], width=400)
            except:
                st.warning("Görsel yüklenemedi: " + soru[9])
        st.markdown(f"A) {soru[4]}")
        st.markdown(f"B) {soru[5]}")
        st.markdown(f"C) {soru[6]}")
        st.markdown(f"D) {soru[7]}")
        st.markdown("---")
    pdf_sorular = [{
        "metin": soru[3],
        "a": soru[4],
        "b": soru[5],
        "c": soru[6],
        "d": soru[7],
        "resim": soru[9]
    } for soru in secilenler]
    
    import os


    if st.button("📄 PDF Olarak İndir"):
        if secilen_konu == "Tümü":
            sinav_baslik = "Genel Sınav"
        else:
            sinav_baslik = f"{secilen_konu} Sınavı"
        dosya = pdf_olustur(sinav_baslik, pdf_sorular, "sinav_cikti.pdf")
        with open(dosya, "rb") as f:
            st.download_button("📥 PDF Dosyasını İndir", f, file_name="sinav.pdf", mime="application/pdf")
        try:
            os.remove(dosya)
        except Exception:
            pass


    from utils.word_utils import word_olustur

    # ... mevcut kodun en altı:



    if st.button("📝 Word Olarak İndir"):
        if secilen_konu == "Tümü":
            sinav_baslik = "Genel Sınav"
        else:
            sinav_baslik = f"{secilen_konu} Sınavı"
        dosya = word_olustur(sinav_baslik, pdf_sorular, "sinav_cikti.docx")
        with open(dosya, "rb") as f:
            st.download_button("📝 Word Dosyasını İndir", f, file_name="sinav.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            # Kullanıcıya buton sunulduktan sonra dosyayı sil
        try:
            os.remove(dosya)
        except Exception:
            pass