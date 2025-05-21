import React from 'react';

const StatCard = ({ title, value, icon: Icon, change, changeType = 'up', loading = false }) => {
  return (
    <div className="card">
      {loading ? (
        <div className="loading h-24 flex flex-col justify-center">
          <div className="h-3 bg-gray-200 rounded w-1/2 mb-2"></div>
          <div className="h-5 bg-gray-300 rounded w-3/4 mb-2"></div>
          <div className="h-3 bg-gray-200 rounded w-1/3"></div>
        </div>
      ) : (
        <>
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-gray-500">{title}</h3>
            {Icon && <Icon className="h-6 w-6 text-coffee-600" />}
          </div>
          <p className="mt-1 text-2xl font-semibold text-gray-900">{value}</p>
          
          {change && (
            <div className="mt-2 flex items-center">
              <span 
                className={`inline-flex items-center ${
                  changeType === 'up' ? 'text-green-500' : 'text-red-500'
                }`}
              >
                <svg 
                  className={`mr-1 h-4 w-4 ${
                    changeType === 'up' ? 'text-green-500' : 'text-red-500'
                  }`} 
                  fill="none" 
                  viewBox="0 0 24 24" 
                  stroke="currentColor"
                >
                  <path 
                    strokeLinecap="round" 
                    strokeLinejoin="round" 
                    strokeWidth={2} 
                    d={changeType === 'up' ? 'M5 15l7-7 7 7' : 'M19 9l-7 7-7-7'} 
                  />
                </svg>
                {change}
              </span>
              <span className="ml-1 text-sm text-gray-500">vs periodo anterior</span>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default StatCard;
