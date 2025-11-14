'use client'

import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Dot } from 'recharts'

const data = [
  { week: 'W1', sentiment: 65 },
  { week: 'W2', sentiment: 72 },
  { week: 'W3', sentiment: 78 },
  { week: 'W4', sentiment: 85 },
]

// Function to get color based on sentiment value (red to green gradient)
const getSentimentColor = (value: number) => {
  if (value < 40) return '#FF4444'; // Red
  if (value < 60) return '#FFA500'; // Orange
  if (value < 75) return '#FFD700'; // Yellow
  return '#4CAF50'; // Green
}

// Custom dot component that colors based on sentiment
const CustomDot = (props: any) => {
  const { cx, cy, payload } = props;
  const color = getSentimentColor(payload.sentiment);
  return (
    <circle cx={cx} cy={cy} r={6} fill={color} stroke="white" strokeWidth={2} opacity={1} />
  );
}

export function SentimentChart() {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <AreaChart data={data}>
        <defs>
          <linearGradient id="colorSentiment" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#4CAF50" stopOpacity={0.8} />
            <stop offset="50%" stopColor="#FFD700" stopOpacity={0.4} />
            <stop offset="95%" stopColor="#FF4444" stopOpacity={0.1} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
        <XAxis dataKey="week" stroke="var(--muted-foreground)" />
        <YAxis stroke="var(--muted-foreground)" domain={[0, 100]} />
        <Tooltip
          contentStyle={{
            backgroundColor: 'var(--card)',
            border: `2px solid var(--border)`,
            borderRadius: '0.875rem',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)',
          }}
          cursor={{ stroke: 'rgba(139, 92, 246, 0.3)', strokeWidth: 2 }}
        />
        <Area
          type="monotone"
          dataKey="sentiment"
          stroke="#4CAF50"
          strokeWidth={3}
          fillOpacity={1}
          fill="url(#colorSentiment)"
          dot={<CustomDot />}
          isAnimationActive={true}
        />
      </AreaChart>
    </ResponsiveContainer>
  )
}
