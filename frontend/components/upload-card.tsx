'use client'

import { useState } from 'react'
import { useDataStore } from '@/lib/store-context'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Upload, CheckCircle, Trash2 } from 'lucide-react'
import Papa from 'papaparse'

interface UploadCardProps {
  category: {
    id: string
    label: string
    fileName: string
    description: string
  }
  isUploaded: boolean
  onPreview: () => void
}

export function UploadCard({ category, isUploaded, onPreview }: UploadCardProps) {
  const { uploadDataset, removeDataset } = useDataStore()
  const [loading, setLoading] = useState(false)
  const [dragActive, setDragActive] = useState(false)

  const handleFile = (file: File) => {
    if (!file.name.endsWith('.csv')) {
      alert('Please upload a CSV file')
      return
    }

    setLoading(true)
    Papa.parse(file, {
      header: true,
      complete: (results) => {
        uploadDataset(category.id, {
          name: category.label,
          data: results.data.filter(row => Object.values(row).some(val => val)),
          fileName: file.name,
          uploadedAt: new Date()
        })
        setLoading(false)
      },
      error: () => {
        alert('Error parsing CSV file')
        setLoading(false)
      }
    })
  }

  const handleDrag = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0])
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0])
    }
  }

  return (
    <Card className={`p-6 shadow-soft border-2 transition-all fancy-card animate-slide-in-up ${
      dragActive ? 'border-primary bg-primary/5' : 'border-border'
    } ${isUploaded ? 'border-green-500/50' : ''}`}>
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div>
            <h3 className="text-lg font-semibold text-foreground">{category.label}</h3>
            <p className="text-sm text-muted-foreground mt-1">{category.description}</p>
          </div>
          {isUploaded && (
            <CheckCircle className="w-6 h-6 text-green-500 flex-shrink-0" />
          )}
        </div>

        {/* Upload area */}
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors cursor-pointer ${
            dragActive
              ? 'border-primary bg-primary/10'
              : 'border-border hover:border-muted-foreground'
          }`}
        >
          <input
            type="file"
            accept=".csv"
            onChange={handleInputChange}
            disabled={loading}
            className="hidden"
            id={`file-input-${category.id}`}
          />
          <label
            htmlFor={`file-input-${category.id}`}
            className="block cursor-pointer"
          >
            <Upload className="w-8 h-8 mx-auto mb-2 text-muted-foreground" />
            <p className="text-sm font-medium text-foreground">Drag & drop your CSV</p>
            <p className="text-xs text-muted-foreground mt-1">or click to browse</p>
          </label>
        </div>

        {/* Actions */}
        <div className="flex gap-2">
          <label
            htmlFor={`file-input-${category.id}`}
            className="flex-1"
          >
            <Button
              asChild
              variant="outline"
              className="w-full cursor-pointer btn-fancy"
              disabled={loading}
            >
              <span>{loading ? 'Uploading...' : 'Upload CSV'}</span>
            </Button>
          </label>
          {isUploaded && (
            <>
              <Button
                variant="outline"
                onClick={onPreview}
                className="flex-1 btn-fancy"
              >
                Preview
              </Button>
              <Button
                variant="outline"
                size="icon"
                onClick={() => removeDataset(category.id)}
                className="text-destructive hover:text-destructive"
              >
                <Trash2 className="w-4 h-4" />
              </Button>
            </>
          )}
        </div>

        {/* File info */}
        {isUploaded && (
          <div className="text-xs text-muted-foreground space-y-1">
            <p>Uploaded: {new Date().toLocaleDateString()}</p>
          </div>
        )}
      </div>
    </Card>
  )
}
