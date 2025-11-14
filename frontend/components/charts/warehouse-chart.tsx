'use client'

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

const data = [
  { warehouse: 'North', efficiency: 85 },
  { warehouse: 'South', efficiency: 78 },
  { warehouse: 'East', efficiency: 92 },
  { warehouse: 'West', efficiency: 80 },
]

export function WarehouseChart() {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data} margin={{ top: 20, right: 20, bottom: 20, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
        <XAxis dataKey="warehouse" stroke="var(--muted-foreground)" />
        <YAxis stroke="var(--muted-foreground)" domain={[0, 100]} />
        <Tooltip
          contentStyle={{
            backgroundColor: 'var(--card)',
            border: `2px solid var(--border)`,
            borderRadius: '0.875rem',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)',
          }}
        />
        <Bar dataKey="efficiency" fill="var(--chart-2)" radius={[8, 8, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}
