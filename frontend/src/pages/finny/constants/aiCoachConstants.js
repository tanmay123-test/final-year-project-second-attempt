export const QUICK_CHIPS = [
  { id: 'stock',     label: 'Analyze a Stock',  message: 'Analyze a stock for me' },
  { id: 'portfolio', label: 'My Portfolio',      message: 'Show my portfolio analysis' },
  { id: 'news',      label: 'Market News',       message: 'What is happening in the market today?' },
  { id: 'sip',       label: 'What is SIP?',      message: 'What is SIP and how does it work?' },
];

export const INTENT_BADGE_MAP = {
  stock_analysis:     { label: 'Stock',     color: 'blue' },
  portfolio_analysis: { label: 'Portfolio', color: 'green' },
  market_news:        { label: 'News',      color: 'amber' },
  knowledge_query:    { label: 'Education', color: 'purple' },
  financial_coach:    { label: 'Coach',     color: 'coral' },
  general_query:      { label: 'General',   color: 'gray' },
};

export const GREETING_MESSAGE = {
  id: 'greeting',
  sender: 'ai',
  type: 'general_query',
  text: null, // fetched from backend on mount — never hardcoded
  timestamp: null,
};

export const DISCLAIMER_TEXT = 'For educational purposes only. Not financial advice.';

export const INPUT_PLACEHOLDER = 'Ask about stocks, savings, investments...';

export const API_ENDPOINT = '/api/ai-coach/chat';
export const GREETING_ENDPOINT = '/api/ai-coach/greeting';
export const HISTORY_ENDPOINT = '/api/ai-coach/history';
