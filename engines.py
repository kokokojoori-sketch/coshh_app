# engines.py
import re

H_TO_HAZARD_GROUP = {
    "H200": "E", "H201": "E", "H202": "E", "H203": "E", "H204": "E", "H205": "E",
    "H220": "E", "H221": "E", "H222": "E", "H223": "E", "H224": "E", "H225": "E", "H226": "E",
    "H228": "E", "H240": "E", "H241": "E", "H242": "E", "H250": "E", "H251": "E", "H252": "E",
    "H260": "E", "H261": "E", "H270": "E", "H271": "E", "H272": "E", "H280": "E", "H281": "E", "H290": "E",
    "H303": "A", "H304": "A", "H305": "A", "H313": "A", "H315": "A", "H316": "A", "H319": "A", "H320": "A", "H333": "A", "H336": "A",
    "H302": "B", "H312": "B", "H332": "B", "H371": "B",
    "H301": "C", "H311": "C", "H314": "C", "H317": "C", "H318": "C", "H331": "C", "H335": "C", "H370": "C", "H373": "C",
    "H300": "D", "H310": "D", "H330": "D", "H351": "D", "H360": "D", "H361": "D", "H362": "D", "H372": "D",
    "H334": "E", "H340": "E", "H341": "E", "H350": "E",
}

# لیست کامل عبارات H برای نمایش در جدول (همراه با توضیح فارسی)
H_STATEMENTS_LIST = [
    ("H315", "تحریک پوست"),
    ("H319", "تحریک شدید چشم"),
    ("H302", "مضر در صورت بلع"),
    ("H332", "مضر در صورت استنشاق"),
    ("H312", "مضر در تماس با پوست"),
    ("H301", "سمی در صورت بلع"),
    ("H331", "سمی در صورت استنشاق"),
    ("H311", "سمی در تماس با پوست"),
    ("H314", "ایجاد سوختگی شدید پوست و آسیب چشم"),
    ("H317", "ممکن است باعث حساسیت پوستی شود"),
    ("H318", "آسیب جدی به چشم"),
    ("H335", "ممکن است باعث تحریک دستگاه تنفسی شود"),
    ("H300", "کشنده در صورت بلع"),
    ("H330", "کشنده در صورت استنشاق"),
    ("H310", "کشنده در تماس با پوست"),
    ("H351", "مشکوک به ایجاد سرطان"),
    ("H350", "ایجاد سرطان"),
    ("H340", "ممکن است باعث نقص ژنتیکی شود"),
    ("H334", "ممکن است باعث علائم آسم یا مشکلات تنفسی شود"),
    ("H372", "آسیب به اعضای بدن در اثر مواجهه طولانی"),
]

HAZARD_GROUP_DESCRIPTION = {
    "A": "کم‌ترین خطر (تحریک پوست/چشم)",
    "B": "مضر با یک بار مواجهه",
    "C": "خطر متوسط (سمی، خورنده، حساسیت‌زا)",
    "D": "خطر بالا (بسیار سمی، سمیت تولیدمثلی)",
    "E": "خطر بسیار بالا (سرطان‌زا، آسم، جهش‌زا)",
}

EXPOSURE_PREDICTOR = {
    ("S", "Low"): 1, ("S", "Medium"): 2, ("S", "High"): 2,
    ("M", "Low"): 2, ("M", "Medium"): 3, ("M", "High"): 3,
    ("L", "Low"): 2, ("L", "Medium"): 4, ("L", "High"): 4,
}

CONTROL_APPROACH_MATRIX = {
    ("A", 1): 1, ("B", 1): 1, ("C", 1): 1, ("D", 1): 2, ("E", 1): 4,
    ("A", 2): 1, ("B", 2): 1, ("C", 2): 2, ("D", 2): 3, ("E", 2): 4,
    ("A", 3): 1, ("B", 3): 2, ("C", 3): 3, ("D", 3): 4, ("E", 3): 4,
    ("A", 4): 2, ("B", 4): 3, ("C", 4): 4, ("D", 4): 4, ("E", 4): 4,
}

CA_DESCRIPTION = {
    1: "تهویه عمومی (General Ventilation)",
    2: "تهویه موضعی (LEV) — کاهش ۱۰ برابری",
    3: "محصورسازی (Containment) — کاهش ۱۰۰ برابری",
    4: "نیازمند بررسی متخصص (Special)",
}

CHEMICAL_DATABASE = {
    "استون (Acetone)": {"h_codes": "H336; H319; H315", "form": "مایع"},
    "تولوئن (Toluene)": {"h_codes": "H336; H315; H319; H361", "form": "مایع"},
    "زایلن (Xylene)": {"h_codes": "H312; H315; H319; H332; H335", "form": "مایع"},
    "بنزن (Benzene)": {"h_codes": "H340; H350; H372", "form": "مایع"},
    "متانول (Methanol)": {"h_codes": "H301; H311; H331; H370", "form": "مایع"},
    "اتانول (Ethanol)": {"h_codes": "H319; H315; H336", "form": "مایع"},
    "ایزوپروپانول (Isopropanol)": {"h_codes": "H319; H336", "form": "مایع"},
    "هیدروکلریک اسید (HCl)": {"h_codes": "H314; H331; H335", "form": "مایع"},
    "سولفوریک اسید (H2SO4)": {"h_codes": "H314; H318", "form": "مایع"},
    "نیتریک اسید (HNO3)": {"h_codes": "H314; H318; H331", "form": "مایع"},
    "آمونیاک (Ammonia)": {"h_codes": "H314; H331; H335", "form": "مایع"},
    "فرمالدهید (Formaldehyde)": {"h_codes": "H301; H311; H314; H317; H331; H350", "form": "مایع"},
    "کلروفرم (Chloroform)": {"h_codes": "H302; H315; H319; H331; H351; H373", "form": "مایع"},
    "دی‌کلرومتان (DCM)": {"h_codes": "H302; H315; H319; H336; H351", "form": "مایع"},
    "کربن تتراکلرید (CCl4)": {"h_codes": "H301; H311; H331; H351; H372", "form": "مایع"},
    "پودر سیلیس (Silica)": {"h_codes": "H350; H372", "form": "جامد"},
    "پودر تالک (Talc)": {"h_codes": "H319; H315", "form": "جامد"},
    "پودر گچ (Gypsum)": {"h_codes": "H315; H319", "form": "جامد"},
    "سیمان (Cement)": {"h_codes": "H315; H318; H335", "form": "جامد"},
    "پودر آهن (Iron Powder)": {"h_codes": "H315; H319", "form": "جامد"},
    "پودر آلومینیوم (Aluminum)": {"h_codes": "H315; H319", "form": "جامد"},
    "پودر روی (Zinc)": {"h_codes": "H315; H319", "form": "جامد"},
    "پودر سرب (Lead)": {"h_codes": "H302; H332; H351; H360; H372", "form": "جامد"},
    "پودر کروم (Chromium)": {"h_codes": "H301; H311; H314; H317; H334; H350", "form": "جامد"},
    "پودر نیکل (Nickel)": {"h_codes": "H301; H311; H314; H317; H334; H350", "form": "جامد"},
}

def assess_coshh(physical_form, h_codes_str, amount_band, emission_band):
    physical_form = physical_form.strip()
    if physical_form not in ("جامد", "مایع"):
        return {"status": "خارج از دامنه", "reason": "COSHH فقط برای جامدات و مایعات است."}

    if not h_codes_str.strip():
        return {"status": "نیازمند اطلاعات", "reason": "هیچ عبارت H انتخاب یا وارد نشده است."}

    cleaned = re.sub(r"[;,]", " ", h_codes_str)
    h_codes = [c.strip().upper() for c in cleaned.split() if c.strip()]

    groups_found = []
    unknown_codes = []
    for code in h_codes:
        if code in H_TO_HAZARD_GROUP:
            groups_found.append(H_TO_HAZARD_GROUP[code])
        else:
            unknown_codes.append(code)

    if not groups_found:
        return {"status": "نیازمند بررسی متخصص", "reason": f"هیچ‌یک از عبارات H شناخته نشد: {', '.join(unknown_codes)}"}

    priority = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5}
    hazard_group = max(groups_found, key=lambda g: priority[g])

    amount_band = amount_band.split()[0].strip().upper()
    exposure_band = EXPOSURE_PREDICTOR.get((amount_band, emission_band))
    
    if not exposure_band:
        return {"status": "نیازمند اطلاعات", "reason": "ترکیب مقدار مصرف و شاخص انتشار نامعتبر است."}

    control_approach = CONTROL_APPROACH_MATRIX.get((hazard_group, exposure_band))

    if hazard_group == "E":
        return {
            "status": "نیازمند بررسی متخصص",
            "reason": "گروه خطر E. کاهش مواجهه تا حد ممکن (ALARP) الزامی است.",
            "hazard_group": hazard_group, "exposure_band": exposure_band, "control_approach": 4,
            "desc": CA_DESCRIPTION[4], "hg_desc": HAZARD_GROUP_DESCRIPTION[hazard_group]
        }

    return {
        "status": "موفق", "hazard_group": hazard_group, "exposure_band": exposure_band,
        "control_approach": control_approach, "desc": CA_DESCRIPTION[control_approach],
        "hg_desc": HAZARD_GROUP_DESCRIPTION[hazard_group]
    }

def risk_score(severity, likelihood):
    if severity not in range(1, 6) or likelihood not in range(1, 6):
        raise ValueError("مقادیر نامعتبر")
    score = severity * likelihood
    if score <= 4: level = "پایین"
    elif score <= 9: level = "متوسط"
    elif score <= 16: level = "بالا"
    else: level = "بسیار بالا"
    return {"score": score, "level": level}