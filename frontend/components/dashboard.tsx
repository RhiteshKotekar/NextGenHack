/**
 * Dashboard Component - Homepage
 * 
 * Displays a high-level overview of the supply chain analytics dashboard with:
 * - Summary widgets showing key metrics
 * - Grid of visualization charts
 * - Call-to-action prompting users to upload data
 * 
 * This is the first page users see when opening the application.
 * Data is sourced from the global store context.
 */

'use client'

import { useEffect, useState } from 'react'
import { useDataStore } from '@/lib/store-context'
import { Activity, Clock, Database, TrendingUp, Package, Truck, AlertTriangle, Star } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { DemandChart } from './charts/demand-chart'
import { WarehouseChart } from './charts/warehouse-chart'
import { TransportationChart } from './charts/transportation-chart'
import { SentimentChart } from './charts/sentiment-chart'
import { DeliveryPerformanceChart } from './charts/delivery-performance-chart'
import { CostAnalysisChart } from './charts/cost-analysis-chart'

interface Metrics {
  total_orders: number
  delay_rate: number
  avg_delivery_days: number
  total_warehouses: number
  avg_processing_hours: number
  avg_on_time_rate: number
  avg_rating: number
  avg_sentiment: number
  total_order_value: number
}

export function Dashboard() {
  // Retrieve stored datasets and metadata from global context
  const { datasets, lastAnalysisTime } = useDataStore()
  
  // Calculate how many datasets have been uploaded (out of 5 required)
  const uploadedCount = Object.keys(datasets).length

  // State for real-time metrics
  const [metrics, setMetrics] = useState<Metrics | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Fetch analytics data
    fetch('http://localhost:5000/api/dashboard/analytics')
      .then(res => res.json())
      .then(result => {
        if (result.success && result.data.metrics) {
          setMetrics(result.data.metrics)
        }
        setLoading(false)
      })
      .catch(err => {
        console.error('Error fetching metrics:', err)
        setLoading(false)
      })
  }, [])

  return (
    <div className="p-4 md:p-8 space-y-8">
      {/* SUMMARY WIDGETS SECTION */}
      {/* Displays key metrics that give a quick overview of system status */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Widget 1: Total Orders */}
        <Card className="p-6 shadow-soft fancy-card animate-slide-in-left">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Total Orders</p>
              <p className="text-3xl font-bold text-foreground mt-2">
                {loading ? '...' : metrics ? metrics.total_orders.toLocaleString() : '0'}
              </p>
            </div>
            <div className="p-3 bg-primary/10 rounded-lg">
              <Package className="w-6 h-6 text-primary" />
            </div>
          </div>
        </Card>

        {/* Widget 2: Delivery Delay Rate */}
        <Card className="p-6 shadow-soft fancy-card">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Delay Rate</p>
              <p className="text-3xl font-bold text-foreground mt-2">
                {loading ? '...' : metrics ? `${metrics.delay_rate.toFixed(1)}%` : '0%'}
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                Avg: {loading ? '...' : metrics ? `${metrics.avg_delivery_days.toFixed(1)} days` : '0 days'}
              </p>
            </div>
            <div className="p-3 bg-red-500/10 rounded-lg">
              <AlertTriangle className="w-6 h-6 text-red-500" />
            </div>
          </div>
        </Card>

        {/* Widget 3: Courier On-Time Rate */}
        <Card className="p-6 shadow-soft fancy-card">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">On-Time Rate</p>
              <p className="text-3xl font-bold text-foreground mt-2">
                {loading ? '...' : metrics ? `${metrics.avg_on_time_rate.toFixed(1)}%` : '0%'}
              </p>
            </div>
            <div className="p-3 bg-green-500/10 rounded-lg">
              <Truck className="w-6 h-6 text-green-500" />
            </div>
          </div>
        </Card>

        {/* Widget 4: Customer Satisfaction */}
        <Card className="p-6 shadow-soft fancy-card">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Avg Rating</p>
              <p className="text-3xl font-bold text-foreground mt-2">
                {loading ? '...' : metrics ? `${metrics.avg_rating.toFixed(1)}/5` : '0/5'}
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                Sentiment: {loading ? '...' : metrics ? `${(metrics.avg_sentiment * 100).toFixed(0)}` : '0'}
              </p>
            </div>
            <div className="p-3 bg-yellow-500/10 rounded-lg">
              <Star className="w-6 h-6 text-yellow-500" />
            </div>
          </div>
        </Card>
      </div>

      {/* ADDITIONAL METRICS ROW */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-6 shadow-soft fancy-card">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Active Warehouses</p>
              <p className="text-2xl font-bold text-foreground mt-2">
                {loading ? '...' : metrics ? metrics.total_warehouses : '0'}
              </p>
            </div>
            <div className="p-3 bg-blue-500/10 rounded-lg">
              <Database className="w-6 h-6 text-blue-500" />
            </div>
          </div>
        </Card>

        <Card className="p-6 shadow-soft fancy-card">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Avg Processing Time</p>
              <p className="text-2xl font-bold text-foreground mt-2">
                {loading ? '...' : metrics ? `${metrics.avg_processing_hours.toFixed(1)}h` : '0h'}
              </p>
            </div>
            <div className="p-3 bg-purple-500/10 rounded-lg">
              <Clock className="w-6 h-6 text-purple-500" />
            </div>
          </div>
        </Card>

        <Card className="p-6 shadow-soft fancy-card">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Total Order Value</p>
              <p className="text-2xl font-bold text-foreground mt-2">
                {loading ? '...' : metrics ? `₹${(metrics.total_order_value / 1000000).toFixed(1)}M` : '₹0'}
              </p>
            </div>
            <div className="p-3 bg-green-500/10 rounded-lg">
              <TrendingUp className="w-6 h-6 text-green-500" />
            </div>
          </div>
        </Card>
      </div>

      {/* CHARTS SECTION */}
      {/* Grid of interactive visualizations showing supply chain metrics */}
      <div className="space-y-6">
        {/* Top Row - Main Analytics */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Seasonal Demand Analysis */}
          <Card className="p-6 shadow-soft fancy-card animate-slide-in-up">
            <div className="mb-4">
              <h3 className="text-lg font-semibold text-foreground">Seasonal Demand Trends</h3>
              <p className="text-sm text-muted-foreground">Monthly demand index and active campaigns</p>
            </div>
            <DemandChart />
          </Card>

          {/* Warehouse Efficiency Analysis */}
          <Card className="p-6 shadow-soft fancy-card animate-slide-in-up">
            <div className="mb-4">
              <h3 className="text-lg font-semibold text-foreground">Warehouse Efficiency Scores</h3>
              <p className="text-sm text-muted-foreground">Top performing warehouses by efficiency</p>
            </div>
            <WarehouseChart />
          </Card>
        </div>

        {/* Middle Row - Transportation & Sentiment */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Courier Performance Chart */}
          <Card className="p-6 shadow-soft fancy-card">
            <div className="mb-4">
              <h3 className="text-lg font-semibold text-foreground">Courier Partner Performance</h3>
              <p className="text-sm text-muted-foreground">On-time delivery rates by courier</p>
            </div>
            <TransportationChart />
          </Card>

          {/* Customer Sentiment Distribution */}
          <Card className="p-6 shadow-soft fancy-card">
            <div className="mb-4">
              <h3 className="text-lg font-semibold text-foreground">Customer Sentiment Analysis</h3>
              <p className="text-sm text-muted-foreground">Review sentiment distribution</p>
            </div>
            <SentimentChart />
          </Card>
        </div>

        {/* Bottom Row - Delivery Performance & Cost Analysis */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Delivery Performance by City */}
          <Card className="p-6 shadow-soft fancy-card">
            <div className="mb-4">
              <h3 className="text-lg font-semibold text-foreground">Delivery Performance by City</h3>
              <p className="text-sm text-muted-foreground">Cities with highest delay rates</p>
            </div>
            <DeliveryPerformanceChart />
          </Card>

          {/* Route Cost Analysis */}
          <Card className="p-6 shadow-soft fancy-card">
            <div className="mb-4">
              <h3 className="text-lg font-semibold text-foreground">Route Cost Analysis</h3>
              <p className="text-sm text-muted-foreground">Transportation costs by destination</p>
            </div>
            <CostAnalysisChart />
          </Card>
        </div>
      </div>

      {/* KEY INSIGHTS SECTION */}
      <Card className="p-8 bg-gradient-to-r from-primary/10 to-accent/10 border border-primary/20 shadow-soft fancy-card">
        <div className="space-y-4">
          <div>
            <h3 className="text-xl font-bold text-foreground">📊 Key Supply Chain Insights</h3>
            <p className="text-muted-foreground mt-2">Based on analysis of {loading ? '...' : metrics ? metrics.total_orders.toLocaleString() : '0'} orders across {loading ? '...' : metrics ? metrics.total_warehouses : '0'} warehouses</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
            <div className="p-4 bg-card rounded-lg border border-border">
              <h4 className="font-semibold text-foreground flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-red-500" />
                Delivery Bottlenecks
              </h4>
              <p className="text-sm text-muted-foreground mt-2">
                {loading ? 'Loading...' : metrics ? 
                  `${metrics.delay_rate.toFixed(1)}% of orders are delayed beyond 2 days. Focus on cities with highest delay rates to improve efficiency.` 
                  : 'No data available'}
              </p>
            </div>

            <div className="p-4 bg-card rounded-lg border border-border">
              <h4 className="font-semibold text-foreground flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-green-500" />
                Courier Excellence
              </h4>
              <p className="text-sm text-muted-foreground mt-2">
                {loading ? 'Loading...' : metrics ? 
                  `Average courier on-time rate is ${metrics.avg_on_time_rate.toFixed(1)}%. Partner with top performers to optimize delivery.` 
                  : 'No data available'}
              </p>
            </div>

            <div className="p-4 bg-card rounded-lg border border-border">
              <h4 className="font-semibold text-foreground flex items-center gap-2">
                <Star className="w-4 h-4 text-yellow-500" />
                Customer Satisfaction
              </h4>
              <p className="text-sm text-muted-foreground mt-2">
                {loading ? 'Loading...' : metrics ? 
                  `Average rating of ${metrics.avg_rating.toFixed(1)}/5 with ${(metrics.avg_sentiment * 100).toFixed(0)} sentiment score. Monitor sentiment trends to maintain quality.` 
                  : 'No data available'}
              </p>
            </div>

            <div className="p-4 bg-card rounded-lg border border-border">
              <h4 className="font-semibold text-foreground flex items-center gap-2">
                <Database className="w-4 h-4 text-blue-500" />
                Warehouse Operations
              </h4>
              <p className="text-sm text-muted-foreground mt-2">
                {loading ? 'Loading...' : metrics ? 
                  `Average processing time of ${metrics.avg_processing_hours.toFixed(1)} hours. Optimize warehouse workflow to reduce processing delays.` 
                  : 'No data available'}
              </p>
            </div>
          </div>
        </div>
      </Card>
    </div>
  )
}
