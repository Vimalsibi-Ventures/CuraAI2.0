import React, { useEffect, useRef } from 'react'

export default function MessageList({ messages }) {
  const containerRef = useRef(null)

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight
    }
  }, [messages])

  return (
    <div
      ref={containerRef}
      className="message-list"
      style={{
        height: '400px',
        overflowY: 'auto',
        padding: '10px',
        border: '1px solid #ccc',
        borderRadius: '8px',
        backgroundColor: '#f9f9f9',
      }}
    >
      {messages.map((msg, index) => (
        <div
          key={index}
          className={`message-bubble ${msg.role}`}
          style={{
            maxWidth: '70%',
            marginBottom: '10px',
            padding: '8px 12px',
            borderRadius: '15px',
            backgroundColor: msg.role === 'user' ? '#007bff' : '#e5e5e5',
            color: msg.role === 'user' ? '#fff' : '#000',
            alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
          }}
        >
          {msg.content}
        </div>
      ))}
    </div>
  )
}
