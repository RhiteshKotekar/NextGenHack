'use client'

import { useEffect, useState } from 'react'
import { ComposedChart, Bar, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

interface RouteCostData {
  city: string
  total_fuel_cost: number
  distance_km: number
  estimated_transit_hours: number
}

export function CostAnalysisChart() {
  const [data, setData] = useState<RouteCostData[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('http://localhost:5000/api/dashboard/analytics')
      .then(res => res.json())
      .then(result => {
        if (result.success && result.data.route_costs) {
          // Get top 15 most expensive routes
          setData(result.data.route_costs.slice(0, 15))
        }
        setLoading(false)
      })
      .catch(err => {
        console.error('Error fetching cost data:', err)
        setLoading(false)
      })
  }, [])

  if (loading) {
    return <div className="flex items-center justify-center h-[300px] text-muted-foreground">Loading cost data...</div>
  }

  if (!data.length) {
    return <div className="flex items-center justify-center h-[300px] text-muted-foreground">No cost data available</div>
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <ComposedChart data={data} margin={{ top: 20, right: 20, bottom: 60, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
        <XAxis 
          dataKey="city" 
          stroke="var(--muted-foreground)" 
          fontSize={10}
          angle={-45}
          textAnchor="end"
          height={80}
        />
        <YAxis 
          yAxisId="left"
          stroke="var(--muted-foreground)" 
          fontSize={12}
          label={{ value: 'Cost (₹)', angle: -90, position: 'insideLeft' }}
        />
        <YAxis 
          yAxisId="right"
          orientation="right"
          stroke="var(--muted-foreground)" 
          fontSize={12}
          label={{ value: 'Distance (km)', angle: 90, position: 'insideRight' }}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: 'var(--card)',
            border: `2px solid var(--border)`,
            borderRadius: '0.875rem',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)',
          }}
          formatter={(value: number, name: string) => {
            if (name === 'total_fuel_cost') return [`₹${value.toFixed(2)}`, 'Avg Fuel Cost']
            if (name === 'distance_km') return [`${value.toFixed(1)} km`, 'Avg Distance']
            if (name === 'estimated_transit_hours') return [`${value.toFixed(1)} hrs`, 'Transit Time']
            return [value, name]
          }}
        />
        <Legend />
        <Bar 
          yAxisId="left"
          dataKey="total_fuel_cost" 
          name="Avg Fuel Cost (₹)" 
          fill="#FF6B6B" 
          radius={[8, 8, 0, 0]} 
        />
        <Line 
          yAxisId="right"
          type="monotone" 
          dataKey="distance_km" 
          name="Avg Distance (km)" 
          stroke="var(--chart-5)" 
          strokeWidth={2}
          dot={{ fill: 'var(--chart-5)', r: 4 }}
        />
      </ComposedChart>
    </ResponsiveContainer>
  )
}
