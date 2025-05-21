import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

const DonutChart = ({ 
  data, 
  title, 
  colors = ['#B58540', '#7D4E1A', '#613C11'], 
  dataKey = 'value',
  nameKey = 'name',
  loading = false 
}) => {
  // Datos para el estado de carga
  const loadingData = [
    { name: 'Cargando 1', value: 400 },
    { name: 'Cargando 2', value: 300 },
    { name: 'Cargando 3', value: 300 }
  ];

  // Configuración del gráfico
  const renderCustomizedLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent }) => {
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
    const x = cx + radius * Math.cos(-midAngle * Math.PI / 180);
    const y = cy + radius * Math.sin(-midAngle * Math.PI / 180);

    return (
      <text 
        x={x} 
        y={y} 
        fill="white" 
        textAnchor="middle" 
        dominantBaseline="central"
        fontSize={12}
      >
        {`${(percent * 100).toFixed(0)}%`}
      </text>
    );
  };

  return (
    <div className="card">
      <h3 className="text-sm font-medium text-gray-500 mb-4">{title}</h3>
      
      <div className="h-64">
        {loading ? (
          <div className="loading w-full h-full bg-gray-100 rounded animate-pulse"></div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data || loadingData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={renderCustomizedLabel}
                outerRadius={80}
                innerRadius={40}
                fill="#8884d8"
                dataKey={dataKey}
                nameKey={nameKey}
              >
                {(data || loadingData).map((entry, index) => (
                  <Cell 
                    key={`cell-${index}`} 
                    fill={colors[index % colors.length]} 
                  />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
};

export default DonutChart;
