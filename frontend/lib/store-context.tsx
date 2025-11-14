/**
 * Global Data Store Context
 * 
 * This module provides a centralized state management system for the Supply Chain Analytics Dashboard.
 * It manages all uploaded CSV datasets and tracks the last analysis execution time using React Context.
 * 
 * Features:
 * - Store multiple uploaded datasets by category
 * - Track analysis metadata (timestamp of last run)
 * - Provide hooks for accessing and modifying the global state
 */

'use client'

import React, { createContext, useContext, useState } from 'react'

/**
 * Represents a single uploaded dataset with metadata
 */
export interface UploadedDataset {
  /** Display name of the dataset */
  name: string
  /** Parsed CSV data as array of objects */
  data: any[]
  /** Original filename of the uploaded CSV */
  fileName: string
  /** Timestamp when the file was uploaded */
  uploadedAt: Date
}

/**
 * Shape of the global data store
 * Provides methods to manage datasets and track analysis history
 */
interface DataStore {
  /** Collection of datasets indexed by category ID */
  datasets: Record<string, UploadedDataset>
  /** Add or update a dataset in the store */
  uploadDataset: (category: string, data: UploadedDataset) => void
  /** Remove a dataset from the store by category ID */
  removeDataset: (category: string) => void
  /** Get all currently stored datasets */
  getAllDatasets: () => Record<string, UploadedDataset>
  /** Timestamp of the most recent analytics run (null if never run) */
  lastAnalysisTime: Date | null
  /** Update the timestamp of the last analysis run */
  setLastAnalysisTime: (time: Date) => void
}

// Create the context with undefined default
// This enforces the use of the provider pattern
const DataStoreContext = createContext<DataStore | undefined>(undefined)

/**
 * Provider component that wraps the application with global state management
 * Must be placed at the root level or above components that need data access
 * 
 * @param {React.ReactNode} children - Components that will have access to the store
 */
export function DataStoreProvider({ children }: { children: React.ReactNode }) {
  const [datasets, setDatasets] = useState<Record<string, UploadedDataset>>({})
  const [lastAnalysisTime, setLastAnalysisTime] = useState<Date | null>(null)

  /**
   * Add or update a dataset in the store
   * Can be called multiple times for different categories
   */
  const uploadDataset = (category: string, data: UploadedDataset) => {
    setDatasets(prev => ({
      ...prev,
      [category]: data
    }))
  }

  /**
   * Remove a dataset from the store by category
   * Useful for allowing users to re-upload or clear uploads
   */
  const removeDataset = (category: string) => {
    setDatasets(prev => {
      const newDatasets = { ...prev }
      delete newDatasets[category]
      return newDatasets
    })
  }

  /**
   * Retrieve all currently stored datasets
   * Used to check if all required datasets are uploaded before running analytics
   */
  const getAllDatasets = () => datasets

  const value: DataStore = {
    datasets,
    uploadDataset,
    removeDataset,
    getAllDatasets,
    lastAnalysisTime,
    setLastAnalysisTime
  }

  return (
    <DataStoreContext.Provider value={value}>
      {children}
    </DataStoreContext.Provider>
  )
}

/**
 * Hook to access the global data store
 * Must be called within a component wrapped by DataStoreProvider
 * 
 * @throws Error if used outside of DataStoreProvider
 * @returns {DataStore} The current state and methods
 * 
 * @example
 * const { datasets, uploadDataset } = useDataStore()
 */
export function useDataStore() {
  const context = useContext(DataStoreContext)
  // Enforce proper usage by throwing an error if context is undefined
  if (!context) {
    throw new Error('useDataStore must be used within DataStoreProvider')
  }
  return context
}
