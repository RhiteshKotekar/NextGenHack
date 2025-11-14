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

import { useDataStore } from '@/lib/store-context'
import { Activity, Clock, Database, TrendingUp } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { DemandChart } from './charts/demand-chart'
import { WarehouseChart } from './charts/warehouse-chart'
import { TransportationChart } from './charts/transportation-chart'
import { SentimentChart } from './charts/sentiment-chart'

export function Dashboard() {
  // Retrieve stored datasets and metadata from global context
  const { datasets, lastAnalysisTime } = useDataStore()

  // Calculate how many datasets have been uploaded (out of 5 required)
  const uploadedCount = Object.keys(datasets).length

  return (
    <div className="p-4 md:p-8 space-y-8">
      {/* SUMMARY WIDGETS SECTION */}
      {/* Displays key metrics that give a quick overview of system status */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Widget 1: Files Uploaded Count */}
        <Card className="p-6 shadow-soft fancy-card animate-slide-in-left">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Files Uploaded</p>
              {/* Display as fraction (e.g., "3/5") */}
              <p className="text-3xl font-bold text-foreground mt-2">{uploadedCount}/5</p>
            </div>
            <div className="p-3 bg-primary/10 rounded-lg">
              <Database className="w-6 h-6 text-primary" />
            </div>
          </div>
        </Card>

        {/* Widget 2: Last Analysis Timestamp */}
        <Card className="p-6 shadow-soft fancy-card">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Last Analysis</p>
              {/* Format date or show "Never" if no analysis run yet */}
              <p className="text-2xl font-bold text-foreground mt-2">
                {lastAnalysisTime ? lastAnalysisTime.toLocaleDateString() : 'Never'}
              </p>
            </div>
            <div className="p-3 bg-accent/10 rounded-lg">
              <Clock className="w-6 h-6 text-accent" />
            </div>
          </div>
        </Card>

        {/* Widget 3: System Status Indicator */}
        <Card className="p-6 shadow-soft fancy-card">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Status</p>
              {/* Show green status indicator */}
              <p className="text-xl font-bold text-foreground mt-2 flex items-center gap-2">
                <span className="w-2 h-2 bg-green-500 rounded-full" />
                Ready
              </p>
            </div>
            <div className="p-3 bg-green-500/10 rounded-lg">
              <Activity className="w-6 h-6 text-green-500" />
            </div>
          </div>
        </Card>

        {/* Widget 4: Number of Available Insights */}
        <Card className="p-6 shadow-soft fancy-card">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Insights</p>
              <p className="text-3xl font-bold text-foreground mt-2">5</p>
            </div>
            <div className="p-3 bg-orange-500/10 rounded-lg">
              <TrendingUp className="w-6 h-6 text-orange-500" />
            </div>
          </div>
        </Card>
      </div>

      {/* CHARTS SECTION */}
      {/* Grid of interactive visualizations showing supply chain metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Demand Forecast Chart */}
        <Card className="p-6 shadow-soft fancy-card animate-slide-in-up">
          <h3 className="text-lg font-semibold text-foreground mb-4">Demand Forecast (6 Months)</h3>
          <DemandChart />
        </Card>

        {/* Warehouse Efficiency Chart */}
        <Card className="rounded-3xl">
          <h3>Warehouse Efficiency</h3>
          <WarehouseChart />
        </Card>

        {/* Transportation Costs Chart */}
        <Card className="p-6 shadow-soft fancy-card">
          <h3 className="text-lg font-semibold text-foreground mb-4">Transportation Costs</h3>
          <TransportationChart />
        </Card>

        {/* Customer Sentiment Chart */}
        <Card className="p-6 shadow-soft fancy-card">
          <h3 className="text-lg font-semibold text-foreground mb-4">Customer Sentiment</h3>
          <SentimentChart />
        </Card>
      </div>

      {/* CALL-TO-ACTION SECTION */}
      {/* Shown when no datasets have been uploaded yet */}
      {uploadedCount === 0 && (
        <Card className="p-8 bg-gradient-to-r from-primary/10 to-accent/10 border border-primary/20 shadow-soft fancy-card">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-xl font-bold text-foreground">Ready to analyze your supply chain?</h3>
              <p className="text-muted-foreground mt-2">Upload your datasets to get started with AI-powered insights.</p>
            </div>
            {/* Link to upload page */}
            <Button className="bg-primary hover:bg-primary/90 text-primary-foreground btn-fancy">
              Upload Data
            </Button>
          </div>
        </Card>
      )}
    </div>
  )
}
