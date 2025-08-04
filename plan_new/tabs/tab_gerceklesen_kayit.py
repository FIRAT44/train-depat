# tab_gerceklesen_kayit.py
import pandas as pd
import streamlit as st
import sqlite3
from datetime import datetime,timedelta
from tabs.plan_naeron_eslestirme_paneli import plan_naeron_eslestirme_ve_elle_duzeltme
import re
import io

def tab_gerceklesen_kayit(st, conn):
    st.subheader("🛬 Gerçekleşen Uçuş Süresi Girişi")

    sekme1, sekme2 = st.tabs(["🛬 Gerçekleşen Uçuşlar - 📂 Naeron Kayıtları", "📊 Özet Panel"])

    with sekme1:
        plan_naeron_eslestirme_ve_elle_duzeltme(st)

    with sekme2:
        st.subheader("📊 Plan - Gerçekleşme Özeti")
        st.markdown("""
            **Durum Açıklamaları:**
            - 🟢 Uçuş Yapıldı: Planlanan görev başarıyla uçulmuş.
            - 🟣 Eksik Uçuş Saati: Uçulmuş ama süre yetersiz.
            - 🔴 Eksik: Planlanan ama hiç uçulmamış.
            - 🟤 Eksik - Beklemede: Takip eden uçuşlar gerçekleşmiş ama bu görev atlanmış.
            - 🟡 Teorik Ders: Sadece teorik plan.
            - ⚪ / 🔷: Phase başarıyla tamamlanmış.
            """)
        # Plan verisini çek
        df = pd.read_sql_query("SELECT * FROM ucus_planlari", conn, parse_dates=["plan_tarihi"])
        if df.empty:
            st.warning("Veri bulunamadı.")
            return

        # Öğrenci kodu
        df["ogrenci_kodu"] = df["ogrenci"].str.split("-").str[0].str.strip()
        secilen_kod = st.selectbox(
            "Öğrenci kodunu seçin",
            df["ogrenci_kodu"].dropna().unique().tolist(),
            key="ozet_ogrenci"
        )
        df_ogrenci = df[df["ogrenci_kodu"] == secilen_kod].sort_values("plan_tarihi")
        

        # Naeron verisini çek
        try:
            conn_naeron = sqlite3.connect("naeron_kayitlari.db")
            df_naeron_raw = pd.read_sql_query("SELECT * FROM naeron_ucuslar", conn_naeron)
            conn_naeron.close()

            # MCC çoklu öğrenci ayrıştırma fonksiyonu
            # --- MCC Çoklu Öğrenci Ayrıştırma (Long Format) ---
            def mcc_coklu_ogrenci(df_naeron):
                mask = df_naeron["Görev"].astype(str).str.upper().str.startswith("MCC")
                df_mcc = df_naeron[mask].copy()
                def extract_ogrenciler(pilot_str):
                    return re.findall(r"\d{3}[A-Z]{2}", str(pilot_str).upper())

                rows = []
                for _, row in df_mcc.iterrows():
                    kodlar = extract_ogrenciler(row["Öğrenci Pilot"])
                    for kod in kodlar:
                        new_row = row.copy()
                        new_row["ogrenci_kodu"] = kod
                        rows.append(new_row)
                return pd.DataFrame(rows)

            df_naeron_mcc = mcc_coklu_ogrenci(df_naeron_raw)

            # Tek öğrenci görevleri
            mask_mcc = df_naeron_raw["Görev"].astype(str).str.upper().str.startswith("MCC")
            df_naeron_other = df_naeron_raw[~mask_mcc].copy()
            df_naeron_other["ogrenci_kodu"] = (
                df_naeron_other["Öğrenci Pilot"].str.split("-").str[0].str.strip()
            )

            # Birleştir ve tüm veride long format
            df_naeron_all = pd.concat([df_naeron_mcc, df_naeron_other], ignore_index=True)

            # Görev isimleri normalize etme fonksiyonu
            def normalize_task(name):
                return re.sub(r"[\s\-]+", "", str(name)).upper()

            df_naeron_all["gorev_norm"] = df_naeron_all["Görev"].apply(normalize_task)

            # Seçilen öğrenciye göre filtrele
            df_naeron = df_naeron_all[df_naeron_all["ogrenci_kodu"] == secilen_kod].copy()

            # Yardımcı dönüştürücüler
            def to_saat(sure_str):
                try:
                    if pd.isna(sure_str) or sure_str == "":
                        return 0
                    parts = [int(p) for p in sure_str.split(":")]
                    # saat + dakika/60 + saniye/3600
                    return parts[0] + parts[1]/60 + (parts[2] if len(parts)>2 else 0)/3600
                except:
                    return 0

            def format_sure(hours_float):
                """Ondalık saat → 'HH:MM' formatına dönüştürür."""
                neg = hours_float < 0
                h_abs = abs(hours_float)
                h = int(h_abs)
                m = int(round((h_abs - h) * 60))
                sign = "-" if neg else ""
                return f"{sign}{h:02}:{m:02}"

            # Görev isimlerini gruplandır burayı PIC kımı için farklı yapman gerekiyor.
            def eslesen_block_sure(gorev_ismi):
                eş = df_naeron[df_naeron["Görev"] == gorev_ismi]
                if not eş.empty:
                    return eş["Block Time"].apply(to_saat).sum()
                return 0

            # Planlanan / gerçekleşen / fark (ondalık)
            df_ogrenci["planlanan_saat_ondalik"] = df_ogrenci["sure"].apply(to_saat)
            df_ogrenci["gerceklesen_saat_ondalik"] = df_ogrenci["gorev_ismi"].apply(eslesen_block_sure)
            df_ogrenci["fark_saat_ondalik"] = df_ogrenci["gerceklesen_saat_ondalik"] - df_ogrenci["planlanan_saat_ondalik"]
            df_ogrenci["durum"] = df_ogrenci["fark_saat_ondalik"].apply(lambda x: "🟢 Uçuş Yapıldı" if x >= 0 else "🔴 Eksik")





            # Ondalık değerleri HH:MM metnine çevir
            df_ogrenci["Planlanan"]    = df_ogrenci["planlanan_saat_ondalik"].apply(format_sure)
            df_ogrenci["Gerçekleşen"]  = df_ogrenci["gerceklesen_saat_ondalik"].apply(format_sure)
            df_ogrenci["Fark"]         = df_ogrenci["fark_saat_ondalik"].apply(format_sure)

            # Yeni: Durum hesaplama
            df_ogrenci["durum"] = df_ogrenci.apply(lambda row: 
                "🟡 Teorik Ders"
                    if row["Planlanan"] == "00:00"
                else "🟢 Uçuş Yapıldı"
                    if row["fark_saat_ondalik"] >= 0
                else "🟣 Eksik Uçuş Saati"
                    if (row["Planlanan"] != "00:00"
                        and row["Gerçekleşen"] != "00:00"
                        and row["fark_saat_ondalik"] < 0)
                else "🔴 Eksik"
            , axis=1)

            
            # Eksik - Beklemede kontrolü (en az 3 uçuş yapıldı ve gerçekleşen süre 00:00 ise)
            for i in range(len(df_ogrenci)):
                mevcut_durum = df_ogrenci.iloc[i]["durum"]
                mevcut_gerceklesen = df_ogrenci.iloc[i]["Gerçekleşen"]

                if mevcut_durum == "🔴 Eksik" and mevcut_gerceklesen == "00:00":
                    sonraki_satirlar = df_ogrenci.iloc[i+1:i+10]  # Güvenli aralık
                    if not sonraki_satirlar.empty:
                        ucus_yapildi_sayisi = (sonraki_satirlar["durum"].str.contains("🟢 Uçuş Yapıldı")).sum()
                        if ucus_yapildi_sayisi >= 3:
                            df_ogrenci.iat[i, df_ogrenci.columns.get_loc("durum")] = "🟤 Eksik - Beklemede"




           # Yeni: ☑️ Phase Tamamlandı

            if "phase" in df_ogrenci.columns:
                tamamlanan_phaseler_df = df_ogrenci[df_ogrenci["phase"].notna()].copy()
                tamamlanan_phaseler_df["phase"] = tamamlanan_phaseler_df["phase"].astype(str).str.strip()

                phase_toplamlar = tamamlanan_phaseler_df.groupby("phase").agg({
                    "planlanan_saat_ondalik": "sum",
                    "gerceklesen_saat_ondalik": "sum"
                }).reset_index()

                phase_toplamlar["fark"] = phase_toplamlar["gerceklesen_saat_ondalik"] - phase_toplamlar["planlanan_saat_ondalik"]
                tamamlanan_phaseler = phase_toplamlar[phase_toplamlar["fark"] >= 0]["phase"].tolist()

                def guncel_durum(row):
                    if row.get("phase") in tamamlanan_phaseler and row["durum"] in ["🟣 Eksik Uçuş Saati", "🔴 Eksik","🟤 Eksik - Beklemede"]:
                        if row["Gerçekleşen"] == "00:00":
                            return "⚪ Phase Tamamlandı - Uçuş Yapılmadı"
                        else:
                            return "🔷 Phase Tamamlandı - 🟣 Eksik Uçuş Saati"
                    return row["durum"]

                df_ogrenci["durum"] = df_ogrenci.apply(guncel_durum, axis=1)





            # Tabloyu göster
            st.markdown("### 📝 Görev Bazlı Gerçekleşme Tablosu")
            st.dataframe(
                df_ogrenci[["plan_tarihi", "gorev_ismi", "Planlanan", "Gerçekleşen", "Fark", "durum"]],
                use_container_width=True
            )

            # Toplamları hesapla ve HH:MM olarak formatla
            toplam_plan    = df_ogrenci["planlanan_saat_ondalik"].sum()
            toplam_gercek  = df_ogrenci["gerceklesen_saat_ondalik"].sum()
            toplam_fark    = toplam_gercek - toplam_plan

            st.markdown("---")
            st.metric("📅 Toplam Planlanan Süre",   format_sure(toplam_plan))
            st.metric("✅ Toplam Gerçekleşen Süre", format_sure(toplam_gercek))
            st.metric("⚠️ Toplam Fark",             format_sure(toplam_fark))


            # Seçilen öğrenci için planla eşleşmeyen Naeron görevlerini göster
            st.markdown("---")
            st.markdown("### ❗ Bu Öğrencinin Planla Eşleşmeyen Naeron Görevleri")
            plan_gorevler = set(df_ogrenci["gorev_ismi"].dropna().str.strip())
            df_naeron_eksik = df_naeron[~df_naeron["Görev"].isin(plan_gorevler)].copy()

            if not df_naeron_eksik.empty:
                def format_str_sure(sure_str):
                    try:
                        return format_sure(to_saat(sure_str))
                    except:
                        return ""
                df_naeron_eksik["sure_str"] = df_naeron_eksik["Block Time"].apply(format_str_sure)
                st.dataframe(df_naeron_eksik[["Uçuş Tarihi 2", "Görev", "sure_str", "Öğrenci Pilot"]], use_container_width=True)
            else:
                st.info("Bu öğrenci için tüm Naeron görevleri plana işlenmiş görünüyor.")
            # Toplam süre hesapla
            toplam_eksik_saat = df_naeron_eksik["Block Time"].apply(to_saat).sum()
            st.metric("🕒 Toplam Eşleşmeyen Naeron Süresi", format_sure(toplam_eksik_saat))
            
            
            # --- PHASE BAZLI ÖZET ---
            if "phase" in df_ogrenci.columns:
                st.markdown("---")
                st.markdown("### 📦 Phase Bazlı Plan - Gerçekleşme Özeti")

                df_phase = df_ogrenci[df_ogrenci["phase"].notna()].copy()
                df_phase["phase"] = df_phase["phase"].astype(str).str.strip()

                phase_ozet = df_phase.groupby("phase").agg({
                    "planlanan_saat_ondalik": "sum",
                    "gerceklesen_saat_ondalik": "sum"
                }).reset_index()

                phase_ozet["fark"] = phase_ozet["gerceklesen_saat_ondalik"] - phase_ozet["planlanan_saat_ondalik"]
                phase_ozet["durum"] = phase_ozet["fark"].apply(lambda x: "✅ Tamamlandı" if x >= 0 else "❌ Tamamlanmadı")

                phase_ozet["Planlanan"] = phase_ozet["planlanan_saat_ondalik"].apply(format_sure)
                phase_ozet["Gerçekleşen"] = phase_ozet["gerceklesen_saat_ondalik"].apply(format_sure)
                phase_ozet["Fark"] = phase_ozet["fark"].apply(format_sure)

                st.dataframe(
                    phase_ozet[["phase", "Planlanan", "Gerçekleşen", "Fark", "durum"]]
                    .rename(columns={"phase": "Phase"}),
                    use_container_width=True
                )
            # --- 📤 Tüm Öğrencileri Döneme Göre Toplu Excel ile İndir ---
            st.markdown("---")
            st.markdown("### 📥 Tüm Öğrencilerin Plan - Gerçekleşme Özeti (Excel)")

            donemler = pd.read_sql_query("SELECT DISTINCT donem FROM ucus_planlari", conn)["donem"].dropna().unique().tolist()
            donem_secimi = st.selectbox("📆 Dönemi Seçiniz", options=donemler, key="excel_donem_secimi")

            if st.button("📥 Excel Olarak İndir (Toplu Öğrenci Özeti)"):

                df_all = pd.read_sql_query("SELECT * FROM ucus_planlari", conn, parse_dates=["plan_tarihi"])
                df_all["ogrenci_kodu"] = df_all["ogrenci"].str.split("-").str[0].str.strip()
                df_all = df_all[df_all["donem"] == donem_secimi]

                conn_naeron = sqlite3.connect("naeron_kayitlari.db")
                df_naeron_raw = pd.read_sql_query("SELECT * FROM naeron_ucuslar", conn_naeron)
                conn_naeron.close()

                # MCC ayrıştırması
                def mcc_coklu(df):
                    mask = df["Görev"].astype(str).str.upper().str.startswith("MCC")
                    df_mcc = df[mask].copy()
                    def extract_ogrenciler(pilot_str):
                        return re.findall(r"\d{3}[A-Z]{2}", str(pilot_str).upper())
                    rows = []
                    for _, row in df_mcc.iterrows():
                        for kod in extract_ogrenciler(row["Öğrenci Pilot"]):
                            r = row.copy()
                            r["ogrenci_kodu"] = kod
                            rows.append(r)
                    return pd.DataFrame(rows)

                df_mcc = mcc_coklu(df_naeron_raw)
                df_other = df_naeron_raw[~df_naeron_raw["Görev"].astype(str).str.upper().str.startswith("MCC")].copy()
                df_other["ogrenci_kodu"] = df_other["Öğrenci Pilot"].str.split("-").str[0].str.strip()
                df_naeron_all = pd.concat([df_mcc, df_other], ignore_index=True)

                df_naeron_all["gorev_norm"] = df_naeron_all["Görev"].apply(lambda x: re.sub(r"[\s\-]+", "", str(x)).upper())

                def to_saat(s):
                    try:
                        if pd.isna(s) or s == "":
                            return 0
                        parts = [int(p) for p in str(s).split(":")]
                        return parts[0] + parts[1]/60 + (parts[2] if len(parts)>2 else 0)/3600
                    except:
                        return 0

                def format_sure(h):
                    neg = h < 0
                    h_abs = abs(h)
                    return f"{'-' if neg else ''}{int(h_abs):02}:{int(round((h_abs - int(h_abs)) * 60)):02}"

                # Export işlemi
                import io
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                    for kod in df_all["ogrenci_kodu"].unique():
                        df_o = df_all[df_all["ogrenci_kodu"] == kod].copy()
                        df_n = df_naeron_all[df_naeron_all["ogrenci_kodu"] == kod].copy()

                        def eslesen_block(gorev):
                            return df_n[df_n["Görev"] == gorev]["Block Time"].apply(to_saat).sum()

                        df_o["planlanan_saat_ondalik"] = df_o["sure"].apply(to_saat)
                        df_o["gerceklesen_saat_ondalik"] = df_o["gorev_ismi"].apply(eslesen_block)
                        df_o["fark_saat_ondalik"] = df_o["gerceklesen_saat_ondalik"] - df_o["planlanan_saat_ondalik"]
                        df_o["Planlanan"] = df_o["planlanan_saat_ondalik"].apply(format_sure)
                        df_o["Gerçekleşen"] = df_o["gerceklesen_saat_ondalik"].apply(format_sure)

                        def durum(row):
                            if row["Planlanan"] == "00:00":
                                return "🟡 Teorik Ders"
                            elif row["fark_saat_ondalik"] >= 0:
                                return "🟢 Uçuş Yapıldı"
                            elif row["Gerçekleşen"] != "00:00":
                                return "🟣 Eksik Uçuş Saati"
                            else:
                                return "🔴 Eksik"
                        df_o["durum"] = df_o.apply(durum, axis=1)

                        # Phase tamamlanmışsa düzelt
                        if "phase" in df_o.columns:
                            df_o["phase"] = df_o["phase"].astype(str).str.strip()
                            ph_sum = df_o.groupby("phase").agg({
                                "planlanan_saat_ondalik":"sum", "gerceklesen_saat_ondalik":"sum"
                            }).reset_index()
                            ph_sum["fark"] = ph_sum["gerceklesen_saat_ondalik"] - ph_sum["planlanan_saat_ondalik"]
                            tamam = ph_sum[ph_sum["fark"] >= 0]["phase"].tolist()

                            def phase_durum(row):
                                if row.get("phase") in tamam and row["durum"] in ["🟣 Eksik Uçuş Saati","🔴 Eksik"]:
                                    if row["Gerçekleşen"] == "00:00":
                                        return "⚪ Phase Tamamlandı - Uçuş Yapılmadı"
                                    return "🔷 Phase Tamamlandı - 🟣 Eksik Uçuş Saati"
                                return row["durum"]

                            df_o["durum"] = df_o.apply(phase_durum, axis=1)

                        export = df_o[["plan_tarihi", "gorev_ismi", "Planlanan", "Gerçekleşen", "durum"]].copy()
                        export.to_excel(writer, sheet_name=str(kod)[:31], index=False)

                output.seek(0)
                st.download_button(
                    label="📁 Excel Dosyasını İndir",
                    data=output,
                    file_name=f"{donem_secimi}_tum_ogrenciler_ozet.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )


        except Exception as e:
            st.error(f"Naeron verisi alınamadı: {e}")

    
    


    



        



def ogrenci_bazli_revize_panel_basit(conn):
    st.subheader("📌 Öğrenci Bazlı Revize Paneli")

    bugun = pd.to_datetime(datetime.today().date())
    df = pd.read_sql_query("SELECT * FROM ucus_planlari", conn, parse_dates=["plan_tarihi"])
    if df.empty:
        st.warning("Veri bulunamadı.")
        return

    df["ogrenci_kodu"] = df["ogrenci"].str.split("-").str[0].str.strip()

    def to_saat(sure_str):
        try:
            if pd.isna(sure_str) or sure_str == "":
                return 0
            if isinstance(sure_str, str):
                parts = [int(p) for p in sure_str.split(":")]
                return parts[0] + parts[1] / 60 + (parts[2] if len(parts) > 2 else 0) / 3600
            return float(sure_str)
        except:
            return 0

    df["planlanan_saat"] = df["sure"].apply(to_saat)
    df["gerceklesen_saat"] = df["gerceklesen_sure"].apply(to_saat)
    df["fark_saat"] = df["gerceklesen_saat"] - df["planlanan_saat"]

    ogrenci_listesi = df["ogrenci"].dropna().unique().tolist()

    for ogrenci in ogrenci_listesi:
        df_o = df[df["ogrenci"] == ogrenci].sort_values("plan_tarihi").copy()
        revize_adaylari = df_o[(df_o["plan_tarihi"] < bugun) & (df_o["fark_saat"] < 0)]
        if revize_adaylari.empty:
            continue

        ilk_revize_index = revize_adaylari.index[0]
        ilk_gorev = df_o.loc[ilk_revize_index, "gorev_ismi"]
        ilk_tarih = df_o.loc[ilk_revize_index, "plan_tarihi"]

        st.markdown("---")
        st.markdown(f"👤 **{ogrenci}** — Revize Edilecek İlk Görev: **{ilk_gorev}** ({ilk_tarih.date()})")

        varsayilan_tarih = bugun + timedelta(days=1)
        yeni_tarih = st.date_input(f"Yeni tarih seçin ({ogrenci})", value=varsayilan_tarih, key=f"yeni_{ogrenci}")

        if st.button("✅ Revize Et", key=f"btn_{ogrenci}"):
            fark = (yeni_tarih - ilk_tarih.date()).days
            if fark <= 0:
                st.warning("Seçilen tarih mevcut tarih ile aynı ya da daha erken.")
                continue

            revize_edilen = 0
            for idx in df_o.index:
                if idx >= ilk_revize_index and df_o.at[idx, "fark_saat"] < 0:
                    eski = df_o.at[idx, "plan_tarihi"]
                    yeni = eski + timedelta(days=fark)
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE ucus_planlari SET plan_tarihi = ?
                        WHERE ogrenci = ? AND gorev_ismi = ?
                    """, (yeni.strftime("%Y-%m-%d"), ogrenci, df_o.at[idx, "gorev_ismi"]))

                    # ✅ Log tablosuna yaz
                    cursor.execute("""
                        INSERT INTO revize_log (ogrenci, gorev_ismi, eski_tarih, yeni_tarih, revize_tarihi)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        ogrenci,
                        df_o.at[idx, "gorev_ismi"],
                        eski.strftime("%Y-%m-%d"),
                        yeni.strftime("%Y-%m-%d"),
                        datetime.today().strftime("%Y-%m-%d")
                    ))
                    revize_edilen += 1
            conn.commit()
            st.success(f"{ogrenci} için {revize_edilen} görev başarıyla revize edildi.")
