'use client'

import { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

interface CourierData {
  courier_partner: string
  on_time_rate_pct: number
  distance_km: number
  fuel_cost_per_km_inr: number
}

export function TransportationChart() {
  const [data, setData] = useState<CourierData[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('http://localhost:5000/api/dashboard/analytics')
      .then(res => res.json())
      .then(result => {
        if (result.success && result.data.courier_performance) {
          setData(result.data.courier_performance.sort(
            (a: CourierData, b: CourierData) => b.on_time_rate_pct - a.on_time_rate_pct
          ))
        }
        setLoading(false)
      })
      .catch(err => {
        console.error('Error fetching courier data:', err)
        setLoading(false)
      })
  }, [])

  if (loading) {
    return <div className="flex items-center justify-center h-[300px] text-muted-foreground">Loading transportation data...</div>
  }

  if (!data.length) {
    return <div className="flex items-center justify-center h-[300px] text-muted-foreground">No transportation data available</div>
  }

  // Calculate dynamic Y-axis range for better visibility
  const onTimeRates = data.map(d => d.on_time_rate_pct)
  const minRate = Math.min(...onTimeRates)
  const maxRate = Math.max(...onTimeRates)
  const padding = (maxRate - minRate) * 0.2 || 5 // Add 20% padding or minimum 5 units
  const yMin = Math.max(0, Math.floor(minRate - padding))
  const yMax = Math.min(100, Math.ceil(maxRate + padding))

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data} margin={{ top: 20, right: 20, bottom: 20, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
        <XAxis dataKey="courier_partner" stroke="var(--muted-foreground)" fontSize={11} />
        <YAxis 
          stroke="var(--muted-foreground)" 
          domain={[yMin, yMax]} 
          fontSize={12}
          tickFormatter={(value) => `${value.toFixed(0)}%`}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: 'var(--card)',
            border: `2px solid var(--border)`,
            borderRadius: '0.875rem',
            boxShadow: '0 12px 32px rgba(139, 92, 246, 0.4)',
          }}
          formatter={(value: number, name: string) => {
            if (name === 'on_time_rate_pct') return [`${value.toFixed(2)}%`, 'On-Time Rate']
            if (name === 'distance_km') return [`${value.toFixed(1)} km`, 'Avg Distance']
            if (name === 'fuel_cost_per_km_inr') return [`₹${value.toFixed(2)}/km`, 'Fuel Cost']
            return [value, name]
          }}
        />
        <Legend />
        <Bar dataKey="on_time_rate_pct" name="On-Time Rate (%)" fill="var(--chart-1)" radius={[8, 8, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}
