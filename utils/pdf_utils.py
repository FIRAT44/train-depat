from fpdf import FPDF
import os

FONT_PATH = "fonts/DejaVuSans.ttf"

class SinavPDF(FPDF):
    def __init__(self, title, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = title
        self.add_font("DejaVu", "", FONT_PATH, uni=True)
        self.add_font("DejaVu", "B", FONT_PATH, uni=True)
        self.set_auto_page_break(auto=True, margin=20)
        self.set_font("DejaVu", "", 12)

    def header(self):
        self.set_font("DejaVu", "B", 14)
        self.cell(0, 10, self.title, ln=True, align="C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("DejaVu", "", 10)
        self.cell(0, 10, f"Sayfa {self.page_no()}", align="C")

    def sinav_bilgileri(self):
        self.set_font("DejaVu", "", 11)
        self.cell(0, 8, "Ad Soyad: ______________________", ln=True)
        self.cell(0, 8, "Öğretmen: ______________________", ln=True)
        self.cell(0, 8, "Tarih: __________________________", ln=True)
        self.cell(0, 8, "Not: ____________________________", ln=True)
        self.ln(8)

    def soru_ekle(self, soru_no, soru):
        self.set_font("DejaVu", "B", 11)
        metin = str(soru.get("metin", "Soru metni eksik")).strip()
        if not metin or metin.isspace():
            metin = "(Soru metni boş)"
        secenekler = ['a', 'b', 'c', 'd']
        # Tahmini toplam yükseklik: soru başlığı + şıklar + (varsa) resim + boşluk
        soru_baslik_yuk = self.get_string_width(f"{soru_no}. {metin}") / (self.w - 2 * self.l_margin) * 8 + 12
        secenek_yuk = 7 * len(secenekler) + 6
        resim_yuk = 0
        resim_yolu = soru.get("resim", "")
        if resim_yolu and os.path.exists(resim_yolu):
            resim_yuk = 40  # Görselin sabit yüksekliği (ayarlayabilirsin)
        toplam_yuk = soru_baslik_yuk + secenek_yuk + resim_yuk

        # Eğer mevcut sayfada yeterli boşluk yoksa yeni sayfa aç
        if self.get_y() + toplam_yuk > self.h - self.b_margin:
            self.add_page()
            # Sadece ilk sayfada sınav bilgileri yazılsın:
            if self.page_no() == 2:  # Sadece ilk sayfada sınav bilgileri yazıldıysa atla
                pass

        # --- SORU BAŞLANGICI ---
        self.set_font("DejaVu", "B", 11)
        self.multi_cell(0, 8, f"{soru_no}. {metin}")
        self.ln(2)
        # Görsel varsa ortala
        if resim_yuk > 0:
            sayfa_genisligi = self.w - 2 * self.l_margin
            resim_genislik = 80
            x = self.l_margin + (sayfa_genisligi - resim_genislik) / 2
            self.image(resim_yolu, x=x, w=resim_genislik)
            self.ln(5)

        self.set_font("DejaVu", "", 11)
        for sec in secenekler:
            secenek_metin = str(soru.get(sec, "")).replace("\n", " ").replace("\r", " ").strip()
            if not secenek_metin or secenek_metin.isspace():
                secenek_metin = "(boş)"
            if len(secenek_metin) > 150:
                secenek_metin = secenek_metin[:147] + "..."
            if max([len(par) for par in secenek_metin.split(" ") if par]) > 60:
                secenek_metin = "(şık çok uzun/bölünemez)"
            self.cell(10)
            self.cell(0, 7, f"{sec.upper()}) {secenek_metin}", ln=True)
        self.ln(6)


def pdf_olustur(sinav_adi, sorular, dosya_yolu="sinav.pdf"):
    pdf = SinavPDF(title=sinav_adi)
    pdf.add_page()
    pdf.sinav_bilgileri()

    for idx, soru in enumerate(sorular, start=1):
        pdf.soru_ekle(idx, soru)

    pdf.output(dosya_yolu, dest='F')
    return dosya_yolu
