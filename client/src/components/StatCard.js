import React from 'react';
import { ArrowUpIcon, ArrowDownIcon } from '@heroicons/react/24/solid';

const StatCard = ({ 
  title, 
  value, 
  icon: Icon, 
  change, 
  changeType = 'up', 
  loading = false,
  description = null
}) => {
  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
      {loading ? (
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
          <div className="h-8 bg-gray-300 rounded w-1/2 mb-4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/4"></div>
        </div>
      ) : (
        <>
          <div className="flex justify-between items-start">
            <div>
              <h3 className="text-gray-500 text-sm font-medium">{title}</h3>
              <p className="text-2xl font-bold mt-1 text-gray-900">{value}</p>
              
              {change && (
                <div className="flex items-center mt-2">
                  {changeType === 'up' ? (
                    <ArrowUpIcon className="h-4 w-4 text-green-500" />
                  ) : (
                    <ArrowDownIcon className="h-4 w-4 text-red-500" />
                  )}
                  <span 
                    className={`ml-1 text-sm ${
                      changeType === 'up' ? 'text-green-500' : 'text-red-500'
                    }`}
                  >
                    {change}
                  </span>
                  {change.includes('%') && <span className="text-sm text-gray-500 ml-1">vs periodo anterior</span>}
                </div>
              )}
              
              {description && (
                <div className="mt-2 text-xs text-gray-500">
                  {description}
                </div>
              )}
            </div>
            
            {Icon && (
              <div className="bg-amber-50 p-3 rounded-lg">
                <Icon className="h-6 w-6 text-amber-800" />
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default StatCard;
