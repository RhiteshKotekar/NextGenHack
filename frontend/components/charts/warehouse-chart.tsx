'use client'

import { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

interface WarehouseData {
  warehouse_id: string
  avg_processing_time_hours: number
  storage_cost_per_pallet_inr: number
  workforce_available: number
  efficiency_score: number
}

export function WarehouseChart() {
  const [data, setData] = useState<WarehouseData[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('http://localhost:5000/api/dashboard/analytics')
      .then(res => res.json())
      .then(result => {
        if (result.success && result.data.warehouse_efficiency) {
          // Get top 15 warehouses by efficiency
          const sortedData = result.data.warehouse_efficiency
            .sort((a: WarehouseData, b: WarehouseData) => b.efficiency_score - a.efficiency_score)
            .slice(0, 15)
          setData(sortedData)
        }
        setLoading(false)
      })
      .catch(err => {
        console.error('Error fetching warehouse data:', err)
        setLoading(false)
      })
  }, [])

  if (loading) {
    return <div className="flex items-center justify-center h-[300px] text-muted-foreground">Loading warehouse data...</div>
  }

  if (!data.length) {
    return <div className="flex items-center justify-center h-[300px] text-muted-foreground">No warehouse data available</div>
  }

  // Calculate dynamic Y-axis range for better visibility
  const efficiencyScores = data.map(d => d.efficiency_score)
  const minScore = Math.min(...efficiencyScores)
  const maxScore = Math.max(...efficiencyScores)
  const padding = (maxScore - minScore) * 0.2 || 5 // Add 20% padding or minimum 5 units
  const yMin = Math.max(0, Math.floor(minScore - padding))
  const yMax = Math.min(100, Math.ceil(maxScore + padding))

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data} margin={{ top: 20, right: 20, bottom: 20, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
        <XAxis dataKey="warehouse_id" stroke="var(--muted-foreground)" fontSize={11} />
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
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)',
          }}
          formatter={(value: number, name: string) => {
            if (name === 'efficiency_score') return [`${value.toFixed(2)}%`, 'Efficiency']
            if (name === 'avg_processing_time_hours') return [`${value.toFixed(1)}h`, 'Processing Time']
            return [value, name]
          }}
        />
        <Legend />
        <Bar dataKey="efficiency_score" name="Efficiency Score" fill="var(--chart-2)" radius={[8, 8, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}
