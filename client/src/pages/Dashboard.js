import React, { useState, useEffect } from 'react';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import { Link } from 'react-router-dom';
import { 
  CubeIcon, 
  BanknotesIcon, 
  ArrowTrendingUpIcon, 
  ScaleIcon,
  ShoppingCartIcon,
  ClockIcon,
  CalculatorIcon,
  ArrowTopRightOnSquareIcon
} from '@heroicons/react/24/outline';

import StatCard from '../components/StatCard';
import AreaChart from '../components/AreaChart';
import DonutChart from '../components/DonutChart';
import apiService from '../services/apiService';

const Dashboard = () => {
  // Estados para almacenar datos
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState(null);
  const [dailyData, setDailyData] = useState([]);
  const [coffeeTypes, setCoffeeTypes] = useState([]);
  
  // Calcular fecha de inicio (7 días atrás) y fin (hoy)
  const endDate = new Date();
  const startDate = new Date();
  startDate.setDate(endDate.getDate() - 7);
  
  // Cargar datos cuando el componente se monta
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Obtener el resumen general
        const summaryData = await apiService.getSummary(startDate, endDate);
        setSummary(summaryData);
        
        // Obtener datos diarios para gráficos
        const dailyData = await apiService.getDailyData(startDate, endDate);
        setDailyData(dailyData);
        
        // Obtener tipos de café
        const coffeeTypesData = await apiService.getCoffeeTypes();
        
        // Convertir a formato para gráfico de donut
        const coffeeTypesArray = Object.entries(coffeeTypesData).map(([name, data]) => ({
          name,
          value: data.kg_total
        }));
        
        setCoffeeTypes(coffeeTypesArray);
        
        setLoading(false);
      } catch (error) {
        console.error('Error al cargar datos del dashboard:', error);
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);
  
  // Preparar datos para el gráfico de métodos de pago
  const preparePaymentMethodsData = () => {
    if (!summary) return [];
    
    const { metodos_pago } = summary;
    return [
      { name: 'Efectivo', value: metodos_pago.efectivo },
      { name: 'Transferencia', value: metodos_pago.transferencia },
      { name: 'Otro', value: metodos_pago.otro }
    ];
  };
  
  // Preparar datos para el gráfico de compras
  const prepareComprasData = () => {
    if (!summary || !summary.compras) return [];
    
    return [
      { name: 'Compras Regulares', value: summary.compras.sin_adelantos },
      { name: 'Compras con Adelantos', value: summary.compras.con_adelantos }
    ];
  };
  
  // Formatear valores para mostrar en componentes
  const formatCurrency = (value) => {
    return `S/. ${parseFloat(value).toFixed(2)}`;
  };
  
  const formatKg = (value) => {
    return `${parseFloat(value).toFixed(1)} kg`;
  };
  
  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return format(date, 'dd MMM', { locale: es });
  };
  
  return (
    <div className="py-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-sm text-gray-500">Resumen de operaciones del negocio de café</p>
      </div>
      
      {/* Tarjetas de estadísticas */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        <StatCard 
          title="Café en Stock"
          value={summary ? formatKg(summary.inventario.kg_disponibles) : "0 kg"}
          icon={CubeIcon}
          loading={loading}
        />
        
        <StatCard 
          title="Ingresos Periodo"
          value={summary ? formatCurrency(summary.financiero.ingresos) : "S/. 0.00"}
          icon={BanknotesIcon}
          loading={loading}
        />
        
        <StatCard 
          title="Gastos Periodo"
          value={summary ? formatCurrency(summary.financiero.gastos) : "S/. 0.00"}
          icon={ScaleIcon}
          loading={loading}
        />
        
        <StatCard 
          title="Ganancia Contable"
          value={summary ? formatCurrency(summary.financiero.ganancia) : "S/. 0.00"}
          icon={ArrowTrendingUpIcon}
          change={summary && summary.financiero.ingresos > 0 ? `${((summary.financiero.ganancia / summary.financiero.ingresos) * 100).toFixed(1)}%` : "0%"}
          changeType={summary && summary.financiero.ganancia > 0 ? 'up' : 'down'}
          loading={loading}
        />
      </div>

      {/* Tarjeta para ganancia real */}
      <div className="mb-6">
        <Link to="/process-profit" className="block">
          <div className="relative">
            <StatCard 
              title="Ganancia Real (Por Proceso)"
              value={summary && summary.financiero.ganancia_real ? formatCurrency(summary.financiero.ganancia_real) : "S/. 0.00"}
              icon={CalculatorIcon}
              loading={loading}
              description="Calculada en base al proceso de transformación del café"
            />
            <div className="absolute top-3 right-3 text-coffee-600 hover:text-coffee-800">
              <ArrowTopRightOnSquareIcon className="h-5 w-5" />
            </div>
          </div>
        </Link>
      </div>

      {/* Tarjetas para montos de compras */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <StatCard 
          title="Compras sin Adelantos"
          value={summary && summary.compras ? formatCurrency(summary.compras.sin_adelantos) : "S/. 0.00"}
          icon={ShoppingCartIcon}
          loading={loading}
        />
        
        <StatCard 
          title="Compras con Adelantos"
          value={summary && summary.compras ? formatCurrency(summary.compras.con_adelantos) : "S/. 0.00"}
          icon={ClockIcon}
          loading={loading}
        />
      </div>
      
      {/* Gráficos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <AreaChart 
          title="Tendencia de Ingresos Diarios"
          data={dailyData}
          dataKey="financiero.ingresos"
          fill="#C6A16C"
          stroke="#96732D"
          labelFormatter={formatDate}
          valueFormatter={formatCurrency}
          loading={loading}
        />
        
        <AreaChart 
          title="Inventario de Café (kg)"
          data={dailyData}
          dataKey="inventario.kg_comprados"
          fill="#A3E4D7"
          stroke="#1ABC9C"
          labelFormatter={formatDate}
          valueFormatter={formatKg}
          loading={loading}
        />
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <DonutChart 
          title="Distribución por Tipo de Café"
          data={coffeeTypes}
          colors={['#B58540', '#7D4E1A', '#613C11', '#96732D', '#C6A16C']}
          loading={loading}
        />
        
        <DonutChart 
          title="Métodos de Pago"
          data={preparePaymentMethodsData()}
          colors={['#5DA5DA', '#4D4D4D', '#F15854']}
          loading={loading}
        />

        <DonutChart 
          title="Compras por Tipo"
          data={prepareComprasData()}
          colors={['#82CD47', '#F7C04A']}
          loading={loading}
        />
      </div>
    </div>
  );
};

export default Dashboard;
