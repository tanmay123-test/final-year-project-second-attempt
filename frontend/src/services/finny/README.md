# Finny Smart Transaction Tracker

## Overview
Finny is a comprehensive financial management service that provides users with smart transaction tracking, analytics, and financial insights.

## Features

### 🏠 Home Screen
- **Unified Finny Dashboard** - Main landing page with monthly summary
- **Donut Chart Visualization** - Interactive spending breakdown
- **Mode Selection** - Quick Mode, Chat Mode, Analytics Mode
- **Bottom Navigation** - Easy access to all features

### 🚀 Quick Mode
- Fast & Simple transaction entry
- Quick add transactions interface
- View transaction history
- Monthly summary access

### 💬 Chat Mode
- Natural language expense entry
- Chat-style financial assistant
- Today's financial summary
- AI-powered insights

### 📊 Analytics Mode
- Comprehensive financial dashboard
- Budget monitoring
- Financial predictions
- Health score tracking

## File Structure

```
services/finny/
├── pages/
│   ├── FinnyHomeScreen.jsx          # Main dashboard
│   ├── QuickTransactionsPage.jsx    # Quick mode interface
│   ├── ChatFinancialAssistantPage.jsx # Chat mode interface
│   └── AnalyticsDashboardPage.jsx   # Analytics mode interface
├── styles/
│   └── FinnyHomeScreen.css          # Main styles
├── index.js                         # Service exports
└── README.md                        # This file
```

## Routes

- `/finny` - Main home screen
- `/finny/quick` - Quick transactions mode
- `/finny/chat` - Chat assistant mode
- `/finny/analytics` - Analytics dashboard

## Color Scheme

### Header Gradient
- Top: #1F5F7A
- Bottom: #2C7DA0

### Category Colors
- Food: #0F4C5C
- Shopping: #F4B400
- Bills: #2E8B57
- Transport: #2C7DA0
- Entertainment: #E67E22

### Navigation
- Active: #F4B400
- Inactive: #6B7280

## Components Used

- **Lucide React Icons** - All UI icons
- **React Router** - Navigation
- **Custom CSS** - Responsive styling

## Responsive Design

The Finny interface is fully responsive and works on:
- Mobile devices (320px+)
- Tablets (768px+)
- Desktop (1024px+)

## Integration

The Finny service integrates with:
- Main authentication system
- User profiles
- Transaction database
- Analytics backend

## Development

To add new features to Finny:

1. Create new components in `pages/` or `components/`
2. Add styles in `styles/`
3. Export from `index.js`
4. Add routes in `App.jsx`

## Notes

- All components are protected routes requiring authentication
- Follows the existing project architecture
- Uses consistent styling with other services
- Maintains responsive design principles
