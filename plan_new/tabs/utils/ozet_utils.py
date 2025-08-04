import re
import pandas as pd
import sqlite3
from datetime import datetime

# --- Yardımcı fonksiyonlar ---
def to_saat(sure_str):
    try:
        if pd.isna(sure_str) or sure_str == "":
            return 0
        parts = [int(p) for p in sure_str.split(":")]
        return parts[0] + parts[1]/60 + (parts[2] if len(parts)>2 else 0)/3600
    except:
        return 0

def format_sure(hours_float):
    neg = hours_float < 0
    h_abs = abs(hours_float)
    h = int(h_abs)
    m = int(round((h_abs - h) * 60))
    sign = "-" if neg else ""
    return f"{sign}{h:02}:{m:02}"

def normalize_task(name):
    """Görev adındaki tüm noktalama/boşluk karakterlerini kaldırıp uppercase yapar."""
    return re.sub(r"[^\w]", "", str(name)).upper()

def ozet_panel_verisi_hazirla(secilen_kod, conn, naeron_db_path="naeron_kayitlari.db"):
    # --- 1) Plan verisi ---
    df = pd.read_sql_query("SELECT * FROM ucus_planlari", conn, parse_dates=["plan_tarihi"])
    df["ogrenci_kodu"] = df["ogrenci"].str.split("-").str[0].str.strip()
    df_ogrenci = df[df["ogrenci_kodu"] == secilen_kod].sort_values("plan_tarihi").copy()
    if df_ogrenci.empty:
        return pd.DataFrame(), pd.DataFrame(), 0, 0, 0, pd.DataFrame()

    # --- 2) Naeron verisini OKU ve birleştir ---
    conn_naeron = sqlite3.connect(naeron_db_path)
    df_naeron_raw = pd.read_sql_query("SELECT * FROM naeron_ucuslar", conn_naeron)
    conn_naeron.close()

    # 2.a) MCC çoklu öğrenci ayrıştırma
    def mcc_coklu_ogrenci(df_naeron):
        mask = df_naeron["Görev"].astype(str).str.upper().str.startswith("MCC")
        df_mcc = df_naeron[mask].copy()
        def extract_ogrenciler(pilot_str):
            return re.findall(r"\d{3}[A-Z]{2}", str(pilot_str).upper())
        rows = []
        for _, row in df_mcc.iterrows():
            for kod in extract_ogrenciler(row["Öğrenci Pilot"]):
                new_row = row.copy()
                new_row["ogrenci_kodu"] = kod
                rows.append(new_row)
        return pd.DataFrame(rows)

    df_naeron_mcc = mcc_coklu_ogrenci(df_naeron_raw)

    # 2.b) MCC dışı öğrenci atama
    mask_mcc = df_naeron_raw["Görev"].astype(str).str.upper().str.startswith("MCC")
    df_naeron_other = df_naeron_raw[~mask_mcc].copy()
    df_naeron_other["ogrenci_kodu"] = (
        df_naeron_other["Öğrenci Pilot"].str.split("-").str[0].str.strip()
    )

    # 2.c) Birleştir ve normalize et
    df_naeron_all = pd.concat([df_naeron_mcc, df_naeron_other], ignore_index=True)
    df_naeron_all["gorev_norm"] = df_naeron_all["Görev"].apply(normalize_task)

    # 2.d) Sadece seçilen öğrenci
    df_naeron = df_naeron_all[df_naeron_all["ogrenci_kodu"] == secilen_kod].copy()
    # Eğer PIC ayrımı gerekiyorsa, mesela:
    # df_naeron = df_naeron[df_naeron["Role"] == "PIC"]

    # --- 3) Görev bazlı eşleşen block time toplama ---
    def eslesen_block_sure(gorev_ismi):
        norm = normalize_task(gorev_ismi)
        eş = df_naeron[df_naeron["gorev_norm"] == norm]
        return eş["Block Time"].apply(to_saat).sum() if not eş.empty else 0

    # --- 4) Planlanan, gerçekleşen, fark ---
    df_ogrenci["planlanan_saat_ondalik"] = df_ogrenci["sure"].apply(to_saat)
    df_ogrenci["gerceklesen_saat_ondalik"] = df_ogrenci["gorev_ismi"].apply(eslesen_block_sure)
    df_ogrenci["fark_saat_ondalik"] = (
        df_ogrenci["gerceklesen_saat_ondalik"] - df_ogrenci["planlanan_saat_ondalik"]
    )

    df_ogrenci["Planlanan"]   = df_ogrenci["planlanan_saat_ondalik"].apply(format_sure)
    df_ogrenci["Gerçekleşen"] = df_ogrenci["gerceklesen_saat_ondalik"].apply(format_sure)
    df_ogrenci["Fark"]        = df_ogrenci["fark_saat_ondalik"].apply(format_sure)

    # --- 5) Durum ataması ---
    def ilk_durum(row):
        if row["Planlanan"] == "00:00":
            return "🟡 Teorik Ders"
        elif row["fark_saat_ondalik"] >= 0:
            return "🟢 Uçuş Yapıldı"
        elif row["Gerçekleşen"] != "00:00":
            return "🟣 Eksik Uçuş Saati"
        else:
            return "🔴 Eksik"
    df_ogrenci["durum"] = df_ogrenci.apply(ilk_durum, axis=1)

    # Eksik - Beklemede kontrolü
    for i in range(len(df_ogrenci)):
        if df_ogrenci.iloc[i]["durum"] == "🔴 Eksik" and df_ogrenci.iloc[i]["Gerçekleşen"] == "00:00":
            sonraki = df_ogrenci.iloc[i+1:i+10]
            if (sonraki["durum"].str.contains("🟢 Uçuş Yapıldı")).sum() >= 3:
                df_ogrenci.iat[i, df_ogrenci.columns.get_loc("durum")] = "🟤 Eksik - Beklemede"

    # --- 6) Phase kontrolü ---
    if "phase" in df_ogrenci.columns:
        df_ogrenci["phase"] = df_ogrenci["phase"].astype(str).str.strip()
        phase_toplamlar = df_ogrenci[df_ogrenci["phase"].notna()].groupby("phase").agg({
            "planlanan_saat_ondalik": "sum",
            "gerceklesen_saat_ondalik": "sum"
        }).reset_index()
        phase_toplamlar["fark"] = (
            phase_toplamlar["gerceklesen_saat_ondalik"] - phase_toplamlar["planlanan_saat_ondalik"]
        )
        tamamlanan = phase_toplamlar[phase_toplamlar["fark"] >= 0]["phase"].tolist()

        def guncel_durum(row):
            if (row.get("phase") in tamamlanan
                and row["durum"] in ["🟣 Eksik Uçuş Saati","🔴 Eksik","🟤 Eksik - Beklemede"]
            ):
                return ("⚪ Phase Tamamlandı - Uçuş Yapılmadı"
                        if row["Gerçekleşen"]=="00:00"
                        else "🔷 Phase Tamamlandı - 🟣 Eksik Uçuş Saati")
            return row["durum"]

        df_ogrenci["durum"] = df_ogrenci.apply(guncel_durum, axis=1)

        phase_toplamlar["Planlanan"]  = phase_toplamlar["planlanan_saat_ondalik"].apply(format_sure)
        phase_toplamlar["Gerçekleşen"] = phase_toplamlar["gerceklesen_saat_ondalik"].apply(format_sure)
        phase_toplamlar["Fark"]        = phase_toplamlar["fark"].apply(format_sure)
        phase_toplamlar["durum"]       = phase_toplamlar["fark"].apply(
            lambda x: "✅ Tamamlandı" if x >= 0 else "❌ Tamamlanmadı"
        )
    else:
        phase_toplamlar = pd.DataFrame()

    # --- 7) Genel toplamlar ve planda olmayan Naeron görevleri ---
    toplam_plan  = df_ogrenci["planlanan_saat_ondalik"].sum()
    toplam_gercek= df_ogrenci["gerceklesen_saat_ondalik"].sum()
    toplam_fark  = toplam_gercek - toplam_plan

    plan_gorevler = set(df_ogrenci["gorev_ismi"].dropna().str.strip())
    df_naeron_eksik = df_naeron[df_naeron["Görev"].isin(plan_gorevler)==False].copy()
    df_naeron_eksik["sure_str"] = df_naeron_eksik["Block Time"].apply(lambda x: format_sure(to_saat(x)))

    return df_ogrenci, phase_toplamlar, toplam_plan, toplam_gercek, toplam_fark, df_naeron_eksik
