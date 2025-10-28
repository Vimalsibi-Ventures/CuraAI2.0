import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { User, ArrowLeft, FileText } from "lucide-react";
import { jsPDF } from "jspdf";

function UserProfilePage() {
  const navigate = useNavigate();
  const [editing, setEditing] = useState(false);

  const [userData, setUserData] = useState({
    name: "Harish Kumar",
    age: 24,
    gender: "Male",
    bloodGroup: "B+",
    weight: "68 kg",
    height: "175 cm",
    medicalConditions: "None",
    medications: "Vitamin D supplements",
    allergies: "Peanuts",
    doctorVisits: "3 (Last: 12 Oct 2025)",
  });

  const handleChange = (key, value) => {
    setUserData({ ...userData, [key]: value });
  };

  const handleSave = () => {
    setEditing(false);
    localStorage.setItem("curaai_profile", JSON.stringify(userData));
  };

  const generatePDF = () => {
    const doc = new jsPDF();
    doc.setFont("helvetica", "bold");
    doc.setFontSize(18);
    doc.text("CuraAI - Health Report", 20, 20);
    doc.setFontSize(12);
    doc.setFont("helvetica", "normal");

    let y = 40;
    for (const [key, value] of Object.entries(userData)) {
      doc.text(`${key}: ${value}`, 20, y);
      y += 10;
    }
    doc.save(`${userData.name}_Health_Report.pdf`);
  };

  return (
    <div
      style={{
        backgroundColor: "#0f0f11",
        minHeight: "100vh",
        width: "100vw",
        color: "#e0e0e0",
        display: "flex",
        flexDirection: "column",
      }}
    >
      {/* Top Navigation */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "16px 24px",
          backgroundColor: "#151517",
          borderBottom: "1px solid #222",
          position: "fixed",
          top: 0,
          left: 0,
          right: 0,
          zIndex: 100,
        }}
      >
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => navigate("/chat-user")}
          style={{
            background: "transparent",
            border: "none",
            color: "#10a37f",
            fontWeight: 600,
            display: "flex",
            alignItems: "center",
            cursor: "pointer",
            fontSize: "0.95rem",
          }}
        >
          <ArrowLeft size={20} style={{ marginRight: "6px" }} /> Back to Chat
        </motion.button>

        <h1
          style={{
            fontSize: "1.2rem",
            fontWeight: "600",
            color: "#fff",
          }}
        >
          👤 User Health Profile
        </h1>

        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={generatePDF}
          style={{
            backgroundColor: "#10a37f",
            color: "#fff",
            border: "none",
            borderRadius: "8px",
            padding: "10px 16px",
            display: "flex",
            alignItems: "center",
            cursor: "pointer",
            fontWeight: 600,
            gap: "6px",
          }}
        >
          <FileText size={18} /> Generate Report
        </motion.button>
      </div>

      {/* Main Section */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        style={{
          flex: 1,
          padding: "100px 20px 40px 20px",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        <div
          style={{
            backgroundColor: "#151517",
            padding: "40px",
            borderRadius: "16px",
            boxShadow: "0 4px 30px rgba(0, 0, 0, 0.4)",
            width: "100%",
            maxWidth: "900px",
            border: "1px solid #222",
          }}
        >
          <div style={{ textAlign: "center", marginBottom: "30px" }}>
            <User size={80} color="#10a37f" />
            <h2 style={{ marginTop: "10px", color: "#fff" }}>{userData.name}</h2>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
              gap: "20px",
            }}
          >
            {Object.entries(userData).map(([key, value]) => (
              <div
                key={key}
                style={{
                  backgroundColor: "#0f0f11",
                  border: "1px solid #222",
                  borderRadius: "10px",
                  padding: "16px",
                  transition: "all 0.3s ease",
                }}
              >
                <label
                  style={{
                    fontSize: "0.85rem",
                    color: "#a0a0a0",
                    marginBottom: "6px",
                    textTransform: "capitalize",
                    display: "block",
                  }}
                >
                  {key.replace(/([A-Z])/g, " $1")}
                </label>
                {editing ? (
                  <input
                    value={value}
                    onChange={(e) => handleChange(key, e.target.value)}
                    style={{
                      width: "100%",
                      backgroundColor: "#1b1b1d",
                      border: "1px solid #333",
                      color: "#fff",
                      borderRadius: "6px",
                      padding: "8px 10px",
                    }}
                  />
                ) : (
                  <p style={{ fontSize: "1rem", color: "#e0e0e0" }}>{value}</p>
                )}
              </div>
            ))}
          </div>

          {/* Action Buttons */}
          <div
            style={{
              display: "flex",
              justifyContent: "center",
              gap: "12px",
              marginTop: "30px",
            }}
          >
            {!editing ? (
              <motion.button
                whileHover={{ scale: 1.05 }}
                onClick={() => setEditing(true)}
                style={{
                  backgroundColor: "#10a37f",
                  color: "#fff",
                  border: "none",
                  borderRadius: "8px",
                  padding: "10px 24px",
                  cursor: "pointer",
                  fontWeight: 600,
                }}
              >
                ✏️ Edit Profile
              </motion.button>
            ) : (
              <motion.button
                whileHover={{ scale: 1.05 }}
                onClick={handleSave}
                style={{
                  backgroundColor: "#10a37f",
                  color: "#fff",
                  border: "none",
                  borderRadius: "8px",
                  padding: "10px 24px",
                  cursor: "pointer",
                  fontWeight: 600,
                }}
              >
                💾 Save Changes
              </motion.button>
            )}
          </div>
        </div>
      </motion.div>
    </div>
  );
}

export default UserProfilePage;
