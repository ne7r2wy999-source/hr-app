import streamlit as st
import pandas as pd
from datetime import date, datetime

st.set_page_config(page_title="نظام إدارة الموارد البشرية HR - التقرير والبادجيت", page_icon="🏢", layout="wide")

# CSS للتنسيق والمظهر المحترف
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
        background-color: #1f77b4;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# دالة تنظيف وتأمين البيانات لعدم حدوث أخطاء JSON
def get_clean_df(df):
    if df is None or df.empty:
        return pd.DataFrame()
    return df.fillna("").astype(str)

# --- قائمة الإدارات المعتمدة في الهيكل التوضيحي ---
DEFAULT_DEPTS = [
    "Executive Office", "Front Office", "Reservation", "Housekeeping", 
    "Recreation", "Laundry", "Food & Beverage", "Kitchen", "Stewarding", 
    "Finance", "Information Technology", "Human Resources", "Security", 
    "Engineering", "Landscape", "Health & Safety", "Pest Control", 
    "Sales & Marketing", "Quality"
]

# --- 1. تهيئة قواعد البيانات (Session State) ---

if "master_df" not in st.session_state:
    st.session_state.master_df = pd.DataFrame([
        {"كود الموظف": "101", "الاسم": "أحمد محمود علي", "الإدارة": "Executive Office", "الوظيفة": "Hotel Manager", "نوع التعيين": "Permenant", "تاريخ التعيين": date(2025, 1, 15), "الراتب": 12000.0, "الحالة": "Active"},
        {"كود الموظف": "102", "الاسم": "محمد مصطفى كامل", "الإدارة": "Information Technology", "الوظيفة": "Director of Information Technology", "نوع التعيين": "Permenant", "تاريخ التعيين": date(2026, 7, 27), "الراتب": 18000.0, "الحالة": "Active"},
        {"كود الموظف": "103", "الاسم": "سارة أحمد حسن", "الإدارة": "Housekeeping", "الوظيفة": "Executive Housekeeping", "نوع التعيين": "Permenant", "تاريخ التعيين": date(2024, 3, 10), "الراتب": 8000.0, "الحالة": "Active"}
    ])

if "budget_df" not in st.session_state:
    # إعداد الهيكل المبدئي للبادجيت طبقاً للملف
    st.session_state.budget_df = pd.DataFrame([
        {"الإدارة": "Executive Office", "الوظيفة": "General Manager", "Target Budget": 0},
        {"الإدارة": "Executive Office", "الوظيفة": "Hotel Manager", "Target Budget": 1},
        {"الإدارة": "Executive Office", "الوظيفة": "Executive Assistant Manager", "Target Budget": 2},
        {"الإدارة": "Front Office", "الوظيفة": "Front Office Manager", "Target Budget": 1},
        {"الإدارة": "Front Office", "الوظيفة": "Guest Service Agent", "Target Budget": 3},
        {"الإدارة": "Housekeeping", "الوظيفة": "Executive Housekeeping", "Target Budget": 1},
        {"الإدارة": "Housekeeping", "الوظيفة": "Room Attendant", "Target Budget": 23},
        {"الإدارة": "Information Technology", "الوظيفة": "Director of Information Technology", "Target Budget": 1},
        {"الإدارة": "Information Technology", "الوظيفة": "IT Help Desk", "Target Budget": 2}
    ])

if "vacations_df" not in st.session_state:
    st.session_state.vacations_df = pd.DataFrame(columns=["كود الموظف", "الاسم", "الإدارة", "الوظيفة", "نوع الحركة", "من تاريخ", "إلى تاريخ", "عدد الأيام"])

if "resignations_df" not in st.session_state:
    st.session_state.resignations_df = pd.DataFrame(columns=["كود الموظف", "الاسم", "الإدارة", "الوظيفة", "تاريخ التعيين", "تاريخ الاستقالة"])

# دالة تصدير لإكسيل
def convert_df_to_excel(df):
    import io
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Report')
    return output.getvalue()

# --- القائمة الجانبية ---
st.sidebar.title("🏢 HR Daily & Budget System")
st.sidebar.markdown("---")

uploaded_file = st.sidebar.file_uploader("📤 رفع ملف السيستم المجمع (.xlsx)", type=["xlsx"])
if uploaded_file is not None:
    try:
        excel_file = pd.ExcelFile(uploaded_file)
        if "Master" in excel_file.sheet_names:
            df_m = pd.read_excel(uploaded_file, sheet_name="Master")
            df_m.columns = df_m.columns.astype(str).str.strip()
            st.session_state.master_df = df_m
        if "Budget" in excel_file.sheet_names:
            df_b = pd.read_excel(uploaded_file, sheet_name="Budget")
            df_b.columns = df_b.columns.astype(str).str.strip()
            st.session_state.budget_df = df_b
        st.sidebar.success("تم تحديث كافة البيانات من الملف المرفوع!")
    except Exception as e:
        st.sidebar.error(f"خطأ أثناء التحميل: {e}")

menu = [
    "📊 التقرير اليومي (Daily Report)",
    "🎯 ميزانية العمالة (Budget Manpower)",
    "📋 شيت الماستر (Master)",
    "🏝️ شيت الإجازات (Vacations)",
    "🚪 شيت الاستقالات (Resignations)"
]
choice = st.sidebar.radio("اختر الشاشة:", menu)

# --- 1. التقرير اليومي الشامل (Daily Report) المطابق للـ PDF ---
if choice == "📊 التقرير اليومي (Daily Report)":
    st.title("📊 Daily Report Sheet - Human Resources Department")
    report_date = st.date_input("📅 Date:", value=date.today())
    
    # تحضير قائمة الإدارات
    depts_in_master = st.session_state.master_df["الإدارة"].dropna().astype(str).unique().tolist() if not st.session_state.master_df.empty and "الإدارة" in st.session_state.master_df.columns else []
    depts_in_budget = st.session_state.budget_df["الإدارة"].dropna().astype(str).unique().tolist() if not st.session_state.budget_df.empty and "الإدارة" in st.session_state.budget_df.columns else []
    all_departments = list(dict.fromkeys(DEFAULT_DEPTS + depts_in_master + depts_in_budget))
    
    daily_rows = []
    
    tot_mg, tot_task, tot_perm, tot_budget, tot_actual = 0, 0, 0, 0, 0
    tot_vac, tot_tf_vac, tot_sick = 0, 0, 0

    for dept in all_departments:
        # حساب البادجيت Target من شيت البادجيت
        if not st.session_state.budget_df.empty and "الإدارة" in st.session_state.budget_df.columns:
            b_target = st.session_state.budget_df[st.session_state.budget_df["الإدارة"] == dept]["Target Budget"].sum() if "Target Budget" in st.session_state.budget_df.columns else 0
        else:
            b_target = 0
            
        # الموظفين الحاليين في الماستر للإدارة
        if not st.session_state.master_df.empty and "الإدارة" in st.session_state.master_df.columns:
            dept_master = st.session_state.master_df[st.session_state.master_df["الإدارة"] == dept]
            mg_count = len(dept_master[dept_master.get("نوع التعيين", "") == "MG"])
            tf_count = len(dept_master[dept_master.get("نوع التعيين", "") == "Task Force"])
            perm_count = len(dept_master[dept_master.get("نوع التعيين", "") == "Permenant"])
            actual_count = len(dept_master)
        else:
            mg_count = tf_count = perm_count = actual_count = 0
            
        # حساب الإجازات والغياب ليوم التقرير
        if not st.session_state.vacations_df.empty and all(c in st.session_state.vacations_df.columns for c in ["الإدارة", "من تاريخ", "إلى تاريخ", "نوع الحركة"]):
            dept_vacs = st.session_state.vacations_df[
                (st.session_state.vacations_df["الإدارة"] == dept) & 
                (pd.to_datetime(st.session_state.vacations_df["من تاريخ"]).dt.date <= report_date) & 
                (pd.to_datetime(st.session_state.vacations_df["إلى تاريخ"]).dt.date >= report_date)
            ]
            vac_count = len(dept_vacs[dept_vacs["نوع الحركة"].isin(["إجازة", "عارضة"])])
            sick_count = len(dept_vacs[dept_vacs["نوع الحركة"] == "مرضي"])
            tf_vac_count = len(dept_vacs[dept_vacs["نوع الحركة"] == "Task Force Vac"])
        else:
            vac_count = sick_count = tf_vac_count = 0
            
        pct_actual = f"{round((actual_count / b_target * 100))}%" if b_target > 0 else ("#DIV/0!" if actual_count == 0 else "100%")
        pct_vacation = f"{round(((vac_count + sick_count) / actual_count * 100))}%" if actual_count > 0 else "0%"
        total_operation = actual_count - (vac_count + sick_count)

        # تجميع الإجماليات
        tot_mg += mg_count
        tot_task += tf_count
        tot_perm += perm_count
        tot_budget += b_target
        tot_actual += actual_count
        tot_vac += vac_count
        tot_tf_vac += tf_vac_count
        tot_sick += sick_count

        daily_rows.append({
            "Department": dept,
            "MG": mg_count if mg_count > 0 else "",
            "Task Force": tf_count if tf_count > 0 else "",
            "Permenant": perm_count if perm_count > 0 else "",
            "Total Budget": b_target,
            "% Actual": pct_actual,
            "Vacation": vac_count,
            "Task Force Vac": tf_vac_count,
            "Sick Leave": sick_count,
            "% Vacation": pct_vacation,
            "Total Operation": total_operation
        })

    # إضافة صف الإجمالي (Total)
    tot_pct_actual = f"{round((tot_actual / tot_budget * 100))}%" if tot_budget > 0 else "0%"
    tot_pct_vac = f"{round(((tot_vac + tot_sick) / tot_actual * 100))}%" if tot_actual > 0 else "0%"
    
    daily_rows.append({
        "Department": "TOTAL",
        "MG": tot_mg,
        "Task Force": tot_task,
        "Permenant": tot_perm,
        "Total Budget": tot_budget,
        "% Actual": tot_pct_actual,
        "Vacation": tot_vac,
        "Task Force Vac": tot_tf_vac,
        "Sick Leave": tot_sick,
        "% Vacation": tot_pct_vac,
        "Total Operation": tot_actual - (tot_vac + tot_sick)
    })

    df_daily_report = pd.DataFrame(daily_rows)
    st.dataframe(get_clean_df(df_daily_report), use_container_width=True, hide_index=True)

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🆕 New Hiring Today")
        if not st.session_state.master_df.empty and "تاريخ التعيين" in st.session_state.master_df.columns:
            nh = st.session_state.master_df[pd.to_datetime(st.session_state.master_df["تاريخ التعيين"]).dt.date == report_date]
            st.dataframe(get_clean_df(nh), use_container_width=True, hide_index=True)
    with c2:
        st.subheader("🚪 Resignations Today")
        if not st.session_state.resignations_df.empty and "تاريخ الاستقالة" in st.session_state.resignations_df.columns:
            rs = st.session_state.resignations_df[pd.to_datetime(st.session_state.resignations_df["تاريخ الاستقالة"]).dt.date == report_date]
            st.dataframe(get_clean_df(rs), use_container_width=True, hide_index=True)

# --- 2. ميزانية العمالة والوظائف التفصيلية (Budget vs Actual) ---
elif choice == "🎯 ميزانية العمالة (Budget Manpower)":
    st.title("🎯 SAHL Hasheesh Manpower Budget vs Actual")

    if not st.session_state.budget_df.empty:
        # حساب الفعلي لكل وظيفة من الماستر
        if not st.session_state.master_df.empty and "الإدارة" in st.session_state.master_df.columns and "الوظيفة" in st.session_state.master_df.columns:
            act_counts = st.session_state.master_df.groupby(["الإدارة", "الوظيفة"]).size().reset_index(name="Actual")
            b_merged = pd.merge(st.session_state.budget_df, act_counts, on=["الإدارة", "الوظيفة"], how="left")
        else:
            b_merged = st.session_state.budget_df.copy()
            b_merged["Actual"] = 0

        b_merged["Target Budget"] = b_merged["Target Budget"].fillna(0).astype(int)
        b_merged["Actual"] = b_merged["Actual"].fillna(0).astype(int)
        b_merged["Diff"] = b_merged["Actual"] - b_merged["Target Budget"]

        st.dataframe(get_clean_df(b_merged[["الإدارة", "الوظيفة", "Target Budget", "Actual", "Diff"]]), use_container_width=True, hide_index=True)
    else:
        st.info("لا توجد بيانات بادجيت مسجلة حالياً.")

# --- 3. شيت الماستر الرئيسي ---
elif choice == "📋 شيت الماستر (Master)":
    st.title("📋 Master Employee List")
    st.dataframe(get_clean_df(st.session_state.master_df), use_container_width=True, hide_index=True)

# --- 4. شيت الإجازات ---
elif choice == "🏝️ شيت الإجازات (Vacations)":
    st.title("🏝️ Vacations & Attendance Movement")
    st.dataframe(get_clean_df(st.session_state.vacations_df), use_container_width=True, hide_index=True)

# --- 5. شيت الاستقالات ---
elif choice == "🚪 شيت الاستقالات (Resignations)":
    st.title("🚪 Resignations & Terminated List")
    st.dataframe(get_clean_df(st.session_state.resignations_df), use_container_width=True, hide_index=True)
