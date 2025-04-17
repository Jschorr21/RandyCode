import { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Search, Upload, X, ArrowUp } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { cn } from "@/lib/utils";
import { useAuth } from "@/contexts/AuthContext";
import { fetchWithAuth } from "@/lib/fetchWithAuth"; // at the top


interface Message {
  id: string;
  content: string;
  role: string;
  created_at: string;
}

interface UploadedFile {
  name: string;
  type: string;
}

interface ChatInterfaceProps {
  currentChatId: string | null;
  setCurrentChatId: (chatId: string | null) => void;
  onFirstMessage: (chatId: string) => void;
  sidebarRef: React.MutableRefObject<{
    moveChatToTop: (chatId: string) => void;
    refreshChatHistories: () => void;
  } | null>;
}

const ChatInterface = ({ currentChatId, setCurrentChatId, onFirstMessage, sidebarRef }: ChatInterfaceProps) => {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [uploadedFile, setUploadedFile] = useState<UploadedFile | null>(null);
  const { toast } = useToast();
  const { user } = useAuth();
  const bottomRef = useRef<HTMLDivElement | null>(null);
  // const [sessionId, setSessionId] = useState<string>(() => {
  //   // Retrieve from localStorage or generate once
  //   return localStorage.getItem("session_id") || generateAndStoreSessionId();
  // });
  
  // function generateAndStoreSessionId() {
  //   const newId = crypto.randomUUID();
  //   localStorage.setItem("session_id", newId);
  //   return newId;
  // }
  

  useEffect(() => {
    if (currentChatId) {
      fetchMessages();
    } else {
      setMessages([]);
    }
  }, [currentChatId]);

  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);
  

  const fetchMessages = async (idOverride?: string) => {
    const id = idOverride || currentChatId;
    // if (!currentChatId || !user) return;
  
    try {
      const res = await fetchWithAuth(`${import.meta.env.VITE_API_BASE_URL}/api/chatapp/${id}/messages/`);
      console.log("📨 Fetching messages for chat ID:", id);
  
      if (!res.ok) throw new Error("Failed to fetch messages");
  
      const data = await res.json();
      console.log("📦 Messages received from backend:", data);
      setMessages(data);
    } catch (error) {
      console.error("❌ Error in fetchMessages:", error);
      toast({
        title: "Error fetching messages",
        description: "Please try again later",
        variant: "destructive",
      });
    }
  };
  

  const handleSendMessage = async () => {
    if ((!message.trim() && !uploadedFile) || !user) {
      console.log("Blocked: no message or no user");
      return;
    }
  
    const messageContent = uploadedFile
      ? `${message}\n[File: ${uploadedFile.name}]`
      : message;
  
    let chatId = currentChatId;
  
    const userMessageObj = {
      id: `${Date.now()}-user`,
      role: "user",
      content: messageContent,
      created_at: new Date().toISOString(),
    };
  
    const typingIndicator = {
      id: `${Date.now()}-typing`,
      role: "bot",
      content: "Typing...",
      created_at: new Date().toISOString(),
    };
  
    try {
      // Display user message and typing indicator immediately
      setMessages((prev) => [...prev, userMessageObj, typingIndicator]);
      setMessage("");
      setUploadedFile(null);

  
      // Create new chat session if necessary
      if (!chatId) {
        
        const res = await fetchWithAuth(`${import.meta.env.VITE_API_BASE_URL}/api/chatapp/`, {
          method: "POST",
          body: JSON.stringify({ sessionId : crypto.randomUUID() }),
        });
  
        if (!res.ok) throw new Error("Failed to create chat");
  
        const data = await res.json();
        chatId = data.id;
        setCurrentChatId(chatId);

        console.log("📤 sending to store_message", {
          session_id: chatId,
          user_message: messageContent,
        });
        
        console.log("🆕 chat created:", data);

        
        await fetchWithAuth(`${import.meta.env.VITE_API_BASE_URL}/api/chatapp/store_message/`, {
          method: "POST",
          body: JSON.stringify({
            session_id: chatId,
            user_message: messageContent,
            bot_response: null, // or omit this field if your backend allows
          }),
        });

        // ✅ Update title from message content
        await fetchWithAuth(`${import.meta.env.VITE_API_BASE_URL}/api/chatapp/${chatId}/`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            title: messageContent.slice(0, 50) + (messageContent.length > 50 ? "..." : ""),
          }),
        });
        
        onFirstMessage(chatId);
        

        // await fetchMessages(chatId);  // <- pass it manually (you’ll need to tweak the function)
      }
      else {
        await fetchWithAuth(`${import.meta.env.VITE_API_BASE_URL}/api/chatapp/store_message/`, {
          method: "POST",
          body: JSON.stringify({
            session_id: chatId,
            user_message: messageContent,
          }),
        });        
      }
  
      // Get AI response
      const chatbotRes = await fetchWithAuth(`${import.meta.env.VITE_API_BASE_URL}/api/chatapp/chatbot/`, {
        method: "POST",
        body: JSON.stringify({ message: messageContent }),
      });
  
      const chatbotData = await chatbotRes.json();
      const botResponse = chatbotData.response;
  
      // Store messages in backend
      await fetchWithAuth(`${import.meta.env.VITE_API_BASE_URL}/api/chatapp/store_message/`, {
        method: "POST",
        body: JSON.stringify({
          session_id: chatId,
          user_message: null,
          bot_response: botResponse,
        }),
      });
  
      // Replace typing indicator with real response
      setMessages((prev) => [
        ...prev.filter((m) => m.id !== typingIndicator.id),
        {
          id: `${Date.now()}-bot`,
          role: "bot",
          content: botResponse,
          created_at: new Date().toISOString(),
        },
      ]);
  
      if (!currentChatId) {
        onFirstMessage(chatId); // no need to pass title, backend owns it
      }      
    } catch (error) {
      console.error("Error sending message:", error);
      toast({
        title: "Error sending message",
        description: "Please try again later",
        variant: "destructive",
      });
      // Remove typing indicator on error
      setMessages((prev) => prev.filter((m) => m.id !== typingIndicator.id));
    }
  };  

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleUpload = () => {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = ".pdf";
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (file) {
        setUploadedFile({
          name: file.name,
          type: file.type,
        });
        toast({
          title: "File uploaded",
          description: `Uploaded: ${file.name}`,
        });
      }
    };
    input.click();
  };

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)]">
      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-3xl mx-auto space-y-6">
          {messages.length === 0 && (
            <div className="text-center">
              <h1 className="text-4xl font-bold mb-8">What can I help with?</h1>
              <div className="space-y-4">
                <div className="flex flex-wrap gap-4 justify-center">
                  <Button variant="outline" className="flex items-center gap-2">
                    Create image
                  </Button>
                  <Button variant="outline" className="flex items-center gap-2">
                    Summarize text
                  </Button>
                  <Button variant="outline" className="flex items-center gap-2">
                    Make a plan
                  </Button>
                  <Button variant="outline" className="flex items-center gap-2">
                    Analyze data
                  </Button>
                </div>
              </div>
            </div>
          )}

          {messages.map((msg) => {
            console.log("🧾 Rendering message:", msg);
            return (
            <div
              key={msg.id}
              className={cn(
                "flex",
                msg.role === 'user' ? "justify-end" : "justify-start"
              )}
            >
              <div
                className={cn(
                  "max-w-[80%] rounded-lg p-4",
                  msg.role === 'user'
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted"
                )}
              >
                {msg.content === "Typing..." ? (
                  <div className="flex gap-1 text-foreground">
                    <span className="animate-bounce">.</span>
                    <span className="animate-bounce delay-100">.</span>
                    <span className="animate-bounce delay-200">.</span>
                  </div>
                ) : (
                  <p className="whitespace-pre-wrap">{msg.content}</p>
                )}
              </div>
            </div>
          )})}
          <div ref={bottomRef} />

        </div>
      </div>

      <div className="p-4">
        <div className="max-w-2xl mx-auto">
          {uploadedFile && (
            <div className="mb-2 p-2 bg-muted rounded-lg flex items-center gap-2">
              <div className="flex-1 flex items-center gap-2">
                <div className="w-8 h-8 bg-pink-200 rounded-lg flex items-center justify-center">
                  <Upload className="w-4 h-4 text-pink-500" />
                </div>
                <span className="text-sm font-medium">{uploadedFile.name}</span>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setUploadedFile(null)}
                className="hover:bg-gray-100"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          )}
          <div className="relative">
            <Input
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="Message ChatGPT..."
              className="pr-32 shadow-lg"
            />
            <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-2">
              <Button
                variant="ghost"
                size="icon"
                onClick={handleUpload}
                className="hover:bg-gray-100"
              >
                <Upload className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="hover:bg-gray-100"
              >
                <Search className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                onClick={handleSendMessage}
                className="hover:bg-gray-100"
              >
                <ArrowUp className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;