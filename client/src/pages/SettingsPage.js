import React from 'react';

const SettingsPage = () => {
  return (
    <div className="py-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Configuración</h1>
        <p className="text-sm text-gray-500">Gestionar configuración del dashboard y conexiones</p>
      </div>
      
      <div className="card mb-6">
        <h2 className="text-xl font-semibold mb-4">Conexión a Google Sheets</h2>
        <div className="mb-4">
          <label className="label" htmlFor="spreadsheet-id">
            ID de Spreadsheet
          </label>
          <input 
            id="spreadsheet-id"
            type="text" 
            className="input w-full" 
            placeholder="Ingrese el ID de la hoja de Google Sheets"
          />
        </div>
        
        <div className="bg-green-50 border border-green-200 rounded-md p-4 mb-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-green-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-green-700">
                Conectado a Google Sheets correctamente.
              </p>
            </div>
          </div>
        </div>
        
        <button className="btn btn-primary">
          Probar Conexión
        </button>
      </div>
      
      <div className="card mb-6">
        <h2 className="text-xl font-semibold mb-4">Preferencias del Dashboard</h2>
        
        <div className="mb-4">
          <label className="label">Zona Horaria</label>
          <select className="input w-full">
            <option>America/Lima</option>
            <option>America/Bogota</option>
            <option>America/Santiago</option>
            <option>America/Buenos_Aires</option>
          </select>
        </div>
        
        <div className="mb-4">
          <label className="label">Moneda</label>
          <select className="input w-full">
            <option>S/. (Sol Peruano)</option>
            <option>$ (Dólar Estadounidense)</option>
            <option>€ (Euro)</option>
          </select>
        </div>
        
        <button className="btn btn-primary">
          Guardar Preferencias
        </button>
      </div>
    </div>
  );
};

export default SettingsPage;
