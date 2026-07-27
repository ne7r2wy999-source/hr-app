import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date

# --- 1. إعدادات الصفحة والتصميم ---
st.set_page_config(
    page_title="نظام الموارد البشرية - HR System",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تطبيق اتجاه RTL للغة العربية
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif;
        direction: rtl;
        text-align: right;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: 700;
    }
    div[data-testid="stMetricValue"] {
        font-weight: 800;
        color: #1e40af;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. تهيئة البيانات في الـ Session State ---
if "users" not in st.session_state:
    st.session_state.users = {
        "admin": {"password": "admin123", "role": "hr", "name": "مدير الموارد البشرية"},
        "emp101": {"password": "123", "role": "employee", "emp_code": "101", "name": "أحمد محمود علي"},
        "emp102": {"password": "123", "role": "employee", "emp_code": "102", "name": "محمد مصطفى كامل"}
    }

if "employees" not in st.session_state:
    st.session_state.employees = pd.DataFrame([
        {"كود الموظف": "101", "الاسم": "أحمد محمود علي", "القسم": "الموارد البشرية", "الوظيفة": "أخصائي HR", "تاريخ التعيين": date(2022, 1, 15), "الراتب الشامل": 12000.0},
        {"كود الموظف": "102", "الاسم": "محمد مصطفى كامل", "القسم": "تكنولوجيا المعلومات", "الوظيفة": "مطور برمجيات", "تاريخ التعيين": date(2021, 5, 1), "الراتب الشامل": 18000.0}
    ])

if "vacations" not in st.session_state:
    st.session_state.vacations = pd.DataFrame([
        {"كود الموظف": "101", "الاسم": "أحمد محمود علي", "عدد الأيام": 3.0, "النوع": "سنوية", "التاريخ": date(2026, 2, 10)}
    ])

if "penalties" not in st.session_state:
    st.session_state.penalties = pd.DataFrame([
        {"كود الموظف": "101", "الاسم": "أحمد محمود علي", "أيام الخصم": 1.0, "السبب": "تأخير بدون إذن", "التاريخ": date(2026, 3, 1)}
    ])

if "attendance_data" not in st.session_state:
    st.session_state.attendance_data = pd.DataFrame()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = None

# --- 3. الدوارج والحسابات ---
def calculate_vacation_balance(emp_code):
    emp = st.session_state.employees[st.session_state.employees["كود الموظف"] == str(emp_code)]
    if emp.empty:
        return 0, 0, 0, 0
    
    emp_row = emp.iloc[0]
    hiring_date = emp_row["تاريخ التعيين"]
    today = date.today()
    days_served = (today - hiring_date).days
    years_served = round(days_served / 365.25, 1)

    annual_entitlement = 30 if years_served >= 10 else 21
    total_accrued = round(years_served * annual_entitlement)

    used_vacs = st.session_state.vacations[st.session_state.vacations["كود الموظف"] == str(emp_code)]
    used_days = used_vacs["عدد الأيام"].sum() if not used_vacs.empty else 0.0

    remaining = total_accrued - used_days
    return years_served, annual_entitlement, used_days, remaining

# --- 4. شاشة تسجيل الدخول ---
if not st.session_state.logged_in:
    st.title("🔐 تسجيل الدخول إلى نظام الموارد البشرية")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        username = st.text_input("اسم المستخدم (Username)")
        password = st.text_input("كلمة السر (Password)", type="password")
        if st.button("تسجيل الدخول"):
            if username in st.session_state.users and st.session_state.users[username]["password"] == password:
                st.session_state.logged_in = True
                st.session_state.current_user = st.session_state.users[username]
                st.success("تم تسجيل الدخول بنجاح!")
                st.rerun()
            else:
                st.error("اسم المستخدم أو كلمة السر غير صحيحة.")
    st.stop()

# --- 5. القائمة الجانبية والصلاحيات ---
user = st.session_state.current_user
is_hr = (user["role"] == "hr")

st.sidebar.title(f"👋 مرحباً {user['name']}")
st.sidebar.caption("نوع الصلاحية: " + ("مدير HR (تعديل كامل)" if is_hr else "موظف (عرض فقط)"))

if st.sidebar.button("🚪 تسجيل الخروج"):
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.rerun()

st.sidebar.markdown("---")

menu = [
    "📊 ملف الموظفين وسجل الحضور (البصمة)",
    "🏝️ تسجيل وحساب رصيد الإجازات",
    "⚠️ تسجيل الجزاءات والاستقطاعات",
    "💰 التسوية النهائية (End of Service)"
]
choice = st.sidebar.radio("انتقل إلى القسم:", menu)

# --- 6. أقسام البرنامج ---

# القسم الأول: الموظفين والبصمة
if choice == "📊 ملف الموظفين وسجل الحضور (البصمة)":
    st.title("📊 إدارة الموظفين وسحب شيت البصمة")

    if is_hr:
        st.subheader("➕ إضافة موظف جديد (صلاحية HR)")
        with st.form("add_emp_form"):
            c1, c2, c3 = st.columns(3)
            code = c1.text_input("كود الموظف")
            name = c2.text_input("اسم الموظف الثلاثي")
            dept = c3.text_input("القسم")

            c4, c5, c6 = st.columns(3)
            pos = c4.text_input("المسمى الوظيفي")
            hiring = c5.date_input("تاريخ التعيين")
            salary = c6.number_input("الراتب الشامل", min_value=0.0, step=500.0)

            pwd = st.text_input("كلمة السر الخاصة بحسابه للـ Login", value="123")

            submit = st.form_submit_button("حفظ الموظف وإنشاء حسابه")
            if submit and code and name:
                new_row = {"كود الموظف": str(code), "الاسم": name, "القسم": dept, "الوظيفة": pos, "تاريخ التعيين": hiring, "الراتب الشامل": float(salary)}
                st.session_state.employees = pd.concat([st.session_state.employees, pd.DataFrame([new_row])], ignore_index=True)
                st.session_state.users[f"emp{code}"] = {"password": pwd, "role": "employee", "emp_code": str(code), "name": name}
                st.success(f"تم إضافة الموظف {name} بنجاح!")
                st.rerun()

    st.markdown("---")

    if is_hr:
        st.subheader("📂 رفع شيت إكسيل بيانات البصمة")
        uploaded_file = st.file_uploader("قم برفع شيت الإكسيل المسحوب من جهاز البصمة (.xlsx / .csv)", type=["xlsx", "xls", "csv"])
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith(".csv"):
                    df_attendance = pd.read_csv(uploaded_file)
                else:
                    df_attendance = pd.read_excel(uploaded_file)
                st.session_state.attendance_data = df_attendance
                st.success("تم رفع ومعالجة شيت البصمة بنجاح!")
            except Exception as e:
                st.error(f"حدث خطأ أثناء قراءة الملف: {e}")

    st.subheader("📋 قائمة الموظفين")
    if is_hr:
        st.dataframe(st.session_state.employees, use_container_width=True)
    else:
        my_data = st.session_state.employees[st.session_state.employees["كود الموظف"] == user.get("emp_code")]
        st.dataframe(my_data, use_container_width=True)

    if not st.session_state.attendance_data.empty:
        st.subheader("⏱️ سجل الحضور والانصراف (البصمة)")
        if is_hr:
            st.dataframe(st.session_state.attendance_data, use_container_width=True)
        else:
            emp_c = user.get("emp_code")
            cols = st.session_state.attendance_data.columns
            match_col = [c for c in cols if 'كود' in c or 'ID' in c or 'id' in c or 'Code' in c]
            if match_col:
                filtered_att = st.session_state.attendance_data[st.session_state.attendance_data[match_col[0]].astype(str) == str(emp_c)]
                st.dataframe(filtered_att, use_container_width=True)
            else:
                st.dataframe(st.session_state.attendance_data, use_container_width=True)

# القسم الثاني: الإجازات
elif choice == "🏝️ تسجيل وحساب رصيد الإجازات":
    st.title("🏝️ إدارة ورصيد الإجازات")

    if is_hr:
        st.subheader("➕ تسجيل إجازة جديدة (خاص بـ HR)")
        with st.form("add_vacation_form"):
            emp_list = st.session_state.employees["كود الموظف"] + " - " + st.session_state.employees["الاسم"]
            selected_emp = st.selectbox("اختر الموظف", emp_list)
            
            c1, c2, c3 = st.columns(3)
            vac_days = c1.number_input("عدد الأيام", min_value=0.5, step=0.5)
            vac_type = c2.selectbox("نوع الإجازة", ["سنوية", "عارضة", "مرضية", "بدون أجر"])
            vac_date = c3.date_input("تاريخ الإجازة")

            if st.form_submit_button("تسجيل الإجازة"):
                e_code = selected_emp.split(" - ")[0]
                e_name = selected_emp.split(" - ")[1]
                new_v = {"كود الموظف": str(e_code), "الاسم": e_name, "عدد الأيام": float(vac_days), "النوع": vac_type, "التاريخ": vac_date}
                st.session_state.vacations = pd.concat([st.session_state.vacations, pd.DataFrame([new_v])], ignore_index=True)
                st.success("تم تسجيل الإجازة بنجاح!")
                st.rerun()

    st.markdown("---")
    st.subheader("📊 أرصدة الإجازات المستحقة")

    balances = []
    for idx, row in st.session_state.employees.iterrows():
        code = row["كود الموظف"]
        yrs, annual, used, rem = calculate_vacation_balance(code)
        daily_rate = row["الراتب الشامل"] / 30.0
        cash_val = round(rem * daily_rate, 2)
        balances.append({
            "كود الموظف": code,
            "الاسم": row["الاسم"],
            "سنوات الخدمة": yrs,
            "المستحق السنوي": annual,
            "المستهلك (أيام)": used,
            "الرصيد المتبقي (أيام)": rem,
            "القيمة النقدية للرصيد (ج.م)": cash_val
        })
    
    df_bal = pd.DataFrame(balances)

    if is_hr:
        st.dataframe(df_bal, use_container_width=True)
        st.subheader("📜 سجل جميع الإجازات المأخوذة")
        st.dataframe(st.session_state.vacations, use_container_width=True)
    else:
        emp_c = user.get("emp_code")
        my_bal = df_bal[df_bal["كود الموظف"] == emp_c]
        st.dataframe(my_bal, use_container_width=True)
        
        st.subheader("📜 سجل إجازاتي")
        my_vacs = st.session_state.vacations[st.session_state.vacations["كود الموظف"] == emp_c]
        st.dataframe(my_vacs, use_container_width=True)

# القسم الثالث: الجزاءات
elif choice == "⚠️ تسجيل الجزاءات والاستقطاعات":
    st.title("⚠️ سجل الجزاءات والاستقطاعات")

    if is_hr:
        st.subheader("➕ تنزيل جزاء / خصم (خاص بـ HR)")
        with st.form("add_pen_form"):
            emp_list = st.session_state.employees["كود الموظف"] + " - " + st.session_state.employees["الاسم"]
            selected_emp = st.selectbox("اختر الموظف", emp_list)

            c1, c2, c3 = st.columns(3)
            pen_days = c1.number_input("خصم (عدد الأيام)", min_value=0.5, step=0.5)
            pen_date = c2.date_input("تاريخ الجزاء")
            pen_reason = c3.text_input("سبب الجزاء", placeholder="تأخير / عدم التزام بالبصمة")

            if st.form_submit_button("تنزيل الخصم"):
                e_code = selected_emp.split(" - ")[0]
                e_name = selected_emp.split(" - ")[1]
                new_p = {"كود الموظف": str(e_code), "الاسم": e_name, "أيام الخصم": float(pen_days), "السبب": pen_reason, "التاريخ": pen_date}
                st.session_state.penalties = pd.concat([st.session_state.penalties, pd.DataFrame([new_p])], ignore_index=True)
                st.success("تم تسجيل الجزاء بنجاح!")
                st.rerun()

    st.markdown("---")
    st.subheader("📋 قائمة الجزاءات الصادرة")

    if is_hr:
        st.dataframe(st.session_state.penalties, use_container_width=True)
    else:
        emp_c = user.get("emp_code")
        my_pen = st.session_state.penalties[st.session_state.penalties["كود الموظف"] == emp_c]
        st.dataframe(my_pen, use_container_width=True)

# القسم الرابع: التسوية النهائية
elif choice == "💰 التسوية النهائية (End of Service)":
    st.title("💰 حاسبة التسوية النهائية وإخلاء الطرف")

    if not is_hr:
        st.warning("⚠️ هذه الصفحة للعرض فقط حسب بياناتك الحالية.")

    if is_hr:
        emp_list = st.session_state.employees["كود الموظف"] + " - " + st.session_state.employees["الاسم"]
        selected_emp = st.selectbox("اختر الموظف لإجراء التسوية", emp_list)
        emp_code = selected_emp.split(" - ")[0]
    else:
        emp_code = user.get("emp_code")

    emp_data = st.session_state.employees[st.session_state.employees["كود الموظف"] == emp_code].iloc[0]

    yrs, annual, used, rem_vac = calculate_vacation_balance(emp_code)
    daily_rate = emp_data["الراتب الشامل"] / 30.0

    p_df = st.session_state.penalties[st.session_state.penalties["كود الموظف"] == emp_code]
    total_pen_days = p_df["أيام الخصم"].sum() if not p_df.empty else 0.0

    st.markdown("---")
    st.subheader(f"📄 بيان تسوية الموظف: {emp_data['الاسم']} ({emp_data['كود الموظف']})")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("الراتب الشهري", f"{emp_data['الراتب الشامل']:,.2f} ج.م")
    c2.metric("تاريخ التعيين", str(emp_data["تاريخ التعيين"]))
    c3.metric("مدة الخدمة", f"{yrs} سنة")
    c4.metric("الأجر اليومي", f"{daily_rate:,.2f} ج.م")

    st.markdown("---")

    col_a, col_b = st.columns(2)
    with col_a:
        work_days = st.number_input("أيام عمل بالشهر الحالي", value=15.0, step=1.0, disabled=not is_hr)
        vac_days_input = st.number_input("رصيد الإجازات المستحق (أيام)", value=float(rem_vac), step=0.5, disabled=not is_hr)
    
    with col_b:
        pen_days_input = st.number_input("الجزاءات والخصومات (أيام)", value=float(total_pen_days), step=0.5, disabled=not is_hr)
        gratuity = yrs * (emp_data["الراتب الشامل"] * 0.5) if yrs <= 5 else (5 * (emp_data["الراتب الشامل"] * 0.5)) + ((yrs - 5) * emp_data["الراتب الشامل"])
        st.metric("مكافأة نهاية الخدمة (تقديري)", f"{gratuity:,.2f} ج.م")

    salary_pay = work_days * daily_rate
    vacation_pay = vac_days_input * daily_rate
    penalty_deduction = pen_days_input * daily_rate
    net_settlement = salary_pay + vacation_pay + gratuity - penalty_deduction

    st.markdown("---")
    st.subheader("🧾 ملخص الحساب الصافي")

    res_col1, res_col2, res_col3, res_col4 = st.columns(4)
    res_col1.metric("مستحق أيام العمل", f"{salary_pay:,.2f} ج.م")
    res_col2.metric("بدل رصيد الإجازات", f"{vacation_pay:,.2f} ج.م")
    res_col3.metric("خصم الجزاءات", f"-{penalty_deduction:,.2f} ج.م", delta_color="inverse")
    res_col4.metric("صافي المستحقات النهائي", f"{net_settlement:,.2f} ج.م")