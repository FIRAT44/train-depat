# tabs/tab_naeron_goruntule.py
import pandas as pd
import sqlite3
import streamlit as st

def tab_naeron_goruntule(st):
    st.subheader("🗂 Naeron Veritabanını Görüntüle, Filtrele, Düzelt, Sil")

    try:
        conn = sqlite3.connect("plan_new/naeron_kayitlari.db")
        df = pd.read_sql_query("SELECT rowid, * FROM naeron_ucuslar", conn)

        if df.empty:
            st.warning("Veritabanında kayıt bulunamadı.")
            return

        # Filtre paneli
        with st.expander("🔍 Filtrele"):
            col1, col2 = st.columns(2)
            with col1:
                ogretmen = st.multiselect("Öğretmen Pilot", options=sorted(df["Öğretmen Pilot"].dropna().unique().tolist()))
                ogrenci = st.multiselect("Öğrenci Pilot", options=sorted(df["Öğrenci Pilot"].dropna().unique().tolist()))
            with col2:
                gorev = st.multiselect("Görev", options=sorted(df["Görev"].dropna().unique().tolist()))
                tarih_araligi = st.date_input("Uçuş Tarihi Aralığı", [])

        df_filtered = df.copy()
        if ogretmen:
            df_filtered = df_filtered[df_filtered["Öğretmen Pilot"].isin(ogretmen)]
        if ogrenci:
            df_filtered = df_filtered[df_filtered["Öğrenci Pilot"].isin(ogrenci)]
        if gorev:
            df_filtered = df_filtered[df_filtered["Görev"].isin(gorev)]
        if len(tarih_araligi) == 2:
            df_filtered = df_filtered[
                (pd.to_datetime(df_filtered["Uçuş Tarihi 2"]) >= pd.to_datetime(tarih_araligi[0])) &
                (pd.to_datetime(df_filtered["Uçuş Tarihi 2"]) <= pd.to_datetime(tarih_araligi[1]))
            ]

        st.markdown("### 📋 Filtrelenmiş Kayıtlar")
        st.dataframe(df_filtered.drop(columns=["rowid"]), use_container_width=True)

        # CSV indir
        csv = df_filtered.drop(columns=["rowid"]).to_csv(index=False).encode("utf-8")
        st.download_button("📥 CSV olarak indir", csv, file_name="naeron_filtreli.csv", mime="text/csv")


        # 🔄 Toplu Düzeltmeler
        with st.expander("🔄 Toplu Düzeltmeler"):
            if st.button("Görev sütunundaki '*' işaretlerini temizle"):
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE naeron_ucuslar
                    SET "Görev" = REPLACE("Görev", '*', '')
                    WHERE "Görev" LIKE '%*%'
                """)
                conn.commit()
                st.success("✅ Görev sütunundaki tüm '*' işaretleri kaldırıldı.")
                st.rerun()

            if st.button("Öğrenci Pilot '130AH - Ali HAMAL' olanları güncelle"):
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE naeron_ucuslar
                    SET "Öğrenci Pilot" = '130AH - Ali HAMAL'
                    WHERE "Öğrenci Pilot" = '130AH'
                """)
                conn.commit()
                st.success("✅ '130NV' olan öğrenci pilotlar '130NV - Nisa Nur VARLI' olarak güncellendi.")
                st.rerun()
            
            if st.button("Görev 'SXC-12-C' → 'SXC-12' olarak güncelle"):
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE naeron_ucuslar
                    SET "Görev" = 'SXC-12'
                    WHERE "Görev" = 'SXC-12 (C)'
                """)
                conn.commit()
                st.success("✅ 'SXC-12-C' olan tüm kayıtlar 'SXC-12' olarak güncellendi.")
                st.rerun()
 
            if st.button("Görev 'SXC-10-C' → 'SXC-10' olarak güncelle"):
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE naeron_ucuslar
                    SET "Görev" = 'SXC-10'
                    WHERE "Görev" = 'SXC-10 (C)'
                """)
                conn.commit()
                st.success("✅ 'SXC-10-C' → 'SXC-10' tamamlandı.")
                st.rerun()

            if st.button("Görev 'SXC-11-C' → 'SXC-11' olarak güncelle"):
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE naeron_ucuslar
                    SET "Görev" = 'SXC-11'
                    WHERE "Görev" = 'SXC-11 (C)'
                """)
                conn.commit()
                st.success("✅ 'SXC-11-C' → 'SXC-11' tamamlandı.")
                st.rerun()
            
            if st.button("Görev 'EÐT. TKR.(SE)' → 'EGT. TKR. (SE)' olarak güncelle"):
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE naeron_ucuslar
                    SET "Görev" = 'EGT. TKR. (SE)'
                    WHERE "Görev" = 'EÐT. TKR.(SE)'
                """)
                conn.commit()
                st.success("✅ 'EÐT. TKR.(SE)' → 'EGT. TKR. (SE)' tamamlandı.")
                st.rerun()

            if st.button("Görev 'E-EÐT.TKR.(SE)' → 'E-EGT.TKR.(SE)' olarak güncelle"):
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE naeron_ucuslar
                    SET "Görev" = 'E-EGT.TKR.(SE)'
                    WHERE "Görev" = 'E-EÐT.TKR.(SE)'
                """)
                conn.commit()
                st.success("✅ 'E-EÐT.TKR.(SE)' → 'E-EGT.TKR.(SE)' tamamlandı.")
                st.rerun()
            
            if st.button("Görev 'EĞT.TKR(SIM)' → 'EGT.TKR(SIM)' olarak güncelle"):
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE naeron_ucuslar
                    SET "Görev" = 'EGT.TKR(SIM)'
                    WHERE "Görev" = 'EĞT.TKR(SIM)'
                """)
                conn.commit()
                st.success("✅ 'EĞT.TKR(SIM)' → 'EGT.TKR(SIM)' tamamlandı.")
                st.rerun()




        if st.button("🕒 Tüm saat sütunlarını HH:MM formatına dönüştür"):
            cursor = conn.cursor()
            for col in ["Off Bl.", "On Bl.", "Block Time", "Flight Time"]:
                cursor.execute(f'''
                    UPDATE naeron_ucuslar
                    SET "{col}" = substr("{col}", 1, 5)
                    WHERE "{col}" LIKE '%:%'
                ''')
            conn.commit()
            st.success("✅ Tüm saat sütunları HH:MM formatına güncellendi.")
            st.rerun()



        # 🧾 Uçuş No'ya göre seçim
        st.markdown("### ✏️ Kayıt Düzelt / 🗑️ Sil")
        secilen_ucus_no = st.selectbox("Bir kayıt seçin (uçuş no)", options=df_filtered["ucus_no"].tolist())

        if secilen_ucus_no:
            secilen_kayit = df[df["ucus_no"] == secilen_ucus_no].iloc[0]

            with st.form("kayit_duzenle_formu"):
                ucus_tarihi = st.date_input("Uçuş Tarihi", pd.to_datetime(secilen_kayit["Uçuş Tarihi 2"]))
                cagri = st.text_input("Çağrı", secilen_kayit["Çağrı"])
                offbl = st.text_input("Off Bl.", secilen_kayit["Off Bl."])
                onbl = st.text_input("On Bl.", secilen_kayit["On Bl."])
                block_time = st.text_input("Block Time", secilen_kayit["Block Time"])
                flight_time = st.text_input("Flight Time", secilen_kayit["Flight Time"])
                ogretmen = st.text_input("Öğretmen Pilot", secilen_kayit["Öğretmen Pilot"])
                ogrenci = st.text_input("Öğrenci Pilot", secilen_kayit["Öğrenci Pilot"])
                kalkis = st.text_input("Kalkış", secilen_kayit["Kalkış"])
                inis = st.text_input("İniş", secilen_kayit["İniş"])
                gorev = st.text_input("Görev", secilen_kayit["Görev"])
                engine = st.text_input("Engine", secilen_kayit["Engine"])
                ifr_suresi = st.text_input("IFR Süresi", secilen_kayit["IFR Süresi"])

                col1, col2 = st.columns(2)
                with col1:
                    guncelle = st.form_submit_button("💾 Kaydı Güncelle")
                with col2:
                    sil = st.form_submit_button("🗑️ Kaydı Sil")

                if guncelle:
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE naeron_ucuslar SET
                            "Uçuş Tarihi 2" = ?, "Çağrı" = ?, "Off Bl." = ?, "On Bl." = ?,
                            "Block Time" = ?, "Flight Time" = ?, "Öğretmen Pilot" = ?, "Öğrenci Pilot" = ?,
                            "Kalkış" = ?, "İniş" = ?, "Görev" = ?, "Engine" = ?, "IFR Süresi" = ?
                        WHERE ucus_no = ?
                    """, (
                        ucus_tarihi, cagri, offbl, onbl,
                        block_time, flight_time, ogretmen, ogrenci,
                        kalkis, inis, gorev, engine, ifr_suresi,
                        secilen_ucus_no
                    ))
                    conn.commit()
                    st.success("✅ Kayıt başarıyla güncellendi.")

                if sil:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM naeron_ucuslar WHERE ucus_no = ?", (secilen_ucus_no,))
                    conn.commit()
                    st.warning("🗑️ Kayıt silindi. Lütfen sayfayı yenileyin.")

        conn.close()

    except Exception as e:
        st.error(f"❌ Hata oluştu: {e}")
