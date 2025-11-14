'use client'

import { useState } from 'react'
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts'

const data = [
  { name: 'Ground', value: 45 },
  { name: 'Air', value: 25 },
  { name: 'Sea', value: 20 },
  { name: 'Rail', value: 10 },
]

const COLORS = ['#6f4bb0', '#8b5cf6', '#c084fc', '#d6bcfa']

// Custom tooltip with white text and animated pop-up
const CustomTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    return (
      <div
        style={{
          backgroundColor: 'var(--card)',
          border: '3px solid var(--accent)',
          borderRadius: '0.875rem',
          padding: '12px 16px',
          boxShadow: '0 12px 32px rgba(139, 92, 246, 0.4)',
          animation: 'popScale 0.35s cubic-bezier(0.34, 1.56, 0.64, 1) forwards',
        }}
      >
        <p style={{ color: '#ffffff', margin: 0, fontSize: '16px', fontWeight: 'bold' }}>
          {payload[0].name}
        </p>
        <p style={{ color: '#8b5cf6', margin: '6px 0 0 0', fontSize: '15px', fontWeight: '600' }}>
          {payload[0].value}%
        </p>
      </div>
    )
  }
  return null
}

export function TransportationChart() {
  const [activeIndex, setActiveIndex] = useState<number | null>(null)

  const handlePieClick = (_: any, index: number) => {
    setActiveIndex(activeIndex === index ? null : index)
  }

  return (
    <>
      <style>{`
        @keyframes popScale {
          0% {
            opacity: 0;
            transform: scale(0.3) translateY(-10px);
          }
          50% {
            opacity: 1;
          }
          100% {
            opacity: 1;
            transform: scale(1) translateY(0);
          }
        }
      `}</style>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, value }) => `${name} ${value}%`}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
            onClick={handlePieClick}
            style={{ cursor: 'pointer' }}
          >
            {data.map((entry, index) => {
              const isActive = activeIndex === index
              const isSelected = activeIndex !== null && activeIndex !== index

              return (
                <Cell
                  key={`cell-${index}`}
                  fill={COLORS[index]}
                  opacity={isSelected ? 0.5 : 1}
                  style={{
                    transition: 'all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1)',
                    filter: isActive ? 'drop-shadow(0 12px 24px rgba(0, 0, 0, 0.4))' : 'none',
                  }}
                />
              )
            })}
          </Pie>
          <Tooltip 
            content={<CustomTooltip />} 
            cursor={{ fill: 'rgba(139, 92, 246, 0.15)' }}
            wrapperStyle={{ outline: 'none' }}
          />
        </PieChart>
      </ResponsiveContainer>
    </>
  )
}
