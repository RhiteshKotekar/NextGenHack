'use client'

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

const data = [
  { month: 'Jan', demand: 4000 },
  { month: 'Feb', demand: 4500 },
  { month: 'Mar', demand: 5200 },
  { month: 'Apr', demand: 5800 },
  { month: 'May', demand: 6100 },
  { month: 'Jun', demand: 6500 },
]

export function DemandChart() {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
        <XAxis dataKey="month" stroke="var(--muted-foreground)" />
        <YAxis stroke="var(--muted-foreground)" />
        <Tooltip
          contentStyle={{
            backgroundColor: 'var(--card)',
            border: `1px solid var(--border)`,
            borderRadius: '0.5rem',
          }}
        />
        <Line
          type="monotone"
          dataKey="demand"
          stroke="var(--primary)"
          strokeWidth={2}
          dot={{ fill: 'var(--primary)', r: 4 }}
        />
      </LineChart>
    </ResponsiveContainer>
  )
}
