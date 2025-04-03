
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Search, Upload, X, ArrowUp } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { cn } from "@/lib/utils";
import { useAuth } from "@/contexts/AuthContext";

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
  onFirstMessage: (chatId: string, message: string) => void;
}

const ChatInterface = ({ currentChatId, setCurrentChatId, onFirstMessage }: ChatInterfaceProps) => {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [uploadedFile, setUploadedFile] = useState<UploadedFile | null>(null);
  const { toast } = useToast();
  const { user } = useAuth();

  useEffect(() => {
    if (currentChatId) {
      fetchMessages();
    } else {
      setMessages([]);
    }
  }, [currentChatId]);

  const fetchMessages = async () => {
    if (!currentChatId || !user) return;
  
    try {
      const token = localStorage.getItem("access");
      const res = await fetch(`http://localhost:8000/api/chatapp/${currentChatId}/messages/`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
  
      if (!res.ok) throw new Error("Failed to fetch messages");
  
      const data = await res.json();
      setMessages(data);
    } catch (error) {
      toast({
        title: "Error fetching messages",
        description: "Please try again later",
        variant: "destructive",
      });
    }
  };
  

  const handleSendMessage = async () => {

    console.log("Message:", message);
    console.log("Uploaded file:", uploadedFile);
    console.log("User:", user);

    if ((!message.trim() && !uploadedFile) || !user) {
      console.log("Blocked: no message or no user");
      return;
    }

  
    const token = localStorage.getItem("access");
    const messageContent = uploadedFile
      ? `${message}\n[File: ${uploadedFile.name}]`
      : message;
  
    try {
      let chatId = currentChatId;
  
      // If no chat, create one
      if (!chatId) {
        const res = await fetch("http://localhost:8000/api/chatapp/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ session_id: crypto.randomUUID() }),
        });
  
        if (!res.ok) throw new Error("Failed to create chat");
  
        const data = await res.json();
        chatId = data.id;
        setCurrentChatId(chatId);
      }
  
      // Get AI response
      const chatbotRes = await fetch("http://localhost:8000/api/chatapp/chatbot/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`, // ← add this
        },
        body: JSON.stringify({ message: messageContent }),
      });
  
      const chatbotData = await chatbotRes.json();
      const botResponse = chatbotData.response;
  
      // Store both user + bot messages
      await fetch("http://localhost:8000/api/chatapp/store_message/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          session_id: chatId,
          user_message: messageContent,
          bot_response: botResponse,
        }),
      });
  
      const newMessages = [
        { id: `${Date.now()}-user`, role: "user", content: messageContent, created_at: new Date().toISOString() },
        { id: `${Date.now()}-bot`, role: "bot", content: botResponse, created_at: new Date().toISOString() },
      ];
  
      setMessages((prev) => [...prev, ...newMessages]);
  
      if (messages.length === 0) {
        onFirstMessage(chatId, messageContent.slice(0, 50) + (messageContent.length > 50 ? "..." : ""));
      }
  
      setMessage("");
      setUploadedFile(null);
    } catch (error) {
      console.error("Error sending message:", error);
      toast({
        title: "Error sending message",
        description: "Please try again later",
        variant: "destructive",
      });
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

          {messages.map((msg) => (
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
                <p className="whitespace-pre-wrap">{msg.content}</p>
              </div>
            </div>
          ))}
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
