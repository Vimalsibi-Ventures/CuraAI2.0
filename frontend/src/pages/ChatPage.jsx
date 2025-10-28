import React, { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { PlusCircle, User, MessageSquare, Loader2, FileDown, BrainCircuit } from "lucide-react";
import api from "../services/api.js"; // 👈 FIXED: Added .js
// 👇 FIXED: Added .jsx and .js extensions
import ReportDisplay from "../components/ReportDisplay.jsx"; 
import { downloadReportTxt } from "../utils/downloadReport.js";
import HospitalFinder from "../components/HospitalFinder.jsx"; // 👈 FIXED: Added .jsx

// Helper component for loading spinner
const LoadingSpinner = () => (
  <motion.div
    animate={{ rotate: 360 }}
    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
    style={{ display: 'inline-block', marginLeft: '10px' }}
  >
    <Loader2 size={18} />
  </motion.div>
);

function ChatPage() {
  // --- STATE ---
  const [messages, setMessages] = useState([]); // Holds { role, content, sources? }
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [reportData, setReportData] = useState(null); // Holds { diseases: [], questions: [] }
  const [showReportButton, setShowReportButton] = useState(false);
  const [sessionId, setSessionId] = useState(null); // Stores the session ID from the API
  const chatEndRef = useRef(null); // For auto-scrolling

  // --- "5-Input Unlock" Logic ---
  useEffect(() => {
    const userMessageCount = messages.filter((m) => m.role === 'user').length;
    if (userMessageCount >= 5 && !reportData) {
      setShowReportButton(true);
    } else {
      setShowReportButton(false);
    }
  }, [messages, reportData]);

  // --- Auto-scroll Logic ---
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading, reportData]);


  // --- API FUNCTIONS ---

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = { role: "user", content: input };
    const newMessages = [...messages, userMessage];
    
    setMessages(newMessages);
    setInput("");
    setIsLoading(true);

    try {
      // Send the user message AND the full history
      const response = await api.postChatMessage(input, messages, sessionId);
      
      const aiMessage = {
        role: "assistant",
        content: response.answer,
        sources: response.sources || [],
      };
      
      setMessages([...newMessages, aiMessage]);
      setSessionId(response.session_id); // Save the session ID from the response

    } catch (error) {
      console.error("Error posting chat message:", error);
      const errorMessage = {
        role: "assistant",
        content: "Sorry, I ran into an error. Please try again.",
      };
      setMessages([...newMessages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateReport = async () => {
    if (isLoading) return;
    setIsLoading(true);
    setShowReportButton(false); // Hide button after click

    try {
      // Send the ENTIRE message history to the report API
      const response = await api.generateReport(messages);
      
      setReportData({
        diseases: response.disease_list,
        questions: response.question_list,
      });

    } catch (error) {
      console.error("Error generating report:", error);
      const errorMessage = {
        role: "assistant",
        content: "There was an error generating your report. Please try again.",
      };
      setMessages([...messages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // --- UI FUNCTIONS ---

  const handleNewChat = () => {
    // This is now a "Reset" button
    setMessages([]);
    setInput("");
    setReportData(null);
    setShowReportButton(false);
    setSessionId(null);
    setIsLoading(false);
  };

  const handleDownloadReport = () => {
    if (reportData) {
      downloadReportTxt(reportData);
    }
  };

  // --- RENDER ---
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
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <BrainCircuit color="#10a37f" size={22} />
          <h2 style={{ fontSize: "18px", fontWeight: "600", color: "#f3f4f6" }}>
            CuraAI
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
          New Session
        </button>
        
        {/* --- NEW: Task 3.3 --- */}
        <HospitalFinder />
        
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
            width: 'calc(100% - 260px)', // Account for sidebar
            position: "fixed",
            top: 0,
            left: "260px",
            zIndex: 50,
          }}
        >
          <h1 style={{ fontSize: "22px", fontWeight: "600", color: "#f3f4f6" }}>
            💬 Symptom Analysis
          </h1>
          
          {/* "5-Input Unlock" Button Render */}
          {showReportButton && !reportData && !isLoading && (
            <motion.button
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              onClick={handleGenerateReport}
              style={{
                display: "flex", alignItems: "center", gap: "8px",
                background: "#10a37f", border: "none", borderRadius: "10px",
                padding: "10px 16px", fontWeight: "600", color: "#fff",
                cursor: "pointer",
              }}
            >
              <FileDown size={18} />
              Generate Report
            </motion.button>
          )}

          {/* Download Button (after report is generated) */}
          {reportData && (
            <motion.button
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              onClick={handleDownloadReport}
              style={{
                display: "flex", alignItems: "center", gap: "8px",
                background: "#0f8c6b", border: "none", borderRadius: "10px",
                padding: "10px 16px", fontWeight: "600", color: "#fff",
                cursor: "pointer",
              }}
            >
              <FileDown size={18} />
              Download Report
            </motion.button>
          )}

        </header>

        {/* Chat Area */}
        <main
          style={{
            flex: 1,
            padding: "100px 30px 20px",
            display: "flex",
            flexDirection: "column",
            justifyContent: "space-between",
            marginLeft: '260px', // Offset for sidebar
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
            {/* Initial Welcome Message */}
            {messages.length === 0 && !isLoading && (
              <p style={{ opacity: 0.5, textAlign: "center", marginTop: "20px" }}>
                You can ask a factual question (e.g., "What is an MRI?")
                or describe your symptoms (e.g., "I have a bad headache").
              </p>
            )}

            {/* Message Bubbles */}
            {messages.map((msg, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                style={{
                  alignSelf: msg.role === "user" ? "flex-end" : "flex-start",
                  background:
                    msg.role === "user"
                      ? "linear-gradient(135deg, #10a37f, #0e8c6b)"
                      : "rgba(255,255,255,0.08)",
                  color: "#f9fafb",
                  padding: "12px 18px",
                  borderRadius:
                    msg.role === "user"
                      ? "16px 16px 4px 16px"
                      : "16px 16px 16px 4px",
                  maxWidth: "70%",
                  fontSize: "15px",
                  boxShadow:
                    msg.role === "user"
                      ? "0 2px 10px rgba(16,163,127,0.3)"
                      : "0 2px 8px rgba(0,0,0,0.2)",
                }}
              >
                {msg.content}
                
                {/* Render Sources if they exist (for RAG) */}
                {msg.sources && msg.sources.length > 0 && (
                  <div style={{ marginTop: '10px', borderTop: '1px solid rgba(255,255,255,0.2)', paddingTop: '8px', fontSize: '12px', opacity: 0.8 }}>
                    <strong>Sources:</strong>
                    {msg.sources.map((source, idx) => (
                      <a key={idx} href={source.url} target="_blank" rel="noopener noreferrer" style={{ display: 'block', color: '#10a37f', textDecoration: 'underline', marginTop: '4px' }}>
                        {source.name}
                      </a>
                    ))}
                  </div>
                )}
              </motion.div>
            ))}
            
            {/* Render Report Component */}
            {reportData && (
              <ReportDisplay report={reportData} />
            )}

            {/* Loading Indicator */}
            {isLoading && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                style={{ alignSelf: 'flex-start', display: 'flex', alignItems: 'center' }}
              >
                <div style={{ background: "rgba(255,255,255,0.08)", color: "#f9fafb", padding: "12px 18px", borderRadius: "16px 16px 16px 4px" }}>
                  Thinking... <LoadingSpinner />
                </div>
              </motion.div>
            )}

            <div ref={chatEndRef} />
          </motion.div>

          {/* Input Box */}
          <form
            onSubmit={handleSendMessage}
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
              placeholder={isLoading ? "Waiting for response..." : "Type your message..."}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={isLoading}
              style={{
                flex: 1,
                background: "transparent",
                border: "none",
                color: "#fff",
                outline: "none",
                fontSize: "15px",
                padding: "10px",
                cursor: isLoading ? 'not-allowed' : 'text',
              }}
            />
            <button
              type="submit"
              disabled={isLoading}
              style={{
                background: isLoading ? '#555' : '#10a37f',
                color: "#fff",
                border: "none",
                borderRadius: "8px",
                padding: "8px 18px",
                fontWeight: "600",
                cursor: isLoading ? 'not-allowed' : 'pointer',
                transition: "background 0.2s ease",
              }}
              onMouseEnter={(e) => !isLoading && (e.currentTarget.style.background = "#0f8c6b")}
              onMouseLeave={(e) => !isLoading && (e.currentTarget.style.background = "#10a37f")}
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

