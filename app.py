import streamlit as st
import pandas as pd
import openpyxl

st.set_page_config(page_title="عرض شيتات الإكسيل بالمعادلات", page_icon="📊", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif;
        direction: rtl;
        text-align: right;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📊 عرض شيتات الإكسيل بنفس أرقام ومعادلات الملف الأصلي")

st.sidebar.title("📁 التحكم بالملف")
uploaded_file = st.sidebar.file_uploader("رفع ملف الإكسيل (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    try:
        # قراءة الشيتات وقيم المعادلات المحسوبة جاهزة من الإكسيل دون إعادة حسابها
        wb = openpyxl.load_workbook(uploaded_file, data_only=True)
        sheet_names = wb.sheetnames
        
        selected_sheet = st.sidebar.selectbox("اختر الشيت للعرض:", sheet_names)
        
        sheet = wb[selected_sheet]
        data = sheet.values
        
        # تحويل البيانات لـ DataFrame بنفس هيئة الإكسيل تماماً
        cols = next(data)
        data = list(data)
        df = pd.DataFrame(data, columns=cols)
        
        # تنظيف الصفوف والأعمدة الفارغة تماماً
        df = df.dropna(how='all').fillna('')

        st.subheader(f"📄 الشيت الحالي: {selected_sheet}")
        st.dataframe(df, use_container_width=True, hide_index=True)

    except Exception as e:
        st.sidebar.error(f"حدث خطأ أثناء قراءة الملف: {e}")
else:
    st.info("👈 يرجى رفع ملف الإكسيل من القائمة الجانبية لعرض أرقامه ومعادلاته كما هي بالظبط.")
