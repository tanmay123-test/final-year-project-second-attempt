 // Natural Language Chat Parser for Finny

export const chatParser = {
  // Merchant to category mapping
  merchantCategoryMap: {
    'swiggy': 'Food',
    'zomato': 'Food',
    'dominos': 'Food',
    'pizza hut': 'Food',
    'starbucks': 'Food',
    'cafe': 'Food',
    'restaurant': 'Food',
    'food': 'Food',
    'lunch': 'Food',
    'dinner': 'Food',
    'breakfast': 'Food',
    'uber': 'Transport',
    'ola': 'Transport',
    'taxi': 'Transport',
    'metro': 'Transport',
    'bus': 'Transport',
    'auto': 'Transport',
    'rickshaw': 'Transport',
    'transport': 'Transport',
    'travel': 'Transport',
    'amazon': 'Shopping',
    'flipkart': 'Shopping',
    'myntra': 'Shopping',
    'shopping': 'Shopping',
    'clothes': 'Shopping',
    'shoes': 'Shopping',
    'jio': 'Bills',
    'airtel': 'Bills',
    'bsnl': 'Bills',
    'electricity': 'Bills',
    'water': 'Bills',
    'gas': 'Bills',
    'internet': 'Bills',
    'phone': 'Bills',
    'bills': 'Bills',
    'rent': 'Bills',
    'netflix': 'Entertainment',
    'prime': 'Entertainment',
    'disney': 'Entertainment',
    'hotstar': 'Entertainment',
    'spotify': 'Entertainment',
    'movie': 'Entertainment',
    'entertainment': 'Entertainment',
    'game': 'Entertainment'
  },

  // Parse natural language input
  parseInput: (input) => {
    const transactions = [];
    
    // Split by common separators
    const parts = input.split(/[\s,]+/).filter(part => part.length > 0);
    
    let currentMerchant = '';
    let currentCategory = '';
    let currentAmount = 0;
    let lastMeaningfulWord = '';
    
    const isNumber = (str) => !isNaN(str) && !isNaN(parseFloat(str));
    const isAmount = (str) => !isNaN(parseFloat(str)) && parseFloat(str) > 0;
    const stopWords = new Set([
      'i', 'was', 'is', 'a', 'the', 'for', 'on', 'at', 'to',
      'my', 'me', 'and', 'in', 'of', 'spent', 'paid', 'bought'
    ]);
    const inferCategory = (word) => {
      const map = {
        food: 'Food & Dining',
        grocery: 'Groceries',
        groceries: 'Groceries',
        electricity: 'Utilities',
        bill: 'Utilities',
        rent: 'Housing',
        travel: 'Transport',
        cab: 'Transport',
        movie: 'Entertainment',
        medicine: 'Healthcare',
        doctor: 'Healthcare',
        clothes: 'Shopping',
        shopping: 'Shopping',
      };
      return map[word?.toLowerCase()] || 'Other';
    };

    for (let i = 0; i < parts.length; i++) {
      const rawPart = parts[i];
      const part = rawPart.toLowerCase();
      if (!stopWords.has(part)) {
        lastMeaningfulWord = rawPart;
      }
      
      // Check if it's a merchant name
      const category = chatParser.merchantCategoryMap[part];
      if (category) {
        // Save previous transaction if exists
        if (currentMerchant && currentAmount > 0) {
          transactions.push({
            merchant: currentMerchant.charAt(0).toUpperCase() + currentMerchant.slice(1),
            category: currentCategory,
            amount: currentAmount
          });
        }
        
        // Start new transaction
        currentMerchant = part;
        currentCategory = category;
        currentAmount = 0;
      }
      // Check if it's a number (amount)
      else if (isNumber(part)) {
        currentAmount = parseFloat(part);
        if (isAmount(part) && !currentMerchant) {
          const next = (parts[i + 1] || '').toLowerCase();
          if (next === 'on' || next === 'for' || next === 'at') {
            currentMerchant = (parts[i + 2] || 'other').toLowerCase();
            i += 2;
          } else {
            currentMerchant = (lastMeaningfulWord || 'other').toLowerCase();
          }
          if (!currentCategory) {
            currentCategory = inferCategory(currentMerchant);
          }
        }
      }
      // If we have a merchant but no category yet, treat as merchant name
      else if (currentMerchant && !currentCategory && !isNumber(part)) {
        currentMerchant = part;
      }
    }
    
    // Add the last transaction
    if (currentMerchant && currentAmount > 0) {
      transactions.push({
        merchant: currentMerchant.charAt(0).toUpperCase() + currentMerchant.slice(1),
        category: currentCategory || 'Other',
        amount: currentAmount,
        type: 'expense'
      });
    }
    
    return transactions;
  },

  // Check if a string is a number
  isNumber: (str) => {
    return !isNaN(str) && !isNaN(parseFloat(str));
  },

  // Get category from merchant name
  getCategory: (merchant) => {
    const normalizedMerchant = merchant.toLowerCase();
    return chatParser.merchantCategoryMap[normalizedMerchant] || 'Other';
  },

  // Format transactions for API
  formatForAPI: (transactions) => {
    return transactions.map(tx => ({
      merchant: tx.merchant,
      category: tx.category,
      amount: tx.amount,
      description: `Added via chat: ${tx.merchant}`,
      date: new Date().toISOString().split('T')[0]
    }));
  }
};
