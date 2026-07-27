import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="نظام إدارة الموارد البشرية",
    page_icon="📊",
    layout="wide"
)

# تطبيق التنسيق والتجاه العربي
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif;
        direction: rtl;
        text-align: right;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📊 نظام عرض بيانات وإدارة شيت الإكسيل الكامل")
st.write("قم برفع ملف الإكسيل الخاص بك لاستعراض كافة الصفحات (Sheets) بالبيانات والعناوين التفصيلية الموجودة بها.")

uploaded_file = st.file_uploader("ارفع ملف الإكسيل الأصلي (.xlsx / .xls)", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        # قراءة كل الشيتات من الملف
        excel_file = pd.ExcelFile(uploaded_file)
        sheet_names = excel_file.sheet_names
        
        st.success(f"تم قراءة الملف بنجاح! يحتوي الملف على {len(sheet_names)} صفحات (Sheets).")
        
        # إنشاء تبويبات (Tabs) لكل شيت موجود في الملف
        tabs = st.tabs(sheet_names)
        
        for i, sheet in enumerate(sheet_names):
            with tabs[i]:
                st.subheader(f"📄 صفحة: {sheet}")
                # قراءة بيانات الشيت المحدد
                df = pd.read_excel(uploaded_file, sheet_name=sheet)
                
                # عرض الجدول بدون عمود الـ index وبإمكانية توسيع الجدول
                st.dataframe(df, use_container_width=True, hide_index=True)
                
    except Exception as e:
        st.error(f"حدث خطأ أثناء قراءة ملف الإكسيل: {e}")
else:
    st.info("في انتظار رفع ملف الإكسيل لعرض الشيتات والبيانات التفصيلية...")
