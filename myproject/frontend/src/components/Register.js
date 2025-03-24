import React, { useState } from "react";

function Register({ onRegister }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleRegister = async (e) => {
    e.preventDefault();

    const response = await fetch(`http://${window.location.hostname}:8000/api/users/register/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    const data = await response.json();

    if (response.ok) {
      alert("Registration successful! You can now log in.");
      onRegister();
    } else {
      alert(data.error || "Registration failed.");
    }
  };

  return (
    <form onSubmit={handleRegister}>
      <h2>Register (.edu only)</h2>
      <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Your .edu Email" />
      <input value={password} onChange={(e) => setPassword(e.target.value)} type="password" placeholder="Password" />
      <button type="submit">Register</button>
    </form>
  );
}

export default Register;
