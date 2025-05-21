import React from 'react';

const FinancialPage = () => {
  return (
    <div className="py-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Finanzas</h1>
        <p className="text-sm text-gray-500">Análisis financiero y seguimiento de gastos e ingresos</p>
      </div>
      
      <div className="card mb-6">
        <h2 className="text-xl font-semibold mb-4">Resumen Financiero</h2>
        <p>Esta sección mostrará un resumen financiero detallado del negocio.</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Ingresos</h2>
          <p>Análisis detallado de ingresos por ventas de café.</p>
        </div>
        
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Gastos</h2>
          <p>Análisis detallado de gastos por categoría.</p>
        </div>
      </div>
    </div>
  );
};

export default FinancialPage;
