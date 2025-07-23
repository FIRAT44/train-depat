import streamlit as st
from utils.user_manager import kullanicilari_yukle, kullanicilari_kaydet

def kullanici_yonetimi():
    st.subheader("👤 Kullanıcı Yönetimi (Sadece Admin)")
    veriler = kullanicilari_yukle()

    # --- Kullanıcı Ekle ---
    st.markdown("### ➕ Yeni Kullanıcı Ekle")
    yeni_ad = st.text_input("Kullanıcı Adı", key="yeni_k_ad")
    yeni_sifre = st.text_input("Şifre", key="yeni_k_sifre")
    yeni_roller = st.text_input("Roller (virgülle ayır)", key="yeni_k_roller")
    if st.button("Kullanıcı Ekle"):
        if not yeni_ad.strip() or not yeni_sifre:
            st.warning("Ad ve şifre boş olamaz!")
        elif yeni_ad in veriler:
            st.error("Bu kullanıcı zaten var!")
        else:
            veriler[yeni_ad] = {
                "sifre": yeni_sifre,
                "roller": [r.strip() for r in yeni_roller.split(",") if r.strip()]
            }
            kullanicilari_kaydet(veriler)
            st.success(f"'{yeni_ad}' eklendi!")
            st.rerun()

    st.markdown("---")

    # --- Mevcut Kullanıcılar Tablosu ve İşlemleri ---
    st.markdown("### 🗂️ Mevcut Kullanıcılar")
    for ad, bilgi in veriler.items():
        with st.expander(f"👤 {ad}"):
            sifre = st.text_input("Şifre", value=bilgi["sifre"], key=f"sifre_{ad}")
            roller = st.text_input("Roller (virgülle)", value=", ".join(bilgi["roller"]), key=f"roller_{ad}")
            col1, col2, col3 = st.columns([1,1,2])
            with col1:
                if st.button("Kaydet", key=f"kaydet_{ad}"):
                    veriler[ad]["sifre"] = sifre
                    veriler[ad]["roller"] = [r.strip() for r in roller.split(",") if r.strip()]
                    kullanicilari_kaydet(veriler)
                    st.success(f"{ad} güncellendi!")
                    st.experimental_rerun()
            with col2:
                if st.button("Sil", key=f"sil_{ad}"):
                    del veriler[ad]
                    kullanicilari_kaydet(veriler)
                    st.warning(f"{ad} silindi!")
                    st.experimental_rerun()
            with col3:
                st.write(f"Roller: {', '.join(bilgi['roller'])}")
