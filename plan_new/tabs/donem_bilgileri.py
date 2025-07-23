import pandas as pd
import streamlit as st
import sqlite3
import io


def donem_bilgileri(st):
    st.title("📘 Tüm Dönem Bilgileri ve Uçuş Eğitim Başlangıçları")

    # Dönem Bilgileri Tablosu Gösterimi ve Güncelleme
    try:
        conn_donem = sqlite3.connect("plan_new/donem_bilgileri.db")
        cursor = conn_donem.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS donem_bilgileri (
                donem TEXT PRIMARY KEY,
                donem_numarasi TEXT,
                donem_tipi TEXT,
                donem_alt_ismi TEXT,
                kisi_sayisi INTEGER,
                baslangic_tarihi TEXT,
                bitis_tarihi TEXT,
                teorik_egitim_baslangic TEXT,
                ucus_egitim_baslangic TEXT
            )
        """)
        conn_donem.commit()
        df_donem = pd.read_sql_query("SELECT * FROM donem_bilgileri", conn_donem)

        st.markdown("### 📝 Dönem Bilgilerini Güncelle")
        edited_df = st.data_editor(
            df_donem,
            use_container_width=True,
            num_rows="dynamic",
            key="donem_editor",
        )

        if st.button("💾 Değişiklikleri Kaydet"):
            cursor.execute("DELETE FROM donem_bilgileri")
            for _, row in edited_df.iterrows():
                cursor.execute("""
                    INSERT INTO donem_bilgileri (
                        donem, donem_numarasi, donem_tipi, donem_alt_ismi, kisi_sayisi,
                        baslangic_tarihi, bitis_tarihi,
                        teorik_egitim_baslangic, ucus_egitim_baslangic
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, tuple(row))
            conn_donem.commit()
            st.success("Tüm değişiklikler kaydedildi!")

    except Exception as e:
        st.error(f"Dönem bilgileri okunamadı: {e}")

    # Öğrencilerin Son Görev Tarihi
    st.markdown("---")
    st.subheader("📅 Seçilen Dönemdeki Öğrencilerin Tahmini Bitiş Tarihleri")

    try:
        conn_plan = sqlite3.connect("plan_new/ucus_egitim.db")
        df_plan = pd.read_sql_query("SELECT * FROM ucus_planlari", conn_plan, parse_dates=["plan_tarihi"])
        secilen_donem = st.selectbox("Dönem Seç", df_plan["donem"].dropna().unique())
        df_donem_sec = df_plan[df_plan["donem"] == secilen_donem]

        ogrenci_son_tarih = df_donem_sec.groupby("ogrenci")["plan_tarihi"].max().reset_index()
        ogrenci_son_tarih = ogrenci_son_tarih.rename(columns={"plan_tarihi": "Son Görev Tarihi"})

        st.dataframe(ogrenci_son_tarih, use_container_width=True)

        if not ogrenci_son_tarih.empty:
            ortalama_tarih = ogrenci_son_tarih["Son Görev Tarihi"].mean()
            st.markdown(f"### 📆 Ortalama Bitiş Tarihi: **{ortalama_tarih.date()}**")

            st.markdown("### 📊 Öğrenci Sıralaması (Erken Bitiren → Geç Bitiren)")
            st.dataframe(ogrenci_son_tarih.sort_values("Son Görev Tarihi"), use_container_width=True)

            st.markdown("### 🟥 Bitirme Süresi Yaklaşanlar")
            kalan_gun_df = ogrenci_son_tarih.copy()
            kalan_gun_df["Kalan Gün"] = (ogrenci_son_tarih["Son Görev Tarihi"] - pd.Timestamp.today()).dt.days
            uyarilacaklar = kalan_gun_df[kalan_gun_df["Kalan Gün"] <= 7]
            if not uyarilacaklar.empty:
                st.warning("⏳ 7 gün içinde bitecek öğrenciler:")
                st.dataframe(uyarilacaklar, use_container_width=True)
            else:
                st.info("🚀 Bitirme süresi yaklaşan öğrenci bulunmamaktadır.")

            # Excel çıktısı
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                ogrenci_son_tarih.to_excel(writer, index=False, sheet_name="Ogrenci Bitis Tarihleri")
            st.download_button(
                label="📥 Excel Olarak İndir",
                data=buffer.getvalue(),
                file_name="bitis_tarihleri.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    except Exception as e:
        st.error(f"Uçuş planları verisi okunamadı: {e}")

    # Tüm dönem ve öğrenciler için bitiş tarihlerini listele
    st.markdown("---")
    st.subheader("📦 Tüm Dönem ve Öğrencilerin Bitiş Tarihleri")
    if st.button("📊 Tümünü Tara ve Excel'e Aktar"):
        try:
            tum_donemler = df_plan["donem"].dropna().unique()
            tum_son_tarihler = []
            for donem in tum_donemler:
                df_d = df_plan[df_plan["donem"] == donem]
                ogrenci_bitis = df_d.groupby("ogrenci")["plan_tarihi"].max().reset_index()
                ogrenci_bitis["donem"] = donem
                ogrenci_bitis = ogrenci_bitis.rename(columns={"plan_tarihi": "Son Görev Tarihi"})
                tum_son_tarihler.append(ogrenci_bitis)

            sonuc_df = pd.concat(tum_son_tarihler).sort_values(["donem", "Son Görev Tarihi"])
            st.dataframe(sonuc_df, use_container_width=True)

            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                sonuc_df.to_excel(writer, index=False, sheet_name="Tum_Bitis_Tarihleri")
            st.download_button(
                label="📥 Tümünü Excel Olarak İndir",
                data=buffer.getvalue(),
                file_name="tum_donem_bitis_tarihleri.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.error(f"Tüm dönemler taranırken hata oluştu: {e}")
