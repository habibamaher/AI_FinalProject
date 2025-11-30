import React from 'react';
import { Languages } from 'lucide-react';

interface LanguageToggleProps {
    language: 'en' | 'ar';
    onLanguageChange: (language: 'en' | 'ar') => void;
}

const LanguageToggle: React.FC<LanguageToggleProps> = ({ language, onLanguageChange }) => {
    return (
        <button
            onClick={() => onLanguageChange(language === 'en' ? 'ar' : 'en')}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gray-800/50 border border-gray-700 hover:bg-gray-700/50 transition-all text-gray-300 hover:text-white"
            title={language === 'en' ? 'Switch to Arabic' : 'التبديل إلى الإنجليزية'}
        >
            <Languages size={18} />
            <span className="text-sm font-medium">
                {language === 'en' ? 'العربية' : 'English'}
            </span>
        </button>
    );
};

export default LanguageToggle;
