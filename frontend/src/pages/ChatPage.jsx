import React, { useState, useRef, useEffect } from "react";

function ChatPage() {
  const [messages, setMessages] = useState([
    { sender: "bot", text: "👋 Hello! I'm CuraAI. How can I assist you today?" },
  ]);
  const [input, setInput] = useState("");
  const [chatHistory, setChatHistory] = useState([
    { id: 1, title: "Chat with Doctor" },
    { id: 2, title: "Health Tips" },
  ]);
  const chatEndRef = useRef(null);

  // Auto-scroll to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const newMsg = { sender: "user", text: input };
    setMessages((prev) => [...prev, newMsg]);

    // Fake AI reply
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: "🤖 Sure! Let’s talk more about that." },
      ]);
    }, 700);

    setInput("");
  };

  const handleNewChat = () => {
    setMessages([{ sender: "bot", text: "🆕 New chat started!" }]);
  };

  return (
    <div
      style={{
        display: "flex",
        height: "100vh",
        width: "100vw",
        overflow: "hidden",
        backgroundColor: "#343541",
        color: "#ececf1",
        fontFamily: "system-ui, -apple-system, sans-serif",
      }}
    >
      {/* 🧭 Sidebar */}
      <aside
        style={{
          width: "260px",
          backgroundColor: "#202123",
          color: "#fff",
          display: "flex",
          flexDirection: "column",
          padding: "15px",
          boxSizing: "border-box",
        }}
      >
        <button
          onClick={handleNewChat}
          style={{
            backgroundColor: "#343541",
            color: "#fff",
            border: "1px solid #565869",
            borderRadius: "6px",
            padding: "10px",
            marginBottom: "15px",
            fontWeight: "500",
            cursor: "pointer",
          }}
          onMouseEnter={(e) => (e.currentTarget.style.background = "#444654")}
          onMouseLeave={(e) => (e.currentTarget.style.background = "#343541")}
        >
          + New Chat
        </button>

        <div
          style={{
            flex: 1,
            overflowY: "auto",
            scrollbarWidth: "thin",
          }}
        >
          <h4 style={{ marginBottom: "10px", opacity: 0.8 }}>Recent Chats</h4>
          {chatHistory.map((chat) => (
            <div
              key={chat.id}
              style={{
                padding: "10px",
                borderRadius: "5px",
                backgroundColor: "#2a2b32",
                marginBottom: "8px",
                cursor: "pointer",
                transition: "background 0.2s",
              }}
              onClick={() =>
                setMessages([
                  { sender: "bot", text: `📄 Loaded: ${chat.title}` },
                ])
              }
              onMouseEnter={(e) => (e.currentTarget.style.background = "#3b3c44")}
              onMouseLeave={(e) => (e.currentTarget.style.background = "#2a2b32")}
            >
              {chat.title}
            </div>
          ))}
        </div>
      </aside>

      {/* 💬 Chat Area */}
      <main
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          backgroundColor: "#343541",
          height: "100vh",
          overflow: "hidden",
        }}
      >
        {/* Header */}
        <header
          style={{
            backgroundColor: "#343541",
            borderBottom: "1px solid #565869",
            padding: "15px 20px",
            fontWeight: "600",
            fontSize: "18px",
            textAlign: "center",
            color: "#ececf1",
          }}
        >
          CuraAI Chat
        </header>

        {/* Message Area */}
        <div
          style={{
            flex: 1,
            overflowY: "auto",
            padding: "25px",
            display: "flex",
            flexDirection: "column",
            gap: "14px",
            boxSizing: "border-box",
            scrollbarWidth: "thin",
          }}
        >
          {messages.map((msg, idx) => (
            <div
              key={idx}
              style={{
                alignSelf: msg.sender === "user" ? "flex-end" : "flex-start",
                backgroundColor:
                  msg.sender === "user" ? "#10a37f" : "#444654",
                color: msg.sender === "user" ? "#fff" : "#ececf1",
                padding: "12px 16px",
                borderRadius: "18px",
                maxWidth: "70%",
                lineHeight: "1.5",
                boxShadow: "0 1px 3px rgba(0,0,0,0.2)",
                whiteSpace: "pre-wrap",
                wordBreak: "break-word",
              }}
            >
              {msg.text}
            </div>
          ))}
          <div ref={chatEndRef} />
        </div>

        {/* Input Field */}
        <form
          onSubmit={handleSend}
          style={{
            display: "flex",
            padding: "16px 20px",
            borderTop: "1px solid #565869",
            backgroundColor: "#40414f",
            boxSizing: "border-box",
          }}
        >
          <input
            type="text"
            placeholder="Send a message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            style={{
              flex: 1,
              padding: "12px 16px",
              borderRadius: "20px",
              border: "1px solid #565869",
              backgroundColor: "#343541",
              color: "#ececf1",
              fontSize: "15px",
              outline: "none",
              marginRight: "10px",
            }}
          />
          <button
            type="submit"
            style={{
              backgroundColor: "#10a37f",
              color: "#fff",
              border: "none",
              borderRadius: "20px",
              padding: "12px 20px",
              fontWeight: "600",
              cursor: "pointer",
              transition: "background 0.2s",
            }}
            onMouseEnter={(e) => (e.currentTarget.style.background = "#0e8c6b")}
            onMouseLeave={(e) => (e.currentTarget.style.background = "#10a37f")}
          >
            Send
          </button>
        </form>
      </main>
    </div>
  );
}

export default ChatPage;
