import { useState, useEffect, useRef } from "react";

const Chat = () => {
  const [userMessage, setUserMessage] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [socket, setSocket] = useState(null);
  const chatContainerRef = useRef(null);

  useEffect(() => {
    // ✅ Establish WebSocket connection when component mounts
    const ws = new WebSocket("ws://127.0.0.1:8000/ws/chat/");

    ws.onopen = () => {
      console.log("✅ WebSocket Connected");
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setChatHistory((prev) => [...prev, { role: "bot", content: data.response }]);
      scrollToBottom();
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
    scrollToBottom();
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      sendMessage();
    }
  };

  const scrollToBottom = () => {
    setTimeout(() => {
      chatContainerRef.current?.scrollTo({
        top: chatContainerRef.current.scrollHeight,
        behavior: "smooth",
      });
    }, 100);
  };

  return (
    <div className="flex flex-col h-screen bg-gray-900 text-white">
      {/* Header */}
      <div className="bg-gray-800 p-4 text-center text-lg font-semibold">
        Vanderbilt Course Chatbot
      </div>

      {/* Chat Container */}
      <div
        ref={chatContainerRef}
        className="flex-1 overflow-y-auto p-4 space-y-3"
      >
        {chatHistory.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`px-4 py-2 rounded-lg ${
                msg.role === "user"
                  ? "bg-blue-500 text-white"
                  : "bg-gray-700 text-gray-200"
              } max-w-[75%]`}
            >
              <strong>{msg.role === "user" ? "You" : "Bot"}:</strong> {msg.content}
            </div>
          </div>
        ))}
      </div>

      {/* Input Box */}
      <div className="bg-gray-800 p-4 flex items-center">
        <input
          type="text"
          value={userMessage}
          onChange={(e) => setUserMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type a message..."
          className="flex-1 p-3 bg-gray-700 text-white rounded-lg outline-none"
        />
        <button
          onClick={sendMessage}
          className="ml-2 px-4 py-2 bg-blue-600 rounded-lg hover:bg-blue-500 transition"
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default Chat;
