import { useState, useEffect, useRef } from "react";

function App() {
  const [userMessage, setUserMessage] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [socket, setSocket] = useState(null);
  const sessionId = useRef(`session-${Date.now()}-${Math.random().toString(36).substring(2, 10)}`);
  const userMessageRef = useRef("");

  useEffect(() => {
    // ✅ Establish WebSocket connection when component mounts
    const ws = new WebSocket("ws://127.0.0.1:8001/ws");

    ws.onopen = () => {
      console.log("✅ WebSocket Connected");
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setChatHistory((prev) => [...prev, { role: "bot", content: data.response }]);
      // Store both user + bot messages in Django
      storeMessageInDjango(sessionId.current, userMessageRef.current, data.response);
    };

    ws.onclose = () => {
      console.log("🔴 WebSocket Disconnected");
    };

    setSocket(ws);

    return () => ws.close(); // ✅ Cleanup WebSocket connection on unmount
  }, []);

  const sendMessage = () => {
    if (!userMessage.trim() || !socket) return;

    userMessageRef.current = userMessage;

    const newMessage = { role: "user", content: userMessage };
    setChatHistory([...chatHistory, newMessage]);

    socket.send(JSON.stringify({ user_message: userMessage, use_agent: false }));
    setUserMessage("");
  };

  const storeMessageInDjango = async (sessionId, userMessage, botResponse) => {
    try {
      await fetch("http://127.0.0.1:8000/api/chatapp/store_message/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          user_message: userMessage,
          bot_response: botResponse,
        }),
      });
    } catch (err) {
      console.error("❌ Failed to store chat:", err);
    }
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
      <form
        onSubmit={(e) => {
          e.preventDefault(); // Prevents page refresh
          sendMessage();
        }}
      >
        <input
          type="text"
          value={userMessage}
          onChange={(e) => setUserMessage(e.target.value)}
          placeholder="Type a message..."
          style={{ width: "80%", padding: "10px" }}
        />
        <button type="submit" style={{ padding: "10px" }}>Send</button>
      </form>

    </div>
  );
}

export default App;
