'use client';

import { Smile, Meh, HelpCircle, AlertTriangle, Frown } from 'lucide-react';

interface EmotionIndicatorProps {
  emotion: string;
  confidence?: number;
  showLabel?: boolean;
  className?: string;
}

export default function EmotionIndicator({ 
  emotion, 
  confidence, 
  showLabel = true,
  className = ''
}: EmotionIndicatorProps) {
  
  const getEmotionConfig = (emotion: string) => {
    switch (emotion) {
      case 'Happy':
        return {
          icon: Smile,
          color: 'text-green-400',
          bg: 'bg-green-400/10',
          border: 'border-green-400/20',
          label: 'Happy'
        };
      case 'Neutral':
        return {
          icon: Meh,
          color: 'text-blue-300',
          bg: 'bg-blue-400/10',
          border: 'border-blue-400/20',
          label: 'Neutral'
        };
      case 'Confused':
        return {
          icon: HelpCircle,
          color: 'text-amber-400',
          bg: 'bg-amber-400/10',
          border: 'border-amber-400/20',
          label: 'Confused'
        };
      case 'Frustrated':
        return {
          icon: AlertTriangle,
          color: 'text-orange-500',
          bg: 'bg-orange-500/10',
          border: 'border-orange-500/20',
          label: 'Frustrated'
        };
      case 'Sad':
        return {
          icon: Frown,
          color: 'text-indigo-400',
          bg: 'bg-indigo-400/10',
          border: 'border-indigo-400/20',
          label: 'Sad'
        };
      default:
        return {
          icon: Meh,
          color: 'text-slate-400',
          bg: 'bg-slate-400/10',
          border: 'border-slate-400/20',
          label: emotion || 'Unknown'
        };
    }
  };

  const config = getEmotionConfig(emotion);
  const Icon = config.icon;

  return (
    <div className={`inline-flex items-center gap-1.5 px-2 py-1 rounded-full border backdrop-blur-sm ${config.bg} ${config.border} ${className}`}>
      <Icon size={14} className={config.color} />
      {showLabel && (
        <span className={`text-xs font-medium ${config.color}`}>
          {config.label}
          {confidence !== undefined && (
            <span className="opacity-70 ml-1">
              {Math.round(confidence * 100)}%
            </span>
          )}
        </span>
      )}
    </div>
  );
}
