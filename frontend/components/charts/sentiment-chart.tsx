'use client'

import { useEffect, useState } from 'react'
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts'

interface SentimentData {
  sentiment: string
  count: number
  [key: string]: any
}

const COLORS = {
  'Positive': '#4CAF50',
  'Neutral': '#FFD700',
  'Negative': '#FF4444'
}

export function SentimentChart() {
  const [data, setData] = useState<SentimentData[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('http://localhost:5000/api/dashboard/analytics')
      .then(res => res.json())
      .then(result => {
        if (result.success && result.data.sentiment_distribution) {
          setData(result.data.sentiment_distribution)
        }
        setLoading(false)
      })
      .catch(err => {
        console.error('Error fetching sentiment data:', err)
        setLoading(false)
      })
  }, [])

  if (loading) {
    return <div className="flex items-center justify-center h-[300px] text-muted-foreground">Loading sentiment data...</div>
  }

  if (!data.length) {
    return <div className="flex items-center justify-center h-[300px] text-muted-foreground">No sentiment data available</div>
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          labelLine={false}
          label={(props: any) => {
            const { sentiment, percent } = props
            return `${sentiment}: ${((percent || 0) * 100).toFixed(1)}%`
          }}
          outerRadius={100}
          fill="#8884d8"
          dataKey="count"
        >
          {data.map((entry, index) => (
            <Cell 
              key={`cell-${index}`} 
              fill={COLORS[entry.sentiment as keyof typeof COLORS] || '#8884d8'} 
            />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{
            backgroundColor: 'var(--card)',
            border: `2px solid var(--border)`,
            borderRadius: '0.875rem',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)',
          }}
          formatter={(value: number, name: string) => [`${value} reviews`, name]}
        />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  )
}
