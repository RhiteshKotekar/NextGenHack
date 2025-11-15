'use client'

import { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

interface DeliveryPerformanceData {
  city: string
  avg_delivery_days: number
  delay_rate: number
  total_orders: number
}

export function DeliveryPerformanceChart() {
  const [data, setData] = useState<DeliveryPerformanceData[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('http://localhost:5000/api/dashboard/analytics')
      .then(res => res.json())
      .then(result => {
        if (result.success && result.data.delivery_performance) {
          // Get top 15 cities with highest delay rates
          setData(result.data.delivery_performance.slice(0, 15))
        }
        setLoading(false)
      })
      .catch(err => {
        console.error('Error fetching delivery performance data:', err)
        setLoading(false)
      })
  }, [])

  if (loading) {
    return <div className="flex items-center justify-center h-[300px] text-muted-foreground">Loading delivery data...</div>
  }

  if (!data.length) {
    return <div className="flex items-center justify-center h-[300px] text-muted-foreground">No delivery data available</div>
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data} margin={{ top: 20, right: 40, bottom: 60, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
        <XAxis 
          dataKey="city" 
          stroke="var(--muted-foreground)" 
          fontSize={10}
          angle={-45}
          textAnchor="end"
          height={80}
        />
        {/* Left Y-axis for Delay Rate (%) */}
        <YAxis 
          yAxisId="left"
          stroke="var(--muted-foreground)" 
          fontSize={12}
          tickFormatter={(value) => `${value}%`}
          label={{ value: 'Delay Rate (%)', angle: -90, position: 'insideLeft', style: { fill: 'var(--muted-foreground)' } }}
        />
        {/* Right Y-axis for Avg Days */}
        <YAxis 
          yAxisId="right"
          orientation="right"
          stroke="var(--muted-foreground)" 
          fontSize={12}
          tickFormatter={(value) => `${value}d`}
          label={{ value: 'Avg Days', angle: 90, position: 'insideRight', style: { fill: 'var(--muted-foreground)' } }}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: 'var(--card)',
            border: `2px solid var(--border)`,
            borderRadius: '0.875rem',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)',
          }}
          formatter={(value: number, name: string) => {
            if (name === 'delay_rate') return [`${value.toFixed(1)}%`, 'Delay Rate']
            if (name === 'avg_delivery_days') return [`${value.toFixed(1)} days`, 'Avg Delivery Time']
            return [value, name]
          }}
        />
        <Legend />
        <Bar yAxisId="left" dataKey="delay_rate" name="Delay Rate (%)" fill="#FF4444" radius={[8, 8, 0, 0]} />
        <Bar yAxisId="right" dataKey="avg_delivery_days" name="Avg Days" fill="var(--chart-4)" radius={[8, 8, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}
