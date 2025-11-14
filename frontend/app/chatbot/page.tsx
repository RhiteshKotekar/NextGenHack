'use client'

import { AppLayout } from '@/components/app-layout'
import { ChatbotPage } from '@/components/chatbot-page'

export default function Chatbot() {
  return (
    <AppLayout hideChat>
      <ChatbotPage />
    </AppLayout>
  )
}
