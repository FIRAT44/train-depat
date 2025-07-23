import streamlit as st
import sqlite3
import pandas as pd
import json
import io
import streamlit.components.v1 as components
from datetime import datetime
import uuid
import icalendar
from utils.auth import login_required
login_required()
# 📅 Aşırı Gelişmiş Uçuş Planlama Sistemi
st.set_page_config(page_title="🛫 Uçuş Planlama ve Takvim", layout="wide")
st.title("🛫 Aşırı Gelişmiş Uçuş Planlama & Takvim")

# --- Veritabanı Hazırlığı ---
def init_db():
    conn = sqlite3.connect("sms_flightplan.db", check_same_thread=False)
    c = conn.cursor()
    # Aircraft tablosu
    c.execute("""
    CREATE TABLE IF NOT EXISTS aircraft (
        reg TEXT PRIMARY KEY,
        type TEXT,
        range_km INTEGER,
        base_airport TEXT
    )""")
    # Pilots tablosu
    c.execute("""
    CREATE TABLE IF NOT EXISTS pilots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE
    )""")
    # Routes tablosu
    c.execute("""
    CREATE TABLE IF NOT EXISTS route (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        origin TEXT,
        destination TEXT,
        distance_km INTEGER
    )""")
    # Schedule tablosu
    c.execute("""
    CREATE TABLE IF NOT EXISTS schedule (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        flight_no TEXT UNIQUE,
        reg TEXT,
        route_id INTEGER,
        dep_time TEXT,
        arr_time TEXT,
        date TEXT,
        pilot_id INTEGER
    )""")
    conn.commit()
    # Ensure status column exists in schedule
    try:
        c.execute("ALTER TABLE schedule ADD COLUMN status TEXT DEFAULT 'Scheduled'")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    return conn

conn = init_db()
cursor = conn.cursor()

# --- Sayfa Sekmeleri ---
tabs = st.tabs(["📋 Yönetim","📅 Takvim","📑 Liste","📥 Dışa Aktarma"])

# 1) Yönetim Sekmesi
with tabs[0]:
    st.subheader("📋 Filoyu, Pilotları ve Rotaları Yönet")
    col1, col2, col3 = st.columns(3)
    # Aircraft Yönetimi
    with col1:
        st.markdown("**✈️ Uçak Ekle / Düzenle**")
        ac_reg = st.text_input("Tescil", key="ac_reg")
        ac_type = st.text_input("Tip", key="ac_type")
        ac_range = st.number_input("Menzil (km)", min_value=100, max_value=20000, value=5000, key="ac_range")
        ac_base = st.text_input("Base Havalimanı (Kod)", key="ac_base")
        if st.button("Kaydet Uçak"):
            cursor.execute(
                "INSERT OR REPLACE INTO aircraft(reg,type,range_km,base_airport) VALUES(?,?,?,?)",
                (ac_reg, ac_type, ac_range, ac_base)
            )
            conn.commit()
            st.success(f"Uçak {ac_reg} kaydedildi.")
        df_air = pd.read_sql("SELECT * FROM aircraft", conn)
        st.data_editor(df_air, key="aircraft_table")
    # Pilot Yönetimi
    with col2:
        st.markdown("**👩‍✈️ Pilot Ekle / Düzenle**")
        new_pilot = st.text_input("Pilot Adı", key="pilot_name")
        if st.button("Kaydet Pilot") and new_pilot:
            cursor.execute(
                "INSERT OR IGNORE INTO pilots(name) VALUES(?)",
                (new_pilot,)
            )
            conn.commit()
            st.success(f"Pilot '{new_pilot}' eklendi.")
        df_pilot = pd.read_sql("SELECT * FROM pilots", conn)
        st.data_editor(df_pilot, key="pilot_table")
    # Rota Yönetimi
    with col3:
        st.markdown("**🛣️ Rota Ekle / Düzenle**")
        r_origin = st.text_input("Kalkış (Kod)", key="r_org")
        r_dest = st.text_input("Varış (Kod)", key="r_dst")
        r_dist = st.number_input("Mesafe (km)", min_value=10, max_value=20000, value=500, key="r_dist")
        if st.button("Kaydet Rota") and r_origin and r_dest:
            cursor.execute(
                "INSERT INTO route(origin,destination,distance_km) VALUES(?,?,?)",
                (r_origin, r_dest, r_dist)
            )
            conn.commit()
            st.success(f"Rota {r_origin} → {r_dest} kaydedildi.")
        df_route = pd.read_sql("SELECT id, origin||'→'||destination AS route, distance_km FROM route", conn)
        st.data_editor(df_route, key="route_table")

# 2) Takvim Sekmesi
with tabs[1]:
    st.subheader("📅 İnteraktif Uçuş Takvimi")
    df_sched = pd.read_sql_query(
        """
        SELECT s.id,
               flight_no || ' / ' || reg ||
               COALESCE(' - ' || p.name, '') AS title,
               date || 'T' || dep_time AS start,
               date || 'T' || arr_time AS end,
               COALESCE(status,'Scheduled') AS status
        FROM schedule s
        LEFT JOIN pilots p ON s.pilot_id = p.id
        ORDER BY date, dep_time
        """, conn)
    events = df_sched.to_dict(orient='records')
    events_json = json.dumps(events, default=str)
    calendar_html = f"""
    <link href='https://cdn.jsdelivr.net/npm/fullcalendar@5.11.3/main.min.css' rel='stylesheet'/>
    <script src='https://cdn.jsdelivr.net/npm/fullcalendar@5.11.3/main.min.js'></script>
    <div id='calendar'></div>
    <script>
      document.addEventListener('DOMContentLoaded', function() {{
        var calendar = new FullCalendar.Calendar(document.getElementById('calendar'), {{
          initialView: 'timeGridWeek', locale: 'tr', editable: true,
          headerToolbar: {{ left: 'prev,next today', center: 'title', right: 'timeGridWeek,timeGridDay,listWeek' }},
          events: {events_json},
          eventDrop: function(info) {{
            console.log('Dropped:', info.event.id, info.event.start);
          }},
          eventResize: function(info) {{
            console.log('Resized:', info.event.id, info.event.end);
          }}
        }});
        calendar.render();
      }});
    </script>
    <style>#calendar {{ max-width:100%; margin:0 auto; }}</style>
    """
    components.html(calendar_html, height=700)

# 3) Liste Sekmesi
with tabs[2]:
    st.subheader("📑 Uçuş Listesi & Filtreler")
    df_list = pd.read_sql("SELECT * FROM schedule", conn)
    cols = st.multiselect("Görünür Sütunlar", df_list.columns.tolist(), default=df_list.columns.tolist())
    df_filtered = df_list[cols].copy()
    df_filtered['date'] = pd.to_datetime(df_filtered['date'])
    st.dataframe(df_filtered, use_container_width=True)

# 4) Dışa Aktarma Sekmesi
with tabs[3]:
    st.subheader("📥 Dışa Aktarma ve Bildirimler")
    # iCal Export
    cal = icalendar.Calendar()
    cal.add('prodid', '-//FlightPlanCalendar//')
    for event in df_sched.to_dict(orient='records'):
        ev = icalendar.Event()
        ev.add('uid', str(uuid.uuid4()))
        ev.add('summary', event['title'])
        ev.add('dtstart', datetime.fromisoformat(event['start']))
        ev.add('dtend', datetime.fromisoformat(event['end']))
        cal.add_component(ev)
    buf = io.BytesIO(cal.to_ical())
    st.download_button(
        '📥 iCal İndir', buf, file_name='flightplan.ics', mime='text/calendar'
    )
    # Excel Export
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        pd.read_sql("SELECT * FROM schedule", conn).to_excel(writer, index=False, sheet_name='Schedule')
    buffer.seek(0)
    st.download_button(
        '📥 Excel Olarak İndir', buffer,
        file_name='flightplan.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    st.success('Dışa aktarma tamamlandı!')
