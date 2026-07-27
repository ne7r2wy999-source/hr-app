import streamlit as st
import pandas as pd
from datetime import date, datetime

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

# --- 1. قائمة الإدارات المعتمدة بالكامل ---
DEPARTMENTS = [
    "Executive Office", "Front Office", "Reservation", "Housekeeping", 
    "Recreation", "Laundry", "Food & Beverage", "Kitchen", "Stewarding", 
    "Finance", "Information Technology", "Human Resources", "Security", 
    "Engineering", "Constraction", "Landscape", "Health & Safety", 
    "Pest Control", "Sales & Marketing", "Quality"
]

# --- 2. تهيئة قاعدة البيانات في الـ Session State ---

if "master_db" not in st.session_state:
    st.session_state.master_db = pd.DataFrame([
        {"Emp Code": "101", "Name": "أحمد محمود علي", "Department": "Executive Office", "Position": "Hotel Manager", "Type": "Permenant", "Hiring Date": date(2025, 1, 15), "Status": "Active"},
        {"Emp Code": "102", "Name": "محمد مصطفى كامل", "Department": "Information Technology", "Position": "Director of IT", "Type": "Permenant", "Hiring Date": date(2026, 7, 27), "Status": "Active"},
        {"Emp Code": "103", "Name": "سارة أحمد حسن", "Department": "Housekeeping", "Position": "Housekeeper", "Type": "Task Force", "Hiring Date": date(2026, 2, 10), "Status": "Active"},
        {"Emp Code": "104", "Name": "محمود السيد", "Department": "Food & Beverage", "Position": "Waiter", "Type": "MG", "Hiring Date": date(2026, 5, 1), "Status": "Active"}
    ])

if "budget_db" not in st.session_state:
    # البادجيت المستهدف لكل إدارة
    st.session_state.budget_db = pd.DataFrame([
        {"Department": "Executive Office", "Target Budget": 4},
        {"Department": "Front Office", "Target Budget": 15},
        {"Department": "Reservation", "Target Budget": 0},
        {"Department": "Housekeeping", "Target Budget": 57},
        {"Department": "Recreation", "Target Budget": 13},
        {"Department": "Laundry", "Target Budget": 0},
        {"Department": "Food & Beverage", "Target Budget": 45},
        {"Department": "Kitchen", "Target Budget": 40},
        {"Department": "Stewarding", "Target Budget": 30},
        {"Department": "Finance", "Target Budget": 28},
        {"Department": "Information Technology", "Target Budget": 6},
        {"Department": "Human Resources", "Target Budget": 31},
        {"Department": "Security", "Target Budget": 31},
        {"Department": "Engineering", "Target Budget": 31},
        {"Department": "Constraction", "Target Budget": 6},
        {"Department": "Landscape", "Target Budget": 0},
        {"Department": "Health & Safety", "Target Budget": 2},
        {"Department": "Pest Control", "Target Budget": 3},
        {"Department": "Sales & Marketing", "Target Budget": 1},
        {"Department": "Quality", "Target Budget": 0}
    ])

if "vacations_db" not in st.session_state:
    st.session_state.vacations_db = pd.DataFrame(columns=[
        "Emp Code", "Name", "Department", "Type", "From Date", "To Date"
    ])

if "resignations_db" not in st.session_state:
    st.session_state.resignations_db = pd.DataFrame(columns=[
        "Emp Code", "Name", "Department", "Position", "Resignation Date", "Reason"
    ])

# --- القائمة الجانبية للتنقل والعمليات ---
st.sidebar.title("🏢 HR Management System")
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

# --- 1. الشاشة الأولى: الدايلى ريبورت الديناميكي التفاعلي ---
if choice == "📊 التقرير اليومي (Daily Report)":
    st.title("📊 Daily Report Sheet - Human Resources Department")
    selected_date = st.date_input("📅 تاريخ التقرير:", value=date.today())
    
    daily_data = []
    
    for dept in DEPARTMENTS:
        # جلب المستهدف من البادجيت
        b_match = st.session_state.budget_db[st.session_state.budget_db["Department"] == dept]
        t_budget = int(b_match["Target Budget"].values[0]) if not b_match.empty else 0
        
        # حساب الموظفين النشطين في الماستر للإدارة
        dept_emps = st.session_state.master_db[
            (st.session_state.master_db["Department"] == dept) & 
            (st.session_state.master_db["Status"] == "Active")
        ]
        
        mg_count = len(dept_emps[dept_emps["Type"] == "MG"])
        tf_count = len(dept_emps[dept_emps["Type"] == "Task Force"])
        perm_count = len(dept_emps[dept_emps["Type"] == "Permenant"])
        actual_total = len(dept_emps)
        
        # حساب الإجازات والغياب في هذا اليوم المحدد
        if not st.session_state.vacations_db.empty:
            v_dept = st.session_state.vacations_db[
                (st.session_state.vacations_db["Department"] == dept) & 
                (pd.to_datetime(st.session_state.vacations_db["From Date"]).dt.date <= selected_date) & 
                (pd.to_datetime(st.session_state.vacations_db["To Date"]).dt.date >= selected_date)
            ]
            vac_count = len(v_dept[v_dept["Type"].isin(["إجازة", "Vacation", "عارضة"])])
            tf_vac_count = len(v_dept[v_dept["Type"] == "Task Force Vac"])
            sick_count = len(v_dept[v_dept["Type"].isin(["مرضي", "Sick Leave"])])
        else:
            vac_count = tf_vac_count = sick_count = 0
            
        # حساب المعادلات
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
        nh = st.session_state.master_db[st.session_state.master_db["Hiring Date"] == selected_date]
        st.dataframe(nh, use_container_width=True, hide_index=True) if not nh.empty else st.info("لا توجد تعيينات اليوم.")
        
    with c2:
        st.subheader("🚪 استقالات اليوم (Resignations Today)")
        if not st.session_state.resignations_db.empty:
            rs = st.session_state.resignations_db[st.session_state.resignations_db["Resignation Date"] == selected_date]
            st.dataframe(rs, use_container_width=True, hide_index=True) if not rs.empty else st.info("لا توجد استقالات اليوم.")
        else:
            st.info("لا توجد استقالات اليوم.")

# --- 2. إضافة موظف جديد ---
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
        if submit:
            if code and name:
                new_row = {"Emp Code": code, "Name": name, "Department": dept, "Position": pos, "Type": emp_type, "Hiring Date": h_date, "Status": "Active"}
                st.session_state.master_db = pd.concat([st.session_state.master_db, pd.DataFrame([new_row])], ignore_index=True)
                st.success(f"تم إضافة الموظف {name} بنجاح والتأثير في التقرير اليومي!")
            else:
                st.error("يرجى ملء كافة البيانات المطلوبة.")

# --- 3. تسجيل إجازة ---
elif choice == "🏝️ تسجيل إجازة (Vacation Entry)":
    st.title("🏝️ تسجيل إجازة / حركة حضور")
    active_emps = st.session_state.master_db[st.session_state.master_db["Status"] == "Active"]
    
    if not active_emps.empty:
        emp_choice = st.selectbox("اختر الموظف:", active_emps["Emp Code"].astype(str) + " - " + active_emps["Name"])
        emp_code = emp_choice.split(" - ")[0]
        emp_info = active_emps[active_emps["Emp Code"] == emp_code].iloc[0]
        
        with st.form("vac_form"):
            vac_type = st.selectbox("نوع الحركة", ["Vacation", "Sick Leave", "Task Force Vac"])
            f_date = st.date_input("من تاريخ", value=date.today())
            t_date = st.date_input("إلى تاريخ", value=date.today())
            
            sub = st.form_submit_button("تسجيل الإجازة")
            if sub:
                vac_row = {"Emp Code": emp_code, "Name": emp_info["Name"], "Department": emp_info["Department"], "Type": vac_type, "From Date": f_date, "To Date": t_date}
                st.session_state.vacations_db = pd.concat([st.session_state.vacations_db, pd.DataFrame([vac_row])], ignore_index=True)
                st.success("تم تسجيل الإجازة بنجاح!")
    else:
        st.warning("لا يوجد موظفين مسجلين.")

# --- 4. تسجيل استقالة ---
elif choice == "🚪 تسجيل استقالة (Resignation Entry)":
    st.title("🚪 تسجيل استقالة / إنهاء خدمة")
    active_emps = st.session_state.master_db[st.session_state.master_db["Status"] == "Active"]
    
    if not active_emps.empty:
        emp_choice = st.selectbox("اختر الموظف الاستقالة:", active_emps["Emp Code"].astype(str) + " - " + active_emps["Name"])
        emp_code = emp_choice.split(" - ")[0]
        emp_info = active_emps[active_emps["Emp Code"] == emp_code].iloc[0]
        
        with st.form("res_form"):
            res_date = st.date_input("تاريخ الاستقالة", value=date.today())
            reason = st.text_area("سبب الاستقالة")
            
            sub = st.form_submit_button("تأكيد الاستقالة")
            if sub:
                # تحويل حالة الموظف لـ Resigned
                st.session_state.master_db.loc[st.session_state.master_db["Emp Code"] == emp_code, "Status"] = "Resigned"
                res_row = {"Emp Code": emp_code, "Name": emp_info["Name"], "Department": emp_info["Department"], "Position": emp_info["Position"], "Resignation Date": res_date, "Reason": reason}
                st.session_state.resignations_db = pd.concat([st.session_state.resignations_db, pd.DataFrame([res_row])], ignore_index=True)
                st.success("تم تسوية استقالة الموظف وتحديث الدايلى ريبورت!")

# --- 5. ميزانية العمالة ---
elif choice == "🎯 ميزانية العمالة (Budget vs Actual)":
    st.title("🎯 Manpower Budget vs Actual")
    
    act_by_dept = st.session_state.master_db[st.session_state.master_db["Status"] == "Active"].groupby("Department").size().reset_index(name="Actual")
    merged_budget = pd.merge(st.session_state.budget_db, act_by_dept, on="Department", how="left").fillna(0)
    merged_budget["Actual"] = merged_budget["Actual"].astype(int)
    merged_budget["Diff"] = merged_budget["Actual"] - merged_budget["Target Budget"]
    
    st.dataframe(merged_budget, use_container_width=True, hide_index=True)

# --- 6. قاعدة البيانات الماستر ---
elif choice == "📋 قاعدة البيانات (Master Database)":
    st.title("📋 Master Employee Database")
    st.dataframe(st.session_state.master_db, use_container_width=True, hide_index=True)
