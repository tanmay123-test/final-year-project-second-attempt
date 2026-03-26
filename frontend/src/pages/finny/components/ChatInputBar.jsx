import React, { useState } from 'react';
import { Send } from 'lucide-react';
import { INPUT_PLACEHOLDER } from '../constants/aiCoachConstants';

const ChatInputBar = ({ onSend, isLoading }) => {
  const [inputText, setInputText] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputText.trim() && !isLoading) {
      onSend(inputText.trim());
      setInputText('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="fixed bottom-16 left-0 right-0 bg-white border-t border-gray-200 px-4 py-3">
      <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
        <div className="flex items-center space-x-2">
          {/* Input Field */}
          <div className="flex-1">
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={INPUT_PLACEHOLDER}
              disabled={isLoading}
              className="w-full px-4 py-3 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent disabled:bg-gray-100 disabled:text-gray-500"
            />
          </div>
          
          {/* Send Button */}
          <button
            type="submit"
            disabled={!inputText.trim() || isLoading}
            className="p-3 bg-gradient-to-r from-teal-700 to-blue-800 text-white rounded-full hover:from-teal-800 hover:to-blue-900 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed transition-all duration-200 flex-shrink-0"
          >
            <Send size={20} className="transform rotate-90" />
          </button>
        </div>
      </form>
    </div>
  );
};

export default ChatInputBar;
