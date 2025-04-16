
import { useState } from "react";
import ChatSidebar from "@/components/ChatSidebar";
import ChatInterface from "@/components/ChatInterface";
import TopNav from "@/components/TopNav";
import { useAuth } from "@/contexts/AuthContext";
import { useRef } from "react"; // already imported


const Index = () => {
  const [currentChatId, setCurrentChatId] = useState<string | null>(null);
  const [isSidebarClosed, setIsSidebarClosed] = useState(false);
  const { user } = useAuth();
  const sidebarRef = useRef<{
    moveChatToTop: (chatId: string) => void;
    refreshChatHistories: () => void;
  }>(null);
  

  return (
    <div className="flex min-h-screen bg-gray-50 transition-all duration-300 ease-in-out">
      <ChatSidebar 
        ref={sidebarRef}
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
              onFirstMessage={(chatId) => {
                sidebarRef.current?.refreshChatHistories(); // pulls new chat from backend
                sidebarRef.current?.moveChatToTop(chatId);  // reorders visually
              }}
              sidebarRef={sidebarRef}              
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Index;
