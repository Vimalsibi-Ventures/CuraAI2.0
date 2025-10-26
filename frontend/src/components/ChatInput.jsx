import React, { useState } from 'react'

export default function ChatInput({ onSendMessage, disabled = false }) {
  const [inputValue, setInputValue] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (inputValue.trim() === '') return
    onSendMessage(inputValue)
    setInputValue('')
  }

  return (
    <form
      className="chat-input-form"
      onSubmit={handleSubmit}
      style={{ display: 'flex', gap: '10px', padding: '10px', alignItems: 'center' }}
    >
      <textarea
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        placeholder="Type your message..."
        rows={2}
        disabled={disabled}
        style={{
          flex: 1,
          resize: 'none',
          padding: '8px',
          borderRadius: '6px',
          border: '1px solid #ccc',
          fontSize: '14px',
        }}
      />
      <button
        type="submit"
        disabled={disabled}
        style={{
          padding: '8px 16px',
          borderRadius: '6px',
          backgroundColor: '#007bff',
          color: '#fff',
          border: 'none',
          cursor: disabled ? 'not-allowed' : 'pointer',
        }}
      >
        Send
      </button>
    </form>
  )
}
