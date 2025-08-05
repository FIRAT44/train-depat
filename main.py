import streamlit as st
from tabs.konu_yonet import konu_yonet
from tabs.soru_ekle import soru_ekle
from tabs.sinav_olustur import sinav_olustur
from tabs.istatistik import istatistik
from tabs.yardim import yardim
from utils.user_manage import kullanicilari_yukle
from sms_app.streamlit_app import sms_app
from plan_new import main as plan_new_main

KULLANICILAR = kullanicilari_yukle()


def giris_paneli():
    st.image("logo/ayjet_logo.png", width=140)
    st.markdown("<h2 style='text-align:center'>Giriş Paneli</h2>", unsafe_allow_html=True)
    kullanici = st.text_input("Kullanıcı Adı")
    sifre = st.text_input("Şifre", type="password")
    giris_btn = st.button("Giriş Yap", use_container_width=True)
    if giris_btn:
        if kullanici in KULLANICILAR and sifre == KULLANICILAR[kullanici]["sifre"]:
            st.session_state["giris"] = True
            st.session_state["kullanici"] = kullanici
            st.rerun()
        else:
            st.error("Kullanıcı adı veya şifre yanlış!")


def sinav_menu():
    st.image("logo/ayjet_logo.png", width=120)
    st.title("✈️ AYJET Soru Havuzu ve Sınav Oluşturma Sistemi")
    menu = st.sidebar.radio("📚 Menü", [ "Soru Ekle","Soruları Düzenle", "Sınav Oluştur", "İstatistik","Konu Yönetimi", "Arşiv", "Yardım"])
    if menu == "Konu Yönetimi":
        konu_yonet()
    elif menu == "Soru Ekle":
        soru_ekle()
    elif menu == "Soruları Düzenle":
        from tabs.soru_duzenle import soru_duzenle
        soru_duzenle()
    elif menu == "Sınav Oluştur":
        sinav_olustur()
    elif menu == "İstatistik":
        istatistik()
    elif menu == "Yardım":
        yardim()
    elif menu == "Arşiv":
        from tabs.arsiv_yonet import arsiv_sorular
        arsiv_sorular()
    if st.sidebar.button("⬅️ Ana Menüye Dön", key="back_main_sinav_menu"):
        st.session_state["uygulama_modu"] = "ana"
        st.rerun()

def kart_modul(emoji, title, desc, state_name, renk1="#243B55", renk2="#141E30"):
    kart_css = f"""
    <style>
    div.stButton > button#btn_{state_name} {{
        background: linear-gradient(135deg, {renk1} 0%, {renk2} 100%);
        border-radius: 1.7rem !important;
        box-shadow: 0 4px 32px #0003;
        color: #fff !important;
        font-size: 1.21rem;
        padding: 2.2rem 1rem 2.3rem 1rem;
        margin: 0.6rem 0.15rem 0.8rem 0.15rem;
        min-height: 175px;
        font-weight: 700;
        width: 100%;
        display: flex !important;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align:center;
        transition: all .18s cubic-bezier(.32,1.56,.64,1);
        border:none;
    }}
    div.stButton > button#btn_{state_name}:hover {{
        background: linear-gradient(120deg, {renk2} 0%, {renk1} 100%);
        transform: scale(1.04) translateY(-2px);
        box-shadow: 0 8px 48px #0005;
    }}
    </style>
    """
    st.markdown(kart_css, unsafe_allow_html=True)
    label = f"{emoji}\n{title}\n{desc}"
    if st.button(label, key=f"btn_{state_name}", use_container_width=True, help=desc):
        st.session_state["uygulama_modu"] = state_name
        st.rerun()

def ana_menu():
    user = st.session_state.get("kullanici", "Bilinmiyor")
    roller = KULLANICILAR.get(user, {}).get("roller", [])
    st.image("logo/ayjet_logo.png", width=160)
    st.markdown(f"<div style='text-align:center;'><b>{user.upper()}</b> olarak giriş yaptınız.</div>", unsafe_allow_html=True)
    st.markdown("""
        <div style='
            text-align:center;font-size:2.3rem;
            font-weight:800;color:#143055;
            letter-spacing:0.02em;margin-bottom:0.2rem;'>
            AYJET Yönetim Platformu Sistemi
        </div>
        <div style='text-align:center;font-size:1.13rem;color:#2a3957;margin-bottom:1.6rem;font-weight:500;'>
            Modülleriniz:
        </div>
    """, unsafe_allow_html=True)

    # Her modül hangi roller görebilir?
    MODUL_YETKI = {
        "sinav": ["ATO", "ADMIN","Eğitmen"],
        "istatistik": ["ATO", "ADMIN", "145", "CAMO", "FSTD", "SMS"],
        "Online Eğitim": ["ATO", "ADMIN", "Eğitmen"],
        "uçuş_planlama": ["ATO", "ADMIN"],
        "🚨 SMS / Hazard Raporlama": ["SMS", "ADMIN"],
        "🛠️ Uçak Bakım Takibi": ["145", "CAMO", "ADMIN"],
        "📈 CAMO Paneli": ["ATO", "ADMIN"],
        "yardim": ["145", "CAMO", "ATO", "FSTD", "SMS", "ADMIN", "Eğitmen"],
        "user_yonetim": ["ADMIN"]
    }
    renkler = [
        ("📝", "Sınav", "Soru ekle , Sınav oluştur", "sinav", "#f6d365", "#f7971e"),
        ("📚", "İstatistik", "Toplam soru sayıları", "istatistik", "#00c6ff", "#0072ff"),
        ("🎥", "Online Eğitim", "Video dersler ve dökümanlar.", "Online Eğitim", "#00b09b", "#96c93d"),
        ("🛫", "Uçuş Planlama", "Görev & uçuş takvimi.", "uçuş_planlama", "#a770ef", "#f6d365"),
        ("🚨", "SMS/Hazard", "Olay & risk raporlama.", "🚨 SMS / Hazard Raporlama", "#ff5858", "#f09819"),
        ("🛠️", "Bakım Takibi", "Filo bakımı ve arıza kaydı.", "🛠️ Uçak Bakım Takibi", "#0093e9", "#80d0c7"),
        ("📈", "CAMO Paneli", "CAMO Yönetim Takibi.", "📈 CAMO Paneli", "#f7971e", "#ffd200"),
        ("❓", "Yardım", "Sık sorulanlar, destek.", "yardim", "#232526", "#414345"),
        ("👤", "Kullanıcı Yönetimi", "Kullanıcı ekle/sil", "user_yonetim", "#ff416c", "#ff4b2b")
    ]
    # SADECE YETKİLİ MODÜLLERİ GÖSTER
    kartlar = [k for k in renkler if
               any(r in roller for r in MODUL_YETKI.get(k[3], []))]
    for i in range(0, len(kartlar), 3):
        cols = st.columns(3)
        for j, col in enumerate(cols):
            if i + j < len(kartlar):
                with col:
                    kart_modul(*kartlar[i + j])
    st.markdown("<div style='margin:1.8rem 0 0.5rem 0;text-align:center;color:#9bb3d6;font-size:0.97rem'>© 2025 AYJET TECHNOLOGY</div>", unsafe_allow_html=True)
    if st.button("Çıkış Yap", use_container_width=True):
        for k in ["giris", "kullanici", "uygulama_modu"]:
            if k in st.session_state: del st.session_state[k]
        st.rerun()


def back_to_main():
    st.session_state["uygulama_modu"] = "ana"
    st.rerun()

def main():
    st.set_page_config(page_title="AYJET Sınav Sistemi", layout="wide")
    if "giris" not in st.session_state or not st.session_state["giris"]:
        giris_paneli()
        return
    if "uygulama_modu" not in st.session_state:
        st.session_state["uygulama_modu"] = "ana"
    mod = st.session_state["uygulama_modu"]
    if mod == "ana":
        ana_menu()
    elif mod == "sinav":
        sinav_menu()
    elif mod == "istatistik":
        istatistik()
        if st.button("⬅️ Ana Menüye Dön", key="back_main_istatistik"):
            back_to_main()
    elif mod == "Online Eğitim":
        st.subheader("Online Eğitim Modülü")
        if st.button("⬅️ Ana Menüye Dön", key="back_main_egitim"):
            back_to_main()
    elif mod == "uçuş_planlama":
        st.subheader("Uçuş Planlama Modülü")
        if st.button("⬅️ Ana Menüye Dön", key="back_main_uçak_planlama"):
            plan_new_main.main()
            



    elif mod == "🚨 SMS / Hazard Raporlama":
        sms_app()

    elif mod == "🛠️ Uçak Bakım Takibi":
        st.subheader("Uçak Bakım Takibi")
        if st.button("⬅️ Ana Menüye Dön", key="back_main_bakim"):
            back_to_main()
    elif mod == "📈 CAMO Paneli":
        st.subheader("CAMO Paneli")
        if st.button("⬅️ Ana Menüye Dön", key="back_main_gelisim"):
            back_to_main()
    elif mod == "yardim":
        yardim()
        if st.button("⬅️ Ana Menüye Dön", key="back_main_yardim"):
            back_to_main()

    elif mod == "user_yonetim":
        from tabs.kullanici_yonetimi import kullanici_yonetimi
        kullanici_yonetimi()
        if st.button("⬅️ Ana Menüye Dön", key="back_main_user_yonetim"):
            back_to_main()
    

if __name__ == "__main__":
    main()
