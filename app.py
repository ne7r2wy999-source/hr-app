import os
import json
import pandas as pd
from PIL import Image
from openpyxl import Workbook
import streamlit as st
import google.generativeai as genai

# --- 1. إعداد الصفحة والتنسيق ---
st.set_page_config(page_title="نظام الأرشيف الذكي - HR Archive", page_icon="📁", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }
    .stButton>button { width: 100%; font-weight: bold; background-color: #28a745; color: white; }
    </style>
""", unsafe_allow_html=True)

# --- 2. إعداد مسارات الأرشيف وشيت الإكسيل ---
ARCHIVE_DIR = "./Employees_Archive"
EXCEL_PATH = "./HR_Master_Database.xlsx"
os.makedirs(ARCHIVE_DIR, exist_ok=True)

HEADERS = [
    "Emp Code", "Employee Name", "National ID", "DOB", "Job Title", 
    "National ID Expiry", "Qualification", "Military Status", 
    "Insurance No", "Health Cert Expiry", "Folder Path"
]

if not os.path.exists(EXCEL_PATH):
    wb = Workbook()
    ws = wb.active
    ws.title = "Master Data"
    ws.append(HEADERS)
    wb.save(EXCEL_PATH)

# --- 3. الدوال الأساسية ---

def generate_next_emp_code():
    """توليد كود موظف جديد تلقائياً (EMP-001, EMP-002...)"""
    if not os.path.exists(EXCEL_PATH):
        return "EMP-001"
    df = pd.read_excel(EXCEL_PATH)
    if df.empty or "Emp Code" not in df.columns:
        return "EMP-001"
    
    existing_codes = df["Emp Code"].dropna().astype(str).tolist()
    numbers = []
    for code in existing_codes:
        if code.startswith("EMP-"):
            try:
                numbers.append(int(code.split("-")[1]))
            except:
                pass
    next_num = max(numbers) + 1 if numbers else 1
    return f"EMP-{next_num:03d}"

def analyze_doc_with_ai(image_obj, api_key):
    """تحليل الوثيقة واستخراج نوعها والبيانات بالذكاء الاصطناعي"""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = """
    أنت خبير أرشيف HR مصري. قم بمسح الوثيقة واستخراج البيانات بنص JSON حصراً وبدون أي مقدمات أو شرح:
    1. حدد نوع الوثيقة من القائمة: 
       ["National_ID", "Birth_Certificate", "Qualification", "Military_Certificate", "Insurance_Print", "Work_Permit", "Criminal_Record", "Health_Certificate", "Skill_Certificate", "Syndicate_Card"]
    
    2. أرجع النتيجة في JSON فقط بالشكل التالي:
    {
       "doc_type_code": "كود الوثيقة بالإنجليزية من القائمة أعلاه",
       "doc_type_arabic": "اسم الوثيقة بالعربي",
       "employee_name": "اسم الموظف إن وجد",
       "national_id": "الرقم القومي (14 رقم) إن وجد",
       "dob": "تاريخ الميلاد YYYY-MM-DD إن وجد",
       "job_title": "المهنة / الوظيفة إن وجد",
       "expiry_date": "تاريخ الانتهاء YYYY-MM-DD إن وجد",
       "military_status": "الموقف من التجنيد إن وجد",
       "qualification": "المؤهل الدراسي إن وجد",
       "insurance_no": "الرقم التأميني إن وجد"
    }
    """
    
    response = model.generate_content([prompt, image_obj])
    clean_json = response.text.replace("```json", "").replace("```", "").strip()
    return json.loads(clean_json)

def save_employee_data(emp_code, extracted_results):
    """حفظ البيانات في شيت الإكسيل وتحديث صف الموظف"""
    df = pd.read_excel(EXCEL_PATH)
    emp_folder = os.path.join(ARCHIVE_DIR, emp_code)
    
    # تحضير صف الموظف
    row_data = {col: "" for col in HEADERS}
    row_data["Emp Code"] = emp_code
    row_data["Folder Path"] = emp_folder
    
    # دمج بيانات الوثائق المرفوعة
    for res in extracted_results:
        data = res["data"]
        if data.get("employee_name") and not row_data["Employee Name"]:
            row_data["Employee Name"] = data["employee_name"]
        if data.get("national_id") and not row_data["National ID"]:
            row_data["National ID"] = str(data["national_id"])
        if data.get("dob") and not row_data["DOB"]:
            row_data["DOB"] = data["dob"]
        if data.get("job_title") and not row_data["Job Title"]:
            row_data["Job Title"] = data["job_title"]
        if data.get("qualification") and not row_data["Qualification"]:
            row_data["Qualification"] = data["qualification"]
        if data.get("military_status") and not row_data["Military Status"]:
            row_data["Military Status"] = data["military_status"]
        if data.get("insurance_no") and not row_data["Insurance No"]:
            row_data["Insurance No"] = str(data["insurance_no"])
            
        if data.get("doc_type_code") == "National_ID":
            row_data["National ID Expiry"] = data.get("expiry_date", "")
        elif data.get("doc_type_code") == "Health_Certificate":
            row_data["Health Cert Expiry"] = data.get("expiry_date", "")

    # إدراج الصف في الإكسيل
    if emp_code in df["Emp Code"].astype(str).values:
        idx = df[df["Emp Code"].astype(str) == emp_code].index[0]
        for key, val in row_data.items():
            if val:
                df.at[idx, key] = val
    else:
        df = pd.concat([df, pd.DataFrame([row_data])], ignore_index=True)
        
    df.to_excel(EXCEL_PATH, index=False)

# --- 4. واجهة المستخدم (Streamlit UI) ---

st.title("📁 نظام الأرشيف الرقمي وإدخال بيانات مسوغات التعيين")

# المفتاح البرمجي
api_key = st.sidebar.text_input("أدخل مفتاح Gemini API Key:", type="password")
st.sidebar.markdown("---")

tab1, tab2 = st.tabs(["📸 مسح أوراق موظف جديد", "📊 عرض شيت الإكسيل الأرشيفي"])

with tab1:
    col_code, col_info = st.columns([1, 2])
    with col_code:
        emp_code = st.text_input("كود الموظف:", value=generate_next_emp_code())
    
    st.info(f"سيتم إنشاء فولدر خاص بهذا الموظف بالمسمى: `{ARCHIVE_DIR}/{emp_code}`")
    
    uploaded_files = st.file_uploader(
        "اسحب أو التقط صور/وثائق الموظف (يمكنك رفع عدة ملفات معاً):", 
        type=["jpg", "jpeg", "png"], 
        accept_multiple_files=True
    )
    
    if st.button("🚀 معالجة الوثائق وحفظ الأرشيف"):
        if not api_key:
            st.error("يرجى إدخال Gemini API Key في القائمة الجانبية أولاً!")
        elif not uploaded_files:
            st.warning("يرجى اختيار أو التقاط صورة وثيقة واحدة على الأقل!")
        else:
            emp_folder = os.path.join(ARCHIVE_DIR, emp_code)
            os.makedirs(emp_folder, exist_ok=True)
            
            extracted_results = []
            
            with st.spinner("جاري تحليل الوثائق وتسميتها بالذكاء الاصطناعي..."):
                for uploaded_file in uploaded_files:
                    image = Image.open(uploaded_file)
                    try:
                        # 1. تحليل الصورة
                        doc_info = analyze_doc_with_ai(image, api_key)
                        
                        # 2. تحديد اسم الملف والحفظ في الفولدر
                        doc_code = doc_info.get("doc_type_code", "Document")
                        file_ext = uploaded_file.name.split(".")[-1]
                        save_filename = f"{doc_code}.{file_ext}"
                        save_path = os.path.join(emp_folder, save_filename)
                        
                        image.save(save_path)
                        
                        extracted_results.append({
                            "filename": save_filename,
                            "data": doc_info
                        })
                        st.success(f"✅ تم التعرف على: **{doc_info.get('doc_type_arabic', doc_code)}** وحفظها كـ `{save_filename}`")
                    except Exception as e:
                        st.error(f"خطأ أثناء معالجة الملف {uploaded_file.name}: {e}")

            # 3. تحديث شيت الإكسيل
            if extracted_results:
                save_employee_data(emp_code, extracted_results)
                st.balloons()
                st.success(f"🎉 تم تسجيل الموظف **{emp_code}** بنجاح وتحديث شيت الإكسيل Main Database!")

with tab2:
    st.subheader("📊 بيانات الموظفين المسجلة في شيت الإكسيل")
    if os.path.exists(EXCEL_PATH):
        df_master = pd.read_excel(EXCEL_PATH)
        st.dataframe(df_master, use_container_width=True)
        
        # زر تحميل شيت الإكسيل
        with open(EXCEL_PATH, "rb") as file:
            st.download_button(
                label="📥 تحميل ملف الإكسيل (HR_Master_Database.xlsx)",
                data=file,
                file_name="HR_Master_Database.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
