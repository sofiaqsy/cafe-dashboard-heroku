import React from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const AreaChartComponent = ({ 
  data, 
  title, 
  dataKey, 
  fill = '#B58540', 
  stroke = '#7D4E1A',
  labelFormatter,
  valueFormatter,
  xAxisDataKey = 'fecha',
  loading = false
}) => {
  // Datos para el estado de carga
  const loadingData = Array(7).fill().map((_, i) => ({ 
    fecha: `Día ${i+1}`, 
    [dataKey]: Math.floor(Math.random() * 50) 
  }));

  return (
    <div className="card">
      <h3 className="text-sm font-medium text-gray-500 mb-4">{title}</h3>
      
      <div className="h-64">
        {loading ? (
          <div className="loading w-full h-full bg-gray-100 rounded animate-pulse"></div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart
              data={data || loadingData}
              margin={{ top: 10, right: 0, left: 0, bottom: 0 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey={xAxisDataKey} 
                tick={{ fontSize: 12 }} 
                tickFormatter={labelFormatter} 
              />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip 
                labelFormatter={labelFormatter} 
                formatter={(value, name) => [
                  valueFormatter ? valueFormatter(value) : value,
                  title
                ]}
              />
              <Area 
                type="monotone" 
                dataKey={dataKey} 
                stroke={stroke} 
                fill={fill} 
                fillOpacity={0.3}
              />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
};

export default AreaChartComponent;
