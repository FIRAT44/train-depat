# tabs/tab_ogrenci_gelisim.py
import pandas as pd
import streamlit as st
from plan_new.tabs.utils.ozet_utils import ozet_panel_verisi_hazirla  # ⬅️ Fonksiyon burada olmalı
import plotly.graph_objects as go

def tab_ogrenci_gelisim(st, conn):
    st.subheader("🧑‍✈️ Öğrenci Gelişim Takibi (Plan vs Gerçekleşen)")

    df = pd.read_sql_query("SELECT * FROM ucus_planlari", conn)
    if df.empty:
        st.warning("Veri bulunamadı.")
        return

    # 🔽 1. Dönem Seçimi
    donemler = df["donem"].dropna().unique().tolist()
    secilen_donem = st.selectbox("📆 Dönem Seçin", sorted(donemler))

    # 🔽 2. Öğrenci Seçimi (döneme göre filtreli)
    df_donem = df[df["donem"] == secilen_donem].copy()
    df_donem["ogrenci_kodu"] = df_donem["ogrenci"].str.split("-").str[0].str.strip()
    ogrenci_kodlari = df_donem["ogrenci_kodu"].dropna().unique().tolist()

    secilen_kod = st.selectbox("👨‍🎓 Öğrenci Kodunu Seçin", sorted(ogrenci_kodlari))

    if secilen_kod:
        df_ogrenci, phase_toplamlar, toplam_plan, toplam_gercek, toplam_fark, df_naeron_eksik = ozet_panel_verisi_hazirla(secilen_kod, conn)

        st.markdown("### 📊 Planlanan ve Gerçekleşen Uçuşlar")
        st.dataframe(df_ogrenci[[
            "plan_tarihi", "gorev_ismi", "Planlanan", "Gerçekleşen", "Fark", "durum"
        ]], use_container_width=True)

        st.markdown("### 📈 Kümülatif Süre Grafiği")
        df_ogrenci["kumulatif_plan"] = df_ogrenci["planlanan_saat_ondalik"].cumsum()
        df_ogrenci["kumulatif_gercek"] = df_ogrenci["gerceklesen_saat_ondalik"].cumsum()

        st.line_chart(df_ogrenci.set_index("plan_tarihi")[["kumulatif_plan", "kumulatif_gercek"]])

        st.markdown("### 📌 Toplam Durum Özeti")
        col1, col2, col3 = st.columns(3)
        col1.metric("Planlanan (saat)", f"{toplam_plan:.2f}")
        col2.metric("Gerçekleşen (saat)", f"{toplam_gercek:.2f}")
        col3.metric("Fark", f"{toplam_fark:.2f}")


        

        st.markdown("### 📊 Görev Bazlı Planlanan vs Gerçekleşen Süre (saat)")

        # Görev bazlı karşılaştırma verisi
        df_plot = df_ogrenci[["gorev_ismi", "planlanan_saat_ondalik", "gerceklesen_saat_ondalik"]].copy()
        df_plot = df_plot[df_plot["planlanan_saat_ondalik"] > 0]

        fig = go.Figure(data=[
            go.Bar(
                name="🟥 Planlanan",
                x=df_plot["gorev_ismi"],
                y=df_plot["planlanan_saat_ondalik"],
                marker_color="crimson"  # 🔴 Kırmızı
            ),
            go.Bar(
                name="🟦 Gerçekleşen",
                x=df_plot["gorev_ismi"],
                y=df_plot["gerceklesen_saat_ondalik"],
                marker_color="royalblue"  # 🔵 Mavi
            )
        ])

        fig.update_layout(
            barmode="group",
            xaxis_title="Görev İsmi",
            yaxis_title="Süre (saat)",
            title="Planlanan vs Gerçekleşen Süre (Görev Bazında)",
            xaxis_tickangle=-45,
            height=450
        )

        st.plotly_chart(fig, use_container_width=True)

        if not phase_toplamlar.empty:
            st.markdown("### 📍 Phase Tamamlanma Durumu")
            st.dataframe(phase_toplamlar[["phase", "Planlanan", "Gerçekleşen", "Fark", "durum"]], use_container_width=True)

        if not df_naeron_eksik.empty:
            st.markdown("### ❗ Naeron'da olup planda olmayan görevler")
            st.dataframe(df_naeron_eksik[["Uçuş Tarihi 2", "Görev", "sure_str"]], use_container_width=True)
