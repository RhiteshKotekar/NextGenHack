/**
 * Chat Panel Component - Floating Chat Sidebar
 * 
 * Renders a floating chat interface on the right side of the screen.
 * Features:
 * - Message history with user/assistant distinction
 * - Auto-scrolling to latest messages
 * - Mock AI responses (ready for backend API integration)
 * - Loading state with animated indicator
 * 
 * This component is hidden by default and shown via a toggle in the header.
 * See also: ChatbotPage for a full-screen chat experience.
 */

'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, X } from 'lucide-react'
import { Button } from '@/components/ui/button'

/**
 * Shape of a single chat message
 */
interface Message {
  /** Unique identifier for the message */
  id: string
  /** Who sent the message: user or AI assistant */
  role: 'user' | 'assistant'
  /** The actual message text content */
  content: string
  /** When the message was sent */
  timestamp: Date
}

/**
 * Props for the ChatPanel component
 */
interface ChatPanelProps {
  /** Callback when user closes the panel */
  onClose: () => void
}

export function ChatPanel({ onClose }: ChatPanelProps) {
  /**
   * Message history state
   * Initialized with a welcome message from the AI assistant
   */
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Hello! I\'m your AI Supply Chain Assistant. I can help you analyze your data and provide insights. Upload your datasets to get started!',
      timestamp: new Date()
    }
  ])
  
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  // Ref to scroll to bottom of messages
  const messagesEndRef = useRef<HTMLDivElement>(null)

  /**
   * Scroll to the bottom of the message list
   * Called whenever new messages arrive
   */
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  /**
   * Auto-scroll when messages change
   */
  useEffect(() => {
    scrollToBottom()
  }, [messages])

  /**
   * Handle sending a new message
   * 1. Add user message to history
   * 2. Clear input field
   * 3. Simulate API call
   * 4. Add AI response
   */
  const handleSendMessage = async () => {
    if (!input.trim()) return

    // Create and add the user's message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    // In production, replace this with actual API call to FastAPI backend
    setTimeout(() => {
      // Array of mock AI responses
      const mockResponses = [
        'Based on your supply chain data, I recommend optimizing warehouse operations in the northeast region.',
        'Your current inventory levels are optimal for the predicted demand. Great work!',
        'I\'ve identified potential cost savings of 15-20% through better route optimization.',
        'Customer satisfaction metrics are trending upward. Keep maintaining current service standards.',
        'The predictive model shows increased demand in Q4. Consider adjusting stock levels now.'
      ]

      // Pick a random response
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: mockResponses[Math.floor(Math.random() * mockResponses.length)],
        timestamp: new Date()
      }

      setMessages(prev => [...prev, assistantMessage])
      setLoading(false)
    }, 1000)
  }

  return (
    <div className="fixed right-0 top-0 h-full w-full md:w-96 bg-white dark:bg-slate-900 border-l border-border shadow-soft-lg z-40 flex flex-col">
      {/* HEADER - Title and close button */}
      <div className="flex items-center justify-between p-4 border-b border-border">
        <h3 className="text-lg font-semibold text-foreground">AI Assistant</h3>
        <Button
          variant="ghost"
          size="icon"
          onClick={onClose}
          className="h-8 w-8"
        >
          <X className="w-4 h-4" />
        </Button>
      </div>

      {/* MESSAGE HISTORY - Scrollable area with all messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map(message => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {/* Message bubble with conditional styling based on role */}
            <div
              className={`max-w-xs px-4 py-2 rounded-lg ${
                message.role === 'user'
                  ? 'bg-primary text-primary-foreground rounded-br-none'
                  : 'bg-muted text-foreground rounded-bl-none'
              }`}
            >
              <p className="text-sm">{message.content}</p>
            </div>
          </div>
        ))}
        
        {loading && (
          <div className="flex justify-start">
            <div className="bg-muted text-foreground px-4 py-2 rounded-lg rounded-bl-none">
              <p className="text-sm">Thinking...</p>
            </div>
          </div>
        )}
        {/* Ref for auto-scrolling to bottom */}
        <div ref={messagesEndRef} />
      </div>

      {/* INPUT AREA - Text input and send button */}
      <div className="border-t border-border p-4 space-y-3">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyPress={e => e.key === 'Enter' && handleSendMessage()}
            placeholder="Ask me anything..."
            className="flex-1 px-3 py-2 rounded-lg bg-input text-foreground placeholder-muted-foreground border border-border focus:outline-none focus:ring-2 focus:ring-primary"
            disabled={loading}
          />
          <Button
            size="icon"
            onClick={handleSendMessage}
            disabled={loading || !input.trim()}
            className="bg-primary hover:bg-primary/90"
          >
            <Send className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  )
}
