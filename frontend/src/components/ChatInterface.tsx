
import { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Search, Upload, X, ArrowUp } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { cn } from "@/lib/utils";
import { useAuth } from "@/contexts/AuthContext";
import { fetchWithAuth } from "@/lib/fetchWithAuth"; // at the top
import ReactMarkdown from "react-markdown";


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
  sidebarRef: React.RefObject<{ moveChatToTop: (chatId: string) => void }>;
}

const ChatInterface = ({ currentChatId, setCurrentChatId, onFirstMessage, sidebarRef }: ChatInterfaceProps) => {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [uploadedFile, setUploadedFile] = useState<UploadedFile | null>(null);
  const { toast } = useToast();
  const { user } = useAuth();
  const bottomRef = useRef<HTMLDivElement | null>(null);
  const [isSending, setIsSending] = useState(false);


  useEffect(() => {
    if (currentChatId) {
      fetchMessages();
    } else {
      setMessages([]);
    }
  }, [currentChatId]);

  useEffect(() => {
    if (!currentChatId) {
      setMessages([]);
    }
  }, [currentChatId]);

  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);
  

  const fetchMessages = async () => {
    if (!currentChatId || !user) return;
  
    try {
      const res = await fetchWithAuth(`${import.meta.env.VITE_API_BASE_URL}/api/chatapp/${currentChatId}/messages/`);
  
      if (!res.ok) throw new Error("Failed to fetch messages");
  
      const data = await res.json();
      console.log("[fetchMessages for]", currentChatId);
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
  

  const handleSendMessage = async (overrideMessage?: string) => {
    if (isSending) return; // prevent double-call
    setIsSending(true);
  
    try {
      const messageToSend = overrideMessage ?? message;
      if ((!messageToSend.trim() && !uploadedFile) || !user) return;
  
      const messageContent = uploadedFile
        ? `${messageToSend}\n[File: ${uploadedFile.name}]`
        : messageToSend;
  
      let chatId = currentChatId;
      const isFirstMessage = messages.length === 0;
  
      // 💥 Only create chat ONCE
      if (!chatId) {
        const res = await fetchWithAuth(`${import.meta.env.VITE_API_BASE_URL}/api/chatapp/`, {
          method: "POST",
          body: JSON.stringify({ session_id: crypto.randomUUID() }),
        });
  
        if (!res.ok) throw new Error("Failed to create chat");
        const data = await res.json();
        chatId = data.id;
        setCurrentChatId(chatId);
      }
  
      const userMessageObj: Message = {
        id: `${Date.now()}-user`,
        role: "user",
        content: messageContent,
        created_at: new Date().toISOString(),
      };
  
      const typingMessageId = `${Date.now()}-bot`;
      const typingIndicator: Message = {
        id: typingMessageId,
        role: "bot",
        content: "",
        created_at: new Date().toISOString(),
      };
  
      setMessages((prev) => [...prev, userMessageObj, typingIndicator]);
      setMessage("");
      setUploadedFile(null);
  
      // 🧠 Always use local `chatId`, never rely on currentChatId
      const res = await fetchWithAuth(
        `${import.meta.env.VITE_API_BASE_URL}/api/chatapp/chatbot/stream/`,
        {
          method: "POST",
          body: JSON.stringify({ message: messageContent, session_id: chatId }),
        }
      );
  
      if (!res.body) throw new Error("No stream available");
  
      const reader = res.body.getReader();
      const decoder = new TextDecoder("utf-8");
  
      let botResponse = "";
  
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        botResponse += chunk;
  
        setMessages((prev) =>
          prev.map((m) =>
            m.id === typingMessageId ? { ...m, content: botResponse } : m
          )
        );
      }
  
      await fetchWithAuth(`${import.meta.env.VITE_API_BASE_URL}/api/chatapp/store_message/`, {
        method: "POST",
        body: JSON.stringify({
          session_id: chatId,
          user_message: messageContent,
          bot_response: botResponse,
        }),
      });
  
      sidebarRef.current?.moveChatToTop(chatId);
      setMessages([]);
      await fetchMessages();
  
    } catch (error) {
      console.error("❌ Error sending message:", error);
      toast({
        title: "Error sending message",
        description: "Please try again later",
        variant: "destructive",
      });
      setMessages((prev) => prev.filter((m) => m.role !== "bot")); // clean up bot
    } finally {
      setIsSending(false);
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
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                  <Button
                    variant="outline"
                    onClick={() => {
                      setMessage("Recommend me some liberal arts electives");
                      handleSendMessage("Recommend me some liberal arts electives");
                    }}
                    className="w-full h-full text-center flex items-center justify-center whitespace-normal break-words transition-all duration-200 ease-in-out hover:shadow-lg hover:-translate-y-1"
                  >
                    Recommend me some liberal arts electives
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => {
                      setMessage("What are the requirements for the computer science major?");
                      handleSendMessage("What are the requirements for the computer science major?");
                    }}
                    className="w-full h-full text-center flex items-center justify-center whitespace-normal break-words transition-all duration-200 ease-in-out hover:shadow-lg hover:-translate-y-1"
                  >
                    What are the requirements for the computer science major?
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => {
                      setMessage("What does CS 2100 cover and are the prerequisites?");
                      handleSendMessage("What does CS 2100 cover and are the prerequisites?");
                    }}
                    className="w-full h-full text-center flex items-center justify-center whitespace-normal break-words transition-all duration-200 ease-in-out hover:shadow-lg hover:-translate-y-1"
                  >
                    What does CS 2100 cover and are the prerequisites?
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => {
                      setMessage("When is the commencement ceremony this year?");
                      handleSendMessage("When is the commencement ceremony this year?");
                    }}
                    className="w-full h-full text-center flex items-center justify-center whitespace-normal break-words transition-all duration-200 ease-in-out hover:shadow-lg hover:-translate-y-1"
                  >
                    When is the commencement ceremony this year?
                  </Button>
                </div>

              </div>
            </div>
          )}

          {messages.map((msg) => {
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
                  msg.role === "bot" ? (
                    <div className="prose max-w-none whitespace-pre-wrap custom-markdown">
                      <ReactMarkdown>{msg.content}</ReactMarkdown>
                    </div>

                  ) : (
                    <p className="whitespace-pre-wrap">{msg.content}</p>
                  )
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
