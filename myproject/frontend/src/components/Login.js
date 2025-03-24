import React, { useState } from "react";

function Login({ onLogin, goToRegister }) {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    const handleLogin = async (e) => {
        e.preventDefault();

        const response = await fetch(`http://${window.location.hostname}:8000/api/users/login/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: email, password }),
        });

        const data = await response.json();

        if (response.ok) {
        localStorage.setItem("access_token", data.access);
        onLogin();
        } else if (data.detail === "No active account found with the given credentials") {
        // assume user not registered
        goToRegister(email);
        } else {
        alert("Login failed.");
        }
    };

    return (
        <form onSubmit={handleLogin}>
        <h2>Login (.edu only)</h2>
        <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Your .edu Email" />
        <input value={password} onChange={(e) => setPassword(e.target.value)} type="password" placeholder="Password" />
        <button type="submit">Login</button>
        </form>
    );
}
  
export default Login;
