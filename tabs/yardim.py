import streamlit as st

def yardim():
    st.subheader("❓ Yardım / SSS")
    st.markdown("""
    **Sık Sorulanlar:**

    - **Soru nasıl eklenir?**  
      'Soru Ekle' sekmesine tıklayın, tüm alanları doldurun ve ekle butonuna basın.

    - **Sınav nasıl oluşturulur?**  
      'Sınav Oluştur' sekmesinde konu ve soru sayısını seçip rastgele sınav oluşturun.

    - **PDF çıktısı bozuk/eksik çıkarsa?**  
      Lütfen sorularda özel karakterler (emoji, özel işaret) kullanmamaya dikkat edin.

    - **Teknik destek:**  
      İletişim: firat@ayjet.aero

    ---
    """)
    st.info("Sistemi kullanırken sorun yaşarsanız yukarıdaki e-posta adresinden destek alabilirsiniz.")
