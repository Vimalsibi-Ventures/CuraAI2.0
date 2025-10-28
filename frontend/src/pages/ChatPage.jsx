import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { PlusCircle, User, MessageSquare } from "lucide-react";

function ChatPage() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [chats, setChats] = useState(["General Chat"]);
  const [activeChat, setActiveChat] = useState("General Chat");
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    setMessages((prev) => [...prev, { sender: "user", text: input }]);
    setInput("");
  };

  const handleNewChat = () => {
    const newChatName = `Chat ${chats.length + 1}`;
    setChats([...chats, newChatName]);
    setActiveChat(newChatName);
    setMessages([]);
  };

  return (
    <div
      style={{
        height: "100vh",
        width: "100vw",
        display: "flex",
        backgroundColor: "#0e0f12",
        color: "#e5e7eb",
        fontFamily: "Inter, system-ui, sans-serif",
        overflow: "hidden",
      }}
    >
      {/* Sidebar */}
      <aside
        style={{
          width: "260px",
          background: "rgba(20, 20, 25, 0.9)",
          borderRight: "1px solid rgba(255,255,255,0.06)",
          display: "flex",
          flexDirection: "column",
          padding: "20px",
          gap: "24px",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "10px",
          }}
        >
          <MessageSquare color="#10a37f" size={22} />
          <h2
            style={{
              fontSize: "18px",
              fontWeight: "600",
              color: "#f3f4f6",
            }}
          >
            CuraAI Chats
          </h2>
        </div>

        <button
          onClick={handleNewChat}
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "8px",
            background: "#10a37f",
            border: "none",
            borderRadius: "10px",
            padding: "10px 0",
            fontWeight: "600",
            color: "#fff",
            cursor: "pointer",
            transition: "background 0.3s",
          }}
          onMouseEnter={(e) => (e.currentTarget.style.background = "#0f8c6b")}
          onMouseLeave={(e) => (e.currentTarget.style.background = "#10a37f")}
        >
          <PlusCircle size={18} />
          New Chat
        </button>

        {/* Chat list */}
        <div
          style={{
            flex: 1,
            overflowY: "auto",
            display: "flex",
            flexDirection: "column",
            gap: "10px",
            paddingRight: "5px",
          }}
        >
          {chats.map((chat, i) => (
            <motion.div
              key={i}
              whileHover={{ scale: 1.02 }}
              onClick={() => {
                setActiveChat(chat);
                setMessages([]);
              }}
              style={{
                background:
                  chat === activeChat
                    ? "rgba(16,163,127,0.2)"
                    : "rgba(255,255,255,0.03)",
                borderRadius: "10px",
                padding: "10px 14px",
                cursor: "pointer",
                color: chat === activeChat ? "#10a37f" : "#9ca3af",
                fontWeight: chat === activeChat ? "600" : "500",
                border:
                  chat === activeChat
                    ? "1px solid rgba(16,163,127,0.4)"
                    : "1px solid transparent",
              }}
            >
              {chat}
            </motion.div>
          ))}
        </div>
      </aside>

      {/* Main Chat Section */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column" }}>
        {/* Header */}
        <header
          style={{
            flexShrink: 0,
            background: "rgba(20, 20, 25, 0.85)",
            borderBottom: "1px solid rgba(255,255,255,0.06)",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            padding: "18px 40px",
            position: "fixed",
            top: 0,
            left: "260px",
            right: 0,
            zIndex: 50,
          }}
        >
          <h1
            style={{
              fontSize: "22px",
              fontWeight: "600",
              color: "#f3f4f6",
            }}
          >
            💬 {activeChat}
          </h1>

          <button
            onClick={() => navigate("/profile")}
            style={{
              display: "flex",
              alignItems: "center",
              gap: "8px",
              background: "transparent",
              border: "1px solid rgba(255,255,255,0.1)",
              borderRadius: "8px",
              color: "#e5e7eb",
              padding: "8px 16px",
              fontWeight: "500",
              cursor: "pointer",
              fontSize: "14px",
              transition: "all 0.2s ease",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = "rgba(255,255,255,0.05)";
              e.currentTarget.style.borderColor = "rgba(255,255,255,0.2)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = "transparent";
              e.currentTarget.style.borderColor = "rgba(255,255,255,0.1)";
            }}
          >
            <User size={16} /> My Profile
          </button>
        </header>

        {/* Chat Area */}
        <main
          style={{
            flex: 1,
            padding: "100px 30px 20px",
            display: "flex",
            flexDirection: "column",
            justifyContent: "space-between",
          }}
        >
          <motion.div
            layout
            style={{
              flexGrow: 1,
              overflowY: "auto",
              padding: "20px",
              background: "rgba(255,255,255,0.03)",
              borderRadius: "14px",
              marginBottom: "20px",
              display: "flex",
              flexDirection: "column",
              gap: "14px",
              boxShadow: "inset 0 0 20px rgba(0,0,0,0.2)",
            }}
          >
            {messages.length === 0 ? (
              <p style={{ opacity: 0.5, textAlign: "center", marginTop: "20px" }}>
                Start chatting in <strong>{activeChat}</strong> 💬
              </p>
            ) : (
              messages.map((msg, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                  style={{
                    alignSelf: msg.sender === "user" ? "flex-end" : "flex-start",
                    background:
                      msg.sender === "user"
                        ? "linear-gradient(135deg, #10a37f, #0e8c6b)"
                        : "rgba(255,255,255,0.08)",
                    color: "#f9fafb",
                    padding: "12px 18px",
                    borderRadius:
                      msg.sender === "user"
                        ? "16px 16px 4px 16px"
                        : "16px 16px 16px 4px",
                    maxWidth: "70%",
                    fontSize: "15px",
                    boxShadow:
                      msg.sender === "user"
                        ? "0 2px 10px rgba(16,163,127,0.3)"
                        : "0 2px 8px rgba(0,0,0,0.2)",
                  }}
                >
                  {msg.text}
                </motion.div>
              ))
            )}
          </motion.div>

          {/* Input Box */}
          <form
            onSubmit={handleSubmit}
            style={{
              display: "flex",
              alignItems: "center",
              background: "rgba(255,255,255,0.04)",
              borderRadius: "14px",
              border: "1px solid rgba(255,255,255,0.07)",
              padding: "10px 15px",
            }}
          >
            <input
              type="text"
              placeholder="Type your message..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              style={{
                flex: 1,
                background: "transparent",
                border: "none",
                color: "#fff",
                outline: "none",
                fontSize: "15px",
                padding: "10px",
              }}
            />
            <button
              type="submit"
              style={{
                background: "#10a37f",
                color: "#fff",
                border: "none",
                borderRadius: "8px",
                padding: "8px 18px",
                fontWeight: "600",
                cursor: "pointer",
                transition: "background 0.2s ease",
              }}
              onMouseEnter={(e) => (e.currentTarget.style.background = "#0f8c6b")}
              onMouseLeave={(e) => (e.currentTarget.style.background = "#10a37f")}
            >
              Send
            </button>
          </form>
        </main>
      </div>
    </div>
  );
}

export default ChatPage;
