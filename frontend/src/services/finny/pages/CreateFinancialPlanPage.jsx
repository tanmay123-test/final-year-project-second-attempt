import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Plus } from 'lucide-react';
import { analyticsApi } from '../api/analyticsApi';
import '../styles/BudgetPage.css';

const CreateFinancialPlanPage = () => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  
  const [formData, setFormData] = useState({
    monthlyIncome: '30000',
    rentMortgage: '',
    educationLoan: '',
    personalLoan: '',
    utilities: '',
    internet: '',
    transport: '',
    insurance: '',
    customExpenses: [],
    food: '',
    shopping: '',
    entertainment: '',
    health: '',
    savingsPercent: 20,
    emergencyFund: '',
    goals: [],
    categoryBudgets: []
  });

  const [categoryBudgets, setCategoryBudgets] = useState(() => {
    const disposable = (parseFloat(formData.monthlyIncome) || 50000) - 0; // totalFixed will be calculated later
    return [
      { name: 'Groceries', amount: disposable * 0.20 },
      { name: 'Transport', amount: disposable * 0.15 },
      { name: 'Utilities', amount: disposable * 0.15 },
      { name: 'Shopping', amount: disposable * 0.15 },
      { name: 'Entertainment', amount: disposable * 0.15 },
      { name: 'Dining Out', amount: disposable * 0.20 },
    ];
  });

  const [newGoal, setNewGoal] = useState({
    name: '',
    targetAmount: '',
    timeline: ''
  });

  // Auto-save plan when reaching step 7
  React.useEffect(() => {
    if (currentStep === 7) {
      const savePlan = async () => {
        try {
          const monthlyIncome = parseFloat(formData.monthlyIncome) || 0;
          const totalFixed = calculateTotalFixed();
          const disposableIncome = monthlyIncome - totalFixed;
          const savingsTarget = disposableIncome * ((formData.savingsPercent || 20) / 100);
          
          await analyticsApi.createFinancialPlan({
            monthlyIncome,
            totalFixed,
            disposableIncome,
            savingsTarget,
            categoryBudgets,
            savingsPercent: formData.savingsPercent || 20,
            createdAt: new Date().toISOString()
          });
        } catch (err) {
          console.error('Plan save failed:', err);
          // Don't block UI on save failure
        }
      };
      
      savePlan();
    }
  }, [currentStep]);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error for this field if exists
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const validateStep = () => {
    const newErrors = {};
    
    switch(currentStep) {
      case 1:
        if (!formData.monthlyIncome || formData.monthlyIncome <= 0) {
          newErrors.monthlyIncome = 'Please enter a valid amount';
        }
        break;
      case 2:
        const fixedFields = ['rentMortgage', 'educationLoan', 'personalLoan', 'utilities', 'internet', 'transport', 'insurance'];
        fixedFields.forEach(field => {
          if (formData[field] && formData[field] < 0) {
            newErrors[field] = 'Please enter a valid amount';
          }
        });
        // Validate custom expenses
        (formData.customExpenses || []).forEach((expense, index) => {
          if (expense.amount && expense.amount < 0) {
            newErrors[`custom_${index}`] = 'Please enter a valid amount';
          }
        });
        break;
      case 3:
        const variableFields = ['food', 'transport', 'shopping', 'entertainment', 'health'];
        variableFields.forEach(field => {
          if (formData[field] && formData[field] < 0) {
            newErrors[field] = 'Please enter a valid amount';
          }
        });
        break;
      case 5:
        if (!formData.emergencyFund || formData.emergencyFund <= 0) {
          newErrors.emergencyFund = 'Please enter a valid amount';
        }
        break;
      case 6:
        if (formData.goals.length === 0) {
          newErrors.goals = 'Please add at least one financial goal';
        }
        break;
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleContinue = () => {
    if (!validateStep()) return;
    
    if (currentStep < 7) {
      setCurrentStep(prev => prev + 1);
    } else {
      handleSubmit();
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(prev => prev - 1);
    } else {
      navigate('/finny/budget');
    }
  };

  const addGoal = () => {
    if (newGoal.name && newGoal.targetAmount && newGoal.timeline) {
      setFormData(prev => ({
        ...prev,
        goals: [...prev.goals, { ...newGoal, id: Date.now() }]
      }));
      setNewGoal({ name: '', targetAmount: '', timeline: '' });
    }
  };

  const removeGoal = (id) => {
    setFormData(prev => ({
      ...prev,
      goals: prev.goals.filter(goal => goal.id !== id)
    }));
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      // Calculate totals
      const totalFixed = parseFloat(formData.rent || 0) + 
                        parseFloat(formData.utilities || 0) + 
                        parseFloat(formData.insurance || 0) + 
                        parseFloat(formData.otherFixed || 0);
      
      const totalVariable = parseFloat(formData.food || 0) + 
                          parseFloat(formData.transport || 0) + 
                          parseFloat(formData.shopping || 0) + 
                          parseFloat(formData.entertainment || 0) + 
                          parseFloat(formData.health || 0);
      
      const savingsAmount = (parseFloat(formData.monthlyIncome) * formData.savingsPercent) / 100;
      const disposable = parseFloat(formData.monthlyIncome) - totalFixed - totalVariable - savingsAmount;

      const planData = {
        ...formData,
        totalFixed,
        totalVariable,
        savingsAmount,
        disposable
      };

      // Call API to save plan
      const response = await analyticsApi.createFinancialPlan(planData);
      
      if (response.success) {
        // Show success message and navigate back
        navigate('/finny/budget', { 
          state: { message: 'Plan created successfully! 🎉' } 
        });
      }
    } catch (error) {
      console.error('Failed to create plan:', error);
      setErrors({ submit: 'Failed to create plan. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  const calculateTotalFixed = () => {
    const fixedFields = ['rentMortgage', 'educationLoan', 'personalLoan', 'utilities', 'internet', 'transport', 'insurance'];
    const fixedTotal = fixedFields.reduce((sum, field) => {
      return sum + (parseFloat(formData[field]) || 0);
    }, 0);
    
    const customTotal = (formData.customExpenses || []).reduce((sum, expense) => {
      return sum + (parseFloat(expense.amount) || 0);
    }, 0);
    
    return fixedTotal + customTotal;
  };

  const calculateSavingsAmount = () => {
    const income = parseFloat(formData.monthlyIncome) || 0;
    return Math.round((income * formData.savingsPercent) / 100);
  };

  const calculateTotals = () => {
    const totalFixed = calculateTotalFixed();
    
    const totalVariable = parseFloat(formData.food || 0) + 
                        parseFloat(formData.shopping || 0) + 
                        parseFloat(formData.entertainment || 0) + 
                        parseFloat(formData.health || 0);
    
    const savingsAmount = calculateSavingsAmount();
    const disposable = parseFloat(formData.monthlyIncome) - totalFixed - totalVariable - savingsAmount;
    
    return { totalFixed, totalVariable, savingsAmount, disposable };
  };

  const renderStepContent = () => {
    // Common calculations used across steps
    const monthlyIncome = parseFloat(formData.monthlyIncome) || 0;
    const totalFixed = calculateTotalFixed();
    const disposableIncome = monthlyIncome - totalFixed;
    const savingsPercent = formData.savingsPercent || 20;
    const formatINR = (amount) => "₹" + Math.round(amount).toLocaleString('en-IN');

    switch(currentStep) {
      case 1:
        return (
          <div className="step-page">
            <h2 className="step-title">Step 1 – Monthly Income</h2>
            <p className="step-subtitle">Enter your total monthly income.</p>
            
            <div className="input-card">
              <span className="input-rupee-icon">₹</span>
              <input
                type="number"
                value={formData.monthlyIncome}
                onChange={(e) => handleInputChange('monthlyIncome', e.target.value)}
                placeholder="30000"
                min="0"
              />
            </div>
            {errors.monthlyIncome && <div className="error-text">{errors.monthlyIncome}</div>}
          </div>
        );

      case 2:
        return (
          <div className="step-page">
            <h2 className="step-title">Step 2 – Fixed Expenses</h2>
            
            {/* Fixed Expense Fields */}
            {[
              { field: 'rentMortgage', label: 'Rent / Mortgage' },
              { field: 'educationLoan', label: 'Education Loan' },
              { field: 'personalLoan', label: 'Personal Loan' },
              { field: 'utilities', label: 'Utilities' },
              { field: 'internet', label: 'Internet' },
              { field: 'transport', label: 'Transport' },
              { field: 'insurance', label: 'Insurance' }
            ].map(({ field, label }) => (
              <div key={field} className="fixed-input-row">
                <span className="fixed-input-label">{label}</span>
                <div className="fixed-input-box">
                  <span>₹</span>
                  <input
                    type="number"
                    value={formData[field]}
                    onChange={(e) => handleInputChange(field, e.target.value)}
                    placeholder="0"
                    min="0"
                  />
                </div>
              </div>
            ))}
            
            {/* Add Custom Expense */}
            <div className="add-custom-expense" onClick={() => {
              setFormData(prev => ({
                ...prev,
                customExpenses: [...(prev.customExpenses || []), { label: '', amount: '' }]
              }));
            }}>
              <span className="add-icon">+</span>
              <span className="add-text">Add Custom Expense</span>
            </div>
            
            {/* Custom Expenses List */}
            {formData.customExpenses?.map((expense, index) => (
              <div key={index} className="fixed-input-row">
                <input
                  type="text"
                  placeholder="Custom expense name"
                  value={expense.label}
                  onChange={(e) => {
                    const newCustom = [...(formData.customExpenses || [])];
                    newCustom[index].label = e.target.value;
                    setFormData(prev => ({ ...prev, customExpenses: newCustom }));
                  }}
                  className="custom-expense-label"
                />
                <div className="fixed-input-box">
                  <span>₹</span>
                  <input
                    type="number"
                    value={expense.amount}
                    onChange={(e) => {
                      const newCustom = [...(formData.customExpenses || [])];
                      newCustom[index].amount = e.target.value;
                      setFormData(prev => ({ ...prev, customExpenses: newCustom }));
                    }}
                    placeholder="0"
                    min="0"
                  />
                </div>
              </div>
            ))}
            
            {/* Total Fixed Card */}
            <div className="total-fixed-card">
              <div className="total-fixed-row">
                <span>Total Fixed</span>
                <span>₹{calculateTotalFixed().toLocaleString('en-IN')}</span>
              </div>
            </div>
          </div>
        );

      case 3:
        const savingsTarget = disposableIncome * (savingsPercent / 100);
        
        const incomeBarWidth = 100;
        const fixedBarWidth = monthlyIncome > 0 ? Math.min((totalFixed / monthlyIncome) * 100, 100) : 0;
        const disposableBarWidth = monthlyIncome > 0 ? Math.min((disposableIncome / monthlyIncome) * 100, 100) : 0;
        const savingsBarWidth = savingsPercent;
        
        return (
          <div className="step-page">
            <h2 className="step-title">Step 3 – Financial Summary</h2>
            
            {/* Card 1 - Monthly Income */}
            <div className="summary-step-card">
              <div className="summary-card-row">
                <span className="summary-card-label">Monthly Income</span>
                <span className="summary-card-amount">{formatINR(monthlyIncome)}</span>
              </div>
              <div className="summary-progress-track">
                <div 
                  className="summary-progress-fill fill-navy"
                  style={{ width: `${incomeBarWidth}%` }}
                ></div>
              </div>
            </div>
            
            {/* Card 2 - Fixed Expenses */}
            <div className="summary-step-card">
              <div className="summary-card-row">
                <span className="summary-card-label">Fixed Expenses</span>
                <span className="summary-card-amount">{formatINR(totalFixed)}</span>
              </div>
              <div className="summary-progress-track">
                <div 
                  className="summary-progress-fill fill-navy"
                  style={{ width: `${fixedBarWidth}%` }}
                ></div>
              </div>
            </div>
            
            {/* Card 3 - Disposable Income */}
            <div className="summary-step-card">
              <div className="summary-card-row">
                <span className="summary-card-label">Disposable Income</span>
                <span className="summary-card-amount">{formatINR(disposableIncome)}</span>
              </div>
              <div className="summary-progress-track">
                <div 
                  className="summary-progress-fill fill-gold"
                  style={{ width: `${disposableBarWidth}%` }}
                ></div>
              </div>
            </div>
            
            {/* Card 4 - Savings Target */}
            <div className="summary-step-card">
              <div className="summary-card-row">
                <span className="summary-card-label">Savings Target ({savingsPercent}%)</span>
                <span className="summary-card-amount">{formatINR(savingsTarget)}</span>
              </div>
              <div className="summary-progress-track">
                <div 
                  className="summary-progress-fill fill-green"
                  style={{ width: `${savingsBarWidth}%` }}
                ></div>
              </div>
            </div>
          </div>
        );

      case 4:
        const savingsAmount = disposableIncome * (savingsPercent / 100);
        const needsAmount = disposableIncome * 0.50;
        const wantsAmount = disposableIncome * 0.30;
        
        return (
          <div className="step-page">
            <h2 className="step-title">Step 4 – Smart Allocation (50/30/20)</h2>
            
            {/* Segmented Toggle Bar */}
            <div className="allocation-toggle">
              <div className="toggle-segment needs">Needs 50%</div>
              <div className="toggle-segment wants">Wants 30%</div>
              <div className="toggle-segment save">Save 20%</div>
            </div>
            
            {/* Allocation Cards */}
            <div className="allocation-card">
              <div className="allocation-label">
                <div className="allocation-dot dot-green"></div>
                <span>Savings</span>
              </div>
              <span className="allocation-amount">{formatINR(savingsAmount)}</span>
            </div>
            
            <div className="allocation-card">
              <div className="allocation-label">
                <div className="allocation-dot dot-navy"></div>
                <span>Needs</span>
              </div>
              <span className="allocation-amount">{formatINR(needsAmount)}</span>
            </div>
            
            <div className="allocation-card">
              <div className="allocation-label">
                <div className="allocation-dot dot-gold"></div>
                <span>Wants</span>
              </div>
              <span className="allocation-amount">{formatINR(wantsAmount)}</span>
            </div>
          </div>
        );

      case 5:
        const handleCategoryChange = (index, value) => {
          const newBudgets = [...categoryBudgets];
          newBudgets[index].amount = parseFloat(value) || 0;
          setCategoryBudgets(newBudgets);
        };

        const totalAllocated = categoryBudgets.reduce((sum, cat) => sum + cat.amount, 0);
        const availableAmount = disposableIncome * 0.50; // 50% for needs
        
        return (
          <div className="step-page">
            <h2 className="step-title">Step 5 – Category Budgets</h2>
            <p className="step-subtitle">Auto-allocated from disposable income.</p>
            
            {/* Category Budget Cards */}
            {categoryBudgets.map((category, index) => (
              <div key={index} className="category-budget-card">
                <span className="category-name">{category.name}</span>
                <div className="category-amount-wrap">
                  <span className="rupee-prefix">₹</span>
                  <input
                    type="number"
                    className="category-amount-input"
                    value={Math.round(category.amount)}
                    onChange={(e) => handleCategoryChange(index, e.target.value)}
                    min="0"
                  />
                </div>
              </div>
            ))}
            
            {/* Total Allocation Status */}
            <div className="total-allocation-card">
              <div className="allocation-status">
                <span>Total Allocated:</span>
                <span className={`allocation-total ${totalAllocated <= availableAmount ? 'within-budget' : 'over-budget'}`}>
                  ₹{Math.round(totalAllocated).toLocaleString('en-IN')} of ₹{Math.round(availableAmount).toLocaleString('en-IN')} available
                </span>
              </div>
            </div>
          </div>
        );

      case 6:
        const monthlySavings = disposableIncome * (savingsPercent / 100);
        const projectionData = [
          { label: 'Now', months: 0, amount: 0 },
          { label: '6mo', months: 6, amount: monthlySavings * 6 },
          { label: '12mo', months: 12, amount: monthlySavings * 12 },
          { label: '24mo', months: 24, amount: monthlySavings * 24 },
        ];
        
        // Custom SVG Line Chart for Projection
        const ProjectionChart = ({ data }) => {
          const maxValue = monthlySavings * 24;
          const chartWidth = 400;
          const chartHeight = 220;
          const padding = { top: 10, right: 16, left: 40, bottom: 30 };
          
          const getXPosition = (index) => {
            const availableWidth = chartWidth - padding.left - padding.right;
            return padding.left + (index * availableWidth / (data.length - 1));
          };
          
          const getYPosition = (value) => {
            const availableHeight = chartHeight - padding.top - padding.bottom;
            return chartHeight - padding.bottom - ((value / maxValue) * availableHeight);
          };
          
          const createSmoothPath = () => {
            if (data.length < 2) return '';
            
            let path = `M ${getXPosition(0)} ${getYPosition(data[0].amount)}`;
            
            for (let i = 1; i < data.length; i++) {
              const x = getXPosition(i);
              const y = getYPosition(data[i].amount);
              const prevX = getXPosition(i - 1);
              const prevY = getYPosition(data[i - 1].amount);
              
              // Create smooth curve using quadratic bezier
              const cpX = (prevX + x) / 2;
              path += ` Q ${cpX} ${prevY}, ${x} ${y}`;
            }
            
            return path;
          };
          
          const formatYAxis = (value) => {
            return value === 0 ? '₹0k' : `₹${value/1000}k`;
          };
          
          return (
            <div style={{ width: '100%', height: '220px' }}>
              <svg width="100%" height="100%" viewBox={`0 0 ${chartWidth} ${chartHeight}`} preserveAspectRatio="none">
                {/* Background */}
                <rect
                  x={padding.left}
                  y={padding.top}
                  width={chartWidth - padding.left - padding.right}
                  height={chartHeight - padding.top - padding.bottom}
                  fill="#F9FAFB"
                />
                
                {/* Grid Lines */}
                {[0, monthlySavings * 6, monthlySavings * 12, monthlySavings * 18, monthlySavings * 24].map((value) => {
                  const y = getYPosition(value);
                  return (
                    <line
                      key={value}
                      x1={padding.left}
                      x2={chartWidth - padding.right}
                      y1={y}
                      y2={y}
                      stroke="#e8e8e8"
                      strokeDasharray="3 3"
                    />
                  );
                })}
                
                {/* X and Y axis lines */}
                <line
                  x1={padding.left}
                  x2={chartWidth - padding.right}
                  y1={chartHeight - padding.bottom}
                  y2={chartHeight - padding.bottom}
                  stroke="#e0e0e0"
                />
                
                {/* Y-axis labels */}
                {[0, monthlySavings * 6, monthlySavings * 12, monthlySavings * 18, monthlySavings * 24].map((value) => {
                  const y = getYPosition(value);
                  return (
                    <text
                      key={value}
                      x={padding.left - 10}
                      y={y + 4}
                      textAnchor="end"
                      fill="#888888"
                      fontSize="11"
                    >
                      {formatYAxis(value)}
                    </text>
                  );
                })}
                
                {/* X-axis labels */}
                {data.map((point, index) => {
                  const x = getXPosition(index);
                  return (
                    <text
                      key={point.label}
                      x={x}
                      y={chartHeight - padding.bottom + 20}
                      textAnchor="middle"
                      fill="#888888"
                      fontSize="11"
                    >
                      {point.label}
                    </text>
                  );
                })}
                
                {/* Line */}
                <path
                  d={createSmoothPath()}
                  fill="none"
                  stroke="#4CAF50"
                  strokeWidth="2.5"
                />
                
                {/* Data points */}
                {data.map((point, index) => {
                  const x = getXPosition(index);
                  const y = getYPosition(point.amount);
                  return (
                    <circle
                      key={index}
                      cx={x}
                      cy={y}
                      r="5"
                      fill="#4CAF50"
                      stroke="#ffffff"
                      strokeWidth="2"
                    />
                  );
                })}
              </svg>
            </div>
          );
        };
        
        return (
          <div className="step-page">
            <h2 className="step-title">Step 6 – Savings Projection</h2>
            
            {/* Projection Chart Card */}
            <div className="projection-chart-card">
              <div className="chart-header-text">
                <span>Monthly Savings: </span>
                <span className="monthly-savings-amount">{formatINR(monthlySavings)}</span>
              </div>
              <ProjectionChart data={projectionData} />
            </div>
            
            {/* Projection Summary Cards */}
            <div className="projection-card">
              <span className="projection-label">6 months</span>
              <span className="projection-amount">{formatINR(monthlySavings * 6)}</span>
            </div>
            
            <div className="projection-card">
              <span className="projection-label">12 months</span>
              <span className="projection-amount">{formatINR(monthlySavings * 12)}</span>
            </div>
            
            <div className="projection-card">
              <span className="projection-label">24 months</span>
              <span className="projection-amount">{formatINR(monthlySavings * 24)}</span>
            </div>
          </div>
        );

      case 7:
        const finalMonthlyIncome = parseFloat(formData.monthlyIncome) || 0;
        const finalTotalFixed = calculateTotalFixed();
        const finalDisposableIncome = finalMonthlyIncome - finalTotalFixed;
        const finalSavingsTarget = finalDisposableIncome * ((formData.savingsPercent || 20) / 100);
        
        return (
          <div className="step-page">
            {/* Success Icon */}
            <div className="success-icon-wrap">
              <span className="success-checkmark">✓</span>
            </div>
            
            {/* Success Title */}
            <h2 className="success-title">Financial Plan Created!</h2>
            
            {/* Summary Cards */}
            <div className="final-summary-card">
              <span className="final-summary-label">Monthly Income</span>
              <span className="final-summary-amount">{formatINR(finalMonthlyIncome)}</span>
            </div>
            
            <div className="final-summary-card">
              <span className="final-summary-label">Fixed Expenses</span>
              <span className="final-summary-amount">{formatINR(finalTotalFixed)}</span>
            </div>
            
            <div className="final-summary-card">
              <span className="final-summary-label">Disposable Income</span>
              <span className="final-summary-amount">{formatINR(finalDisposableIncome)}</span>
            </div>
            
            <div className="final-summary-card">
              <span className="final-summary-label">Savings Target</span>
              <span className="final-summary-amount">{formatINR(finalSavingsTarget)}</span>
            </div>
            
            {/* Back to Dashboard Button */}
            <button 
              className="back-to-dashboard-btn"
              onClick={() => navigate('/finny/budget')}
            >
              Back to Dashboard
            </button>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="create-plan-page">
      {/* Header */}
      <div className="create-plan-header">
        <div className="header-content">
          <button className="back-btn" onClick={handleBack}>
            <ArrowLeft size={20} color="white" />
          </button>
          <div className="header-text">
            <h1 className="header-title">Create Financial Plan</h1>
            <p className="header-subtitle">Step {currentStep} of 7</p>
          </div>
        </div>
        
        {/* Progress Bar */}
        <div className="progress-bar-container">
          {[1, 2, 3, 4, 5, 6, 7].map(i => (
            <div
              key={i}
              className={`progress-segment ${i <= currentStep ? 'active' : ''}`}
            />
          ))}
        </div>
      </div>

      {/* Step Content */}
      {renderStepContent()}

      {/* Continue Button */}
      <div className="continue-btn-container">
        <button 
          className="continue-btn"
          onClick={handleContinue}
          disabled={loading}
        >
          {loading ? 'Creating...' : currentStep === 7 ? 'Create My Plan ✓' : 'Continue →'}
        </button>
      </div>

      {/* Error Message */}
      {errors.submit && <div className="error-message">{errors.submit}</div>}

      {/* Bottom Navigation */}
      <div className="finny-bottom-nav">
        <div className="nav-item" onClick={() => navigate('/finny')}>
          <div className="nav-icon">💰</div>
          <div className="nav-label">Finny</div>
        </div>
        <div className="nav-item active" onClick={() => navigate('/finny/budget')}>
          <div className="nav-icon">📊</div>
          <div className="nav-label">Budget</div>
        </div>
        <div className="nav-item" onClick={() => navigate('/finny/loan')}>
          <div className="nav-icon">📈</div>
          <div className="nav-label">Loan</div>
        </div>
        <div className="nav-item" onClick={() => navigate('/finny/goal-jar')}>
          <div className="nav-icon">🎯</div>
          <div className="nav-label">Goal Jar</div>
        </div>
        <div className="nav-item" onClick={() => navigate('/finny/ai-coach')}>
          <div className="nav-icon">🤖</div>
          <div className="nav-label">AI Coach</div>
        </div>
      </div>
    </div>
  );
};

export default CreateFinancialPlanPage;
