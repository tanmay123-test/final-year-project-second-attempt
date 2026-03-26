import React from 'react';

const TypingIndicator = () => {
  return (
    <div className="flex justify-start mb-4">
      <div className="flex items-start space-x-2">
        {/* Invisible spacer for alignment with AI avatar */}
        <div className="w-6 h-6 flex-shrink-0"></div>
        
        {/* Typing Bubble */}
        <div className="bg-white rounded-xl shadow-sm p-3">
          <div className="flex space-x-1">
            <div className="w-2 h-2 bg-teal-500 rounded-full animate-typing-dot-1"></div>
            <div className="w-2 h-2 bg-teal-500 rounded-full animate-typing-dot-2"></div>
            <div className="w-2 h-2 bg-teal-500 rounded-full animate-typing-dot-3"></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TypingIndicator;
