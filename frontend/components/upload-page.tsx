'use client'

import { useState } from 'react'
import { useDataStore } from '@/lib/store-context'
import { UploadCard } from './upload-card'
import { DataPreview } from './data-preview'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'

const UPLOAD_CATEGORIES = [
  { id: 'orders', label: 'Orders Data', fileName: 'orders_sample.csv', description: 'Upload your orders dataset' },
  { id: 'demand', label: 'Seasonal Demand', fileName: 'seasonal_demand_sample.csv', description: 'Upload demand forecasting data' },
  { id: 'warehouse', label: 'Warehouse Operations', fileName: 'warehouse_ops_sample.csv', description: 'Upload warehouse efficiency data' },
  { id: 'transportation', label: 'Transportation', fileName: 'transportation_sample.csv', description: 'Upload transportation logistics data' },
  { id: 'reviews', label: 'Customer Reviews', fileName: 'customer_reviews_sample.csv', description: 'Upload customer sentiment data' },
]

export function UploadDataPage() {
  const { datasets, uploadDataset } = useDataStore()
  const [selectedPreview, setSelectedPreview] = useState<string | null>(null)

  const handleRunAnalytics = async () => {
    // Mock analytics trigger
    const allUploaded = UPLOAD_CATEGORIES.every(cat => datasets[cat.id])
    if (allUploaded) {
      console.log('Running analytics with all datasets...')
      // In a real app, this would send data to FastAPI backend
    }
  }

  return (
    <div className="p-4 md:p-8 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-foreground">Upload Your Data</h1>
        <p className="text-muted-foreground mt-2">
          Upload each dataset separately to enable AI-powered supply chain analytics
        </p>
      </div>

      {/* Upload cards grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {UPLOAD_CATEGORIES.map(category => (
          <UploadCard
            key={category.id}
            category={category}
            isUploaded={!!datasets[category.id]}
            onPreview={() => setSelectedPreview(category.id)}
          />
        ))}
      </div>

      {/* Data preview */}
      {selectedPreview && datasets[selectedPreview] && (
        <Card className="p-6 shadow-soft">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-foreground">
              Data Preview: {datasets[selectedPreview].fileName}
            </h3>
            <button
              onClick={() => setSelectedPreview(null)}
              className="text-muted-foreground hover:text-foreground"
            >
              ✕
            </button>
          </div>
          <DataPreview data={datasets[selectedPreview].data} />
        </Card>
      )}

      {/* Analytics button */}
      <div className="flex justify-center">
        <Button
          onClick={handleRunAnalytics}
          disabled={!UPLOAD_CATEGORIES.every(cat => datasets[cat.id])}
          className="bg-primary hover:bg-primary/90 text-primary-foreground px-8 py-3 text-lg"
        >
          {UPLOAD_CATEGORIES.every(cat => datasets[cat.id])
            ? 'Run Analytics'
            : `Upload all datasets to run analytics (${Object.keys(datasets).length}/${UPLOAD_CATEGORIES.length})`
          }
        </Button>
      </div>

      {/* Progress indicator */}
      <Card className="p-6 bg-muted/50">
        <h3 className="font-semibold text-foreground mb-4">Upload Progress</h3>
        <div className="space-y-2">
          {UPLOAD_CATEGORIES.map(category => (
            <div key={category.id} className="flex items-center gap-3">
              <div
                className={`w-5 h-5 rounded border-2 flex items-center justify-center ${
                  datasets[category.id]
                    ? 'bg-green-500 border-green-500'
                    : 'border-muted-foreground'
                }`}
              >
                {datasets[category.id] && (
                  <span className="text-white text-xs">✓</span>
                )}
              </div>
              <span className="text-foreground">{category.label}</span>
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}
