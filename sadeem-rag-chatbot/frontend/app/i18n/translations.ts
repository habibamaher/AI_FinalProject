// Frontend translations for Arabic and English
export const translations = {
    en: {
        // Welcome
        welcome_title: "Welcome to Sadeem!",
        welcome_subtitle: "I'm your AI assistant for Sadeem Fuel Cards. I can help with fees, features, applications, and more.",

        // Quick prompts
        quick_prompt_fees: "What are the card fees?",
        quick_prompt_apply: "How do I apply?",
        quick_prompt_benefitpay: "Can I use BenefitPay?",
        quick_prompt_features: "What are Sadeem's features?",

        // Chat interface
        type_message: "Type your message...",
        send: "Send",
        new_chat: "New Chat",
        typing: "Sadeem is typing...",

        // Emotions
        emotion_happy: "Happy",
        emotion_neutral: "Neutral",
        emotion_confused: "Confused",
        emotion_frustrated: "Frustrated",
        emotion_sad: "Sad",

        // Rating
        rating_prompt: "How helpful was this conversation?",
        rating_thanks: "Thank you for your feedback!",

        // Analytics
        emotion_analytics: "Emotion Analytics",
        overall_mood: "Overall Mood",
        conversation_insights: "Conversation Insights",

        // Errors
        error_connection: "Failed to connect to backend",
        error_message: "Failed to send message",

        // Language
        language: "Language",
        switch_to_arabic: "العربية",
        switch_to_english: "English"
    },
    ar: {
        // Welcome
        welcome_title: "مرحباً في سديم!",
        welcome_subtitle: "أنا مساعدك الذكي لكروت الوقود سديم. أقدر أساعدك في الرسوم، الميزات، التقديم، وأكثر.",

        // Quick prompts
        quick_prompt_fees: "وش رسوم الكرت؟",
        quick_prompt_apply: "كيف أقدم؟",
        quick_prompt_benefitpay: "أقدر أستخدم بنفت باي؟",
        quick_prompt_features: "وش ميزات سديم؟",

        // Chat interface
        type_message: "اكتب رسالتك...",
        send: "إرسال",
        new_chat: "محادثة جديدة",
        typing: "سديم يكتب...",

        // Emotions
        emotion_happy: "سعيد",
        emotion_neutral: "محايد",
        emotion_confused: "محتار",
        emotion_frustrated: "منزعج",
        emotion_sad: "حزين",

        // Rating
        rating_prompt: "كيف كانت المحادثة؟",
        rating_thanks: "شكراً على تقييمك!",

        // Analytics
        emotion_analytics: "تحليل المشاعر",
        overall_mood: "المزاج العام",
        conversation_insights: "ملخص المحادثة",

        // Errors
        error_connection: "فشل الاتصال بالخادم",
        error_message: "فشل إرسال الرسالة",

        // Language
        language: "اللغة",
        switch_to_arabic: "العربية",
        switch_to_english: "English"
    }
};

export type Language = 'en' | 'ar';

export function t(key: string, language: Language = 'en'): string {
    return translations[language][key as keyof typeof translations.en] || key;
}
