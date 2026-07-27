import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="HR Operational System", page_icon="📊", layout="wide")

# CSS بسيط للاتجاه والتنسيق
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }
    .stButton>button { width: 100%; font-weight: bold; background-color: #1f77b4; color: white; }
    </style>
""", unsafe_allow_html=True)

# تهيئة الـ Session State
if "master_df" not in st.session_state:
    st.session_state.master_df = pd.DataFrame()
if "budget_df" not in st.session_state:
    st.session_state.budget_df = pd.DataFrame()
if "vacations_df" not in st.session_state:
    st.session_state.vacations_df = pd.DataFrame()
if "resignations_df" not in st.session_state:
    st.session_state.resignations_df = pd.DataFrame()

# القائمة الجانبية
st.sidebar.title("📁 التحكم والرفع")
uploaded_file = st.sidebar.file_uploader("رفع ملف الإكسيل الأصلي (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    try:
        excel_file = pd.ExcelFile(uploaded_file)
        sheets = excel_file.sheet_names
        
        # قراءة الشيتات بدون تعديل أي اسم عمود اطلاقاً
        for sheet in sheets:
            s_clean = sheet.strip().lower()
            if 'master' in s_clean:
                st.session_state.master_df = pd.read_excel(uploaded_file, sheet_name=sheet)
            elif 'budget' in s_clean:
                st.session_state.budget_df = pd.read_excel(uploaded_file, sheet_name=sheet)
            elif 'vacation' in s_clean or 'إجازات' in s_clean or 'leave' in s_clean:
                st.session_state.vacations_df = pd.read_excel(uploaded_file, sheet_name=sheet)
            elif 'resignation' in s_clean or 'استقالات' in s_clean:
                st.session_state.resignations_df = pd.read_excel(uploaded_file, sheet_name=sheet)

        st.sidebar.success("✅ تم تحميل الملف بنفس أسماء الأعمدة والشيتات الأصلية!")
    except Exception as e:
        st.sidebar.error(f"خطأ أثناء قراءة الملف: {e}")

st.sidebar.markdown("---")
menu = [
    "📊 الدايلى ريبورت (Daily Report)",
    "➕ إضافة تعيين جديد",
    "🏝️ تسجيل إجازة",
    "🚪 تسجيل استقالة",
    "🎯 شيت البادجيت (Budget)",
    "📋 شيت الماستر (Master)"
]
choice = st.sidebar.radio("اختر القائمة:", menu)

# --- 1. الدايلى ريبورت ---
if choice == "📊 الدايلى ريبورت (Daily Report)":
    st.title("📊 HR Daily Report")
    selected_date = st.date_input("تاريخ التقرير:", value=date.today())
    
    if st.session_state.master_df.empty and st.session_state.budget_df.empty:
        st.info("👈 يرجى رفع ملف الإكسيل من القائمة الجانبية لعرض التقرير ببياناتك الأصلية.")
    else:
        # البحث عن عمود الإدارة من الأعمدة الحقيقية الموجودة في الملف
        master_cols = st.session_state.master_df.columns.tolist() if not st.session_state.master_df.empty else []
        budget_cols = st.session_state.budget_df.columns.tolist() if not st.session_state.budget_df.empty else []
        
        dept_col_m = next((c for c in master_cols if 'dept' in str(c).lower() or 'إدارة' in str(c).lower() or 'department' in str(c).lower()), master_cols[0] if master_cols else None)
        dept_col_b = next((c for c in budget_cols if 'dept' in str(c).lower() or 'إدارة' in str(c).lower() or 'department' in str(c).lower()), budget_cols[0] if budget_cols else None)
        
        depts_m = st.session_state.master_df[dept_col_m].dropna().unique().tolist() if dept_col_m else []
        depts_b = st.session_state.budget_df[dept_col_b].dropna().unique().tolist() if dept_col_b else []
        all_depts = sorted(list(set(depts_m + depts_b)))

        # تجميع البيانات بنفس الأعمدة المطلوبة للتقرير اليومي
        daily_rows = []
        for d in all_depts:
            # حساب الفعلي من الماستر
            act_count = 0
            if dept_col_m:
                act_count = len(st.session_state.master_df[st.session_state.master_df[dept_col_m] == d])
            
            # حساب البادجيت
            bud_val = 0
            if dept_col_b:
                bud_col_target = next((c for c in budget_cols if 'budget' in str(c).lower() or 'ميزانية' in str(c).lower() or 'target' in str(c).lower()), None)
                if bud_col_target:
                    bud_val = pd.to_numeric(st.session_state.budget_df[st.session_state.budget_df[dept_col_b] == d][bud_col_target], errors='coerce').sum()

            pct_act = f"{int(round((act_count / bud_val) * 100))}%" if bud_val > 0 else "0%"

            daily_rows.append({
                "Department": d,
                "Actual Total": act_count,
                "Total Budget": int(bud_val),
                "% Actual": pct_act
            })

        df_daily = pd.DataFrame(daily_rows)
        st.dataframe(df_daily, use_container_width=True, hide_index=True)

# --- 2. باقي الشاشات لعرض الشيتات الخام كما هي بالظبط ---
elif choice == "🎯 شيت البادجيت (Budget)":
    st.title("🎯 شيت البادجيت الأصلي")
    st.dataframe(st.session_state.budget_df, use_container_width=True, hide_index=True)

elif choice == "📋 شيت الماستر (Master)":
    st.title("📋 شيت الماستر الأصلي")
    st.dataframe(st.session_state.master_df, use_container_width=True, hide_index=True)

elif choice == "➕ إضافة تعيين جديد":
    st.title("➕ إضافة موظف إلى شيت الماستر")
    if not st.session_state.master_df.empty:
        cols = st.session_state.master_df.columns
        with st.form("add_form"):
            inputs = {}
            for col in cols:
                inputs[col] = st.text_input(f"{col}")
            submit = st.form_submit_button("حفظ الموظف")
            if submit:
                st.session_state.master_df = pd.concat([st.session_state.master_df, pd.DataFrame([inputs])], ignore_index=True)
                st.success("تم التحديث في شيت الماستر بنجاح!")

elif choice == "🏝️ تسجيل إجازة":
    st.title("🏝️ شيت الإجازات")
    st.dataframe(st.session_state.vacations_df, use_container_width=True, hide_index=True)

elif choice == "🚪 تسجيل استقالة":
    st.title("🚪 شيت الاستقالات")
    st.dataframe(st.session_state.resignations_df, use_container_width=True, hide_index=True)
