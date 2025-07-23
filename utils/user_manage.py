import json
import os

def kullanicilari_yukle(json_path="kullanicilar.json"):
    if not os.path.exists(json_path):
        return {}
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)




def kullanici_ekle(ad, sifre, roller, json_path="kullanicilar.json"):
    veriler = kullanicilari_yukle(json_path)
    veriler[ad] = {"sifre": sifre, "roller": roller}
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(veriler, f, ensure_ascii=False, indent=2)