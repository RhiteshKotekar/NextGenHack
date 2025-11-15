'use client'

import { useEffect, useState } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

interface DemandData {
  month: string
  demand_index: number
  campaign_flag: number
}

export function DemandChart() {
  const [data, setData] = useState<DemandData[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('http://localhost:5000/api/dashboard/analytics')
      .then(res => res.json())
      .then(result => {
        if (result.success && result.data.seasonal_demand) {
          setData(result.data.seasonal_demand)
        }
        setLoading(false)
      })
      .catch(err => {
        console.error('Error fetching demand data:', err)
        setLoading(false)
      })
  }, [])

  if (loading) {
    return <div className="flex items-center justify-center h-[300px] text-muted-foreground">Loading demand data...</div>
  }

  if (!data.length) {
    return <div className="flex items-center justify-center h-[300px] text-muted-foreground">No demand data available</div>
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
        <XAxis dataKey="month" stroke="var(--muted-foreground)" fontSize={12} />
        <YAxis stroke="var(--muted-foreground)" fontSize={12} />
        <Tooltip
          contentStyle={{
            backgroundColor: 'var(--card)',
            border: `1px solid var(--border)`,
            borderRadius: '0.5rem',
          }}
        />
        <Legend />
        <Line
          type="monotone"
          dataKey="demand_index"
          name="Demand Index"
          stroke="var(--primary)"
          strokeWidth={2}
          dot={{ fill: 'var(--primary)', r: 4 }}
        />
        <Line
          type="monotone"
          dataKey="campaign_flag"
          name="Active Campaigns"
          stroke="var(--chart-3)"
          strokeWidth={2}
          dot={{ fill: 'var(--chart-3)', r: 3 }}
        />
      </LineChart>
    </ResponsiveContainer>
  )
}
