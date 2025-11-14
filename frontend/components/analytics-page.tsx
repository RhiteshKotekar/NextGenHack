'use client'

import { useState, useEffect } from 'react'
import { useDataStore } from '@/lib/store-context'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { AlertCircle, BarChart3, Zap } from 'lucide-react'
import { AdvancedDemandChart } from './charts/advanced-demand-chart'
import { WarehouseEfficiencyChart } from './charts/warehouse-efficiency-chart'
import { TransportationOptimization } from './charts/transportation-optimization'
import { CustomerSentimentAnalysis } from './charts/customer-sentiment-analysis'

interface InsightCard {
  icon: React.ReactNode
  title: string
  value: string
  description: string
  color: string
}

export function AnalyticsPage() {
  const { datasets, setLastAnalysisTime } = useDataStore()
  const [analyticsRun, setAnalyticsRun] = useState(false)
  const [loading, setLoading] = useState(false)

  const uploadedCount = Object.keys(datasets).length
  const canRunAnalytics = uploadedCount === 5

  const insights: InsightCard[] = [
    {
      icon: <Zap className="w-6 h-6" />,
      title: 'Demand Forecast',
      value: '+18.5%',
      description: 'Expected demand increase for Q4',
      color: 'bg-blue-500/10 text-blue-600 dark:text-blue-400'
    },
    {
      icon: <BarChart3 className="w-6 h-6" />,
      title: 'Warehouse Efficiency',
      value: '87%',
      description: 'Average operational efficiency',
      color: 'bg-cyan-500/10 text-cyan-600 dark:text-cyan-400'
    },
    {
      icon: <AlertCircle className="w-6 h-6" />,
      title: 'Cost Savings',
      value: '15-20%',
      description: 'Potential through optimization',
      color: 'bg-green-500/10 text-green-600 dark:text-green-400'
    },
    {
      icon: <BarChart3 className="w-6 h-6" />,
      title: 'Customer Satisfaction',
      value: '4.8/5',
      description: 'Current sentiment score',
      color: 'bg-purple-500/10 text-purple-600 dark:text-purple-400'
    }
  ]

  const handleRunAnalytics = async () => {
    if (!canRunAnalytics) return
    
    setLoading(true)
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000))
    setAnalyticsRun(true)
    setLastAnalysisTime(new Date())
    setLoading(false)
  }

  if (!canRunAnalytics && !analyticsRun) {
    return (
      <div className="p-4 md:p-8">
        <Card className="p-8 md:p-12 text-center shadow-soft">
          <div className="mb-6">
            <BarChart3 className="w-16 h-16 mx-auto text-muted-foreground opacity-50" />
          </div>
          <h2 className="text-2xl font-bold text-foreground mb-2">Ready to analyze?</h2>
          <p className="text-muted-foreground mb-6 max-w-md mx-auto">
            Upload all 5 datasets to run comprehensive supply chain analytics and get AI-powered insights.
          </p>
          <div className="space-y-2 text-sm mb-8 max-w-md mx-auto">
            {[
              `Orders Data (${datasets['orders'] ? '✓' : '✗'})`,
              `Seasonal Demand (${datasets['demand'] ? '✓' : '✗'})`,
              `Warehouse Operations (${datasets['warehouse'] ? '✓' : '✗'})`,
              `Transportation (${datasets['transportation'] ? '✓' : '✗'})`,
              `Customer Reviews (${datasets['reviews'] ? '✓' : '✗'})`
            ].map((item, idx) => (
              <div key={idx} className="text-muted-foreground">
                {item}
              </div>
            ))}
          </div>
          <Button
            disabled={!canRunAnalytics}
            onClick={handleRunAnalytics}
            className="bg-primary hover:bg-primary/90 text-primary-foreground px-8"
          >
            Go to Upload Page
          </Button>
        </Card>
      </div>
    )
  }

  return (
    <div className="p-4 md:p-8 space-y-8">
      {/* Header with refresh */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Analytics Results</h1>
          <p className="text-muted-foreground mt-2">
            AI-powered insights from your supply chain data
          </p>
        </div>
        <Button
          onClick={handleRunAnalytics}
          disabled={loading}
          className="bg-primary hover:bg-primary/90 text-primary-foreground"
        >
          {loading ? 'Analyzing...' : 'Refresh Analysis'}
        </Button>
      </div>

      {/* Key insights cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {insights.map((insight, idx) => (
          <Card key={idx} className="p-6 shadow-soft">
            <div className={`w-12 h-12 rounded-lg ${insight.color} flex items-center justify-center mb-4`}>
              {insight.icon}
            </div>
            <p className="text-sm font-medium text-muted-foreground">{insight.title}</p>
            <p className="text-2xl font-bold text-foreground mt-2">{insight.value}</p>
            <p className="text-sm text-muted-foreground mt-2">{insight.description}</p>
          </Card>
        ))}
      </div>

      {/* Detailed charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="p-6 shadow-soft">
          <h3 className="text-lg font-semibold text-foreground mb-4">Demand Forecast (6 Months Ahead)</h3>
          <AdvancedDemandChart />
        </Card>

        <Card className="p-6 shadow-soft">
          <h3 className="text-lg font-semibold text-foreground mb-4">Warehouse Efficiency by Region</h3>
          <WarehouseEfficiencyChart />
        </Card>

        <Card className="p-6 shadow-soft">
          <h3 className="text-lg font-semibold text-foreground mb-4">Transportation Bottlenecks</h3>
          <TransportationOptimization />
        </Card>

        <Card className="p-6 shadow-soft">
          <h3 className="text-lg font-semibold text-foreground mb-4">Customer Sentiment Trend</h3>
          <CustomerSentimentAnalysis />
        </Card>
      </div>

      {/* Recommendations */}
      <Card className="p-6 shadow-soft border border-primary/20 bg-primary/5">
        <h3 className="text-lg font-semibold text-foreground mb-4">AI Recommendations</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[
            'Increase inventory in Northeast region by 15% before Q4',
            'Optimize Route 7 to reduce delivery times by 23%',
            'Schedule preventive maintenance for Warehouse B',
            'Launch promotional campaign based on customer sentiment trends'
          ].map((rec, idx) => (
            <div key={idx} className="flex gap-3">
              <span className="text-primary font-bold flex-shrink-0">→</span>
              <p className="text-foreground">{rec}</p>
            </div>
          ))}
        </div>
      </Card>

      {/* Order fulfillment optimization */}
      <Card className="p-6 shadow-soft">
        <h3 className="text-lg font-semibold text-foreground mb-4">Order Fulfillment Optimization</h3>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-foreground">Current fulfillment speed</span>
            <span className="font-semibold text-foreground">2.3 days</span>
          </div>
          <div className="w-full bg-muted rounded-full h-2">
            <div className="bg-primary h-2 rounded-full" style={{ width: '78%' }} />
          </div>
          <div className="flex items-center justify-between">
            <span className="text-foreground">Target fulfillment speed</span>
            <span className="font-semibold text-foreground">1.8 days</span>
          </div>
          <p className="text-sm text-muted-foreground mt-4">
            By implementing recommended changes, you can reduce fulfillment time by 22% and improve customer satisfaction scores.
          </p>
        </div>
      </Card>
    </div>
  )
}
