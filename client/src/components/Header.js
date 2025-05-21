import React, { useState } from 'react';
import { BellIcon, CalendarIcon } from '@heroicons/react/24/outline';
import DatePicker from '../components/DatePicker';

const Header = () => {
  const [dateRange, setDateRange] = useState({
    start: new Date(new Date().setDate(new Date().getDate() - 7)),
    end: new Date()
  });

  const handleDateChange = (newDateRange) => {
    setDateRange(newDateRange);
    // Aquí se podría implementar la lógica para actualizar los datos según el rango de fechas
  };

  return (
    <header className="bg-white shadow-sm py-4 px-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <h2 className="text-2xl font-semibold text-gray-800 mr-4">
            Dashboard
          </h2>
          <DatePicker 
            startDate={dateRange.start}
            endDate={dateRange.end}
            onChange={handleDateChange}
          />
        </div>
        
        <div className="flex items-center space-x-4">
          <button className="p-2 rounded-full hover:bg-gray-100 relative">
            <CalendarIcon className="h-6 w-6 text-gray-500" />
          </button>
          
          <button className="p-2 rounded-full hover:bg-gray-100 relative">
            <BellIcon className="h-6 w-6 text-gray-500" />
            <span className="absolute top-0 right-0 h-2 w-2 rounded-full bg-red-500"></span>
          </button>
          
          <div className="flex items-center">
            <span className="mr-2 text-sm font-medium text-gray-700">Admin</span>
            <div className="h-8 w-8 rounded-full bg-coffee-600 text-white flex items-center justify-center">
              A
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
