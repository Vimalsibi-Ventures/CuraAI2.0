import React, { useState, useRef, useEffect } from "react";

function DoctorChatPage() {
  const [messages, setMessages] = useState([
    { sender: "bot", text: "👋 Hello Doctor! Ready to consult patients today?" },
  ]);
  const [input, setInput] = useState("");
  const [chatHistory, setChatHistory] = useState([
    { id: 1, title: "Patient - John Doe" },
    { id: 2, title: "Patient - Jane Smith" },
  ]);
  const chatEndRef = useRef(null);

  // Auto-scroll
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const newMsg = { sender: "doctor", text: input };
    setMessages((prev) => [...prev, newMsg]);

    // Simulated system response
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          text: "🩺 Noted! The patient details have been updated successfully.",
        },
      ]);
    }, 700);

    setInput("");
  };

  const handleNewChat = () => {
    setMessages([{ sender: "bot", text: "🆕 New consultation started!" }]);
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
          + New Consultation
        </button>

        <div
          style={{
            flex: 1,
            overflowY: "auto",
            scrollbarWidth: "thin",
          }}
        >
          <h4 style={{ marginBottom: "10px", opacity: 0.8 }}>Patient Chats</h4>
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
            backgroundColor: "#2b2c30",
            borderBottom: "1px solid #565869",
            padding: "15px 20px",
            fontWeight: "600",
            fontSize: "18px",
            textAlign: "center",
            color: "#42e6a4",
          }}
        >
          CuraAI Doctor Portal
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
                alignSelf:
                  msg.sender === "doctor" ? "flex-end" : "flex-start",
                backgroundColor:
                  msg.sender === "doctor" ? "#0077ff" : "#444654",
                color: msg.sender === "doctor" ? "#fff" : "#ececf1",
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
            placeholder="Write a response..."
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
              backgroundColor: "#0077ff",
              color: "#fff",
              border: "none",
              borderRadius: "20px",
              padding: "12px 20px",
              fontWeight: "600",
              cursor: "pointer",
              transition: "background 0.2s",
            }}
            onMouseEnter={(e) => (e.currentTarget.style.background = "#0062d6")}
            onMouseLeave={(e) => (e.currentTarget.style.background = "#0077ff")}
          >
            Send
          </button>
        </form>
      </main>
    </div>
  );
}

export default DoctorChatPage;
