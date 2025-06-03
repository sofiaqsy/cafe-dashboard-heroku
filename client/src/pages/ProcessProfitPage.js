import React, { useState, useEffect } from 'react';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import { 
  ArrowTrendingUpIcon, 
  CalendarIcon,
  CurrencyDollarIcon,
  ReceiptPercentIcon,
  ArrowTopRightOnSquareIcon,
  ArrowsRightLeftIcon,
} from '@heroicons/react/24/outline';

import DateRangePicker from '../components/DateRangePicker';
import StatCard from '../components/StatCard';
import apiService from '../services/apiService';
import LoadingSpinner from '../components/LoadingSpinner';

const ProcessProfitPage = () => {
  const [loading, setLoading] = useState(true);
  const [processData, setProcessData] = useState(null);
  const [startDate, setStartDate] = useState(() => {
    const date = new Date();
    date.setMonth(date.getMonth() - 1);
    return date;
  });
  const [endDate, setEndDate] = useState(new Date());
  
  // Cargar datos de ganancias por proceso
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        const data = await apiService.getProcessProfit(startDate, endDate);
        setProcessData(data);
        
        setLoading(false);
      } catch (error) {
        console.error('Error al cargar datos de ganancias por proceso:', error);
        setLoading(false);
      }
    };
    
    fetchData();
  }, [startDate, endDate]);
  
  // Función para formatear fecha
  const formatDate = (dateStr) => {
    if (!dateStr) return 'Fecha desconocida';
    const date = new Date(dateStr);
    return format(date, 'dd MMM yyyy', { locale: es });
  };
  
  // Función para formatear moneda
  const formatCurrency = (value) => {
    return `S/. ${parseFloat(value).toFixed(2)}`;
  };
  
  // Función para formatear peso
  const formatWeight = (value) => {
    return `${parseFloat(value).toFixed(1)} kg`;
  };
  
  // Manejar cambio de rango de fechas
  const handleDateRangeChange = (start, end) => {
    setStartDate(start);
    setEndDate(end);
  };
  
  return (
    <div className="py-6">
      <div className="mb-6 flex flex-col md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Ganancia por Proceso</h1>
          <p className="text-sm text-gray-500">Análisis detallado de la ganancia real por cada proceso de café</p>
        </div>
        
        <div className="mt-4 md:mt-0">
          <DateRangePicker 
            startDate={startDate}
            endDate={endDate}
            onChange={handleDateRangeChange}
          />
        </div>
      </div>
      
      {/* Cards con el resumen */}
      {loading ? (
        <div className="flex justify-center py-12">
          <LoadingSpinner size="lg" />
        </div>
      ) : (
        <>
          {processData && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
              <StatCard
                title="Total Procesos"
                value={processData.resumen.total_procesos}
                icon={ArrowsRightLeftIcon}
                loading={loading}
              />
              
              <StatCard
                title="Costo de Compras"
                value={formatCurrency(processData.resumen.total_costo)}
                icon={CurrencyDollarIcon}
                loading={loading}
              />
              
              <StatCard
                title="Ingresos por Ventas"
                value={formatCurrency(processData.resumen.total_ingresos)}
                icon={ReceiptPercentIcon}
                loading={loading}
              />
              
              <StatCard
                title="Ganancia Real"
                value={formatCurrency(processData.resumen.total_ganancia)}
                icon={ArrowTrendingUpIcon}
                change={processData.resumen.total_ingresos > 0 
                  ? `${((processData.resumen.total_ganancia / processData.resumen.total_ingresos) * 100).toFixed(1)}%` 
                  : "0%"}
                changeType={processData.resumen.total_ganancia > 0 ? 'up' : 'down'}
                loading={loading}
              />
            </div>
          )}
          
          {/* Tabla de detalle de procesos */}
          <div className="card overflow-hidden">
            <h2 className="text-xl font-semibold mb-4">Detalle por Proceso</h2>
            
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Proceso
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Fecha
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Tipo de Café
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Cantidad
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Costo
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Ingresos
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Ganancia
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      % Ganancia
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {processData && processData.procesos.map((proceso, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{proceso.proceso_id}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-500">{formatDate(proceso.fecha_proceso)}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-500">{proceso.tipo_cafe}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-500">{formatWeight(proceso.cantidad_entrada)}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-500">{formatCurrency(proceso.costo_compra)}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-500">{formatCurrency(proceso.ingresos_ventas)}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className={`text-sm font-medium ${proceso.ganancia >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {formatCurrency(proceso.ganancia)}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className={`text-sm font-medium ${proceso.ganancia >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {proceso.ingresos_ventas > 0 
                            ? `${((proceso.ganancia / proceso.ingresos_ventas) * 100).toFixed(1)}%` 
                            : "-"}
                        </div>
                      </td>
                    </tr>
                  ))}
                  
                  {(!processData || processData.procesos.length === 0) && (
                    <tr>
                      <td colSpan="8" className="px-6 py-4 text-center text-sm text-gray-500">
                        No se encontraron datos para el período seleccionado
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
          
          {/* Sección para mostrar el detalle de ventas por proceso */}
          {processData && processData.procesos.length > 0 && (
            <div className="mt-8 grid grid-cols-1 gap-6">
              {processData.procesos.map((proceso, index) => (
                <div key={`detail-${index}`} className="card">
                  <h3 className="text-lg font-semibold mb-3">
                    Detalle del Proceso: {proceso.proceso_id}
                  </h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-4">
                    <div>
                      <h4 className="text-md font-medium mb-2">Información de Compra</h4>
                      {proceso.detalles.compra ? (
                        <div className="bg-gray-50 p-4 rounded-lg">
                          <p className="text-sm mb-1"><span className="font-medium">Fecha:</span> {formatDate(proceso.detalles.compra.fecha)}</p>
                          <p className="text-sm mb-1"><span className="font-medium">Tipo de café:</span> {proceso.detalles.compra.tipo_cafe}</p>
                          <p className="text-sm mb-1"><span className="font-medium">Cantidad:</span> {formatWeight(proceso.detalles.compra.cantidad)}</p>
                          <p className="text-sm mb-1"><span className="font-medium">Precio/kg:</span> {formatCurrency(proceso.detalles.compra.precio_kg)}</p>
                          <p className="text-sm mb-1"><span className="font-medium">Total compra:</span> {formatCurrency(proceso.detalles.compra.total)}</p>
                        </div>
                      ) : (
                        <p className="text-sm text-gray-500">No hay información disponible</p>
                      )}
                    </div>
                    
                    <div>
                      <h4 className="text-md font-medium mb-2">Información de Almacén</h4>
                      {proceso.detalles.almacen && proceso.detalles.almacen.length > 0 ? (
                        <div className="bg-gray-50 p-4 rounded-lg">
                          {proceso.detalles.almacen.map((item, idx) => (
                            <div key={`almacen-${idx}`} className={idx > 0 ? 'mt-3 pt-3 border-t border-gray-200' : ''}>
                              <p className="text-sm mb-1"><span className="font-medium">ID Almacén:</span> {item.almacen_id}</p>
                              <p className="text-sm mb-1"><span className="font-medium">Fecha:</span> {formatDate(item.fecha)}</p>
                              <p className="text-sm mb-1"><span className="font-medium">Tipo de café:</span> {item.tipo_cafe}</p>
                              <p className="text-sm mb-1"><span className="font-medium">Cantidad:</span> {formatWeight(item.cantidad)}</p>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-sm text-gray-500">No hay información disponible</p>
                      )}
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="text-md font-medium mb-2">Ventas Relacionadas</h4>
                    {proceso.ventas && proceso.ventas.length > 0 ? (
                      <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                          <thead className="bg-gray-50">
                            <tr>
                              <th scope="col" className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Fecha
                              </th>
                              <th scope="col" className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Cliente
                              </th>
                              <th scope="col" className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Tipo de Café
                              </th>
                              <th scope="col" className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Cantidad
                              </th>
                              <th scope="col" className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Precio/kg
                              </th>
                              <th scope="col" className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Total
                              </th>
                            </tr>
                          </thead>
                          <tbody className="bg-white divide-y divide-gray-200">
                            {proceso.ventas.map((venta, vidx) => (
                              <tr key={`venta-${vidx}`}>
                                <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-500">
                                  {formatDate(venta.fecha)}
                                </td>
                                <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-500">
                                  {venta.cliente}
                                </td>
                                <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-500">
                                  {venta.tipo_cafe}
                                </td>
                                <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-500">
                                  {formatWeight(venta.cantidad)}
                                </td>
                                <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-500">
                                  {formatCurrency(venta.precio_kg)}
                                </td>
                                <td className="px-4 py-2 whitespace-nowrap text-sm font-medium text-gray-900">
                                  {formatCurrency(venta.total)}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    ) : (
                      <p className="text-sm text-gray-500">No hay ventas registradas</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default ProcessProfitPage;
