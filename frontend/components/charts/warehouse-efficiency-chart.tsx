'use client'

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

const data = [
  { region: 'Northeast', efficiency: 92, capacity: 95 },
  { region: 'Southeast', efficiency: 85, capacity: 88 },
  { region: 'Midwest', efficiency: 88, capacity: 90 },
  { region: 'Southwest', efficiency: 80, capacity: 92 },
  { region: 'West', efficiency: 90, capacity: 93 },
]

export function WarehouseEfficiencyChart() {
  return (
    <ResponsiveContainer width="100%" height={350}>
      <BarChart data={data} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
        <XAxis dataKey="region" stroke="var(--muted-foreground)" />
        <YAxis stroke="var(--muted-foreground)" />
        <Tooltip
          contentStyle={{
            backgroundColor: 'var(--card)',
            border: `1px solid var(--border)`,
            borderRadius: '0.5rem',
          }}
        />
        <Legend />
        <Bar dataKey="efficiency" fill="var(--chart-1)" radius={[8, 8, 0, 0]} name="Efficiency %" />
        <Bar dataKey="capacity" fill="var(--chart-4)" radius={[8, 8, 0, 0]} name="Capacity %" />
      </BarChart>
    </ResponsiveContainer>
  )
}
