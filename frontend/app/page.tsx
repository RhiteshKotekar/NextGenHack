'use client'

import { useDataStore } from '@/lib/store-context'
import { AppLayout } from '@/components/app-layout'
import { Dashboard } from '@/components/dashboard'

export default function Home() {
  return (
    <AppLayout>
      <Dashboard />
    </AppLayout>
  )
}
