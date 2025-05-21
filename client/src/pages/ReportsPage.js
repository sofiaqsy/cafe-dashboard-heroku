import React from 'react';

const ReportsPage = () => {
  return (
    <div className="py-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Reportes</h1>
        <p className="text-sm text-gray-500">Generación y descarga de reportes personalizados</p>
      </div>
      
      <div className="card mb-6">
        <h2 className="text-xl font-semibold mb-4">Generador de Reportes</h2>
        <p>Esta sección permitirá generar reportes personalizados según diversos parámetros.</p>
        
        <div className="mt-4">
          <button className="btn btn-primary mr-2">
            Generar Reporte
          </button>
          <button className="btn btn-secondary">
            Exportar a Excel
          </button>
        </div>
      </div>
      
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Reportes Guardados</h2>
        <p>Aquí se mostrarán los reportes generados anteriormente para su rápido acceso.</p>
        
        <div className="mt-4">
          <div className="border-t border-gray-200 pt-4">
            <p className="text-sm text-gray-500">Aún no hay reportes guardados.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReportsPage;
