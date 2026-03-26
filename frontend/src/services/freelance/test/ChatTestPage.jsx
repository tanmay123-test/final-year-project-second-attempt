import React, { useState } from 'react';
import { useAuth } from '../../../context/AuthContext';
import RealTimeChat from '../components/RealTimeChat';

const ChatTestPage = () => {
  const { user } = useAuth();
  const [testProjectId] = useState(1); // Test with project ID 1
  const [showChat, setShowChat] = useState(true);

  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      <h1>Freelance Chat Test Page</h1>
      
      <div style={{ marginBottom: '20px' }}>
        <p><strong>User ID:</strong> {user?.user_id || 'Not logged in'}</p>
        <p><strong>Test Project ID:</strong> {testProjectId}</p>
        <p><strong>Status:</strong> {user ? '✅ Logged in' : '❌ Not logged in'}</p>
      </div>

      <div style={{ marginBottom: '20px' }}>
        <button 
          onClick={() => setShowChat(!showChat)}
          style={{
            padding: '10px 20px',
            background: '#667eea',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer'
          }}
        >
          {showChat ? 'Hide Chat' : 'Show Chat'}
        </button>
      </div>

      {showChat && (
        <div style={{ 
          height: '600px', 
          border: '2px solid #e5e7eb',
          borderRadius: '12px',
          overflow: 'hidden'
        }}>
          <RealTimeChat 
            projectId={testProjectId}
            currentUserId={user?.user_id}
            projectTitle="Test Project - Real-time Communication"
          />
        </div>
      )}

      <div style={{ marginTop: '20px', padding: '15px', background: '#f3f4f6', borderRadius: '8px' }}>
        <h3>Test Instructions:</h3>
        <ol>
          <li>Make sure you're logged in</li>
          <li>Start the backend server: <code>python app.py</code></li>
          <li>Open this page in two different browser windows</li>
          <li>Send messages from one window</li>
          <li>Verify they appear in real-time in the other window</li>
          <li>Check browser console for any errors</li>
        </ol>
      </div>
    </div>
  );
};

export default ChatTestPage;
