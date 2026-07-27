import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="نظام إدارة الموارد البشرية HR - Daily & Budget", page_icon="🏢", layout="wide")

# التنسيق والتصميم العربي
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

# --- 1. البيانات الأساسية المدمجة طبقاً للملفات المرفقة ---

INITIAL_DAILY_DATA = [
    {"Department": "Executive Office", "MG": 5, "Task Force": 0, "Permenant": 3, "Total Budget": 4, "Vacation": 0, "Task Force Vac": 0, "Sick Leave": 0},
    {"Department": "Front Office", "MG": 22, "Task Force": 3, "Permenant": 12, "Total Budget": 15, "Vacation": 0, "Task Force Vac": 0, "Sick Leave": 0},
    {"Department": "Reservation", "MG": 0, "Task Force": 0, "Permenant": 0, "Total Budget": 0, "Vacation": 0, "Task Force Vac": 0, "Sick Leave": 0},
    {"Department": "Housekeeping", "MG": 60, "Task Force": 1, "Permenant": 56, "Total Budget": 57, "Vacation": 0, "Task Force Vac": 10, "Sick Leave": 0},
    {"Department": "Recreation", "MG": 19, "Task Force": 0, "Permenant": 13, "Total Budget": 13, "Vacation": 0, "Task Force Vac": 0, "Sick Leave": 0},
    {"Department": "Laundry", "MG": 12, "Task Force": 0, "Permenant": 0, "Total Budget": 0, "Vacation": 0, "Task Force Vac": 0, "Sick Leave": 0},
    {"Department": "Food & Beverage", "MG": 85, "Task Force": 0, "Permenant": 45, "Total Budget": 45, "Vacation": 0, "Task Force Vac": 0, "Sick Leave": 0},
    {"Department": "Kitchen", "MG": 58, "Task Force": 0, "Permenant": 40, "Total Budget": 40, "Vacation": 0, "Task Force Vac": 0, "Sick Leave": 0},
    {"Department": "Stewarding", "MG": 37, "Task Force": 1, "Permenant": 30, "Total Budget": 30, "Vacation": 0, "Task Force Vac": 10, "Sick Leave": 0},
    {"Department": "Finance", "MG": 35, "Task Force": 0, "Permenant": 27, "Total Budget": 28, "Vacation": 0, "Task Force Vac": 0, "Sick Leave": 0},
    {"Department": "Information Technology", "MG": 9, "Task Force": 2, "Permenant": 6, "Total Budget": 6, "Vacation": 0, "Task Force Vac": 0, "Sick Leave": 0},
    {"Department": "Human Resources", "MG": 32, "Task Force": 5, "Permenant": 23, "Total Budget": 31, "Vacation": 0, "Task Force Vac": 0, "Sick Leave": 0},
    {"Department": "Security", "MG": 39, "Task Force": 6, "Permenant": 29, "Total Budget": 31, "Vacation": 0, "Task Force Vac": 0, "Sick Leave": 0},
    {"Department": "Engineering", "MG": 26, "Task Force": 0, "Permenant": 26, "Total Budget": 31, "Vacation": 0, "Task Force Vac": 10, "Sick Leave": 0},
    {"Department": "Constraction", "MG": 0, "Task Force": 0, "Permenant": 0, "Total Budget": 6, "Vacation": 0, "Task Force Vac": 0, "Sick Leave": 0},
    {"Department": "Landscape", "MG": 6, "Task Force": 0, "Permenant": 0, "Total Budget": 0, "Vacation": 0, "Task Force Vac": 0, "Sick Leave": 0},
    {"Department": "Health & Safety", "MG": 5, "Task Force": 1, "Permenant": 1, "Total Budget": 2, "Vacation": 0, "Task Force Vac": 0, "Sick Leave": 0},
    {"Department": "Pest Control", "MG": 5, "Task Force": 0, "Permenant": 3, "Total Budget": 3, "Vacation": 0, "Task Force Vac": 0, "Sick Leave": 0},
    {"Department": "Sales & Marketing", "MG": 1, "Task Force": 0, "Permenant": 1, "Total Budget": 1, "Vacation": 0, "Task Force Vac": 0, "Sick Leave": 0},
    {"Department": "Quality", "MG": 1, "Task Force": 0, "Permenant": 0, "Total Budget": 0, "Vacation": 0, "Task Force Vac": 0, "Sick Leave": 0}
]

# تهيئة الـ Session State
if "daily_db" not in st.session_state:
    st.session_state.daily_db = pd.DataFrame(INITIAL_DAILY_DATA)

# --- القائمة الجانبية ---
st.sidebar.title("🏢 HR Daily & Budget System")
st.sidebar.markdown("---")

menu = [
    "📊 التقرير اليومي (Daily Report)",
    "🎯 ميزانية العمالة (Budget Manpower)",
    "📋 شيت الماستر (Master)",
    "🏝️ شيت الإجازات (Vacations)",
    "🚪 شيت الاستقالات (Resignations)"
]
choice = st.sidebar.radio("اختر الشاشة:", menu)

# --- 1. الشاشة الأولى: الدايلى ريبورت (Daily Report) ---
if choice == "📊 التقرير اليومي (Daily Report)":
    st.title("📊 Daily Report Sheet - Human Resources Department")
    report_date = st.date_input("📅 Date:", value=date(2026, 7, 27))
    
    df = st.session_state.daily_db.copy()
    
    # حساب الأعمدة التفاعلية والمعادلات
    df["Actual Total"] = df["Task Force"] + df["Permenant"]
    
    # حساب نسبة % Actual مع حماية القسمة على صفر
    df["% Actual"] = df.apply(
        lambda r: f"{int(round((r['Actual Total'] / r['Total Budget']) * 100))}%" if r['Total Budget'] > 0 else "0%", axis=1
    )
    
    # حساب Total Operation
    df["Total Operation"] = df["Actual Total"] - (df["Vacation"] + df["Sick Leave"])
    
    # حساب % Vacation
    df["% Vacation"] = df.apply(
        lambda r: f"{int(round(((r['Vacation'] + r['Sick Leave']) / r['Actual Total']) * 100))}%" if r['Actual Total'] > 0 else "0%", axis=1
    )
    
    # ترتيب الأعمدة بالظبط زي الملف الأصلي
    df_display = df[[
        "Department", "MG", "Task Force", "Permenant", "Actual Total",
        "Total Budget", "% Actual", "Vacation", "Task Force Vac", 
        "Sick Leave", "% Vacation", "Total Operation"
    ]]
    
    # حساب صف الإجمالي Total
    tot_mg = df["MG"].sum()
    tot_tf = df["Task Force"].sum()
    tot_perm = df["Permenant"].sum()
    tot_actual = df["Actual Total"].sum()
    tot_budget = df["Total Budget"].sum()
    tot_vac = df["Vacation"].sum()
    tot_tf_vac = df["Task Force Vac"].sum()
    tot_sick = df["Sick Leave"].sum()
    tot_op = df["Total Operation"].sum()
    
    pct_actual_tot = f"{int(round((tot_actual / tot_budget) * 100))}%" if tot_budget > 0 else "0%"
    pct_vac_tot = f"{int(round(((tot_vac + tot_sick) / tot_actual) * 100))}%" if tot_actual > 0 else "0%"
    
    total_row = pd.DataFrame([{
        "Department": "TOTAL",
        "MG": tot_mg,
        "Task Force": tot_tf,
        "Permenant": tot_perm,
        "Actual Total": tot_actual,
        "Total Budget": tot_budget,
        "% Actual": pct_actual_tot,
        "Vacation": tot_vac,
        "Task Force Vac": tot_tf_vac,
        "Sick Leave": tot_sick,
        "% Vacation": pct_vac_tot,
        "Total Operation": tot_op
    }])
    
    df_final = pd.concat([df_display, total_row], ignore_index=True)
    
    st.dataframe(df_final, use_container_width=True, hide_index=True)

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🆕 New Hiring")
        st.table(pd.DataFrame([{"Name": "—", "Dept.": "—", "Position": "—", "Hiring Date": "—"}]))
    with col2:
        st.subheader("Outsider / Driver & Workers")
        st.table(pd.DataFrame([{"Category": "Driver", "No. of Staff": 4}, {"Category": "Worker / New Hiring", "No. of Staff": 20}, {"Category": "Total", "No. of Staff": 24}]))

# --- 2. باقي الشاشات للتنقل السريع ---
elif choice == "🎯 ميزانية العمالة (Budget Manpower)":
    st.title("🎯 SAHL Hasheesh Manpower 2025/2026")
    st.info("يتم عرض شيت البادجيت والـ Diff لكل وظيفة تفصيلياً.")

elif choice == "📋 شيت الماستر (Master)":
    st.title("📋 Employee Master List")
    st.info("شيت الماستر الخاص ببيانات جميع العاملين.")

elif choice == "🏝️ شيت الإجازات (Vacations)":
    st.title("🏝️ Vacations & Attendance")
    st.info("شيت تسجيل حركة الإجازات والغياب.")

elif choice == "🚪 شيت الاستقالات (Resignations)":
    st.title("🚪 Resignations List")
    st.info("شيت تسجيل الاستقالات والإنهاءات.")
