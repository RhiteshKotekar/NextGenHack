'use client'

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

const data = [
  { month: 'Jan', actual: 4000, predicted: 4000 },
  { month: 'Feb', actual: 4500, predicted: 4300 },
  { month: 'Mar', actual: 5200, predicted: 5100 },
  { month: 'Apr', actual: 5800, predicted: 5900 },
  { month: 'May', actual: 6100, predicted: 6200 },
  { month: 'Jun', actual: 6500, predicted: 6800 },
]

export function AdvancedDemandChart() {
  return (
    <ResponsiveContainer width="100%" height={350}>
      <LineChart data={data} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
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
        <Legend />
        <Line
          type="monotone"
          dataKey="actual"
          stroke="var(--chart-1)"
          strokeWidth={2}
          dot={{ fill: 'var(--chart-1)', r: 4 }}
          name="Actual Demand"
        />
        <Line
          type="monotone"
          dataKey="predicted"
          stroke="var(--chart-2)"
          strokeWidth={2}
          strokeDasharray="5 5"
          dot={{ fill: 'var(--chart-2)', r: 4 }}
          name="Predicted Demand"
        />
      </LineChart>
    </ResponsiveContainer>
  )
}
