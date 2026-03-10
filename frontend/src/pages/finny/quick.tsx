import React, { useState, useEffect } from 'react';
import { ArrowLeft, Search } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { moneyService } from '../../shared/api';

interface Transaction {
  id: number;
  merchant: string;
  category: string;
  amount: number;
  description: string;
  date: string;
  category_color?: string;
}

const FinnyQuick: React.FC = () => {
  const navigate = useNavigate();
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [filteredTransactions, setFilteredTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [activeTab, setActiveTab] = useState('Transactions');

  const categories = ['All', 'Food', 'Transport', 'Shopping', 'Bills', 'Entertainment'];

  const categoryColors: { [key: string]: string } = {
    'Food': 'bg-blue-500',
    'Shopping': 'bg-yellow-500',
    'Transport': 'bg-teal-500',
    'Bills': 'bg-green-500',
    'Entertainment': 'bg-orange-500',
  };

  useEffect(() => {
    fetchTransactions();
  }, []);

  useEffect(() => {
    filterTransactions();
  }, [transactions, searchTerm, selectedCategory]);

  const fetchTransactions = async () => {
    try {
      setLoading(true);
      const response = await moneyService.getTransactions();
      setTransactions(response.data.transactions || []);
    } catch (error) {
      console.error('Failed to fetch transactions:', error);
      // Fallback data for demo
      setTransactions([
        {
          id: 1,
          merchant: "Swiggy",
          category: "Food",
          amount: 250,
          description: "Lunch order",
          date: "2026-03-09"
        },
        {
          id: 2,
          merchant: "Amazon",
          category: "Shopping",
          amount: 1200,
          description: "Headphones",
          date: "2026-03-08"
        },
        {
          id: 3,
          merchant: "Uber",
          category: "Transport",
          amount: 180,
          description: "Ride to office",
          date: "2026-03-07"
        },
        {
          id: 4,
          merchant: "Netflix",
          category: "Entertainment",
          amount: 299,
          description: "Monthly subscription",
          date: "2026-03-06"
        },
        {
          id: 5,
          merchant: "Electric Bill",
          category: "Bills",
          amount: 850,
          description: "March electricity bill",
          date: "2026-03-05"
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const filterTransactions = () => {
    let filtered = transactions;

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(transaction =>
        transaction.merchant.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Filter by category
    if (selectedCategory !== 'All') {
      filtered = filtered.filter(transaction =>
        transaction.category === selectedCategory
      );
    }

    setFilteredTransactions(filtered);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      year: 'numeric' 
    });
  };

  const getCategoryColor = (category: string) => {
    return categoryColors[category] || 'bg-gray-500';
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-500 to-blue-600 text-white p-4">
        <div className="flex items-center mb-2">
          <button 
            onClick={() => navigate(-1)}
            className="mr-3 p-2 rounded-full hover:bg-white/20 transition-colors"
          >
            <ArrowLeft size={20} />
          </button>
          <div>
            <h1 className="text-xl font-bold">Quick Mode</h1>
            <p className="text-sm opacity-90">Fast & Simple tracking</p>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white shadow-sm px-4 py-3">
        <div className="flex space-x-2">
          {['Quick Add', 'Transactions', 'Summary', 'Analytics'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                activeTab === tab
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      {/* Search and Filter Bar */}
      <div className="bg-white px-4 py-3 border-b">
        <div className="flex items-center space-x-3">
          <div className="flex-1 relative">
            <Search size={18} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search merchant..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {categories.map((category) => (
              <option key={category} value={category}>
                {category}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Transaction List */}
      <div className="flex-1 overflow-y-auto p-4">
        {loading ? (
          <div className="flex justify-center items-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          </div>
        ) : filteredTransactions.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-gray-500">No transactions found</p>
          </div>
        ) : (
          <div className="space-y-3">
            {filteredTransactions.map((transaction) => (
              <div
                key={transaction.id}
                className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3 flex-1">
                    <div className={`w-3 h-3 rounded-full ${getCategoryColor(transaction.category)} mt-1`}></div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900">{transaction.merchant}</h3>
                      <p className="text-sm text-gray-600">
                        {transaction.category} • {formatDate(transaction.date)}
                      </p>
                      <p className="text-sm text-gray-500 mt-1">{transaction.description}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-red-600">-₹{transaction.amount.toLocaleString()}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Bottom Navigation */}
      <div className="bg-white border-t border-gray-200">
        <div className="flex justify-around py-2">
          {[
            { name: 'Finny', icon: '₹', active: true },
            { name: 'Budget', icon: '📊', active: false },
            { name: 'Loan', icon: '💰', active: false },
            { name: 'Goal Jar', icon: '🎯', active: false },
            { name: 'AI Coach', icon: '🤖', active: false },
          ].map((item) => (
            <button
              key={item.name}
              className={`flex flex-col items-center py-2 px-3 rounded-lg transition-colors ${
                item.active ? 'text-blue-500' : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <span className="text-xl mb-1">{item.icon}</span>
              <span className="text-xs font-medium">{item.name}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default FinnyQuick;
