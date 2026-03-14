import React from 'react';

const ChatAssistant = () => {
  return (
    <div className="chat-assistant">
      <div className="assistant-bubble">
        <div className="assistant-content">
          <div className="assistant-greeting">
            <span className="sparkle">✨</span>
            <span className="assistant-title">Hi! I'm Finny 🤖</span>
          </div>
          <p className="assistant-message">
            Tell me your expenses in natural language and I'll track them for you!
          </p>
          <div className="assistant-example">
            <p className="example-title">Try:</p>
            <p className="example-text">"food 200 transport 150"</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatAssistant;
