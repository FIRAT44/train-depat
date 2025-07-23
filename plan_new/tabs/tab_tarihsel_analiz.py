import pandas as pd
import streamlit as st

def tab_tarihsel_analiz(st, conn):
    st.subheader("📈 Tarihsel Uçuş Süre Analizi")

    query = "SELECT plan_tarihi, sure, gorev_tipi FROM ucus_planlari"
    df = pd.read_sql_query(query, conn, parse_dates=["plan_tarihi"])

    if df.empty:
        st.warning("Veri bulunamadı.")
        return

    # sure kolonunu saat cinsinden floata çevir
    df["sure_saat"] = pd.to_timedelta(df["sure"]).dt.total_seconds() / 3600

    gorev_tipleri = df["gorev_tipi"].dropna().unique().tolist()
    gorev_tipleri.sort()

    selected_tips = st.multiselect(
        "Gösterilecek Görev Tiplerini Seçin", 
        options=gorev_tipleri, 
        default=gorev_tipleri
    )

    # 1) Tüm Görev Tiplerinin Toplamı ("Total") - En Üste
    st.markdown("## 🔷 Total (Tüm Görev Tipleri)")
    df_gunluk_total = df.groupby("plan_tarihi")["sure_saat"].sum().reset_index()
    df_gunluk_total = df_gunluk_total.sort_values("plan_tarihi")

    st.line_chart(
        df_gunluk_total.set_index("plan_tarihi"),
        height=300,
        use_container_width=True
    )
    st.dataframe(df_gunluk_total, use_container_width=True)

    # 2) Seçilen Görev Tiplerinin Alt Alta Ayrı Gösterimi
    if not selected_tips:
        st.info("En az bir görev tipi seçmelisiniz.")
        return

    for tip in selected_tips:
        st.markdown(f"---\n## {tip}")
        df_tip = df[df["gorev_tipi"] == tip]
        df_gunluk = df_tip.groupby("plan_tarihi")["sure_saat"].sum().reset_index()
        df_gunluk = df_gunluk.sort_values("plan_tarihi")

        st.line_chart(
            df_gunluk.set_index("plan_tarihi"),
            height=250,
            use_container_width=True
        )
        st.dataframe(df_gunluk, use_container_width=True)
