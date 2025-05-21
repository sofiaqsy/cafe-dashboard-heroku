import React from 'react';

const InventoryPage = () => {
  return (
    <div className="py-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Inventario</h1>
        <p className="text-sm text-gray-500">Gestión y seguimiento de inventario de café</p>
      </div>
      
      <div className="card mb-6">
        <h2 className="text-xl font-semibold mb-4">Inventario Actual</h2>
        <p>Esta sección mostrará el inventario detallado por tipo de café y fase de procesamiento.</p>
      </div>
      
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Movimientos de Inventario</h2>
        <p>Aquí se mostrarán los movimientos históricos de inventario, incluyendo compras, ventas y procesamiento.</p>
      </div>
    </div>
  );
};

export default InventoryPage;
