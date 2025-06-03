import React, { useState } from 'react';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import { CalendarIcon } from '@heroicons/react/24/outline';

const DateRangePicker = ({ startDate, endDate, onChange }) => {
  const [isOpen, setIsOpen] = useState(false);
  
  const handleToggle = () => {
    setIsOpen(!isOpen);
  };
  
  const handleStartDateChange = (e) => {
    const newStartDate = new Date(e.target.value);
    onChange(newStartDate, endDate);
  };
  
  const handleEndDateChange = (e) => {
    const newEndDate = new Date(e.target.value);
    onChange(startDate, newEndDate);
  };
  
  const formatDateForDisplay = (date) => {
    return format(date, 'dd MMM yyyy', { locale: es });
  };
  
  const formatDateForInput = (date) => {
    return format(date, 'yyyy-MM-dd');
  };
  
  return (
    <div className="relative">
      <button
        onClick={handleToggle}
        className="flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-coffee-500"
      >
        <CalendarIcon className="h-5 w-5 mr-2 text-gray-400" />
        <span>
          {formatDateForDisplay(startDate)} - {formatDateForDisplay(endDate)}
        </span>
      </button>
      
      {isOpen && (
        <div className="absolute right-0 mt-2 p-4 bg-white rounded-md shadow-lg z-10 border border-gray-200">
          <div className="flex flex-col space-y-4 sm:flex-row sm:space-y-0 sm:space-x-4">
            <div>
              <label htmlFor="start-date" className="block text-sm font-medium text-gray-700 mb-1">
                Fecha inicial
              </label>
              <input
                type="date"
                id="start-date"
                name="start-date"
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-coffee-500 focus:border-coffee-500 sm:text-sm"
                value={formatDateForInput(startDate)}
                onChange={handleStartDateChange}
                max={formatDateForInput(endDate)}
              />
            </div>
            
            <div>
              <label htmlFor="end-date" className="block text-sm font-medium text-gray-700 mb-1">
                Fecha final
              </label>
              <input
                type="date"
                id="end-date"
                name="end-date"
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-coffee-500 focus:border-coffee-500 sm:text-sm"
                value={formatDateForInput(endDate)}
                onChange={handleEndDateChange}
                min={formatDateForInput(startDate)}
              />
            </div>
          </div>
          
          <div className="mt-4 flex justify-end">
            <button
              type="button"
              className="px-4 py-2 bg-coffee-600 text-white rounded-md text-sm font-medium hover:bg-coffee-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-coffee-500"
              onClick={handleToggle}
            >
              Aplicar
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default DateRangePicker;
