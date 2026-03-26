import { useState, useEffect, useCallback } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { useAuth } from '../../../context/AuthContext';
import { 
  API_ENDPOINT, 
  GREETING_ENDPOINT, 
  HISTORY_ENDPOINT,
  GREETING_MESSAGE 
} from '../constants/aiCoachConstants';

export const useAiChat = () => {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const { user } = useAuth();

  // Fetch greeting and history on mount
  useEffect(() => {
    if (user?.user_id) {
      fetchGreeting();
      fetchHistory();
    }
  }, [user?.user_id]);

  const fetchGreeting = async () => {
    try {
      const response = await fetch(`${GREETING_ENDPOINT}?user_id=${user.user_id}`);
      const data = await response.json();
      
      if (data.success && data.greeting) {
        const greetingMessage = {
          id: uuidv4(),
          sender: 'ai',
          type: 'general_query',
          text: data.greeting,
          timestamp: data.timestamp || new Date().toISOString()
        };
        setMessages(prev => [greetingMessage]);
      }
    } catch (err) {
      console.error('Error fetching greeting:', err);
    }
  };

  const fetchHistory = async () => {
    try {
      const response = await fetch(`${HISTORY_ENDPOINT}?user_id=${user.user_id}&limit=20`);
      const data = await response.json();
      
      if (data.success && data.history) {
        setMessages(prev => {
          const historyMessages = data.history.map(msg => ({
            id: msg.id || uuidv4(),
            sender: msg.sender,
            text: msg.text,
            type: msg.type || 'general_query',
            timestamp: msg.timestamp
          }));
          return [...prev, ...historyMessages];
        });
      }
    } catch (err) {
      console.error('Error fetching history:', err);
    }
  };

  const sendMessage = useCallback(async (text) => {
    if (!text.trim() || isLoading) return;

    const userMessage = {
      id: uuidv4(),
      sender: 'user',
      text: text.trim(),
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_ENDPOINT}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: user.user_id,
          message: text.trim()
        })
      });

      const data = await response.json();
      
      if (data.success) {
        const aiMessage = {
          id: uuidv4(),
          sender: 'ai',
          text: data.ai_response,
          type: data.message_type || 'general_query',
          timestamp: data.timestamp || new Date().toISOString()
        };
        setMessages(prev => [...prev, aiMessage]);
      } else {
        throw new Error(data.error || 'Failed to send message');
      }
    } catch (err) {
      console.error('Error sending message:', err);
      const errorMessage = {
        id: uuidv4(),
        sender: 'ai',
        text: 'Something went wrong. Please try again.',
        type: 'error',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [user.user_id, isLoading]);

  const sendChip = useCallback((chip) => {
    sendMessage(chip.message);
  }, [sendMessage]);

  return {
    messages,
    inputText,
    setInputText,
    isLoading,
    error,
    sendMessage,
    sendChip
  };
};
