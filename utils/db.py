import sqlite3

DB_PATH = "questions.db"

def db_baglanti():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS konular (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ad TEXT UNIQUE NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            konu TEXT,
            zorluk TEXT,
            soru_metni TEXT,
            secenek_a TEXT,
            secenek_b TEXT,
            secenek_c TEXT,
            secenek_d TEXT,
            dogru_cevap TEXT,
            resim_yolu TEXT
        )
    """)
    conn.commit()
    return conn

def konu_ekle(konu):
    conn = db_baglanti()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO konular (ad) VALUES (?)", (konu,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()

def konu_listele():
    conn = db_baglanti()
    cursor = conn.cursor()
    cursor.execute("SELECT ad FROM konular")
    sonuc = [row[0] for row in cursor.fetchall()]
    conn.close()
    return sonuc if sonuc else ["METAR", "TAF", "Airmanship", "Hava Hukuku", "Uçuş Performansı"]

def soru_sil(soru_id):
    conn = db_baglanti()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM questions WHERE id = ?", (soru_id,))
    conn.commit()
    conn.close()

def konu_listele():
    conn = db_baglanti()
    cursor = conn.cursor()
    cursor.execute("SELECT ad FROM konular")
    sonuc = [row[0] for row in cursor.fetchall()]
    conn.close()
    return sonuc if sonuc else ["METAR", "TAF", "Airmanship", "Hava Hukuku", "Uçuş Performansı"]


def db_baglanti():
    conn = sqlite3.connect("questions.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS konular (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ad TEXT UNIQUE
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            konu TEXT,
            zorluk TEXT,
            soru_metni TEXT,
            secenek_a TEXT,
            secenek_b TEXT,
            secenek_c TEXT,
            secenek_d TEXT,
            dogru_cevap TEXT,
            resim_yolu TEXT
        )
    """)
    # --- Arşiv tablosu ---
    conn.execute("""
        CREATE TABLE IF NOT EXISTS arsiv_sorular (
            id INTEGER PRIMARY KEY,
            konu TEXT,
            zorluk TEXT,
            soru_metni TEXT,
            secenek_a TEXT,
            secenek_b TEXT,
            secenek_c TEXT,
            secenek_d TEXT,
            dogru_cevap TEXT,
            resim_yolu TEXT,
            arsiv_tarihi TEXT
        )
    """)
    return conn
