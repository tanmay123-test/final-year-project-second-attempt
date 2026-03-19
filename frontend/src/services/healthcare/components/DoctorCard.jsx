import React from 'react';
import { Star, MapPin, Clock } from 'lucide-react';

const DoctorCard = ({ doctor }) => {
  const getInitial = (name) => {
    return name.split(' ').map(word => word[0]).join('').substring(0, 1);
  };

  return (
    <div className="bg-white rounded-2xl p-5 shadow-sm" style={{ borderRadius: '18px', padding: '18px' }}>
      <div className="flex gap-4">
        <div className="w-16 h-16 rounded-full bg-purple-100 flex items-center justify-center">
          <span className="text-xl font-bold text-purple-600">{getInitial(doctor.name)}</span>
        </div>
        <div className="flex-1">
          <h3 className="font-semibold text-gray-900">{doctor.name}</h3>
          <p className="text-sm text-gray-600">{doctor.specialization}</p>
          <div className="flex items-center gap-2 mt-1">
            <div className="flex items-center">
              <Star className="w-4 h-4 text-yellow-500 fill-current" />
              <span className="text-sm font-medium ml-1">{doctor.rating}</span>
            </div>
            <span className="text-sm text-gray-500">•</span>
            <span className="text-sm text-gray-500">{doctor.experience} yrs</span>
          </div>
          <div className="flex items-center gap-1 mt-1 text-gray-500">
            <MapPin className="w-3 h-3" />
            <span className="text-xs">{doctor.hospital}</span>
          </div>
          <div className="flex items-center justify-between mt-3">
            <div className="flex items-center gap-1 text-gray-500">
              <Clock className="w-3 h-3" />
              <span className="text-xs">Available today</span>
            </div>
            <button 
              className="px-5 py-2.5 text-white font-medium rounded-full transition-colors hover:opacity-90"
              style={{ 
                backgroundColor: '#7B4BB7',
                borderRadius: '20px',
                padding: '10px 18px'
              }}
            >
              Book Now
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DoctorCard;
