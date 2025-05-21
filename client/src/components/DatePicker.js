import React, { useState } from 'react';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import { CalendarIcon } from '@heroicons/react/24/outline';

const DatePicker = ({ startDate, endDate, onChange }) => {
  const [isOpen, setIsOpen] = useState(false);

  const formatDateRange = () => {
    const formattedStart = format(startDate, 'dd MMM', { locale: es });
    const formattedEnd = format(endDate, 'dd MMM yyyy', { locale: es });
    return `${formattedStart} - ${formattedEnd}`;
  };

  // Opciones predefinidas de rangos de fechas
  const dateOptions = [
    { label: 'Hoy', days: 0 },
    { label: 'Ayer', days: 1 },
    { label: 'Últimos 7 días', days: 7 },
    { label: 'Últimos 30 días', days: 30 },
    { label: 'Este mes', type: 'month' },
    { label: 'Personalizado', type: 'custom' }
  ];

  const handleOptionSelect = (option) => {
    const today = new Date();
    let start = new Date();
    let end = new Date();

    if (option.type === 'month') {
      // Primer día del mes actual
      start = new Date(today.getFullYear(), today.getMonth(), 1);
    } else if (option.type === 'custom') {
      // Abrir selector personalizado (se implementaría con una librería como react-datepicker)
      // Por ahora, simplemente cerramos el dropdown
      setIsOpen(false);
      return;
    } else {
      // Restar días según la opción seleccionada
      start = new Date(today);
      start.setDate(today.getDate() - option.days);
    }

    onChange({ start, end });
    setIsOpen(false);
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center px-3 py-2 text-sm border rounded-md bg-white focus:outline-none focus:ring-2 focus:ring-coffee-500"
      >
        <CalendarIcon className="h-5 w-5 mr-1 text-gray-500" />
        <span>{formatDateRange()}</span>
      </button>

      {isOpen && (
        <div className="absolute mt-1 w-56 bg-white shadow-lg rounded-md z-10 border">
          <ul className="py-1">
            {dateOptions.map((option) => (
              <li 
                key={option.label}
                onClick={() => handleOptionSelect(option)}
                className="px-4 py-2 hover:bg-coffee-50 cursor-pointer text-sm"
              >
                {option.label}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default DatePicker;
