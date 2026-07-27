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

if "budget_df" not in st.session_state:
    st.session_state.budget_df = pd.DataFrame([
        {"الإدارة": "الموارد البشرية", "الوظيفة": "أخصائي HR", "الميزانية (Budget)": 2},
        {"الإدارة": "الموارد البشرية", "الوظيفة": "مدير موارد بشرية", "الميزانية (Budget)": 1},
        {"الإدارة": "تكنولوجيا المعلومات", "الوظيفة": "مطور برمجيات", "الميزانية (Budget)": 3},
        {"الإدارة": "تكنولوجيا المعلومات", "الوظيفة": "دعم فني IT", "الميزانية (Budget)": 2},
        {"الإدارة": "العمليات", "الوظيفة": "خدمة عملاء", "الميزانية (Budget)": 5},
        {"الإدارة": "العمليات", "الوظيفة": "مشرف عمليات", "الميزانية (Budget)": 2}
    ])

if "master_df" not in st.session_state:
    st.session_state.master_df = pd.DataFrame([
        {"كود الموظف": "101", "الاسم": "أحمد محمود علي", "الإدارة": "الموارد البشرية", "الوظيفة": "أخصائي HR", "تاريخ التعيين": date(2025, 1, 15), "الراتب": 12000.0, "الحالة": "Active"},
        {"كود الموظف": "102", "الاسم": "محمد مصطفى كامل", "الإدارة": "تكنولوجيا المعلومات", "الوظيفة": "مطور برمجيات", "تاريخ التعيين": date(2026, 7, 27), "الراتب": 18000.0, "الحالة": "Active"},
        {"كود الموظف": "103", "الاسم": "سارة أحمد حسن", "الإدارة": "العمليات", "الوظيفة": "خدمة عملاء", "تاريخ التعيين": date(2024, 3, 10), "الراتب": 8000.0, "الحالة": "Active"}
    ])

if "vacations_df" not in st.session_state:
    st.session_state.vacations_df = pd.DataFrame([
        {"كود الموظف": "103", "الاسم": "سارة أحمد حسن", "الإدارة": "العمليات", "الوظيفة": "خدمة عملاء", "نوع الحركة": "إجازة", "من تاريخ": date(2026, 7, 27), "إلى تاريخ": date(2026, 7, 29), "عدد الأيام": 3}
    ])

if "resignations_df" not in st.session_state:
    st.session_state.resignations_df = pd.DataFrame(columns=["كود الموظف", "الاسم", "الإدارة", "الوظيفة", "تاريخ التعيين", "تاريخ الاستقالة"])

# دالة تحويل DataFrame لإكسيل
def convert_df_to_excel(df):
    import io
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Data')
    return output.getvalue()

# --- القائمة الجانبية ---
st.sidebar.title("🏢 نظام الـ HR الموحد")

# إضافة خيار رفع ملف الإكسيل المجمع في القائمة الجانبية
st.sidebar.markdown("---")
st.sidebar.subheader("📤 رفع بيانات السيستم المجمعة")
uploaded_file = st.sidebar.file_uploader("ارفع ملف إكسيل الشامل (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    try:
        excel_file = pd.ExcelFile(uploaded_file)
        sheet_names = excel_file.sheet_names
        
        updated_sheets = []
        if "Master" in sheet_names:
            df_m = pd.read_excel(uploaded_file, sheet_name="Master")
            # إزالة المسافات الزائدة من أسماء الأعمدة
            df_m.columns = df_m.columns.str.strip()
            
            # التأكد من وجود أعمدة هامة وحمايتها
            if "تاريخ التعيين" in df_m.columns:
                df_m["تاريخ التعيين"] = pd.to_datetime(df_m["تاريخ التعيين"], errors='coerce').dt.date
            
            st.session_state.master_df = df_m
            updated_sheets.append("الماستر (Master)")

        if "Budget" in sheet_names:
            df_b = pd.read_excel(uploaded_file, sheet_name="Budget")
            df_b.columns = df_b.columns.str.strip()
            st.session_state.budget_df = df_b
            updated_sheets.append("البادجيت (Budget)")

        if "Vacations" in sheet_names:
            df_v = pd.read_excel(uploaded_file, sheet_name="Vacations")
            df_v.columns = df_v.columns.str.strip()
            if "من تاريخ" in df_v.columns:
                df_v["من تاريخ"] = pd.to_datetime(df_v["من تاريخ"], errors='coerce').dt.date
            if "إلى تاريخ" in df_v.columns:
                df_v["إلى تاريخ"] = pd.to_datetime(df_v["إلى تاريخ"], errors='coerce').dt.date
            st.session_state.vacations_df = df_v
            updated_sheets.append("الإجازات (Vacations)")

        if "Resignations" in sheet_names:
            df_r = pd.read_excel(uploaded_file, sheet_name="Resignations")
            df_r.columns = df_r.columns.str.strip()
            if "تاريخ التعيين" in df_r.columns:
                df_r["تاريخ التعيين"] = pd.to_datetime(df_r["تاريخ التعيين"], errors='coerce').dt.date
            if "تاريخ الاستقالة" in df_r.columns:
                df_r["تاريخ الاستقالة"] = pd.to_datetime(df_r["تاريخ الاستقالة"], errors='coerce').dt.date
            st.session_state.resignations_df = df_r
            updated_sheets.append("الاستقالات (Resignations)")

        st.sidebar.success(f"تم رفع وتحديث: {', '.join(updated_sheets)}")
    except Exception as e:
        st.sidebar.error(f"حدث خطأ أثناء قراءة الملف: {e}")

st.sidebar.markdown("---")

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
        available_depts = sorted(st.session_state.budget_df["الإدارة"].dropna().unique().tolist()) if not st.session_state.budget_df.empty and "الإدارة" in st.session_state.budget_df.columns else []
        
        c1, c2 = st.columns(2)
        code = c1.text_input("كود الموظف *")
        name = c2.text_input("الاسم بالكامل *")
        
        c3, c4 = st.columns(2)
        selected_dept = c3.selectbox("الإدارة *", available_depts if available_depts else ["لا يوجد إدارات محددة"])
        
        if selected_dept and not st.session_state.budget_df.empty and "الإدارة" in st.session_state.budget_df.columns and "الوظيفة" in st.session_state.budget_df.columns:
            filtered_positions = sorted(st.session_state.budget_df[st.session_state.budget_df["الإدارة"] == selected_dept]["الوظيفة"].dropna().unique().tolist())
        else:
            filtered_positions = []
            
        selected_pos = c4.selectbox("الوظيفة (مقترنة بالإدارة) *", filtered_positions if filtered_positions else ["اختر الإدارة أولاً"])
        
        c5, c6 = st.columns(2)
        hiring_date = c5.date_input("تاريخ التعيين", value=date.today())
        salary = c6.number_input("الراتب", min_value=0.0, step=500.0)
        
        if st.button("حفظ الموظف في الماستر"):
            if code and name and selected_dept and selected_pos:
                if "كود الموظف" in st.session_state.master_df.columns and str(code) in st.session_state.master_df["كود الموظف"].astype(str).values:
                    st.error("⚠️ كود الموظف موجود بالفعل في الماستر!")
                else:
                    new_emp = {
                        "كود الموظف": str(code), "الاسم": name, "الإدارة": selected_dept,
                        "الوظيفة": selected_pos, "تاريخ التعيين": hiring_date, "الراتب": salary, "الحالة": "Active"
                    }
                    st.session_state.master_df = pd.concat([st.session_state.master_df, pd.DataFrame([new_emp])], ignore_index=True)
                    st.success(f"تم إضافة الموظف {name} بنجاح إلى شيت الماستر!")
                    st.rerun()
            else:
                st.warning("يرجى ملء جميع الحقول المطلوبة.")

    st.subheader("👥 قائمة الموظفين الحاليين (Active Only)")
    st.dataframe(st.session_state.master_df, use_container_width=True, hide_index=True)
    
    excel_data = convert_df_to_excel(st.session_state.master_df)
    st.download_button("📥 تحميل شيت الماستر (Excel)", data=excel_data, file_name="Master_Data.xlsx", mime="application/vnd.ms-excel")

# --- 2. شيت الإجازات ---
elif choice == "🏝️ شيت الإجازات (Vacations)":
    st.title("🏝️ تسجيل وحركات الإجازات والغياب")
    
    with st.expander("➕ إضافة حركة جديدة لموظف", expanded=False):
        # التحقق من وجود أعمدة الماستر المطلوبة قبل بناء قائمة الموظفين
        required_cols = ["كود الموظف", "الاسم", "الإدارة", "الوظيفة"]
        if not st.session_state.master_df.empty and all(col in st.session_state.master_df.columns for col in required_cols):
            st.session_state.master_df["emp_label"] = (
                st.session_state.master_df["كود الموظف"].astype(str) + " - " + 
                st.session_state.master_df["الاسم"].astype(str) + " (" + 
                st.session_state.master_df["الإدارة"].astype(str) + ")"
            )
            emp_options = st.session_state.master_df["emp_label"].tolist()
            
            selected_emp_label = st.selectbox("ابحث عن الموظف (بالكود أو الاسم):", emp_options)
            
            selected_code = selected_emp_label.split(" - ")[0]
            emp_info = st.session_state.master_df[st.session_state.master_df["كود الموظف"].astype(str) == selected_code].iloc[0]
            
            st.info(f"👤 الموظف المختار: **{emp_info['الاسم']}** | الكود: **{emp_info['كود الموظف']}** | الإدارة: **{emp_info['الإدارة']}** | الوظيفة: **{emp_info['الوظيفة']}**")
            
            c1, c2, c3 = st.columns(3)
            vac_type = c1.selectbox("نوع الحركة", ["إجازة", "مرضي", "غياب", "عارضة", "بدون أجر"])
            from_date = c2.date_input("من تاريخ", value=date.today())
            to_date = c3.date_input("إلى تاريخ", value=date.today())
            
            if to_date >= from_date:
                days_count = (to_date - from_date).days + 1
                st.caption(f"⏱️ إجمالي فترة الإجازة: **{days_count}** يوم/أيام")
            else:
                st.error("⚠️ تاريخ 'إلى' يجب أن يكون مساوياً أو بعد تاريخ 'من'")
                days_count = 0
            
            if st.button("تسجيل الإجازة"):
                if days_count > 0:
                    new_vac = {
                        "كود الموظف": str(selected_code),
                        "الاسم": emp_info["الاسم"],
                        "الإدارة": emp_info["الإدارة"],
                        "الوظيفة": emp_info["الوظيفة"],
                        "نوع الحركة": vac_type,
                        "من تاريخ": from_date,
                        "إلى تاريخ": to_date,
                        "عدد الأيام": days_count
                    }
                    st.session_state.vacations_df = pd.concat([st.session_state.vacations_df, pd.DataFrame([new_vac])], ignore_index=True)
                    st.success("تم تسجيل حركة الإجازة بنجاح!")
                    st.rerun()
        else:
            st.warning("⚠️ يرجى التأكد من رفع شيت Master يحتوي على الأعمدة التالية: [كود الموظف، الاسم، الإدارة، الوظيفة].")

    st.subheader("📜 سجل الإجازات والحركات الكامل")
    st.dataframe(st.session_state.vacations_df, use_container_width=True, hide_index=True)
    
    excel_vac = convert_df_to_excel(st.session_state.vacations_df)
    st.download_button("📥 تحميل شيت الإجازات (Excel)", data=excel_vac, file_name="Vacations_Data.xlsx", mime="application/vnd.ms-excel")

# --- 3. شيت الاستقالات ---
elif choice == "🚪 شيت الاستقالات (Resignations)":
    st.title("🚪 تسجيل الاستقالات ونقل الموظفين")
    
    required_cols = ["كود الموظف", "الاسم", "الإدارة", "الوظيفة"]
    if not st.session_state.master_df.empty and all(col in st.session_state.master_df.columns for col in required_cols):
        st.session_state.master_df["emp_label_res"] = (
            st.session_state.master_df["كود الموظف"].astype(str) + " - " + 
            st.session_state.master_df["الاسم"].astype(str)
        )
        emp_res_options = st.session_state.master_df["emp_label_res"].tolist()
        
        selected_res_label = st.selectbox("ابحث عن الموظف المستقيل (بالكود أو الاسم):", emp_res_options)
        selected_code = selected_res_label.split(" - ")[0]
        emp_info = st.session_state.master_df[st.session_state.master_df["كود الموظف"].astype(str) == selected_code].iloc[0]
        
        st.warning(f"⚠️ بيانات الموظف المحدد: **{emp_info['الاسم']}** ({emp_info['الإدارة']} - {emp_info['الوظيفة']})")
        res_date = st.date_input("تاريخ الاستقالة", value=date.today())
        
        if st.button("🚨 تأكيد الاستقالة ونقل الموظف"):
            res_data = {
                "كود الموظف": str(selected_code),
                "الاسم": emp_info["الاسم"],
                "الإدارة": emp_info["الإدارة"],
                "الوظيفة": emp_info["الوظيفة"],
                "تاريخ التعيين": emp_info.get("تاريخ التعيين", None),
                "تاريخ الاستقالة": res_date
            }
            st.session_state.resignations_df = pd.concat([st.session_state.resignations_df, pd.DataFrame([res_data])], ignore_index=True)
            st.session_state.master_df = st.session_state.master_df[st.session_state.master_df["كود الموظف"].astype(str) != selected_code]
            
            st.success(f"تم نقل الموظف {emp_info['الاسم']} إلى شيت الاستقالات وحذفه من الماستر بنجاح!")
            st.rerun()
    else:
        st.info("لا يوجد موظفين حاليين أو شيت الماستر ينقصه أعمدة أصلية.")

    st.subheader("📜 سجل الموظفين المستقيلين (Resignations Sheet)")
    st.dataframe(st.session_state.resignations_df, use_container_width=True, hide_index=True)
    
    excel_res = convert_df_to_excel(st.session_state.resignations_df)
    st.download_button("📥 تحميل شيت الاستقالات (Excel)", data=excel_res, file_name="Resignations_Data.xlsx", mime="application/vnd.ms-excel")

# --- 4. شيت البادجيت ---
elif choice == "🎯 شيت البادجيت (Budget)":
    st.title("🎯 الميزانية الشاغرة (Budget vs Actual)")
    
    if not st.session_state.master_df.empty and "الإدارة" in st.session_state.master_df.columns and "الوظيفة" in st.session_state.master_df.columns:
        master_counts = st.session_state.master_df.groupby(["الإدارة", "الوظيفة"]).size().reset_index(name="الفعلي (Actual)")
        if "الإدارة" in st.session_state.budget_df.columns and "الوظيفة" in st.session_state.budget_df.columns:
            budget_merged = pd.merge(st.session_state.budget_df, master_counts, on=["الإدارة", "الوظيفة"], how="left")
        else:
            budget_merged = st.session_state.budget_df.copy()
            budget_merged["الفعلي (Actual)"] = 0
    else:
        budget_merged = st.session_state.budget_df.copy()
        budget_merged["الفعلي (Actual)"] = 0
        
    budget_merged["الفعلي (Actual)"] = budget_merged["الفعلي (Actual)"].fillna(0).astype(int)
    if "الميزانية (Budget)" in budget_merged.columns:
        budget_merged["الشواغر (Vacancy)"] = budget_merged["الميزانية (Budget)"] - budget_merged["الفعلي (Actual)"]
    
    st.dataframe(budget_merged, use_container_width=True, hide_index=True)

# --- 5. الدايلى ريبورت ---
elif choice == "📊 التقرير اليومي (Daily Report)":
    st.title("📊 التقرير اليومي الشامل (Daily Report)")
    
    report_date = st.date_input("🗓️ اختر تاريخ التقرير اليومي:", value=date.today())
    st.markdown(f"### 📈 تقرير حركة العمل يوم: `{report_date}`")
    
    depts = sorted(st.session_state.budget_df["الإدارة"].dropna().unique().tolist()) if not st.session_state.budget_df.empty and "الإدارة" in st.session_state.budget_df.columns else []
    daily_summary = []
    
    for dept in depts:
        dept_budget = st.session_state.budget_df[st.session_state.budget_df["الإدارة"] == dept]["الميزانية (Budget)"].sum() if "الميزانية (Budget)" in st.session_state.budget_df.columns else 0
        dept_actual = len(st.session_state.master_df[st.session_state.master_df["الإدارة"] == dept]) if not st.session_state.master_df.empty and "الإدارة" in st.session_state.master_df.columns else 0
        variance = dept_budget - dept_actual
        
        if not st.session_state.vacations_df.empty and all(col in st.session_state.vacations_df.columns for col in ["الإدارة", "من تاريخ", "إلى تاريخ", "نوع الحركة"]):
            day_vacs = st.session_state.vacations_df[
                (st.session_state.vacations_df["الإدارة"] == dept) & 
                (st.session_state.vacations_df["من تاريخ"] <= report_date) & 
                (st.session_state.vacations_df["إلى تاريخ"] >= report_date)
            ]
            vac_count = len(day_vacs[day_vacs["نوع الحركة"].isin(["إجازة", "عارضة"])])
            sick_count = len(day_vacs[day_vacs["نوع الحركة"] == "مرضي"])
            absent_count = len(day_vacs[day_vacs["نوع الحركة"] == "غياب"])
        else:
            vac_count = sick_count = absent_count = 0
            
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
    
    with col_a:
        st.subheader("🆕 التعيينات الجديدة (New Hiring)")
        if not st.session_state.master_df.empty and "تاريخ التعيين" in st.session_state.master_df.columns:
            new_hires = st.session_state.master_df[st.session_state.master_df["تاريخ التعيين"] == report_date]
            if not new_hires.empty:
                st.dataframe(new_hires, use_container_width=True, hide_index=True)
            else:
                st.info("لا توجد تعيينات جديدة في هذا التاريخ.")
        else:
            st.info("لا توجد بيانات تعيينات.")
            
    with col_b:
        st.subheader("🚪 الاستقالات (Resignations)")
        if not st.session_state.resignations_df.empty and "تاريخ الاستقالة" in st.session_state.resignations_df.columns:
            res_today = st.session_state.resignations_df[st.session_state.resignations_df["تاريخ الاستقالة"] == report_date]
            if not res_today.empty:
                st.dataframe(res_today, use_container_width=True, hide_index=True)
            else:
                st.info("لا توجد استقالات في هذا التاريخ.")
        else:
            st.info("لا توجد بيانات استقالات.")
