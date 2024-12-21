import React, { useEffect, useState } from 'react';
import { Button } from "@/components/ui/button"
import { PlusCircle, PenToolIcon as Tool, Menu, ChevronLeft , FileText,
  MessageSquare, Clock
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { ScrollArea } from "@/components/ui/scroll-area"
import { useRouter } from 'next/navigation'

interface RelevantPage {
  title: string;
  content: string;
  relevance_score: number;
}

interface ChatHistoryItem {
  chat_id: string;
  pdf_title: string;
  url: string;
}

interface LeftSidebarProps {
  onNewChat: () => void;
  onToggleToolbox: () => void;
  isToolboxOpen: boolean;
  onToggleSidebar: () => void;
  currentChatId: string | null;
  relevantPages?: RelevantPage[];
  onChatSelect: (chatId: string) => void;
}

export const LeftSidebar: React.FC<LeftSidebarProps> = ({
  onNewChat,
  onToggleToolbox,
  isToolboxOpen,
  onToggleSidebar,
  currentChatId,
  relevantPages = []
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [showPages, setShowPages] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [localChatHistory, setLocalChatHistory] = useState<ChatHistoryItem[]>([]);
  const router = useRouter();

  const fetchChatHistory = async () => {
    try {
      const response = await fetch('http://localhost:8000/chats/history');
      if (!response.ok) {
        throw new Error('Failed to fetch chat history');
      }
      const data = await response.json();
      
      setLocalChatHistory(data.history);
      console.log("Fetched chat history:", data.history);
    } catch (error) {
      console.error('Error fetching chat history:', error);
    }
  };

  const handleChatSelect = (chatId: string) => {
    router.push(`/chat/${chatId}`);
  };



  const toggleExpand = () => {
    setIsExpanded(!isExpanded);
    onToggleSidebar();
  };

  const togglePages = () => {
    setShowPages(!showPages);
    if (!isExpanded) {
      setIsExpanded(true);
      onToggleSidebar();
    }
  };

  const toggleHistory = () => {
    const willShowHistory = !showHistory;
    setShowHistory(willShowHistory);
  
    console.log("Toggle History:", willShowHistory);
  
    if (willShowHistory) {
      console.log("Fetching chat history...");
      fetchChatHistory();
      console.log("Fetched");

    }
  
    if (!isExpanded) {
      setIsExpanded(true);
      onToggleSidebar();
    }
  };
  

  return (
    <div className={`fixed left-0 top-0 bottom-0 bg-gray-900 text-white flex flex-col items-center py-4 z-10 transition-all duration-300 ${isExpanded ? 'w-64' : 'w-16'}`}>
      <Button
        variant="ghost"
        size="icon"
        onClick={toggleExpand}
        className="mb-6 hover:bg-gray-800 w-full flex justify-center"
      >
        {isExpanded ? (
          <div className="flex items-center w-full px-4">
            <ChevronLeft className="h-6 w-6" />
            <span className="ml-2">Collapse</span>
          </div>
        ) : (
          <Menu className="h-6 w-6" />
        )}
      </Button>

      <AnimatePresence>
        <motion.div 
          className="flex flex-col w-full gap-2"
          initial={false}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <Button
            variant="ghost"
            onClick={onNewChat}
            className={`hover:bg-gray-800 w-full flex justify-${isExpanded ? 'start' : 'center'} px-4`}
          >
            <PlusCircle className="h-6 w-6" />
            {isExpanded && <span className="ml-2">New Chat</span>}
          </Button>

          <Button
            variant="ghost"
            onClick={onToggleToolbox}
            className={`hover:bg-gray-800 w-full flex justify-${isExpanded ? 'start' : 'center'} px-4 ${isToolboxOpen ? 'bg-gray-700' : ''}`}
          >
            <Tool className="h-6 w-6" />
            {isExpanded && <span className="ml-2">Tools</span>}
          </Button>
          <Button
            variant="ghost"
            onClick={togglePages}
            className={`hover:bg-gray-800 w-full flex justify-${isExpanded ? 'start' : 'center'} px-4 ${showPages ? 'bg-gray-700' : ''}`}
          >
            <FileText className="h-6 w-6" />
            {isExpanded && <span className="ml-2">Relevant Pages</span>}
          </Button>
          <Button
            variant="ghost"
            onClick={toggleHistory}
            className={`hover:bg-gray-800 w-full flex justify-${isExpanded ? 'start' : 'center'} px-4 ${showHistory ? 'bg-gray-700' : ''}`}
          >
            <MessageSquare className="h-6 w-6" />
            {isExpanded && <span className="ml-2">Chat History</span>}
          </Button>
        </motion.div>
      </AnimatePresence>

      {isExpanded && showPages && relevantPages.length > 0 && (
        <ScrollArea className="w-full mt-4 px-2">
          <div className="space-y-2">
            {relevantPages.map((page, index) => (
              <div
                key={index}
                className="p-2 rounded bg-gray-800 hover:bg-gray-700 cursor-pointer text-sm"
              >
                <div className="font-semibold mb-1">{page.title}</div>
                <div className="text-gray-400 text-xs">
                  Score: {page.relevance_score.toFixed(2)}
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>
      )}

      {isExpanded && showHistory && localChatHistory.length > 0 && (
        <ScrollArea className="w-full mt-4 px-2">
          <div className="space-y-2">
            {localChatHistory.map((chat, index) => (
              <div
                key={index}
                onClick={() => handleChatSelect(chat.chat_id)}
                className={`p-2 rounded hover:bg-gray-700 cursor-pointer text-sm ${
                  currentChatId === chat.chat_id ? 'bg-gray-700' : 'bg-gray-800'
                }`}
              >
                <div className="font-semibold mb-1 truncate">{chat.pdf_title}</div>
                <div className="text-gray-400 text-xs truncate">{chat.url}</div>
              </div>
            ))}
          </div>
        </ScrollArea>
      )}
    </div>
  );
};