import React from 'react';
import { QUICK_CHIPS } from '../constants/aiCoachConstants';

const QuickChips = ({ onChipClick, isVisible }) => {
  if (!isVisible) return null;

  return (
    <div className="px-4 py-3 bg-gray-50">
      <div className="flex space-x-2 overflow-x-auto no-scrollbar">
        {QUICK_CHIPS.map((chip) => (
          <button
            key={chip.id}
            onClick={() => onChipClick(chip)}
            className="px-4 py-2 bg-white border border-gray-200 rounded-full text-sm font-medium text-gray-700 hover:bg-gray-50 hover:border-gray-300 active:bg-gray-100 transition-colors whitespace-nowrap"
          >
            {chip.label}
          </button>
        ))}
      </div>
    </div>
  );
};

export default QuickChips;
