'use client'

import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

const data = [
  { delay: 2, cost: 1200, size: 400 },
  { delay: 5, cost: 1900, size: 300 },
  { delay: 1, cost: 980, size: 200 },
  { delay: 8, cost: 2500, size: 500 },
  { delay: 3, cost: 1500, size: 350 },
  { delay: 6, cost: 2200, size: 450 },
]

export function TransportationOptimization() {
  return (
    <ResponsiveContainer width="100%" height={350}>
      <ScatterChart margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
        <XAxis dataKey="delay" name="Delay (days)" stroke="var(--muted-foreground)" />
        <YAxis dataKey="cost" name="Cost ($)" stroke="var(--muted-foreground)" />
        <Tooltip
          contentStyle={{
            backgroundColor: 'var(--card)',
            border: `1px solid var(--border)`,
            borderRadius: '0.5rem',
          }}
          cursor={{ strokeDasharray: '3 3' }}
        />
        <Scatter name="Routes" data={data} fill="var(--chart-2)" />
      </ScatterChart>
    </ResponsiveContainer>
  )
}
