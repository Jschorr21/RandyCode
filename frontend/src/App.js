import { useState, useEffect } from "react";

function App() {
  const [userMessage, setUserMessage] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [socket, setSocket] = useState(null);

  useEffect(() => {
    // ✅ Establish WebSocket connection when component mounts
    const ws = new WebSocket("ws://127.0.0.1:8000/ws");

    ws.onopen = () => {
      console.log("✅ WebSocket Connected");
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setChatHistory((prev) => [...prev, { role: "bot", content: data.response }]);
    };

    ws.onclose = () => {
      console.log("🔴 WebSocket Disconnected");
    };

    setSocket(ws);

    return () => ws.close(); // ✅ Cleanup WebSocket connection on unmount
  }, []);

  const sendMessage = () => {
    if (!userMessage.trim() || !socket) return;

    const newMessage = { role: "user", content: userMessage };
    setChatHistory([...chatHistory, newMessage]);

    socket.send(JSON.stringify({ user_message: userMessage, use_agent: false }));
    setUserMessage("");
  };

  return (
    <div style={{ padding: "20px", maxWidth: "600px", margin: "auto", alignItems: "center" }}>
      <h2>Vanderbilt Course Chatbot</h2>
      <div style={{ border: "1px solid #ccc", padding: "10px", height: "500px", overflowY: "scroll" }}>
        {chatHistory.map((msg, idx) => (
          <p key={idx} style={{ textAlign: msg.role === "user" ? "right" : "left" }}>
            <strong>{msg.role === "user" ? "You" : "Bot"}:</strong> {msg.content}
          </p>
        ))}
      </div>
      <input
        type="text"
        value={userMessage}
        onChange={(e) => setUserMessage(e.target.value)}
        placeholder="Type a message..."
        style={{ width: "80%", padding: "10px" }}
        onSubmit={sendMessage}
      />
      <button onClick={sendMessage} style={{ padding: "10px" }}>Send</button>
    </div>
  );
}

export default App;
