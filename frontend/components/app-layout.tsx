/**
 * Main Application Layout Component
 * 
 * Provides the primary layout structure for the entire dashboard including:
 * - Responsive sidebar navigation (collapses to hamburger on mobile)
 * - Header with chat toggle button
 * - Main content area
 * - Optional floating chat panel
 * 
 * This component should wrap all page content to ensure consistent layout
 */

'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Menu, X, MessageCircle, LogOutIcon as LogoIcon } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { ChatPanel } from './chat-panel'

/**
 * Props for the AppLayout component
 */
interface AppLayoutProps {
  /** Child components to render in the main content area */
  children: React.ReactNode
  /** Optional flag to hide the chat panel (used on dedicated chatbot page) */
  hideChat?: boolean
}

export function AppLayout({ children, hideChat = false }: AppLayoutProps) {
  // Get current route for active nav highlighting
  const pathname = usePathname()
  
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [chatOpen, setChatOpen] = useState(false)

  /**
   * Navigation items displayed in the sidebar
   * Each item maps to a route in the application
   */
  const navItems = [
    { name: 'Dashboard', href: '/' },
    { name: 'Upload Data', href: '/upload' },
    { name: 'Analytics', href: '/analytics' },
    { name: 'Chatbot', href: '/chatbot' },
    { name: 'Settings', href: '/settings' },
  ]

  return (
    <div className="flex h-screen bg-background">
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 md:hidden bg-black/50"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* SIDEBAR NAVIGATION */}
      <div
        className={`fixed md:relative w-64 h-full bg-white dark:bg-slate-900 border-r border-border shadow-soft-md z-50 transform transition-all duration-300 ease-out ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        }`}
      >
        {/* Logo and branding section */}
        <div className="p-6 border-b border-border">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
              <span className="text-primary-foreground font-bold">AI</span>
            </div>
            <h1 className="text-xl font-bold text-white">Supply Chain</h1>
          </div>
        </div>

        {/* Navigation menu with active state highlighting */}
        <nav className="flex-1 p-4 space-y-2">
          {navItems.map(item => (
            <Link
              key={item.href}
              href={item.href}
              onClick={() => setSidebarOpen(false)}
              className={`block px-4 py-3 rounded-2xl transition-all duration-300 ease-out transform hover:scale-105 ${
                pathname === item.href
                  ? 'bg-primary text-primary-foreground shadow-lg scale-105'
                  : 'text-white hover:bg-primary/20 dark:text-white hover:shadow-md'
              }`}
            >
              {item.name}
            </Link>
          ))}
        </nav>
      </div>

      {/* MAIN CONTENT AREA */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* HEADER */}
        <header className="border-b border-border bg-white dark:bg-slate-900 shadow-soft">
          <div className="flex items-center justify-between px-4 md:px-8 py-4">
            <div className="flex items-center gap-4">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="md:hidden p-2 hover:bg-muted rounded-xl"
              >
                {sidebarOpen ? (
                  <X className="w-5 h-5" />
                ) : (
                  <Menu className="w-5 h-5" />
                )}
              </button>
              <h2 className="text-2xl font-bold text-foreground">
                {pathname === '/chatbot' ? 'Chatbot' : 'Dashboard'}
              </h2>
            </div>
            {/* Chat toggle button in header */}
            <Button
              variant="outline"
              size="icon"
              onClick={() => setChatOpen(!chatOpen)}
              className="relative transition-all duration-300 hover:scale-110 hover:shadow-lg"
            >
              <MessageCircle className="w-5 h-5" />
            </Button>
          </div>
        </header>

        {/* Main content container with auto-scrolling */}
        <main className="flex-1 overflow-auto">
          {children}
        </main>
      </div>

      {/* Floating chat panel (only shown if not hidden and chat is open) */}
      {!hideChat && chatOpen && (
        <ChatPanel onClose={() => setChatOpen(false)} />
      )}
    </div>
  )
}
