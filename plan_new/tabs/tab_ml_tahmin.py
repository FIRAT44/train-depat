# tabs/tab_ml_tahmin.py
import pandas as pd
import streamlit as st
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import numpy as np

def tab_ml_tahmin(st, conn):
    st.subheader("📈 ML ile Tahmini Görev Süresi Analizi")

    df = pd.read_sql_query("SELECT * FROM ucus_planlari", conn, parse_dates=["plan_tarihi"])
    if df.empty:
        st.warning("Veri bulunamadı.")
        return

    # sure_saat hesapla
    df["sure_saat"] = pd.to_timedelta(df["sure"]).dt.total_seconds() / 3600
    df = df.dropna(subset=["ogrenci", "sure_saat", "gorev_tipi"])

    # Kodlayıcılar
    df["ogrenci_encoded"] = df["ogrenci"].astype("category").cat.codes
    df["gorev_encoded"] = df["gorev_tipi"].astype("category").cat.codes
    df["tarih_ordinal"] = df["plan_tarihi"].map(pd.Timestamp.toordinal)

    X = df[["ogrenci_encoded", "gorev_encoded", "tarih_ordinal"]]
    y = df["sure_saat"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = LinearRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    st.markdown(f"### 🔍 Ortalama Hata (MSE): `{mse:.2f}` saat²")

    ogrenci_sec = st.selectbox("Öğrenci seçin", df["ogrenci"].unique(), key="tahmin_ogrenci")
    gorev_sec = st.selectbox("Görev Tipi seçin", df["gorev_tipi"].unique(), key="tahmin_gorev")
    tarih_sec = st.date_input("Planlanan Tarih", key="tahmin_tarih")

    if st.button("🧠 Tahmini Süreyi Hesapla", key="tahmin_btn"):
        encoded_ogrenci = df[df["ogrenci"] == ogrenci_sec]["ogrenci_encoded"].iloc[0]
        encoded_gorev = df[df["gorev_tipi"] == gorev_sec]["gorev_encoded"].iloc[0]
        tarih_ord = pd.to_datetime(tarih_sec).toordinal()

        input_data = np.array([[encoded_ogrenci, encoded_gorev, tarih_ord]])
        tahmin = model.predict(input_data)[0]
        st.success(f"🕒 Bu görev için tahmini süre: {tahmin:.2f} saat")
