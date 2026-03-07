import React, { useState } from 'react';

const ProviderAuth = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
    service_type: 'Housekeeping'
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    const endpoint = isLogin ? '/housekeeping/provider/auth/login' : '/housekeeping/provider/auth/signup';
    // Call API
    console.log(`Submitting to ${endpoint}`, formData);
  };

  return (
    <div className="provider-auth-container">
      <h2>{isLogin ? 'Provider Login' : 'Provider Signup'}</h2>
      <form onSubmit={handleSubmit}>
        {!isLogin && (
          <div className="form-group">
            <label>Full Name</label>
            <input 
              type="text" 
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
            />
          </div>
        )}
        
        <div className="form-group">
          <label>Email</label>
          <input 
            type="email" 
            value={formData.email}
            onChange={(e) => setFormData({...formData, email: e.target.value})}
          />
        </div>
        
        <div className="form-group">
          <label>Password</label>
          <input 
            type="password" 
            value={formData.password}
            onChange={(e) => setFormData({...formData, password: e.target.value})}
          />
        </div>

        <button type="submit">{isLogin ? 'Login' : 'Sign Up'}</button>
      </form>
      
      <p onClick={() => setIsLogin(!isLogin)}>
        {isLogin ? 'Need an account? Sign up' : 'Already have an account? Login'}
      </p>
    </div>
  );
};

export default ProviderAuth;
