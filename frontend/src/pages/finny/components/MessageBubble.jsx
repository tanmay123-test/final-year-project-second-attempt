import React from 'react';
import { Bot } from 'lucide-react';
import { INTENT_BADGE_MAP } from '../constants/aiCoachConstants';

const MessageBubble = ({ message }) => {
  const isAI = message.sender === 'ai';
  const isError = message.type === 'error';

  const formatTime = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: true 
    });
  };

  const getIntentBadge = () => {
    if (!isAI || !message.type || message.type === 'error') return null;
    const badgeConfig = INTENT_BADGE_MAP[message.type];
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
      <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium mb-2 ${colorClasses[badgeConfig.color]}`}>
        {badgeConfig.label}
      </span>
    );
  };

  if (isAI) {
    return (
      <div className="flex justify-start mb-4">
        <div className="flex items-start space-x-2 max-w-[80%]">
          {/* AI Avatar */}
          <div className="w-6 h-6 bg-teal-600 rounded-full flex items-center justify-center flex-shrink-0">
            <Bot size={14} className="text-white" />
          </div>
          
          {/* Message Content */}
          <div className="flex flex-col">
            {/* Intent Badge */}
            {getIntentBadge()}
            
            {/* Message Bubble */}
            <div className={`bg-white rounded-xl shadow-sm p-3 ${isError ? 'border border-red-200' : ''}`}>
              <p className={`text-sm ${isError ? 'text-red-600' : 'text-gray-800'} whitespace-pre-wrap break-words`}>
                {message.text}
              </p>
            </div>
            
            {/* Timestamp */}
            <span className="text-xs text-gray-500 mt-1">
              {formatTime(message.timestamp)}
            </span>
          </div>
        </div>
      </div>
    );
  }

  // User Message
  return (
    <div className="flex justify-end mb-4">
      <div className="max-w-[80%]">
        {/* Message Bubble */}
        <div className="bg-gradient-to-r from-teal-700 to-blue-800 text-white rounded-xl p-3">
          <p className="text-sm whitespace-pre-wrap break-words">
            {message.text}
          </p>
        </div>
        
        {/* Timestamp */}
        <div className="text-right">
          <span className="text-xs text-gray-500 mt-1">
            {formatTime(message.timestamp)}
          </span>
        </div>
      </div>
    </div>
  );
};

export default MessageBubble;
