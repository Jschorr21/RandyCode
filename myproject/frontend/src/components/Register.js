import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

function Register({ onRegister }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate(); // 👈 Add this

  const handleRegister = async (e) => {
    e.preventDefault();

    const response = await fetch(`http://${window.location.hostname}:8000/api/users/register/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    const data = await response.json();

    if (response.ok) {
      alert("Registration successful! Redirecting to chat...");
      onRegister();           // optional cleanup logic
      navigate("/chat");      // 👈 Redirect to main page
    } else {
      alert(data.error || "Registration failed.");
    }
  };

  return (
    <form onSubmit={handleRegister}>
      <h2>Register (.edu only)</h2>
      <input
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Your .edu Email"
      />
      <input
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        type="password"
        placeholder="Password"
      />
      <button type="submit">Register</button>
    </form>
  );
}

export default Register;
