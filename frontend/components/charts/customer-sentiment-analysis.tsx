'use client'

import { AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ComposedChart } from 'recharts'

const data = [
  { week: 'W1', positive: 65, neutral: 20, negative: 15 },
  { week: 'W2', positive: 72, neutral: 18, negative: 10 },
  { week: 'W3', positive: 78, neutral: 15, negative: 7 },
  { week: 'W4', positive: 85, neutral: 10, negative: 5 },
]

export function CustomerSentimentAnalysis() {
  return (
    <ResponsiveContainer width="100%" height={350}>
      <ComposedChart data={data} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
        <XAxis dataKey="week" stroke="var(--muted-foreground)" />
        <YAxis stroke="var(--muted-foreground)" />
        <Tooltip
          contentStyle={{
            backgroundColor: 'var(--card)',
            border: `1px solid var(--border)`,
            borderRadius: '0.5rem',
          }}
        />
        <Bar dataKey="positive" fill="var(--chart-3)" name="Positive" />
        <Bar dataKey="neutral" fill="var(--chart-4)" name="Neutral" />
        <Bar dataKey="negative" fill="var(--destructive)" name="Negative" />
      </ComposedChart>
    </ResponsiveContainer>
  )
}
