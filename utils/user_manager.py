import json
import os

JSON_PATH = "kullanicilar.json"

def kullanicilari_yukle():
    if not os.path.exists(JSON_PATH):
        return {}
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def kullanicilari_kaydet(veriler):
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(veriler, f, ensure_ascii=False, indent=2)
