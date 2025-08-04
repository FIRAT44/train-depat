# main.py
import streamlit as st
import sqlite3
from db import initialize_database
from PIL import Image
from datetime import date
import pandas as pd

# Sekme içerikleri
from tabs.tab_plan_olustur import tab_plan_olustur
from tabs.tab_gerceklesen_kayit import tab_gerceklesen_kayit
from tabs.tab_donem_raporu import tab_donem_raporu
from tabs.tab_tarihsel_analiz import tab_tarihsel_analiz
from tabs.tab_ogrenci_gelisim import tab_ogrenci_gelisim
from tabs.tab_tekil_gorev import tekil_gorev
from tabs.tab_coklu_gorev import tab_coklu_gorev
from tabs.tab_ihtiyac_analizi import tab_ihtiyac_analizi
from tabs.tab_tum_veriler import tab_tum_veriler
from tabs.tab_naeron_yukle import tab_naeron_yukle
from tabs.tab_naeron_goruntule import tab_naeron_goruntule


from tabs.weekly_program import haftalik_ucus_programi
from tabs.tab_donem_ogrenci_yonetimi import tab_donem_ogrenci_yonetimi
from tabs.tab_taslak_plan import tab_taslak_plan
from tabs.tab_taslak_coklu_gorev import tab_taslak_coklu_gorev
from tabs.new.excel_to_db_loader import tab_taslak_olustur
from tabs.openMeteo.open_Meteo_connect_python import ruzgar_verisi_getir
from tabs.fams_to_naeeron.tab_fams_to_naeron import tab_fams_to_naeron



st.set_page_config(page_title="AYJET-TECHNOLOGY", layout="wide")
# Logo ve başlık
col1, col2 = st.columns([3, 10])
with col1:
    st.image("logo.png", width=180)
with col2:
    st.title("🛫 Uçuş Eğitimi Planlayıcı")

# Veritabanı
conn = sqlite3.connect("ucus_egitim.db", check_same_thread=False)
cursor = conn.cursor()
initialize_database(cursor)

# Yüklenen günler tablosu (varsa oluştur)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS naeron_log (
        tarih TEXT PRIMARY KEY,
        kayit_sayisi INTEGER
    )
""")
conn.commit()

<<<<<<< HEAD
# Menü
menu = st.selectbox("📚 Menü", [
    "📋 Planlama",
    "📊 Analiz ve Raporlar",
    "📂 Naeron İşlemleri",
    "🤖 Revize İşlemleri",
    #"✈️ Uçak Bazlı Uçuş Süresi Analizi",
    "Meteoroloji Verileri",
    "🔄 FAMS → Naeron",
    "deneme"
])

if menu == "📋 Planlama":
    tab_sec = st.radio("📋 Planlama Sekmesi", ["TASLAK OLUŞTURMA","Plan Oluştur","📚 Dönem ve Öğrenci Yönetimi", "Gerçekleşen Giriş","Taslak Plan","🧪 Taslak Plan Çoklu Görev"], horizontal=True)
    if tab_sec == "Plan Oluştur":
        tab_plan_olustur(st, conn, cursor)
    



    elif tab_sec == "TASLAK OLUŞTURMA":
        st.subheader("📂 TASLAK OLUŞTURMA - DENEYSEL (Şimdilik Excel ile yükleme yapılacaktır")
        tab_taslak_olustur(st)






    elif tab_sec == "Gerçekleşen Giriş":
        tab_gerceklesen_kayit(st, conn)
    elif tab_sec == "📚 Dönem ve Öğrenci Yönetimi":
        tab_donem_ogrenci_yonetimi(st, conn)
    elif tab_sec == "Taslak Plan":
        tab_taslak_plan(st)
    elif tab_sec == "🧪 Taslak Plan Çoklu Görev":
        tab_taslak_coklu_gorev(conn)
    

elif menu == "📊 Analiz ve Raporlar":
    tab_sec = st.radio("📊 Rapor ve Analiz Sekmesi", [
        "Haftalık Program","Otomatik Planlama","Kayıtlı Planlar","Dönem Raporu", "Tarihsel Analiz", "Gelişim Takibi", "Tekil Görev","Coklu Görev", "İhtiyaç Analizi", "Tüm Veriler"], horizontal=True)
    if tab_sec == "Haftalık Program":
        conn_plan = sqlite3.connect("ucus_egitim.db", check_same_thread=False)
        conn_naeron = sqlite3.connect("naeron_kayitlari.db", check_same_thread=False)
        haftalik_ucus_programi(conn_plan, conn_naeron)
    
    elif tab_sec == "Otomatik Planlama":
        from tabs.otomatikPlanlama.autoPlan import haftalik_ucus_akilli_program
        conn_plan = sqlite3.connect("ucus_egitim.db", check_same_thread=False)
        conn_naeron = sqlite3.connect("naeron_kayitlari.db", check_same_thread=False)
        haftalik_ucus_akilli_program(conn_plan, conn_naeron)

    elif tab_sec == "Kayıtlı Planlar":
        st.subheader("📋 Kayıtlı Planlar")
        from tabs.otomatikPlanlama.kayitli_planlar import main as kayitli_planlar_main
        kayitli_planlar_main()
        
        
        
    elif tab_sec == "Dönem Raporu":
        tab_donem_raporu(st, conn)
    elif tab_sec == "Tarihsel Analiz":
        tab_tarihsel_analiz(st, conn)
    elif tab_sec == "Gelişim Takibi":
        tab_ogrenci_gelisim(st, conn)

    elif tab_sec == "Tekil Görev":
        tekil_gorev(conn)
    elif tab_sec == "Coklu Görev":
        tab_coklu_gorev(conn)
    elif tab_sec == "İhtiyaç Analizi":
        tab_ihtiyac_analizi(st, conn)
    elif tab_sec == "Tüm Veriler":
        tab_tum_veriler(st, conn, cursor)

elif menu == "📂 Naeron İşlemleri":
    st.caption("📅 Yüklemek istediğiniz günün verisini aşağıdan seçin")
    secilen_veri_tarihi = st.date_input("📆 Yüklenecek Uçuş Tarihi", max_value=date.today().replace(day=date.today().day))
    st.session_state["naeron_veri_tarihi"] = secilen_veri_tarihi

    tab_sec = st.radio("📂 Naeron Sekmesi", ["Naeron Yükle", "Naeron Verileri Filtrele","API ile NAERON veri çeekme"], horizontal=True)
    if tab_sec == "Naeron Yükle":
        tab_naeron_yukle(st, st.session_state["naeron_veri_tarihi"], conn)
    elif tab_sec == "Naeron Verileri Filtrele":
        tab_naeron_goruntule(st)
    elif tab_sec == "API ile NAERON veri çeekme":
        from tabs.NaeronApi.api_use import naeron_api_use
        naeron_api_use(st, conn)

elif menu == "🤖 Revize İşlemleri":
    print("Revize paneli başlatılıyor...")
    tab_sec = st.radio("🤖 Revize İşlemleri Sekmesi", ["Bireysel Revize Paneli", "Genel tarama","Takvimden Revize"], horizontal=True)
    if tab_sec == "Bireysel Revize Paneli":
        from tabs.revize_panel_bireysel import panel
        panel(conn)
    elif tab_sec == "Genel tarama":
        from tabs.revize_panel_genel import panel_tum_donemler
        panel_tum_donemler(conn)
    elif tab_sec == "Takvimden Revize":
        from tabs.takvimdenRevize.takvimdenOtomatikRevize import tab_geride_olanlar
        tab_geride_olanlar(st, conn)
   



# elif menu == "✈️ Uçak Bazlı Uçuş Süresi Analizi":
#     tab_ucak_analiz(st)

elif menu == "Meteoroloji Verileri":
    tab_sec = st.radio("Meteoroloji Sekmesi", ["Meteoroloji Verileri"], horizontal=True)
    if tab_sec == "Meteoroloji Verileri":
        st.subheader("🌬️ Rüzgar Tahmini Görüntüleyici\t📍 Konum: **41.1025°N, 28.5461°E** (Hezarfen Havaalanı Yakını)")

        ruzgar_verisi_getir()


elif menu == "🔄 FAMS → Naeron":
    tab_sec = st.radio("🔄 FAMS → Naeron Sekmesi", ["FAMS → Naeron"], horizontal=True)
    if tab_sec == "FAMS → Naeron":
        tab_fams_to_naeron(st, conn)

elif menu == "deneme":
    from tabs.tab_deneme import deneme
    deneme(st, conn)
=======
    # Menü
    menu = st.selectbox("📚 Menü", [
        "📋 Planlama",
        "📊 Analiz ve Raporlar",
        "📂 Naeron İşlemleri",
        "🤖 Revize İşlemleri",
        #"✈️ Uçak Bazlı Uçuş Süresi Analizi",
        "Meteoroloji Verileri",
        "🔄 FAMS → Naeron",
        "deneme"
    ])

    if menu == "📋 Planlama":
        tab_sec = st.radio("📋 Planlama Sekmesi", ["TASLAK OLUŞTURMA","Plan Oluştur","📚 Dönem ve Öğrenci Yönetimi", "Gerçekleşen Giriş","Taslak Plan","🧪 Taslak Plan Çoklu Görev"], horizontal=True)
        if tab_sec == "Plan Oluştur":
            tab_plan_olustur(st, conn, cursor)
        



        elif tab_sec == "TASLAK OLUŞTURMA":
            st.subheader("📂 TASLAK OLUŞTURMA - DENEYSEL (Şimdilik Excel ile yükleme yapılacaktır")
            tab_taslak_olustur(st)






        elif tab_sec == "Gerçekleşen Giriş":
            tab_gerceklesen_kayit(st, conn)
        elif tab_sec == "📚 Dönem ve Öğrenci Yönetimi":
            tab_donem_ogrenci_yonetimi(st, conn)
        elif tab_sec == "Taslak Plan":
            tab_taslak_plan(st)
        elif tab_sec == "🧪 Taslak Plan Çoklu Görev":
            tab_taslak_coklu_gorev(conn)
        

    elif menu == "📊 Analiz ve Raporlar":
        tab_sec = st.radio("📊 Rapor ve Analiz Sekmesi", [
            "Haftalık Program","Dönem Raporu", "Tarihsel Analiz", "Gelişim Takibi", "Tekil Görev","Coklu Görev", "İhtiyaç Analizi", "Tüm Veriler"], horizontal=True)
        if tab_sec == "Haftalık Program":
            conn_plan = sqlite3.connect("plan_new/ucus_egitim.db", check_same_thread=False)
            conn_naeron = sqlite3.connect("plan_new/naeron_kayitlari.db", check_same_thread=False)
            haftalik_ucus_programi(conn_plan, conn_naeron)
            
        elif tab_sec == "Dönem Raporu":
            tab_donem_raporu(st, conn)
        elif tab_sec == "Tarihsel Analiz":
            tab_tarihsel_analiz(st, conn)
        elif tab_sec == "Gelişim Takibi":
            tab_ogrenci_gelisim(st, conn)

        elif tab_sec == "Tekil Görev":
            tekil_gorev(conn)
        elif tab_sec == "Coklu Görev":
            tab_coklu_gorev(conn)
        elif tab_sec == "İhtiyaç Analizi":
            tab_ihtiyac_analizi(st, conn)
        elif tab_sec == "Tüm Veriler":
            tab_tum_veriler(st, conn, cursor)

    elif menu == "📂 Naeron İşlemleri":
        st.caption("📅 Yüklemek istediğiniz günün verisini aşağıdan seçin. Bugünün verisi kabul edilmez.")
        secilen_veri_tarihi = st.date_input("📆 Yüklenecek Uçuş Tarihi", max_value=date.today().replace(day=date.today().day - 1))
        st.session_state["naeron_veri_tarihi"] = secilen_veri_tarihi

        tab_sec = st.radio("📂 Naeron Sekmesi", ["Naeron Yükle", "Naeron Verileri Filtrele","API ile NAERON veri çeekme"], horizontal=True)
        if tab_sec == "Naeron Yükle":
            tab_naeron_yukle(st, st.session_state["naeron_veri_tarihi"], conn)
        elif tab_sec == "Naeron Verileri Filtrele":
            tab_naeron_goruntule(st)
        elif tab_sec == "API ile NAERON veri çeekme":
            from plan_new.tabs.NaeronApi.api_use import naeron_api_use
            naeron_api_use(st, conn)

    elif menu == "🤖 Revize İşlemleri":
        print("Revize paneli başlatılıyor...")
        tab_sec = st.radio("🤖 Revize İşlemleri Sekmesi", ["Bireysel Revize Paneli", "Genel tarama"], horizontal=True)
        if tab_sec == "Bireysel Revize Paneli":
            from plan_new.tabs.revize_panel_bireysel import panel
            panel(conn)
        elif tab_sec == "Genel tarama":
            from plan_new.tabs.revize_panel_genel import panel_tum_donemler
            panel_tum_donemler(conn)

    # elif menu == "✈️ Uçak Bazlı Uçuş Süresi Analizi":
    #     tab_ucak_analiz(st)

    elif menu == "Meteoroloji Verileri":
        tab_sec = st.radio("Meteoroloji Sekmesi", ["Meteoroloji Verileri"], horizontal=True)
        if tab_sec == "Meteoroloji Verileri":
            st.subheader("🌬️ Rüzgar Tahmini Görüntüleyici\t📍 Konum: **41.1025°N, 28.5461°E** (Hezarfen Havaalanı Yakını)")

            ruzgar_verisi_getir()


    elif menu == "🔄 FAMS → Naeron":
        tab_sec = st.radio("🔄 FAMS → Naeron Sekmesi", ["FAMS → Naeron"], horizontal=True)
        if tab_sec == "FAMS → Naeron":
            tab_fams_to_naeron(st, conn)

    elif menu == "deneme":
        from tabs.tab_deneme import deneme
        deneme(st, conn)

    
    if st.sidebar.button("⬅️ Ana Menüye Dön", key="back_main_sinav_menu"):
        st.session_state["uygulama_modu"] = "ana"
        st.rerun()
>>>>>>> 185331e6c4edb677f7cdd7223083ad47b64ca149
