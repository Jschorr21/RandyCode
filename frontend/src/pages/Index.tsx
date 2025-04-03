
import { useState } from "react";
import ChatSidebar from "@/components/ChatSidebar";
import ChatInterface from "@/components/ChatInterface";
import TopNav from "@/components/TopNav";
import { useAuth } from "@/contexts/AuthContext";

const Index = () => {
  const [currentChatId, setCurrentChatId] = useState<string | null>(null);
  const [isSidebarClosed, setIsSidebarClosed] = useState(false);
  const { user } = useAuth();

  return (
    <div className="flex min-h-screen bg-gray-50 transition-all duration-300 ease-in-out">
      <ChatSidebar 
        onChatSelect={setCurrentChatId} 
        currentChatId={currentChatId} 
        onToggleCollapse={setIsSidebarClosed} 
      />

      <div 
        className={`transition-all duration-300 ease-in-out ${
          isSidebarClosed ? "ml-16" : "ml-64"
        } flex-1 flex flex-col`}
      >
        <TopNav />
        
        <div className="flex-1 pt-16 flex justify-center">
          <div className="w-full max-w-4xl">
            <ChatInterface 
              currentChatId={currentChatId}
              setCurrentChatId={setCurrentChatId}
              onFirstMessage={(chatId, message) => {
                const updateChatTitle = async (chatId: string, title: string) => {
                  try {
                    const token = localStorage.getItem("access");
                    const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/chatapp/${chatId}/`, {
                      method: "PATCH",
                      headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${token}`,
                      },
                      body: JSON.stringify({ title }),
                    });
              
                    if (!res.ok) throw new Error("Failed to update title");
                  } catch (err) {
                    console.error("Error updating chat title:", err);
                  }
                };
              
                updateChatTitle(chatId, message.slice(0, 50) + (message.length > 50 ? "..." : ""));
              }}              
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Index;
