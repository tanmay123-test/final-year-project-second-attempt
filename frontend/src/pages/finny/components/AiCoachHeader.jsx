import React from 'react';
import { Bot, Clock, History } from 'lucide-react';
import { INTENT_BADGE_MAP } from '../constants/aiCoachConstants';

const AiCoachHeader = ({ onHistoryClick, currentIntent }) => {
  const getIntentBadge = () => {
    if (!currentIntent) return null;
    const badgeConfig = INTENT_BADGE_MAP[currentIntent];
    if (!badgeConfig) return null;

    const colorClasses = {
      blue: 'bg-blue-100 text-blue-800',
      green: 'bg-green-100 text-green-800',
      amber: 'bg-amber-100 text-amber-800',
      purple: 'bg-purple-100 text-purple-800',
      coral: 'bg-orange-100 text-orange-800',
      gray: 'bg-gray-100 text-gray-800'
    };

    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${colorClasses[badgeConfig.color]}`}>
        {badgeConfig.label}
      </span>
    );
  };

  return (
    <div className="bg-gradient-to-r from-teal-700 to-blue-800 px-4 py-3 flex items-center justify-between">
      {/* Left side */}
      <div className="flex items-center space-x-3">
        <div className="w-8 h-8 bg-teal-500 rounded-full flex items-center justify-center">
          <Bot size={16} className="text-white" />
        </div>
        <div>
          <h1 className="text-white font-bold text-lg">AI Financial Assistant</h1>
          <p className="text-teal-100 text-xs">Powered by Gemini AI</p>
        </div>
      </div>

      {/* Right side */}
      <div className="flex items-center space-x-2">
        {currentIntent && getIntentBadge()}
        <button
          onClick={onHistoryClick}
          className="p-2 text-white hover:bg-white hover:bg-opacity-10 rounded-full transition-colors"
          title="Chat History"
        >
          <Clock size={20} />
        </button>
      </div>
    </div>
  );
};

export default AiCoachHeader;
