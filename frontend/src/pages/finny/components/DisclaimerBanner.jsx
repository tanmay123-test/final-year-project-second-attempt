import React from 'react';
import { AlertTriangle } from 'lucide-react';
import { DISCLAIMER_TEXT } from '../constants/aiCoachConstants';

const DisclaimerBanner = () => {
  return (
    <div className="bg-amber-50 border border-amber-200 px-4 py-2 flex items-center space-x-2">
      <AlertTriangle size={16} className="text-amber-600 flex-shrink-0" />
      <p className="text-amber-800 text-sm font-medium">
        ⚠ {DISCLAIMER_TEXT}
      </p>
    </div>
  );
};

export default DisclaimerBanner;
