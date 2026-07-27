import streamlit as st
import pandas as pd
from datetime import date, datetime

st.set_page_config(page_title="نظام إدارة الموارد البشرية HR", page_icon="🏢", layout="wide")

# CSS للتنسيق والدعم العربي
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

# --- 1. تهيئة قواعد البيانات الداخليّة (Session State) ---

if "master_df" not in st.session_state:
    st.session_state.master_df = pd.DataFrame([
        {"كود الموظف": "101", "الاسم": "أحمد محمود علي", "الإدارة": "الموارد البشرية", "الوظيفة": "أخصائي HR", "تاريخ التعيين": date(2025, 1, 15), "الراتب": 12000.0, "الحالة": "Active"},
        {"كود الموظف": "102", "الاسم": "محمد مصطفى كامل", "الإدارة": "تكنولوجيا المعلومات", "الوظيفة": "مطور برمجيات", "تاريخ التعيين": date(2026, 7, 27), "الراتب": 18000.0, "الحالة": "Active"},
        {"كود الموظف": "103", "الاسم": "سارة أحمد حسن", "الإدارة": "العمليات", "الوظيفة": "خدمة عملاء", "تاريخ التعيين": date(2024, 3, 10), "الراتب": 8000.0, "الحالة": "Active"}
    ])

if "vacations_df" not in st.session_state:
    st.session_state.vacations_df = pd.DataFrame([
        {"كود الموظف": "103", "الاسم": "سارة أحمد حسن", "الإدارة": "العمليات", "الوظيفة": "خدمة عملاء", "نوع الحركة": "إجازة", "التاريخ": date(2026, 7, 27)}
    ])

if "resignations_df" not in st.session_state:
    st.session_state.resignations_df = pd.DataFrame(columns=["كود الموظف", "الاسم", "الإدارة", "الوظيفة", "تاريخ التعيين", "تاريخ الاستقالة"])

if "budget_df" not in st.session_state:
    st.session_state.budget_df = pd.DataFrame([
        {"الإدارة": "الموارد البشرية", "الوظيفة": "أخصائي HR", "الميزانية (Budget)": 2},
        {"الإدارة": "تكنولوجيا المعلومات", "الوظيفة": "مطور برمجيات", "الميزانية (Budget)": 3},
        {"الإدارة": "العمليات", "الوظيفة": "خدمة عملاء", "الميزانية (Budget)": 5}
    ])

# دالة لتحويل DataFrame إلى إكسيل للتنزيل
def convert_df_to_excel(df):
    import io
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Data')
    return output.getvalue()

# --- القائمة الجانبية ---
st.sidebar.title("🏢 نظام الـ HR الموحد")
menu = [
    "📋 شيت الماستر (Master)",
    "🏝️ شيت الإجازات (Vacations)",
    "🚪 شيت الاستقالات (Resignations)",
    "🎯 شيت البادجيت (Budget)",
    "📊 التقرير اليومي (Daily Report)"
]
choice = st.sidebar.radio("اختر الشاشة:", menu)

# --- 1. شيت الماستر ---
if choice == "📋 شيت الماستر (Master)":
    st.title("📋 إدارة بيانات الموظفين (المستند الرئيسي - Master)")
    
    with st.expander("➕ إضافة موظف جديد إلى الماستر", expanded=False):
        with st.form("add_master_form"):
            c1, c2, c3 = st.columns(3)
            code = c1.text_input("كود الموظف *")
            name = c2.text_input("الاسم بالكامل *")
            dept = c3.text_input("الإدارة *")
            
            c4, c5, c6 = st.columns(3)
            pos = c4.text_input("الوظيفة *")
            hiring_date = c5.date_input("تاريخ التعيين", value=date.today())
            salary = c6.number_input("الراتب", min_value=0.0, step=500.0)
            
            if st.form_submit_button("حفظ الموظف"):
                if code and name and dept and pos:
                    if str(code) in st.session_state.master_df["كود الموظف"].astype(str).values:
                        st.error("⚠️ كود الموظف موجود بالفعل في الماستر!")
                    else:
                        new_emp = {
                            "كود الموظف": str(code), "الاسم": name, "الإدارة": dept,
                            "الوظيفة": pos, "تاريخ التعيين": hiring_date, "الراتب": salary, "الحالة": "Active"
                        }
                        st.session_state.master_df = pd.concat([st.session_state.master_df, pd.DataFrame([new_emp])], ignore_index=True)
                        st.success(f"تم إضافة الموظف {name} بنجاح إلى شيت الماستر!")
                        st.rerun()
                else:
                    st.warning("يرجى ملء جميع الحقول المطلوبة.")

    st.subheader("👥 قائمة الموظفين الحاليين (Active Only)")
    st.dataframe(st.session_state.master_df, use_container_width=True, hide_index=True)
    
    # تحميل إكسيل
    excel_data = convert_df_to_excel(st.session_state.master_df)
    st.download_button("📥 تحميل شيت الماستر (Excel)", data=excel_data, file_name="Master_Data.xlsx", mime="application/vnd.ms-excel")

# --- 2. شيت الإجازات ---
elif choice == "🏝️ شيت الإجازات (Vacations)":
    st.title("🏝️ تسجيل وحركات الإجازات والغياب")
    
    with st.form("add_vacation_form"):
        st.subheader("➕ إضافة حركة جديدة لموظف")
        emp_codes = st.session_state.master_df["كود الموظف"].tolist()
        
        selected_code = st.selectbox("اختر كود الموظف", emp_codes if emp_codes else ["لا يوجد موظفين"])
        
        if emp_codes:
            emp_info = st.session_state.master_df[st.session_state.master_df["كود الموظف"] == selected_code].iloc[0]
            st.info(f"👤 الموظف: **{emp_info['الاسم']}** | الإدارة: **{emp_info['الإدارة']}** | الوظيفة: **{emp_info['الوظيفة']}**")
            
            col1, col2 = st.columns(2)
            vac_type = col1.selectbox("نوع الحركة", ["إجازة", "مرضي", "غياب", "عارضة", "بدون أجر"])
            vac_date = col2.date_input("تاريخ الحركة", value=date.today())
            
            if st.form_submit_button("تسجيل الحركة"):
                new_vac = {
                    "كود الموظف": str(selected_code),
                    "الاسم": emp_info["الاسم"],
                    "الإدارة": emp_info["الإدارة"],
                    "الوظيفة": emp_info["الوظيفة"],
                    "نوع الحركة": vac_type,
                    "التاريخ": vac_date
                }
                st.session_state.vacations_df = pd.concat([st.session_state.vacations_df, pd.DataFrame([new_vac])], ignore_index=True)
                st.success("تم تسجيل الحركة بنجاح!")
                st.rerun()

    st.subheader("📜 سجل الإجازات والحركات الكامل")
    st.dataframe(st.session_state.vacations_df, use_container_width=True, hide_index=True)
    
    excel_vac = convert_df_to_excel(st.session_state.vacations_df)
    st.download_button("📥 تحميل شيت الإجازات (Excel)", data=excel_vac, file_name="Vacations_Data.xlsx", mime="application/vnd.ms-excel")

# --- 3. شيت الاستقالات ---
elif choice == "🚪 شيت الاستقالات (Resignations)":
    st.title("🚪 تسجيل الاستقالات ونقل الموظفين")
    
    st.write("عند تأكيد استقالة موظف، يتم تحويل بياناته لشيت الاستقالات وحذفه تلقائياً من شيت الماستر.")
    
    emp_codes = st.session_state.master_df["كود الموظف"].tolist()
    
    if emp_codes:
        selected_code = st.selectbox("اختر كود الموظف المستقيل", emp_codes)
        emp_info = st.session_state.master_df[st.session_state.master_df["كود الموظف"] == selected_code].iloc[0]
        
        st.warning(f"⚠️ الموظف المحدد: **{emp_info['الاسم']}** ({emp_info['الإدارة']} - {emp_info['الوظيفة']})")
        res_date = st.date_input("تاريخ الاستقالة", value=date.today())
        
        if st.button("🚨 تأكيد الاستقالة ونقل الموظف"):
            # 1. إضافته لشيت الاستقالات
            res_data = {
                "كود الموظف": str(selected_code),
                "الاسم": emp_info["الاسم"],
                "الإدارة": emp_info["الإدارة"],
                "الوظيفة": emp_info["الوظيفة"],
                "تاريخ التعيين": emp_info["تاريخ التعيين"],
                "تاريخ الاستقالة": res_date
            }
            st.session_state.resignations_df = pd.concat([st.session_state.resignations_df, pd.DataFrame([res_data])], ignore_index=True)
            
            # 2. حذفه من الماستر
            st.session_state.master_df = st.session_state.master_df[st.session_state.master_df["كود الموظف"] != selected_code]
            
            st.success(f"تم نقل الموظف {emp_info['الاسم']} إلى شيت الاستقالات وحذفه من الماستر بنجاح!")
            st.rerun()
    else:
        st.info("لا يوجد موظفين حاليين في شيت الماستر.")

    st.subheader("📜 سجل الموظفين المستقيلين (Resignations Sheet)")
    st.dataframe(st.session_state.resignations_df, use_container_width=True, hide_index=True)
    
    excel_res = convert_df_to_excel(st.session_state.resignations_df)
    st.download_button("📥 تحميل شيت الاستقالات (Excel)", data=excel_res, file_name="Resignations_Data.xlsx", mime="application/vnd.ms-excel")

# --- 4. شيت البادجيت ---
elif choice == "🎯 شيت البادجيت (Budget)":
    st.title("🎯 الميزانية الشاغرة (Budget vs Actual)")
    
    # حساب الأكتوال ديناميكياً من شيت الماستر
    master_counts = st.session_state.master_df.groupby(["الإدارة", "الوظيفة"]).size().reset_index(name="الفعلي (Actual)")
    
    budget_merged = pd.merge(st.session_state.budget_df, master_counts, on=["الإدارة", "الوظيفة"], how="left")
    budget_merged["الفعلي (Actual)"] = budget_merged["الفعلي (Actual)"].fillna(0).astype(int)
    budget_merged["الشواغر (Vacancy)"] = budget_merged["الميزانية (Budget)"] - budget_merged["الفعلي (Actual)"]
    
    st.dataframe(budget_merged, use_container_width=True, hide_index=True)

# --- 5. الدايلى ريبورت ---
elif choice == "📊 التقرير اليومي (Daily Report)":
    st.title("📊 التقرير اليومي الشامل (Daily Report)")
    
    report_date = st.date_input("🗓️ اختر تاريخ التقرير اليومي:", value=date.today())
    st.markdown(f"### 📈 تقرير حركة العمل يوم: `{report_date}`")
    
    # 1. تجهيز بيانات الإدارات
    depts = st.session_state.budget_df["الإدارة"].unique()
    daily_summary = []
    
    for dept in depts:
        # Budget
        dept_budget = st.session_state.budget_df[st.session_state.budget_df["الإدارة"] == dept]["الميزانية (Budget)"].sum()
        # Actual من الماستر
        dept_actual = len(st.session_state.master_df[st.session_state.master_df["الإدارة"] == dept])
        variance = dept_budget - dept_actual
        
        # الحركات في نفس تاريخ التقرير
        day_vacs = st.session_state.vacations_df[
            (st.session_state.vacations_df["الإدارة"] == dept) & 
            (st.session_state.vacations_df["التاريخ"] == report_date)
        ]
        
        vac_count = len(day_vacs[day_vacs["نوع الحركة"].isin(["إجازة", "عارضة"])])
        sick_count = len(day_vacs[day_vacs["نوع الحركة"] == "مرضي"])
        absent_count = len(day_vacs[day_vacs["نوع الحركة"] == "غياب"])
        
        total_absent = vac_count + sick_count + absent_count
        actual_operation = dept_actual - total_absent
        vac_ratio = f"{round((total_absent / dept_actual * 100), 1)}%" if dept_actual > 0 else "0%"
        
        daily_summary.append({
            "الإدارة": dept,
            "الميزانية (Budget)": dept_budget,
            "الفعلي (Actual)": dept_actual,
            "الفرق (Variance)": variance,
            "إجازة": vac_count,
            "مرضي": sick_count,
            "غياب": absent_count,
            "الفعلي بالتشغيل (Operation)": actual_operation,
            "نسبة الغياب/الإجازات": vac_ratio
        })
    
    st.dataframe(pd.DataFrame(daily_summary), use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    col_a, col_b = st.columns(2)
    
    # New Hiring
    with col_a:
        st.subheader("🆕 التعيينات الجديدة (New Hiring)")
        new_hires = st.session_state.master_df[st.session_state.master_df["تاريخ التعيين"] == report_date]
        if not new_hires.empty:
            st.dataframe(new_hires[["الاسم", "الإدارة", "الوظيفة", "تاريخ التعيين"]], use_container_width=True, hide_index=True)
        else:
            st.info("لا توجد تعيينات جديدة في هذا التاريخ.")
            
    # Resignations
    with col_b:
        st.subheader("🚪 الاستقالات (Resignations)")
        res_today = st.session_state.resignations_df[st.session_state.resignations_df["تاريخ الاستقالة"] == report_date]
        if not res_today.empty:
            st.dataframe(res_today[["الاسم", "الإدارة", "الوظيفة", "تاريخ الاستقالة"]], use_container_width=True, hide_index=True)
        else:
            st.info("لا توجد استقالات في هذا التاريخ.")
