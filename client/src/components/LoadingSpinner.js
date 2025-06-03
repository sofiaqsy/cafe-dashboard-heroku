import React from 'react';

const LoadingSpinner = ({ size = 'md' }) => {
  // Determinar tamaño basado en prop
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-6 w-6',
    lg: 'h-8 w-8',
    xl: 'h-12 w-12'
  };
  
  const spinnerSize = sizeClasses[size] || sizeClasses.md;
  
  return (
    <div className="flex items-center justify-center">
      <div className={`${spinnerSize} animate-spin rounded-full border-2 border-coffee-200 border-t-coffee-600`} role="status">
        <span className="sr-only">Cargando...</span>
      </div>
    </div>
  );
};

export default LoadingSpinner;
