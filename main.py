# main.py
import tkinter as tk
from tkinter import messagebox, filedialog
import customtkinter as ctk
import tkinter.ttk as ttk
import os
from engines import assess_coshh, CHEMICAL_DATABASE, risk_score, H_STATEMENTS_LIST
from database import save_assessment, list_assessments, get_assessment, delete_assessment

ctk.set_appearance_mode("Dark") 
ctk.set_default_color_theme("green")

def fix_text(text):
    if text.endswith(":"):
        return ":" + text[:-1]
    return text

FONT_PATH = "Vazirmatn-Regular.ttf"
if os.path.exists(FONT_PATH):
    try:
        ctk.FontManager.load_font(FONT_PATH)
        FONT_FAMILY = "Vazirmatn"
    except:
        FONT_FAMILY = "Tahoma"
else:
    FONT_FAMILY = "Tahoma"

FONT_SIZE_NORMAL = 14
FONT_SIZE_TITLE = 16
FONT_SIZE_HEADER = 22
FONT_SIZE_REPORT = 15
FONT_SIZE_TABLE = 15

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("سامانه حرفه‌ای ارزیابی COSHH Essentials")
        self.geometry("1350x900")
        self.minsize(1200, 850)
        self.current_id = None
        self.configure(fg_color="#1a1a1a")
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", font=(FONT_FAMILY, 13), rowheight=40, background="#333333", fieldbackground="#333333", foreground="white", borderwidth=0)
        style.configure("Treeview.Heading", font=(FONT_FAMILY, 14, "bold"), background="#176b5b", foreground="white", relief="flat")
        style.map("Treeview", background=[('selected', '#176b5b')])

        self.header_frame = ctk.CTkFrame(self, fg_color="#176b5b", corner_radius=0, height=70)
        self.header_frame.pack(fill="x")
        self.header = ctk.CTkLabel(self.header_frame, text="سامانه ارزیابی ریسک مواد شیمیایی | COSHH Essentials", 
                                   font=(FONT_FAMILY, FONT_SIZE_HEADER, "bold"), text_color="white")
        self.header.pack(pady=15)

        self.nav_frame = ctk.CTkFrame(self, fg_color="#2b2b2b", corner_radius=10)
        self.nav_frame.pack(fill="x", padx=15, pady=(5, 0))
        
        self.buttons = {}
        self.current_tab = None
        
        tabs = [
            ("tab_base", "۱. اطلاعات پایه"),
            ("tab_coshh", "۲. خطرات COSHH"),
            ("tab_result", "۳. تحلیل و نتیجه"),
            ("tab_records", "سوابق")
        ]
        
        for key, text in tabs:
            btn = ctk.CTkButton(self.nav_frame, text=text, font=(FONT_FAMILY, 16, "bold"), 
                                fg_color="transparent", hover_color="#176b5b", text_color="white",
                                height=45, width=150, corner_radius=8,
                                command=lambda k=key: self.switch_tab(k))
            btn.pack(side="right", padx=15, pady=10)
            self.buttons[key] = btn

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=15, pady=10)
        
        self.frames = {}
        for k in ["tab_base", "tab_coshh", "tab_result", "tab_records"]:
            self.frames[k] = ctk.CTkFrame(self.container, fg_color="transparent")
        
        self.build_tab_base(self.frames["tab_base"])
        self.build_tab_coshh(self.frames["tab_coshh"])
        self.build_tab_result(self.frames["tab_result"])
        self.build_tab_records(self.frames["tab_records"])
        
        self.switch_tab("tab_base")

    def switch_tab(self, tab_key):
        for frame in self.frames.values():
            frame.pack_forget()
        for key, btn in self.buttons.items():
            btn.configure(fg_color="transparent")
            
        self.frames[tab_key].pack(fill="both", expand=True)
        self.buttons[tab_key].configure(fg_color="#176b5b")
        self.current_tab = tab_key

    def build_tab_base(self, tab):
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(tab, text=fix_text("عنوان ارزیابی:"), font=(FONT_FAMILY, FONT_SIZE_NORMAL, "bold"), text_color="#e0e0e0").grid(row=0, column=1, sticky="e", padx=20, pady=15)
        self.title_var = tk.StringVar()
        ctk.CTkEntry(tab, textvariable=self.title_var, justify="right", font=(FONT_FAMILY, FONT_SIZE_NORMAL), width=450, fg_color="#3a3a3a", border_color="#176b5b").grid(row=0, column=0, sticky="ew", padx=20, pady=15)

        ctk.CTkLabel(tab, text=fix_text("نام ماده شیمیایی:"), font=(FONT_FAMILY, FONT_SIZE_NORMAL, "bold"), text_color="#e0e0e0").grid(row=1, column=1, sticky="e", padx=20, pady=15)
        self.chem_var = tk.StringVar()
        self.chem_combo = ctk.CTkComboBox(tab, variable=self.chem_var, values=list(CHEMICAL_DATABASE.keys()), 
                                          font=(FONT_FAMILY, FONT_SIZE_NORMAL), dropdown_font=(FONT_FAMILY, 14), justify="right", width=450, 
                                          fg_color="#3a3a3a", border_color="#176b5b", command=self.on_chem_select)
        self.chem_combo.grid(row=1, column=0, sticky="ew", padx=20, pady=15)

        ctk.CTkLabel(tab, text=fix_text("نام ارزیاب:"), font=(FONT_FAMILY, FONT_SIZE_NORMAL, "bold"), text_color="#e0e0e0").grid(row=2, column=1, sticky="e", padx=20, pady=15)
        self.assessor_var = tk.StringVar()
        ctk.CTkEntry(tab, textvariable=self.assessor_var, justify="right", font=(FONT_FAMILY, FONT_SIZE_NORMAL), width=450, fg_color="#3a3a3a", border_color="#176b5b").grid(row=2, column=0, sticky="ew", padx=20, pady=15)

        ctk.CTkLabel(tab, text="ماتریس ریسک ۵×۵ (ابزار مدیریتی):", font=(FONT_FAMILY, FONT_SIZE_TITLE, "bold"), text_color="#fca311").grid(row=3, column=0, columnspan=2, sticky="e", pady=(40, 15), padx=20)
        
        risk_frame = ctk.CTkFrame(tab, fg_color="#333333", corner_radius=10)
        risk_frame.grid(row=4, column=0, columnspan=2, pady=10, padx=20, sticky="ew")
        
        ctk.CTkLabel(risk_frame, text=fix_text("شدت پیامد (۱-۵):"), font=(FONT_FAMILY, FONT_SIZE_NORMAL), text_color="white").pack(side="right", padx=20, pady=15)
        self.sev_var = tk.StringVar(value="3")
        ctk.CTkComboBox(risk_frame, variable=self.sev_var, values=["1","2","3","4","5"], width=80, font=(FONT_FAMILY, FONT_SIZE_NORMAL), dropdown_font=(FONT_FAMILY, FONT_SIZE_NORMAL)).pack(side="right", padx=10)
        
        ctk.CTkLabel(risk_frame, text=fix_text("احتمال وقوع (۱-۵):"), font=(FONT_FAMILY, FONT_SIZE_NORMAL), text_color="white").pack(side="right", padx=20, pady=15)
        self.lik_var = tk.StringVar(value="3")
        ctk.CTkComboBox(risk_frame, variable=self.lik_var, values=["1","2","3","4","5"], width=80, font=(FONT_FAMILY, FONT_SIZE_NORMAL), dropdown_font=(FONT_FAMILY, FONT_SIZE_NORMAL)).pack(side="right", padx=10)

    def build_tab_coshh(self, tab):
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(tab, text=fix_text("حالت فیزیکی:"), font=(FONT_FAMILY, FONT_SIZE_NORMAL), text_color="#e0e0e0").grid(row=0, column=1, sticky="e", padx=20, pady=10)
        self.form_var = tk.StringVar(value="مایع")
        ctk.CTkComboBox(tab, variable=self.form_var, values=["جامد", "مایع", "گاز"], font=(FONT_FAMILY, FONT_SIZE_NORMAL), justify="right", width=300, fg_color="#3a3a3a").grid(row=0, column=0, sticky="ew", padx=20, pady=10)

        ctk.CTkLabel(tab, text=fix_text("مقدار مصرف:"), font=(FONT_FAMILY, FONT_SIZE_NORMAL), text_color="#e0e0e0").grid(row=1, column=1, sticky="e", padx=20, pady=10)
        self.amount_var = tk.StringVar(value="S (گرم/میلی‌لیتر)")
        ctk.CTkComboBox(tab, variable=self.amount_var, values=["S (گرم/میلی‌لیتر)", "M (کیلوگرم/لیتر)", "L (تن/متر مکعب)"], font=(FONT_FAMILY, FONT_SIZE_NORMAL), justify="right", width=300, fg_color="#3a3a3a").grid(row=1, column=0, sticky="ew", padx=20, pady=10)

        ctk.CTkLabel(tab, text=fix_text("گردوغبار/فرّاریت:"), font=(FONT_FAMILY, FONT_SIZE_NORMAL), text_color="#e0e0e0").grid(row=2, column=1, sticky="e", padx=20, pady=10)
        self.emis_var = tk.StringVar(value="Low")
        ctk.CTkComboBox(tab, variable=self.emis_var, values=["Low", "Medium", "High"], font=(FONT_FAMILY, FONT_SIZE_NORMAL), justify="right", width=300, fg_color="#3a3a3a").grid(row=2, column=0, sticky="ew", padx=20, pady=10)

        ctk.CTkLabel(tab, text="جدول عبارات H (برای انتخاب روی ردیف کلیک کنید):", font=(FONT_FAMILY, FONT_SIZE_TITLE, "bold"), text_color="#fca311").grid(row=3, column=0, columnspan=2, sticky="e", pady=(20,10), padx=20)
        
        h_frame = ctk.CTkFrame(tab, fg_color="#2b2b2b")
        h_frame.grid(row=4, column=0, columnspan=2, sticky="nsew", padx=20, pady=5)
        tab.grid_rowconfigure(4, weight=1)
        
        self.h_tree = ttk.Treeview(h_frame, columns=("code", "desc", "select"), show="headings")
        self.h_tree.heading("code", text="کد خطر")
        self.h_tree.heading("desc", text="توضیحات خطر سلامت")
        self.h_tree.heading("select", text="وضعیت انتخاب")
        self.h_tree.column("code", width=100, anchor="center")
        self.h_tree.column("desc", width=750, anchor="e")
        self.h_tree.column("select", width=120, anchor="center")
        
        scrollbar = ttk.Scrollbar(h_frame, orient="vertical", command=self.h_tree.yview)
        self.h_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="left", fill="y")
        self.h_tree.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        for code, desc in H_STATEMENTS_LIST:
            self.h_tree.insert("", "end", values=(code, desc, "☐"), iid=code)
            
        self.h_tree.bind("<ButtonRelease-1>", self.toggle_h_select)

        self.selected_h_label = ctk.CTkLabel(tab, text="کدهای انتخاب شده: هیچ", font=(FONT_FAMILY, 13, "bold"), text_color="#aaaaaa")
        self.selected_h_label.grid(row=5, column=0, columnspan=2, sticky="e", padx=20, pady=10)

    def build_tab_result(self, tab):
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(2, weight=1)
        
        btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
        btn_frame.grid(row=0, column=0, pady=10)
        
        ctk.CTkButton(btn_frame, text="ارزیابی و تحلیل", command=self.evaluate, font=(FONT_FAMILY, FONT_SIZE_NORMAL, "bold"), width=200, height=45, fg_color="#1f538d", hover_color="#14375e").pack(side="right", padx=10)
        ctk.CTkButton(btn_frame, text="ذخیره در دیتابیس", command=self.save, font=(FONT_FAMILY, FONT_SIZE_NORMAL, "bold"), width=200, height=45, fg_color="#2b712b", hover_color="#1f521f").pack(side="right", padx=10)
        ctk.CTkButton(btn_frame, text="خروجی PDF", command=self.pdf, font=(FONT_FAMILY, FONT_SIZE_NORMAL, "bold"), width=150, height=45, fg_color="#8b0000", hover_color="#5c0000").pack(side="right", padx=10)

        # جدول گرافیکی اختصاصی
        self.table_frame = ctk.CTkFrame(tab, fg_color="#2b2b2b", corner_radius=10)
        self.table_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=5)
        
        header_row = ctk.CTkFrame(self.table_frame, fg_color="#176b5b", corner_radius=5)
        header_row.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(header_row, text="شاخص ارزیابی", font=(FONT_FAMILY, FONT_SIZE_TABLE, "bold"), text_color="white", width=300, anchor="e").pack(side="right", padx=10, pady=5)
        ctk.CTkLabel(header_row, text="نتیجه", font=(FONT_FAMILY, FONT_SIZE_TABLE, "bold"), text_color="white", anchor="e").pack(side="right", fill="x", expand=True, padx=10, pady=5)

        self.res_rows = {}
        keys = ["hazard", "band", "ca", "score", "level"]
        labels = ["گروه خطر (Hazard Group)", "باند مواجهه (Exposure Band)", "سطح کنترل (Control Approach)", "امتیاز ماتریس ریسک", "سطح ریسک"]
        
        for i, (key, label) in enumerate(zip(keys, labels)):
            row = ctk.CTkFrame(self.table_frame, fg_color="#333333" if i%2==0 else "#2b2b2b", corner_radius=5)
            row.pack(fill="x", padx=5, pady=2)
            ctk.CTkLabel(row, text=label, font=(FONT_FAMILY, FONT_SIZE_TABLE), text_color="#e0e0e0", width=300, anchor="e").pack(side="right", padx=10, pady=5)
            val_lbl = ctk.CTkLabel(row, text="-", font=(FONT_FAMILY, FONT_SIZE_TABLE, "bold"), text_color="white", anchor="e")
            val_lbl.pack(side="right", fill="x", expand=True, padx=10, pady=5)
            self.res_rows[key] = val_lbl

        self.output_box = ctk.CTkTextbox(tab, font=(FONT_FAMILY, FONT_SIZE_REPORT), state="disabled", fg_color="#222222", text_color="#e0e0e0", border_color="#176b5b", border_width=2, corner_radius=10, wrap="word")
        self.output_box.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        
        self.output_box.tag_config("title", foreground="#fca311", justify="right")
        self.output_box.tag_config("success", foreground="#2ecc71", justify="right")
        self.output_box.tag_config("warning", foreground="#e74c3c", justify="right")
        self.output_box.tag_config("normal", foreground="#e0e0e0", justify="right")
        self.output_box.tag_config("highlight", foreground="#3498db", justify="right")
        self.output_box.tag_config("header_box", background="#176b5b", foreground="white", justify="right")

    def build_tab_records(self, tab):
        top = ctk.CTkFrame(tab, fg_color="transparent")
        top.pack(fill="x", pady=10, padx=10)
        
        self.search_var = tk.StringVar()
        ctk.CTkEntry(top, textvariable=self.search_var, placeholder_text="جستجوی عنوان یا ماده...", justify="right", font=(FONT_FAMILY, 13), fg_color="#3a3a3a").pack(side="right", padx=10, fill="x", expand=True)
        ctk.CTkButton(top, text="جستجو", width=80, command=self.refresh_records, fg_color="#1f538d").pack(side="right", padx=5)
        ctk.CTkButton(top, text="مشاهده/ویرایش", width=100, command=self.load_selected, fg_color="#555555").pack(side="right", padx=5)
        ctk.CTkButton(top, text="حذف", width=80, fg_color="#8b0000", hover_color="#5c0000", command=self.delete_selected).pack(side="right", padx=5)

        tree_frame = ctk.CTkFrame(tab, fg_color="#2b2b2b")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        cols = ("id", "title", "chemical", "assessor", "updated_at")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings")
        heads = {"id":"شناسه", "title":"عنوان ارزیابی", "chemical":"ماده", "assessor":"ارزیاب", "updated_at":"آخرین ویرایش"}
        for c in cols:
            self.tree.heading(c, text=heads[c])
            self.tree.column(c, width=150, anchor="center")
            
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="left", fill="y")
        self.tree.pack(side="right", fill="both", expand=True)
        
        self.refresh_records()

    def on_chem_select(self, choice):
        if choice in CHEMICAL_DATABASE:
            info = CHEMICAL_DATABASE[choice]
            for child in self.h_tree.get_children():
                self.h_tree.set(child, "select", "☐")
                self.h_tree.item(child, tags=())
            
            codes = [c.strip() for c in info["h_codes"].split(";")]
            for code in codes:
                if self.h_tree.exists(code):
                    self.h_tree.set(code, "select", "☑")
                    self.h_tree.item(code, tags=("selected",))
            self.h_tree.tag_configure("selected", background="#176b5b")
            
            self.form_var.set(info["form"])
            self.update_selected_label()

    def toggle_h_select(self, event):
        item = self.h_tree.identify_row(event.y)
        if not item: return
        
        current = self.h_tree.set(item, "select")
        if current == "☐":
            self.h_tree.set(item, "select", "☑")
            self.h_tree.item(item, tags=("selected",))
            self.h_tree.tag_configure("selected", background="#176b5b")
        else:
            self.h_tree.set(item, "select", "☐")
            self.h_tree.item(item, tags=())
        
        self.update_selected_label()

    def update_selected_label(self):
        selected = [child for child in self.h_tree.get_children() if self.h_tree.set(child, "select") == "☑"]
        if selected:
            self.selected_h_label.configure(text=f"کدهای انتخاب شده: {', '.join(selected)}", text_color="#2ecc71")
        else:
            self.selected_h_label.configure(text="کدهای انتخاب شده: هیچ", text_color="#aaaaaa")

    def get_data(self):
        selected_h = [child for child in self.h_tree.get_children() if self.h_tree.set(child, "select") == "☑"]
        return {
            "title": self.title_var.get(),
            "chemical": self.chem_var.get(),
            "assessor": self.assessor_var.get(),
            "physical_form": self.form_var.get(),
            "h_codes": "; ".join(selected_h),
            "amount_band": self.amount_var.get(),
            "emission_band": self.emis_var.get(),
            "severity": int(self.sev_var.get()),
            "likelihood": int(self.lik_var.get()),
        }

    def evaluate(self):
        d = self.get_data()
        coshh = assess_coshh(d["physical_form"], d["h_codes"], d["amount_band"], d["emission_band"])
        risk = risk_score(d["severity"], d["likelihood"])

        # به روز رسانی جدول
        self.res_rows["hazard"].configure(text=f"{coshh.get('hazard_group', '-')} ({coshh.get('hg_desc', '-')})")
        self.res_rows["band"].configure(text=str(coshh.get('exposure_band', '-')))
        self.res_rows["ca"].configure(text=f"{coshh.get('control_approach', '-')} ({coshh.get('desc', '-')})")
        self.res_rows["score"].configure(text=f"{risk['score']} از ۲۵")
        
        level_color = "#2ecc71" if risk['level'] in ["پایین", "متوسط"] else "#e74c3c"
        self.res_rows["level"].configure(text=risk['level'], text_color=level_color)

        # به روز رسانی متن
        self.output_box.configure(state="normal")
        self.output_box.delete("1.0", "end")
        
        self.output_box.insert("end", " " * 80 + "\n", "header_box")
        self.output_box.insert("end", "📋 گزارش تحلیلی جامع ارزیابی ریسک\n", "header_box")
        self.output_box.insert("end", " " * 80 + "\n\n", "header_box")
        
        self.output_box.insert("end", "👤 مشخصات پایه\n", "title")
        self.output_box.insert("end", f"• ارزیاب: {d['assessor'] if d['assessor'] else 'ثبت نشده'}\n", "normal")
        self.output_box.insert("end", f"• ماده شیمیایی: {d['chemical'] if d['chemical'] else 'ثبت نشده'}\n", "normal")
        self.output_box.insert("end", "-" * 80 + "\n\n", "normal")

        self.output_box.insert("end", "📌 تحلیل عبارات H\n", "title")
        if d["h_codes"]:
            for code in d["h_codes"].split(";"):
                code = code.strip()
                if code:
                    desc = next((item[1] for item in H_STATEMENTS_LIST if item[0] == code), "توضیح نامشخص")
                    self.output_box.insert("end", f"  • {code}: {desc}\n", "normal")
        else:
            self.output_box.insert("end", "  • هیچ کد H انتخاب نشده است.\n", "warning")
        self.output_box.insert("end", "\n" + "-" * 80 + "\n\n", "normal")

        self.output_box.insert("end", "💼 توصیه‌های شغلی و اقدامات کنترلی\n", "title")
        if coshh["status"] == "موفق":
            ca = coshh["control_approach"]
            if ca == 1:
                self.output_box.insert("end", "  • استفاده از تهویه عمومی کافی در محیط کار الزامی است.\n", "normal")
                self.output_box.insert("end", "  • استفاده از وسایل حفاظت فردی (PPE) پایه توصیه می‌شود.\n", "normal")
            elif ca == 2:
                self.output_box.insert("end", "  • نصب و استفاده از سیستم تهویه موضعی (LEV) ضروری است.\n", "warning")
                self.output_box.insert("end", "  • مانیتورینگ دوره‌ای عملکرد سیستم تهویه انجام شود.\n", "normal")
                self.output_box.insert("end", "  • استفاده از ماسک تنفسی مناسب (RPE) و دستکش الزامی است.\n", "normal")
            elif ca == 3:
                self.output_box.insert("end", "  • محصورسازی فرآیند و جلوگیری از انتشار ماده در محیط الزامی است.\n", "warning")
                self.output_box.insert("end", "  • استفاده از تجهیزات حفاظت فردی کامل (PPE + RPE) ضروری است.\n", "warning")
                self.output_box.insert("end", "  • پایش بیولوژیکی و سلامت کارگران باید به طور منظم انجام شود.\n", "normal")
            elif ca == 4:
                self.output_box.insert("end", "  • خطر بسیار بالا! توقف فعالیت تا بررسی کامل متخصص.\n", "warning")
                self.output_box.insert("end", "  • کاهش مواجهه تا حد ممکن (ALARP) و استفاده از حداکثر کنترل‌های مهندسی.\n", "warning")
                self.output_box.insert("end", "  • پایش مستمر هوا و پایش سلامت تخصصی الزامی است.\n", "warning")
        
        if risk['level'] in ["بالا", "بسیار بالا"]:
            self.output_box.insert("end", "  • ⚠️ توجه: سطح ریسک بالا است. اقدامات اصلاحی فوری انجام شود.\n", "warning")
        
        self.output_box.insert("end", "\n" + "-" * 80 + "\n\n", "normal")
        
        # تحلیل اختصاصی
        self.output_box.insert("end", "🧠 تحلیل اختصاصی ماده و شرایط\n", "title")
        analysis = ""
        form = d["physical_form"]
        amt = d["amount_band"][0]
        emis = d["emission_band"]
        
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
        self.output_box.insert("end", analysis, "normal")
        self.output_box.insert("end", "\n" + "-" * 80 + "\n\n", "normal")
        
        self.output_box.insert("end", "🚨 هشدار و محدودیت‌ها\n", "title")
        self.output_box.insert("end", "• این گزارش ابزار تصمیم‌یار است و جایگزین اندازه‌گیری‌های میدانی یا قضاوت متخصص نیست.\n", "warning")
        self.output_box.insert("end", "• استفاده از وسایل حفاظت فردی (PPE) باید آخرین خط دفاعی باشد.\n", "warning")

        self.output_box.configure(state="disabled")
        self.switch_tab("tab_result")

    def save(self):
        d = self.get_data()
        if not d["title"]: d["title"] = d["chemical"] or "ارزیابی بدون عنوان"
        aid = save_assessment(d, self.current_id)
        self.current_id = aid
        messagebox.showinfo("ذخیره شد", f"ارزیابی با شناسه {aid} با موفقیت ذخیره شد.")
        self.refresh_records()

    def pdf(self):
        d = self.get_data()
        coshh = assess_coshh(d["physical_form"], d["h_codes"], d["amount_band"], d["emission_band"])
        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF","*.pdf")], initialfile="coshh_report.pdf")
        if not path: return
        try:
            from reports import create_pdf
            create_pdf(d, coshh, path)
            messagebox.showinfo("موفق", f"فایل PDF ذخیره شد:\n{path}")
        except Exception as e:
            messagebox.showerror("خطا در تولید PDF", str(e))

    def refresh_records(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for r in list_assessments(self.search_var.get()):
            self.tree.insert("", "end", values=(r["id"], r["title"], r["chemical"], r["assessor"], r["updated_at"]))

    def load_selected(self):
        sel = self.tree.selection()
        if not sel: return
        aid = int(self.tree.item(sel[0])["values"][0])
        row = get_assessment(aid)
        if not row: return
        self.current_id = aid
        d = row["payload"]
        
        self.title_var.set(d.get("title",""))
        self.chem_var.set(d.get("chemical",""))
        self.assessor_var.set(d.get("assessor",""))
        self.form_var.set(d.get("physical_form","مایع"))
        self.amount_var.set(d.get("amount_band","S (گرم/میلی‌لیتر)"))
        self.emis_var.set(d.get("emission_band","Low"))
        self.sev_var.set(str(d.get("severity",3)))
        self.lik_var.set(str(d.get("likelihood",3)))
        
        h_str = d.get("h_codes","")
        for child in self.h_tree.get_children():
            self.h_tree.set(child, "select", "☐")
            self.h_tree.item(child, tags=())
        if h_str:
            for code in [c.strip() for c in h_str.split(";")]:
                if self.h_tree.exists(code):
                    self.h_tree.set(code, "select", "☑")
                    self.h_tree.item(code, tags=("selected",))
            self.h_tree.tag_configure("selected", background="#176b5b")
        self.update_selected_label()
        
        self.evaluate()

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel: return
        aid = int(self.tree.item(sel[0])["values"][0])
        if messagebox.askyesno("تأیید حذف", "آیا از حذف این ارزیابی مطمئن هستید؟"):
            delete_assessment(aid)
            self.refresh_records()

if __name__ == "__main__":
    app = App()
    app.mainloop()