"""
Arabic translations for Sadeem Chatbot
Using Bahraini dialect where appropriate
"""

# Knowledge Base Translations (Bahraini dialect)
SADEEM_KB_AR = {
    "general": {
        "keywords": ["سديم", "وش", "خدمة", "بابكو", "تزويد", "عن"],
        "documents": [
            "سديم خدمة ذكية للدفع بالوقود من بابكو تزويد",
            "تقدر تدفع للوقود في المحطات بالكرت الفيزيائي أو تطبيق بنفت باي",
            "سديم بدل نظام القسائم الورقية القديم بحل رقمي",
            "مصمم للأفراد والشركات لإدارة مصاريف الوقود",
            "تقدر تستخدم سديم في كل محطات بابكو والمحطات الخاصة في البحرين"
        ]
    },
    "benefitpay": {
        "keywords": ["بنفت باي", "تطبيق", "موبايل", "رقمي", "شحن", "دفع", "آبل", "أندرويد", "قوقل"],
        "documents": [
            "سديم متكامل مع تطبيق بنفت باي",
            "تقدر تحمل بنفت باي من آب ستور أو قوقل بلاي أو للأندرويد",
            "التطبيق يخليك تشحن حسابك رقمياً بدون ما تروح الفرع",
            "تقدر تدفع مباشرة في المحطات من التطبيق",
            "ما تحتاج الكرت الفيزيائي إذا تستخدم بنفت باي"
        ]
    },
    "topup": {
        "keywords": ["شحن", "رصيد", "إضافة فلوس", "موقع", "أونلاين"],
        "documents": [
            "تقدر تشحن حسابك من تطبيق بنفت باي",
            "كروت سديم تنشحن من الموقع الرسمي",
            "الشحن فوري وتقدر تستخدم الرصيد على طول",
            "تقدر تشوف تاريخ المعاملات والرصيد أونلاين"
        ]
    },
    "fees": {
        "keywords": ["رسوم", "تكلفة", "سعر", "كم", "إصدار", "تجديد"],
        "documents": [
            "رسوم إصدار الكرت واستبداله: 3.300 دينار",
            "رسوم التجديد السنوي: 2.200 دينار (تنخصم تلقائياً من الرصيد)",
            "تعديل قيود الكرت (مثل رقم اللوحة، الحدود): 1.100 دينار",
            "الكرت صالح لمدة 3 سنوات"
        ]
    },
    "features": {
        "keywords": ["ميزة", "فائدة", "عرض", "تحكم", "حد", "قيد"],
        "documents": [
            "معاملات وقود آمنة بدون كاش",
            "تقدر تحدد نوع الوقود (مثلاً جيد أو ممتاز بس)",
            "تقدر تحدد سيارات معينة باستخدام رقم اللوحة",
            "إدارة استهلاك الوقود للعائلة أو الأسطول تحت حساب واحد",
            "منع الاستخدام غير المصرح به بقيود ذكية"
        ]
    },
    "formats": {
        "keywords": ["نوع", "مسبق الدفع", "ائتمان", "كرت"],
        "documents": [
            "سديم متوفر ككرت مسبق الدفع (للأفراد والشركات)",
            "سديم متوفر ككرت ائتماني (للشركات المؤهلة)",
            "النوعين يوفرون نفس الأمان وميزات الإدارة"
        ]
    }
}

# UI Translations
UI_TRANSLATIONS_AR = {
    # Welcome messages
    "welcome_title": "مرحباً في سديم!",
    "welcome_subtitle": "أنا مساعدك الذكي لكروت الوقود سديم. أقدر أساعدك في الرسوم، الميزات، التقديم، وأكثر.",
    
    # Quick prompts
    "quick_prompt_fees": "وش رسوم الكرت؟",
    "quick_prompt_apply": "كيف أقدم؟",
    "quick_prompt_benefitpay": "أقدر أستخدم بنفت باي؟",
    "quick_prompt_features": "وش ميزات سديم؟",
    
    # Chat interface
    "type_message": "اكتب رسالتك...",
    "send": "إرسال",
    "new_chat": "محادثة جديدة",
    "typing": "سديم يكتب...",
    
    # Emotions
    "emotion_happy": "سعيد",
    "emotion_neutral": "محايد",
    "emotion_confused": "محتار",
    "emotion_frustrated": "منزعج",
    "emotion_sad": "حزين",
    
    # Rating
    "rate_experience": "لو عندك دقيقة، قيّم تجربتك معي!",
    "rating_thanks": "شكراً على تقييمك!",
    "rating_prompt": "كيف كانت المحادثة؟",
    
    # Analytics
    "emotion_analytics": "تحليل المشاعر",
    "overall_mood": "المزاج العام",
    "conversation_insights": "ملخص المحادثة",
    
    # Errors
    "error_connection": "فشل الاتصال بالخادم",
    "error_message": "فشل إرسال الرسالة",
    
    # System messages
    "bot_name": "سديم",
    "greeting": "مرحباً! أنا سديم، مساعدك لكروت الوقود. كيف أقدر أساعدك اليوم؟",
    "goodbye": "شكراً على تواصلك معي! إذا تحتاج مساعدة بسديم مستقبلاً، أنا دايماً هني. يومك سعيد!",
    "fallback": "أنا مساعد سديم! أقدر أساعدك في ميزات الكرت، الرسوم، التقديم، القيود، بنفت باي، وأكثر. وش تبي تعرف؟"
}

# Emotion labels in Arabic
EMOTION_LABELS_AR = {
    "Happy": "سعيد",
    "Neutral": "محايد",
    "Confused": "محتار",
    "Frustrated": "منزعج",
    "Sad": "حزين"
}

def get_translation(key: str, language: str = "en") -> str:
    """Get translation for a UI string"""
    if language == "ar":
        return UI_TRANSLATIONS_AR.get(key, key)
    return key

def get_emotion_label(emotion: str, language: str = "en") -> str:
    """Get emotion label in specified language"""
    if language == "ar":
        return EMOTION_LABELS_AR.get(emotion, emotion)
    return emotion
