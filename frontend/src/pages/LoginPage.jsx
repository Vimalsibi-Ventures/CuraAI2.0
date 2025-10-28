// frontend/src/pages/LoginPage.jsx

import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log("Login attempt:", email, password);
    // No backend for now — so we’ll keep this as a placeholder
  };

  return (
    <div
      className="login-container"
      style={{ maxWidth: "400px", margin: "50px auto", textAlign: "center" }}
    >
      <h2>Login</h2>

      <form
        onSubmit={handleSubmit}
        style={{ display: "flex", flexDirection: "column", gap: "15px" }}
      >
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          style={{ padding: "10px", borderRadius: "6px", border: "1px solid #ccc" }}
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={{ padding: "10px", borderRadius: "6px", border: "1px solid #ccc" }}
        />

        <button
          type="submit"
          style={{
            padding: "10px",
            borderRadius: "6px",
            backgroundColor: "#007bff",
            color: "#fff",
            border: "none",
          }}
        >
          Login
        </button>
      </form>

      {/* ✅ Temporary navigation buttons for testing */}
      <div style={{ marginTop: "20px", display: "flex", flexDirection: "column", gap: "10px" }}>
        <button
          onClick={() => navigate("/chat-user")}
          style={{
            padding: "10px",
            borderRadius: "6px",
            backgroundColor: "#28a745",
            color: "#fff",
            border: "none",
          }}
        >
          Go to User Chat
        </button>

        <button
          onClick={() => navigate("/chat-doctor")}
          style={{
            padding: "10px",
            borderRadius: "6px",
            backgroundColor: "#6f42c1",
            color: "#fff",
            border: "none",
          }}
        >
          Go to Doctor Chat
        </button>
      </div>

      <p style={{ marginTop: "15px" }}>
        Don't have an account?{" "}
        <Link to="/signup" style={{ color: "#007bff" }}>
          Sign Up
        </Link>
      </p>
    </div>
  );
}

export default LoginPage;
