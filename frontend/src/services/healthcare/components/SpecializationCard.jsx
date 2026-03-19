import React from 'react';

const SpecializationCard = ({ name, icon: Icon }) => {
  return (
    <div className="flex-shrink-0 w-24 flex flex-col items-center gap-2">
      <div 
        className="w-16 h-16 rounded-2xl flex items-center justify-center"
        style={{ 
          backgroundColor: '#F4F4F6',
          borderRadius: '16px',
          padding: '16px'
        }}
      >
        <Icon className="w-8 h-8 text-purple-600" />
      </div>
      <span className="text-xs text-gray-700 text-center font-medium">{name}</span>
    </div>
  );
};

export default SpecializationCard;
