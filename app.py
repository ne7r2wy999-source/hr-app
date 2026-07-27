import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="نظام إدارة الموارد البشرية المتكامل - HR System", page_icon="🏢", layout="wide")

# CSS للتنسيق
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
        border-radius: 6px;
        font-weight: 700;
        background-color: #1f77b4;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# --- 1. قائمة الإدارات المعتمدة ---
DEPARTMENTS = [
    "Executive Office", "Front Office", "Reservation", "Housekeeping", 
    "Recreation", "Laundry", "Food & Beverage", "Kitchen", "Stewarding", 
    "Finance", "Information Technology", "Human Resources", "Security", 
    "Engineering", "Constraction", "Landscape", "Health & Safety", 
    "Pest Control", "Sales & Marketing", "Quality"
]

# --- 2. تهيئة قواعد البيانات في الـ Session State ---

if "master_db" not in st.session_state:
    st.session_state.master_db = pd.DataFrame(columns=["Emp Code", "Name", "Department", "Position", "Type", "Hiring Date", "Status"])

if "budget_db" not in st.session_state:
    st.session_state.budget_db = pd.DataFrame([{"Department": d, "Target Budget": 0} for d in DEPARTMENTS])

if "vacations_db" not in st.session_state:
    st.session_state.vacations_db = pd.DataFrame(columns=["Emp Code", "Name", "Department", "Type", "From Date", "To Date"])

if "resignations_db" not in st.session_state:
    st.session_state.resignations_db = pd.DataFrame(columns=["Emp Code", "Name", "Department", "Position", "Resignation Date", "Reason"])

# --- القائمة الجانبية ورفع الملفات ---
st.sidebar.title("🏢 HR Management System")
st.sidebar.markdown("---")

st.sidebar.subheader("📤 رفع بيانات الشيت الخاص بك")
uploaded_file = st.sidebar.file_uploader("اختر ملف الإكسيل (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    try:
        excel_file = pd.ExcelFile(uploaded_file)
        sheets = excel_file.sheet_names
        
        # قراءة شيت الماستر
        master_sheet = [s for s in sheets if 'master' in s.lower()]
        if master_sheet:
            df_m = pd.read_excel(uploaded_file, sheet_name=master_sheet[0])
            df_m.columns = [str(c).strip() for c in df_m.columns]
            st.session_state.master_db = df_m
            
        # قراءة شيت البادجيت
        budget_sheet = [s for s in sheets if 'budget' in s.lower()]
        if budget_sheet:
            df_b = pd.read_excel(uploaded_file, sheet_name=budget_sheet[0])
            df_b.columns = [str(c).strip() for c in df_b.columns]
            st.session_state.budget_db = df_b

        # قراءة شيت الإجازات
        vac_sheet = [s for s in sheets if 'vacation' in s.lower() or 'leave' in s.lower()]
        if vac_sheet:
            df_v = pd.read_excel(uploaded_file, sheet_name=vac_sheet[0])
            df_v.columns = [str(c).strip() for c in df_v.columns]
            st.session_state.vacations_db = df_v

        # قراءة شيت الاستقالات
        res_sheet = [s for s in sheets if 'resignation' in s.lower() or 'term' in s.lower()]
        if res_sheet:
            df_r = pd.read_excel(uploaded_file, sheet_name=res_sheet[0])
            df_r.columns = [str(c).strip() for c in df_r.columns]
            st.session_state.resignations_db = df_r

        st.sidebar.success("✅ تم تحميل بيانات الشيت وتحديث السيستم بنجاح!")
    except Exception as e:
        st.sidebar.error(f"خطأ أثناء قراءة الملف: {e}")

st.sidebar.markdown("---")

menu = [
    "📊 التقرير اليومي (Daily Report)",
    "➕ إضافة موظف جديد (New Hiring)",
    "🏝️ تسجيل إجازة (Vacation Entry)",
    "🚪 تسجيل استقالة (Resignation Entry)",
    "🎯 ميزانية العمالة (Budget vs Actual)",
    "📋 قاعدة البيانات (Master Database)"
]
choice = st.sidebar.radio("اختر الشاشة أو الإجراء:", menu)

# --- 1. الدايلى ريبورت الديناميكي ---
if choice == "📊 التقرير اليومي (Daily Report)":
    st.title("📊 Daily Report Sheet - Human Resources Department")
    selected_date = st.date_input("📅 تاريخ التقرير:", value=date.today())
    
    # تحديد الإدارات (إما المعتمدة أو الموجودة في البيانات المرفوعة)
    active_depts = DEPARTMENTS
    if not st.session_state.master_db.empty and "Department" in st.session_state.master_db.columns:
        uploaded_depts = st.session_state.master_db["Department"].dropna().unique().tolist()
        active_depts = sorted(list(set(DEPARTMENTS + uploaded_depts)))

    daily_data = []
    
    for dept in active_depts:
        # البادجيت
        t_budget = 0
        if not st.session_state.budget_db.empty and "Department" in st.session_state.budget_db.columns:
            b_match = st.session_state.budget_db[st.session_state.budget_db["Department"] == dept]
            if not b_match.empty and "Target Budget" in b_match.columns:
                t_budget = int(pd.to_numeric(b_match["Target Budget"].values[0], errors='coerce') or 0)
        
        # الماستر
        mg_count = tf_count = perm_count = actual_total = 0
        if not st.session_state.master_db.empty and "Department" in st.session_state.master_db.columns:
            dept_emps = st.session_state.master_db[st.session_state.master_db["Department"] == dept]
            
            # فلترة حسب الحالة إن وجدت
            if "Status" in dept_emps.columns:
                dept_emps = dept_emps[dept_emps["Status"] != "Resigned"]
                
            actual_total = len(dept_emps)
            
            type_col = "Type" if "Type" in dept_emps.columns else ("نوع التعيين" if "نوع التعيين" in dept_emps.columns else None)
            if type_col:
                mg_count = len(dept_emps[dept_emps[type_col].astype(str).str.upper() == "MG"])
                tf_count = len(dept_emps[dept_emps[type_col].astype(str).str.upper().isin(["TASK FORCE", "TASKFORCE"])])
                perm_count = len(dept_emps[dept_emps[type_col].astype(str).str.upper().isin(["PERMENANT", "PERMANENT"])])
            else:
                perm_count = actual_total

        # الإجازات
        vac_count = tf_vac_count = sick_count = 0
        if not st.session_state.vacations_db.empty and "Department" in st.session_state.vacations_db.columns:
            v_dept = st.session_state.vacations_db[st.session_state.vacations_db["Department"] == dept]
            if "From Date" in v_dept.columns and "To Date" in v_dept.columns:
                v_dept = v_dept[
                    (pd.to_datetime(v_dept["From Date"], errors='coerce').dt.date <= selected_date) & 
                    (pd.to_datetime(v_dept["To Date"], errors='coerce').dt.date >= selected_date)
                ]
                v_type_col = "Type" if "Type" in v_dept.columns else "نوع الحركة"
                if v_type_col in v_dept.columns:
                    vac_count = len(v_dept[v_dept[v_type_col].isin(["إجازة", "Vacation", "عارضة"])])
                    tf_vac_count = len(v_dept[v_dept[v_type_col] == "Task Force Vac"])
                    sick_count = len(v_dept[v_dept[v_type_col].isin(["مرضي", "Sick Leave"])])

        # الحسابات
        pct_actual = f"{int(round((actual_total / t_budget) * 100))}%" if t_budget > 0 else "0%"
        pct_vacation = f"{int(round(((vac_count + sick_count) / actual_total) * 100))}%" if actual_total > 0 else "0%"
        total_op = actual_total - (vac_count + sick_count)
        
        daily_data.append({
            "Department": dept,
            "MG": mg_count,
            "Task Force": tf_count,
            "Permenant": perm_count,
            "Actual Total": actual_total,
            "Total Budget": t_budget,
            "% Actual": pct_actual,
            "Vacation": vac_count,
            "Task Force Vac": tf_vac_count,
            "Sick Leave": sick_count,
            "% Vacation": pct_vacation,
            "Total Operation": total_op
        })

    df_daily = pd.DataFrame(daily_data)
    
    # صف الإجمالي (TOTAL)
    tot_mg = df_daily["MG"].sum()
    tot_tf = df_daily["Task Force"].sum()
    tot_perm = df_daily["Permenant"].sum()
    tot_act = df_daily["Actual Total"].sum()
    tot_bud = df_daily["Total Budget"].sum()
    tot_vac = df_daily["Vacation"].sum()
    tot_tf_vac = df_daily["Task Force Vac"].sum()
    tot_sick = df_daily["Sick Leave"].sum()
    tot_op = df_daily["Total Operation"].sum()
    
    tot_pct_act = f"{int(round((tot_act / tot_bud) * 100))}%" if tot_bud > 0 else "0%"
    tot_pct_vac = f"{int(round(((tot_vac + tot_sick) / tot_act) * 100))}%" if tot_act > 0 else "0%"
    
    total_row = pd.DataFrame([{
        "Department": "TOTAL",
        "MG": tot_mg, "Task Force": tot_tf, "Permenant": tot_perm,
        "Actual Total": tot_act, "Total Budget": tot_bud, "% Actual": tot_pct_act,
        "Vacation": tot_vac, "Task Force Vac": tot_tf_vac, "Sick Leave": tot_sick,
        "% Vacation": tot_pct_vac, "Total Operation": tot_op
    }])
    
    full_report = pd.concat([df_daily, total_row], ignore_index=True)
    st.dataframe(full_report, use_container_width=True, hide_index=True)

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🆕 تعيينات اليوم (New Hiring Today)")
        if not st.session_state.master_db.empty and "Hiring Date" in st.session_state.master_db.columns:
            nh = st.session_state.master_db[pd.to_datetime(st.session_state.master_db["Hiring Date"], errors='coerce').dt.date == selected_date]
            st.dataframe(nh, use_container_width=True, hide_index=True) if not nh.empty else st.info("لا توجد تعيينات اليوم.")
        else:
            st.info("لا توجد تعيينات اليوم.")
        
    with c2:
        st.subheader("🚪 استقالات اليوم (Resignations Today)")
        if not st.session_state.resignations_db.empty and "Resignation Date" in st.session_state.resignations_db.columns:
            rs = st.session_state.resignations_db[pd.to_datetime(st.session_state.resignations_db["Resignation Date"], errors='coerce').dt.date == selected_date]
            st.dataframe(rs, use_container_width=True, hide_index=True) if not rs.empty else st.info("لا توجد استقالات اليوم.")
        else:
            st.info("لا توجد استقالات اليوم.")

# --- باقي الشاشات ---
elif choice == "➕ إضافة موظف جديد (New Hiring)":
    st.title("➕ إضافة موظف جديد إلى السيستم")
    with st.form("add_emp_form"):
        col1, col2 = st.columns(2)
        with col1:
            code = st.text_input("كود الموظف (Emp Code)")
            name = st.text_input("اسم الموظف")
            dept = st.selectbox("الإدارة", DEPARTMENTS)
        with col2:
            pos = st.text_input("الوظيفة (Position)")
            emp_type = st.selectbox("نوع التعيين (Type)", ["Permenant", "Task Force", "MG"])
            h_date = st.date_input("تاريخ التعيين", value=date.today())
            
        submit = st.form_submit_button("حفظ الموظف")
        if submit and code and name:
            new_row = {"Emp Code": code, "Name": name, "Department": dept, "Position": pos, "Type": emp_type, "Hiring Date": h_date, "Status": "Active"}
            st.session_state.master_db = pd.concat([st.session_state.master_db, pd.DataFrame([new_row])], ignore_index=True)
            st.success(f"تم إضافة الموظف {name} بنجاح والتأثير في التقرير اليومي!")

elif choice == "🏝️ تسجيل إجازة (Vacation Entry)":
    st.title("🏝️ تسجيل إجازة / حركة حضور")
    st.dataframe(st.session_state.vacations_db, use_container_width=True, hide_index=True)

elif choice == "🚪 تسجيل استقالة (Resignation Entry)":
    st.title("🚪 تسجيل استقالة / إنهاء خدمة")
    st.dataframe(st.session_state.resignations_db, use_container_width=True, hide_index=True)

elif choice == "🎯 ميزانية العمالة (Budget vs Actual)":
    st.title("🎯 Manpower Budget vs Actual")
    st.dataframe(st.session_state.budget_db, use_container_width=True, hide_index=True)

elif choice == "📋 قاعدة البيانات (Master Database)":
    st.title("📋 Master Employee Database")
    st.dataframe(st.session_state.master_db, use_container_width=True, hide_index=True)
