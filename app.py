def analyze_doc_with_ai(image_obj, api_key):
    """تحليل الوثيقة واستخراج نوعها والبيانات بالذكاء الاصطناعي"""
    genai.configure(api_key=api_key)
    
    # استخدام الموديل المستقر المحدث
    model = genai.GenerativeModel('gemini-2.5-flash')
    
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
