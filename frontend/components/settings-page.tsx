'use client'

import { useState } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Bell, Eye, Lock, Palette, Save, Trash2 } from 'lucide-react'

export function SettingsPage() {
  const [notificationsEnabled, setNotificationsEnabled] = useState(true)
  const [dailyDigest, setDailyDigest] = useState(true)
  const [dataRetention, setDataRetention] = useState('90')
  const [theme, setTheme] = useState('auto')
  const [saved, setSaved] = useState(false)

  const handleSave = () => {
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  const handleClearData = () => {
    if (confirm('Are you sure you want to clear all uploaded data? This cannot be undone.')) {
      // Would clear data from store
    }
  }

  return (
    <div className="p-4 md:p-8 space-y-8 max-w-4xl">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-foreground">Settings</h1>
        <p className="text-muted-foreground mt-2">Manage your dashboard preferences and data</p>
      </div>

      {/* Notifications */}
      <Card className="p-6 shadow-soft">
        <div className="flex items-start justify-between mb-6">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-blue-500/10 rounded-lg">
              <Bell className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-foreground">Notifications</h3>
              <p className="text-sm text-muted-foreground mt-1">Manage alert preferences</p>
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-foreground">Email notifications</p>
              <p className="text-sm text-muted-foreground">Get alerts for analysis results</p>
            </div>
            <button
              onClick={() => setNotificationsEnabled(!notificationsEnabled)}
              className={`relative inline-flex h-8 w-14 items-center rounded-full transition-colors ${
                notificationsEnabled ? 'bg-primary' : 'bg-muted'
              }`}
            >
              <span
                className={`inline-block h-6 w-6 transform rounded-full bg-white transition-transform ${
                  notificationsEnabled ? 'translate-x-7' : 'translate-x-1'
                }`}
              />
            </button>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-foreground">Daily digest</p>
              <p className="text-sm text-muted-foreground">Summary of key metrics each morning</p>
            </div>
            <button
              onClick={() => setDailyDigest(!dailyDigest)}
              className={`relative inline-flex h-8 w-14 items-center rounded-full transition-colors ${
                dailyDigest ? 'bg-primary' : 'bg-muted'
              }`}
            >
              <span
                className={`inline-block h-6 w-6 transform rounded-full bg-white transition-transform ${
                  dailyDigest ? 'translate-x-7' : 'translate-x-1'
                }`}
              />
            </button>
          </div>
        </div>
      </Card>

      {/* Appearance */}
      <Card className="p-6 shadow-soft">
        <div className="flex items-start justify-between mb-6">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-purple-500/10 rounded-lg">
              <Palette className="w-6 h-6 text-purple-600 dark:text-purple-400" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-foreground">Appearance</h3>
              <p className="text-sm text-muted-foreground mt-1">Customize how the dashboard looks</p>
            </div>
          </div>
        </div>

        <div className="space-y-3">
          <label className="flex items-center gap-3">
            <input
              type="radio"
              value="light"
              checked={theme === 'light'}
              onChange={e => setTheme(e.target.value)}
              className="w-4 h-4"
            />
            <span className="text-foreground">Light theme</span>
          </label>
          <label className="flex items-center gap-3">
            <input
              type="radio"
              value="dark"
              checked={theme === 'dark'}
              onChange={e => setTheme(e.target.value)}
              className="w-4 h-4"
            />
            <span className="text-foreground">Dark theme</span>
          </label>
          <label className="flex items-center gap-3">
            <input
              type="radio"
              value="auto"
              checked={theme === 'auto'}
              onChange={e => setTheme(e.target.value)}
              className="w-4 h-4"
            />
            <span className="text-foreground">Auto (system preference)</span>
          </label>
        </div>
      </Card>

      {/* Privacy & Data */}
      <Card className="p-6 shadow-soft">
        <div className="flex items-start justify-between mb-6">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-green-500/10 rounded-lg">
              <Lock className="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-foreground">Privacy & Data</h3>
              <p className="text-sm text-muted-foreground mt-1">Control how your data is stored</p>
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Data retention period
            </label>
            <select
              value={dataRetention}
              onChange={e => setDataRetention(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-input text-foreground border border-border focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="30">30 days</option>
              <option value="90">90 days</option>
              <option value="180">6 months</option>
              <option value="365">1 year</option>
              <option value="unlimited">Unlimited</option>
            </select>
            <p className="text-sm text-muted-foreground mt-2">
              Older data will be automatically deleted after the selected period
            </p>
          </div>

          <div className="p-4 bg-orange-500/10 border border-orange-200 dark:border-orange-900 rounded-lg">
            <p className="text-sm text-foreground font-medium">Danger Zone</p>
            <p className="text-sm text-muted-foreground mt-1 mb-4">
              Clear all uploaded datasets and analysis results
            </p>
            <Button
              variant="outline"
              onClick={handleClearData}
              className="text-destructive hover:text-destructive border-destructive/50"
            >
              <Trash2 className="w-4 h-4 mr-2" />
              Clear All Data
            </Button>
          </div>
        </div>
      </Card>

      {/* API Settings */}
      <Card className="p-6 shadow-soft">
        <div className="flex items-start justify-between mb-6">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-cyan-500/10 rounded-lg">
              <Eye className="w-6 h-6 text-cyan-600 dark:text-cyan-400" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-foreground">API Integration</h3>
              <p className="text-sm text-muted-foreground mt-1">Connect to external services</p>
            </div>
          </div>
        </div>

        <div className="space-y-3">
          <div className="p-3 bg-muted rounded-lg">
            <p className="text-sm font-medium text-foreground">FastAPI Backend</p>
            <p className="text-sm text-muted-foreground mt-1">http://localhost:8000</p>
          </div>
        </div>
      </Card>

      {/* Save button */}
      <div className="flex gap-4">
        <Button
          onClick={handleSave}
          className="bg-primary hover:bg-primary/90 text-primary-foreground px-6"
        >
          <Save className="w-4 h-4 mr-2" />
          Save Settings
        </Button>
        {saved && (
          <div className="flex items-center gap-2 text-green-600 dark:text-green-400">
            <span className="w-2 h-2 bg-green-600 dark:bg-green-400 rounded-full" />
            <span className="text-sm font-medium">Settings saved</span>
          </div>
        )}
      </div>
    </div>
  )
}
