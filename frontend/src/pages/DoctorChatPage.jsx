import React, { useState } from 'react'
import MessageList from '../components/MessageList'
import ChatInput from '../components/ChatInput'

export default function ChatPage() {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello! How can I help you today?' },
  ])
  const [isLoading, setIsLoading] = useState(false)

  const handleSendMessage = (message) => {
    // Add user message
    const newMessages = [...messages, { role: 'user', content: message }]
    setMessages(newMessages)
    setIsLoading(true)

    // Dummy AI reply after 1 second
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'This is a dummy response.' },
      ])
      setIsLoading(false)
    }, 1000)
  }

  return (
    <div
      style={{
        maxWidth: '600px',
        margin: '50px auto',
        display: 'flex',
        flexDirection: 'column',
        gap: '10px',
      }}
    >
      <MessageList messages={messages} />
      {isLoading && <p style={{ textAlign: 'center' }}>Thinking...</p>}
      <ChatInput onSendMessage={handleSendMessage} disabled={isLoading} />
    </div>
  )
}
