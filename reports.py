from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_RIGHT
from xml.sax.saxutils import escape

def _rtl(text):
    try:
        import arabic_reshaper
        from bidi.algorithm import get_display
        return get_display(arabic_reshaper.reshape(str(text)))
    except Exception:
        return str(text)

def create_pdf(data: dict, result: dict, output_path: str):
    # تلاش برای پیدا کردن فونت فارسی
    candidates = [
        Path(__file__).parent / "Vazirmatn-Regular.ttf",
        Path("C:/Windows/Fonts/tahoma.ttf"), # فونت پیش‌فرض ویندوز
        Path("C:/Windows/Fonts/arial.ttf")
    ]
    
    font_name = "Helvetica"
    for font in candidates:
        if font.exists():
            try:
                pdfmetrics.registerFont(TTFont("PersianFont", str(font)))
                font_name = "PersianFont"
                break
            except Exception:
                pass

    styles = getSampleStyleSheet()
    normal = ParagraphStyle("Persian", parent=styles["Normal"], fontName=font_name,
                            fontSize=10, leading=16, alignment=TA_RIGHT)
    heading = ParagraphStyle("PersianHeading", parent=styles["Heading2"], fontName=font_name,
                             fontSize=14, leading=20, alignment=TA_RIGHT)

    story = [Paragraph(_rtl("گزارش ارزیابی ریسک COSHH Essentials"), heading), Spacer(1, 15)]
    
    # بخش اطلاعات
    fields = [
        ("عنوان ارزیابی", data.get("title", "")),
        ("نام ماده شیمیایی", data.get("chemical", "")),
        ("نام ارزیاب", data.get("assessor", "")),
        ("عبارات H", data.get("h_codes", "")),
        ("حالت فیزیکی", data.get("physical_form", "")),
        ("مقدار مصرف", data.get("amount_band", "")),
        ("گردوغبار/فراریت", data.get("emission_band", "")),
    ]
    
    rows = [[Paragraph(_rtl(escape(k)), normal), Paragraph(_rtl(escape(str(v))), normal)] for k, v in fields]
    t = Table(rows, colWidths=[120, 380])
    t.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("BACKGROUND", (0,0), (0,-1), colors.whitesmoke),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
    ]))
    
    story += [t, Spacer(1, 15), Paragraph(_rtl("نتایج ارزیابی"), heading), Spacer(1, 5)]

    # بخش نتایج
    if result.get("status") == "موفق":
        res_text = f"وضعیت: موفق\nگروه خطر (Hazard Group): {result.get('hazard_group')}\n"
        res_text += f"باند مواجهه (Exposure Band): {result.get('exposure_band')}\n"
        res_text += f"سطح کنترل (Control Approach): {result.get('control_approach')}\n"
        res_text += f"توضیح: {result.get('desc')}"
    else:
        res_text = f"وضعیت: {result.get('status')}\nدلیل: {result.get('reason')}"
        
    story.append(Paragraph(_rtl(res_text).replace("\n", "<br/>"), normal))

    story += [Spacer(1, 20), Paragraph(_rtl("محدودیت: این گزارش ابزار تصمیم‌یار است و جایگزین ارزیابی میدانی یا قضاوت متخصص نیست."), normal)]

    # ساخت PDF
    doc = SimpleDocTemplate(output_path, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    doc.build(story)
    return output_path