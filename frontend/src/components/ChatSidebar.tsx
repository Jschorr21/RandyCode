import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { ChevronLeft, Plus, MoreVertical, Trash } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { useToast } from "@/hooks/use-toast";
import { cn } from "@/lib/utils";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

interface ChatHistory {
  id: string;
  title: string;
  created_at: string;
}

interface ChatSidebarProps {
  onChatSelect: (chatId: string | null) => void;
  currentChatId: string | null;
  onToggleCollapse: (isCollapsed: boolean) => void;
}

const ChatSidebar = ({ onChatSelect, currentChatId, onToggleCollapse }: ChatSidebarProps) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [chatHistories, setChatHistories] = useState<ChatHistory[]>([]);
  const { user } = useAuth();
  const { toast } = useToast();

  useEffect(() => {
    if (user) fetchChatHistories();
  }, [user]);

  const fetchChatHistories = async () => {
    try {
      const token = localStorage.getItem("access");
      const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/chatapp/`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!res.ok) throw new Error("Failed to fetch");

      const data = await res.json();

      if (!Array.isArray(data)) {
        console.error("Expected array but got:", data);
        setChatHistories([]); // fallback to avoid crash
        return;
      }

      setChatHistories(data); // ✅ safe to call .map()

    } catch (error) {
      toast({
        title: "Error fetching chat history",
        description: "Please try again later",
        variant: "destructive",
      });
    }
  };

  const deleteChat = async (chatId: string) => {
    try {
      const token = localStorage.getItem("access");
      const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/chatapp/${chatId}/`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!res.ok) throw new Error("Failed to delete");

      if (currentChatId === chatId) {
        onChatSelect(null);
      }

      setChatHistories(prev => prev.filter(chat => chat.id !== chatId));

      toast({
        title: "Chat deleted successfully",
      });
    } catch (error) {
      toast({
        title: "Error deleting chat",
        description: "Please try again later",
        variant: "destructive",
      });
    }
  };

  const createNewChat = () => {
    onChatSelect(null);
  };

  const handleCollapse = () => {
    setIsCollapsed(!isCollapsed);
    onToggleCollapse(!isCollapsed);
  };

  return (
    <div
      className={`bg-white border-r border-gray-200 transition-all duration-300 ease-in-out ${
        isCollapsed ? "w-16" : "w-64"
      } h-screen fixed left-0 top-0 flex flex-col`}
    >
      <div className="flex items-center justify-between p-2 border-b">
        <Button
          variant="ghost"
          size="icon"
          onClick={handleCollapse}
          className="hover:bg-gray-100"
        >
          <ChevronLeft
            className={`h-4 w-4 transition-transform ${
              isCollapsed ? "rotate-180" : ""
            }`}
          />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          onClick={createNewChat}
          className="hover:bg-gray-100"
        >
          <Plus className="h-4 w-4" />
        </Button>
      </div>

      <div className="flex-1 overflow-y-auto">
        {!isCollapsed && (
          <div className="p-2 space-y-1">
            {chatHistories.map((chat) => (
              <div
                key={chat.id}
                className={cn(
                  "flex items-center justify-between group",
                  currentChatId === chat.id && "bg-gray-100 rounded-lg"
                )}
              >
                <Button
                  variant="ghost"
                  className="w-[85%] justify-start text-sm truncate h-auto py-2"
                  onClick={() => onChatSelect(chat.id)}
                >
                  {chat.title || "Untitled Chat"}
                </Button>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8 opacity-0 group-hover:opacity-100"
                    >
                      <MoreVertical className="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem
                      onClick={() => deleteChat(chat.id)}
                      className="text-red-600"
                    >
                      <Trash className="h-4 w-4 mr-2" />
                      Delete chat
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatSidebar;
