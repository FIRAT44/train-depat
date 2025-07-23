import streamlit as st
import pandas as pd
import datetime, os

# Board renkleri ve ikonları (gerekirse kişiselleştir)
GROUP_COLORS = ["#0079BF", "#61BD4F", "#F2D600", "#FF9F1A", "#EB5A46", "#C377E0"]
GROUP_EMOJIS = ["🟦", "🟩", "🟨", "🟧", "🟥", "🟪"]

@st.cache_data
def load_data():
    df = pd.read_excel("checklist.xlsx")
    df.fillna('', inplace=True)
    return df

df = load_data()
gruplar = df["GRUP ADI"].unique()

# Style ayarları
st.set_page_config(layout="wide", page_title="Trello-Stil Basit Kanban Checklist")
st.markdown("""
    <style>
    .board-col {
        min-width: 340px;
        max-width: 410px;
        background: #212529;
        border-radius: 14px;
        margin: 0 14px 0 0;
        padding: 18px 8px 24px 8px;
        display: inline-block;
        vertical-align: top;
    }
    .board-header {
        font-size: 19px;
        font-weight: bold;
        color: #fff;
        background: #1f364d;
        border-radius: 10px;
        padding: 13px 8px 11px 13px;
        margin-bottom: 18px;
        letter-spacing: 1px;
        box-shadow: 0 2px 12px #003;
    }
    .kanban-card {
        background: #fff;
        color: #222;
        border-radius: 11px;
        margin-bottom: 16px;
        padding: 17px 17px 11px 17px;
        box-shadow: 0 1px 7px #0002;
        font-size: 15.6px;
        font-weight: 500;
        cursor: pointer;
        transition: box-shadow 0.2s;
        min-height: 36px;
        max-width: 370px;
    }
    .kanban-card:hover {
        box-shadow: 0 3px 14px #0079bf55;
    }
    .stRadio > div { flex-direction: row !important; gap: 16px; }
    </style>
""", unsafe_allow_html=True)

st.title("🟢 Trello-Stil Checklist Board (Sade)")
st.markdown("**Her grup bir sütun, her soru bir kart. Sadece başlık ve kısa açıklama, Trello görünümünde!**")

# State
if "board_answers" not in st.session_state:
    st.session_state.board_answers = {}

cols = st.columns(len(gruplar))
for idx, (col, grup) in enumerate(zip(cols, gruplar)):
    with col:
        color = GROUP_COLORS[idx % len(GROUP_COLORS)]
        emoji = GROUP_EMOJIS[idx % len(GROUP_EMOJIS)]
        st.markdown(
            f"<div class='board-header' style='background:{color}'>{emoji} {grup}</div>",
            unsafe_allow_html=True
        )

        sorular = df[df["GRUP ADI"] == grup]
        for i, row in sorular.iterrows():
            soru_id = f"{grup}-{row['SORU NUMARASI']}"
            ana_soru = str(row["Ana Soru"])
            # Soru başlığı kısaltılır (ilk 80 karakter, gerekirse...)
            kart_title = ana_soru.split("?")[0][:80] + ("..." if len(ana_soru) > 80 else "")
            st.markdown(
                f"<div class='kanban-card'><b>{row['Ana Soru Kodu']}</b><br>{kart_title}</div>",
                unsafe_allow_html=True
            )
            # Cevap için sade radio
            cevap = st.radio(
                "", ["Belirtilmedi", "Evet", "Hayır"],
                key=f"main_{soru_id}", horizontal=True, label_visibility="collapsed"
            )
            st.session_state.board_answers[soru_id] = {"Cevap": cevap}

def save_board(answers):
    if not os.path.exists("outputs"):
        os.makedirs("outputs")
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"outputs/trello_kanban_{now}.xlsx"
    rows = []
    for soru_id, data in answers.items():
        grup, soru_no = soru_id.split("-", 1)
        rows.append({
            "GRUP": grup,
            "SORU NUMARASI": soru_no,
            "CEVAP": data["Cevap"]
        })
    pd.DataFrame(rows).to_excel(file_name, index=False)
    return file_name

st.markdown("---")
if st.button("📥 Tüm Cevapları Excel'e Kaydet & İndir"):
    dosya = save_board(st.session_state.board_answers)
    with open(dosya, "rb") as file:
        st.download_button(
            label="Excel olarak indir",
            data=file,
            file_name=os.path.basename(dosya),
            mime="application/vnd.ms-excel"
        )
    st.success("Tüm kartlar kaydedildi!")

st.markdown("""
<div style='text-align:center;color:#aaa;margin-top:1.2em;'>
  <small>
    <b>Trello Board Stili Checklist</b> • FIRAT TANIR • 2025
  </small>
</div>
""", unsafe_allow_html=True)
