# app.py
import streamlit as st
from engines import assess_coshh, CHEMICAL_DATABASE, risk_score, H_STATEMENTS_LIST

# تنظیمات صفحه
st.set_page_config(page_title="سامانه ارزیابی COSHH", layout="wide")

# تزریق CSS برای راست‌چین کردن کل صفحه
st.markdown("""
    <style>
    .stApp { direction: rtl; text-align: right; }
    div[data-testid="stMarkdownContainer"] { direction: rtl; text-align: right; }
    .stSelectbox, .stTextInput, .stNumberInput, .stMultiSelect { direction: rtl; text-align: right; }
    .stDataFrame { direction: rtl; text-align: right; }
    </style>
    """, unsafe_allow_html=True)

st.title("سامانه حرفه‌ای ارزیابی COSHH Essentials")

# --- فرم ورودی ---
with st.form("assessment_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        title = st.text_input("عنوان ارزیابی", value="ارزیابی ریسک")
        chemical = st.selectbox("نام ماده شیمیایی", list(CHEMICAL_DATABASE.keys()))
        assessor = st.text_input("نام ارزیاب", value="")
        
    with col2:
        physical_form = st.selectbox("حالت فیزیکی", ["جامد", "مایع", "گاز"])
        amount_band = st.selectbox("مقدار مصرف", ["S (گرم/میلی‌لیتر)", "M (کیلوگرم/لیتر)", "L (تن/متر مکعب)"])
        emission_band = st.selectbox("گردوغبار/فراریت", ["Low", "Medium", "High"])

    st.subheader("ماتریس ریسک ۵×۵")
    col_sev, col_lik = st.columns(2)
    with col_sev:
        severity = st.slider("شدت پیامد (۱-۵)", 1, 5, 3)
    with col_lik:
        likelihood = st.slider("احتمال وقوع (۱-۵)", 1, 5, 3)

    # انتخاب عبارات H به صورت چندگانه
    st.subheader("عبارات H (می‌توانید چند مورد انتخاب کنید)")
    h_options = [f"{code} - {desc}" for code, desc in H_STATEMENTS_LIST]
    selected_h_options = st.multiselect("کدهای خطر سلامت", h_options)
    
    submit = st.form_submit_button("ارزیابی و تحلیل")

# --- منطق ارزیابی ---
if submit:
    # استخراج کدهای H انتخاب شده
    h_codes = "; ".join([opt.split(" - ")[0] for opt in selected_h_options])
    
    # اگر ماده از دیتابیس انتخاب شده، کدهای H و حالت فیزیکی خودکار پر شوند
    if chemical in CHEMICAL_DATABASE:
        info = CHEMICAL_DATABASE[chemical]
        h_codes = info["h_codes"]
        physical_form = info["form"]
    else:
        h_codes = h_codes # استفاده از کدهایی که کاربر انتخاب کرده است

    # اجرای ارزیابی
    coshh = assess_coshh(physical_form, h_codes, amount_band, emission_band)
    risk = risk_score(severity, likelihood)
    
    st.success("ارزیابی با موفقیت انجام شد!")
    
    # --- نمایش جدول نتایج ---
    st.subheader("📊 جدول نتایج ارزیابی")
    data = {
        "شاخص": ["گروه خطر", "باند مواجهه", "سطح کنترل", "امتیاز ریسک", "سطح ریسک"],
        "نتیجه": [
            f"{coshh.get('hazard_group', '-')} ({coshh.get('hg_desc', '-')})" if coshh['status'] == "موفق" else "-",
            str(coshh.get('exposure_band', '-')),
            f"{coshh.get('control_approach', '-')} ({coshh.get('desc', '-')})" if coshh['status'] == "موفق" else "-",
            f"{risk['score']} از ۲۵",
            risk['level']
        ]
    }
    st.table(data)

    # --- نمایش تحلیل H-Codes ---
    st.subheader("📌 تحلیل عبارات H")
    if h_codes:
        for code in h_codes.split(";"):
            code = code.strip()
            desc = next((item[1] for item in H_STATEMENTS_LIST if item[0] == code), "توضیح نامشخص")
            st.write(f"- **{code}**: {desc}")
    else:
        st.warning("هیچ کد H انتخاب نشده است.")

    # --- توصیه‌های شغلی ---
    st.subheader("💼 توصیه‌های شغلی و اقدامات کنترلی")
    if coshh["status"] == "موفق":
        ca = coshh["control_approach"]
        if ca == 1:
            st.info("استفاده از تهویه عمومی کافی در محیط کار الزامی است.\nاستفاده از وسایل حفاظت فردی (PPE) پایه توصیه می‌شود.")
        elif ca == 2:
            st.warning("نصب و استفاده از سیستم تهویه موضعی (LEV) ضروری است.\nمانیتورینگ دوره‌ای عملکرد سیستم تهویه انجام شود.\nاستفاده از ماسک تنفسی مناسب (RPE) و دستکش الزامی است.")
        elif ca == 3:
            st.error("محصورسازی فرآیند و جلوگیری از انتشار ماده در محیط الزامی است.\nاستفاده از تجهیزات حفاظت فردی کامل (PPE + RPE) ضروری است.\nپایش بیولوژیکی و سلامت کارگران باید به طور منظم انجام شود.")
        elif ca == 4:
            st.error("خطر بسیار بالا! توقف فعالیت تا بررسی کامل متخصص.\nکاهش مواجهه تا حد ممکن (ALARP) و استفاده از حداکثر کنترل‌های مهندسی.\nپایش مستمر هوا و پایش سلامت تخصصی الزامی است.")

    if risk['level'] in ["بالا", "بسیار بالا"]:
        st.error("⚠️ توجه: سطح ریسک بالا است. اقدامات اصلاحی فوری انجام شود.")

    # --- تحلیل اختصاصی ماده و شرایط ---
    st.subheader("🧠 تحلیل اختصاصی ماده و شرایط")
    analysis = ""
    form = physical_form
    amt = amount_band[0]
    emis = emission_band
    
    if form == "گاز":
        analysis += "  • ماده مورد بررسی در حالت گاز است. با توجه به اینکه COSHH Essentials برای گازها طراحی نشده، لازم است از مدل‌های تخصصی مواجهه استفاده شود.\n"
    elif form == "جامد":
        analysis += "  • ماده به صورت جامد است. اگر به صورت پودر ریز باشد، احتمال ایجاد گردوغبار و مواجهه تنفسی وجود دارد.\n"
    elif form == "مایع":
        analysis += "  • ماده به صورت مایع است. خطر اصلی در صورت فرّاریت بالا، انتشار بخارات سمی در هواست.\n"
        
    if amt == "L":
        analysis += "  • با توجه به مقدار مصرف بالا (L)، احتمال پخش شدن ماده در محیط و مواجهه کارگران بیشتر است.\n"
    elif amt == "M":
        analysis += "  • مقدار مصرف متوسط (M) است؛ اما در صورت عدم وجود تهویه مناسب، احتمال تجمع ماده وجود دارد.\n"
        
    if emis == "High":
        analysis += "  • شاخص گردوغبارزایی یا فرّاریت بالاست (High)؛ این یعنی ماده به سرعت در هوا پخش می‌شود و کنترل آن سخت‌تر است.\n"
        
    if coshh["status"] == "موفق" and coshh["hazard_group"] == "E":
        analysis += "  • خطر بسیار جدی! ماده در گروه E (سرطان‌زا/جهش‌زا) قرار دارد. حتی مقادیر بسیار کم آن نیز خطرناک است و باید با جدیت کنترل شود.\n"
        
    analysis += f"  • جمع‌بندی: با توجه به موارد فوق و سطح ریسک {risk['level']}، اجرای اقدامات کنترلی پیشنهادی در اسرع وقت ضروری است.\n"
    st.info(analysis)

    # --- هشدارها ---
    st.subheader("🚨 هشدار و محدودیت‌ها")
    st.warning("این گزارش ابزار تصمیم‌یار است و جایگزین اندازه‌گیری‌های میدانی یا قضاوت متخصص نیست.\nاستفاده از وسایل حفاظت فردی (PPE) باید آخرین خط دفاعی باشد.")