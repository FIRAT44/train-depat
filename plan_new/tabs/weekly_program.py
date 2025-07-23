import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta

def haftalik_ucus_programi(conn_plan, conn_naeron):
    st.title("📅 Haftalık Uçuş Programı")

    # Tarih seçimi
    baslangic_tarihi = st.date_input("Hafta Başlangıç Tarihini Seçiniz", datetime.today())
    bitis_tarihi = baslangic_tarihi + timedelta(days=6)

    st.write(f"### 📌 {baslangic_tarihi} ile {bitis_tarihi} Arasındaki Uçuş Programı")

    query_plan = """
        SELECT ogrenci, plan_tarihi, gorev_tipi, gorev_ismi, sure
        FROM ucus_planlari
        WHERE plan_tarihi BETWEEN ? AND ?
        ORDER BY plan_tarihi, ogrenci
    """

    df_plan = pd.read_sql_query(query_plan, conn_plan, params=[baslangic_tarihi, bitis_tarihi], parse_dates=["plan_tarihi"])

    if df_plan.empty:
        st.warning("Seçilen haftaya ait uçuş programı bulunamadı.")
        return

    # Naeron verisini al ve uçuşların gerçekleşip gerçekleşmediğini kontrol et
    df_naeron = pd.read_sql_query("SELECT * FROM naeron_ucuslar", conn_naeron)
    df_naeron["ogrenci_kodu"] = df_naeron["Öğrenci Pilot"].str.split("-").str[0].str.strip()

    def ucus_yapildi(row):
        ogrenci_kod = row["ogrenci"].split("-")[0].strip()
        gorev = row["gorev_ismi"]
        tarih = row["plan_tarihi"].strftime("%Y-%m-%d")
        eslesen = df_naeron[
            (df_naeron["ogrenci_kodu"] == ogrenci_kod) &
            (df_naeron["Görev"] == gorev) &
            (df_naeron["Uçuş Tarihi 2"] == tarih)  # Düzeltildi
        ]
        return not eslesen.empty

    df_plan["ucus_yapildi"] = df_plan.apply(ucus_yapildi, axis=1)

    # Yalnızca yapılmamış uçuşları göster
    df_gerceklesmeyen = df_plan[~df_plan["ucus_yapildi"]]

    if df_gerceklesmeyen.empty:
        st.success("Bu haftaki tüm uçuşlar yapılmıştır!")
    else:
        program_df = df_gerceklesmeyen.pivot_table(
            index=["ogrenci"],
            columns=["plan_tarihi"],
            values=["gorev_ismi"],
            aggfunc=lambda x: ' \n '.join(x)
        ).fillna("-")
        program_df.columns = program_df.columns.droplevel(0)
        program_df.columns.name = "Tarih"

        st.dataframe(program_df, use_container_width=True)

