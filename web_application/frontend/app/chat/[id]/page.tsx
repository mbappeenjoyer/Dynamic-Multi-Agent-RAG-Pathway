'use client';

import { useEffect, useState } from 'react';
import ChatInterface from '@/components/chatinterface';
import { LeftSidebar } from '@/components/leftsidebar';
import { useParams, useSearchParams, useRouter } from 'next/navigation';
import { CustomToolsSidebar } from '@/components/custom-tools-sidebar';
import { CustomTool } from '@/types';

interface ChatData {
  id: string;
  title: string;
  files: Array<{
    filename: string;
    original_filename: string;
  }>;
  messages: Array<{
    role: 'user' | 'assistant';
    content: string;
    feedback?: 'positive' | 'negative';
  }>;
}

export default function ChatPage() {
  const params = useParams();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [chatData, setChatData] = useState<ChatData | null>(null);
  const [isToolboxOpen, setIsToolboxOpen] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const initialQuery = searchParams.get('query') || '';
  const [isToolsSidebarOpen, setIsToolsSidebarOpen] = useState(false);
  const [tools, setTools] = useState<CustomTool[]>([]);

  const handleNewChat = () => {
    setChatData(null);
    setTools([]);
    setIsToolboxOpen(false);
    setIsToolsSidebarOpen(false);
    router.push('/');
  };

  useEffect(() => {
    const fetchChat = async () => {
      setIsLoading(true);
      try {
        router.replace(`/chat/${params.id}${initialQuery ? `?query=${initialQuery}` : ''}`);
        const response = await fetch(`http://localhost:8000/chats/${params.id}`);
        if (!response.ok) {
          throw new Error('Failed to fetch chat data');
        }
        const data = await response.json();
        setChatData(data);
      } catch (error) {
        console.error('Error:', error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchChat();
  }, [initialQuery, params.id, router]);


  // if (isLoading) {
  //   return (
  //     <div className="flex h-screen items-center justify-center">
  //       <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-gray-900"></div>
  //     </div>
  //   );
  // }

  return (
    <div className="flex h-screen bg-white">
      <div 
        className={`
          fixed top-0 left-0 h-full z-30
          transition-all duration-300 ease-in-out
          ${isSidebarOpen ? 'w-64' : 'w-14'}
        `}
      >
        <LeftSidebar 
          onNewChat={handleNewChat}
          onToggleToolbox={() => setIsToolsSidebarOpen(!isToolsSidebarOpen)}
          onChatSelect={(chatId) => router.push(`/chat/${chatId}`)}
          isToolboxOpen={isToolsSidebarOpen}
          onToggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
          currentChatId={params.id === 'new' ? null : params.id as string}
        />
      </div>
      
      <div 
        className={`
          flex-1 h-full
          transition-all duration-300 ease-in-out
          ${isSidebarOpen ? 'ml-64' : 'ml-14'}
        `}
      >
        <div className="h-full flex flex-col">
          {chatData && (
            <div className="flex-1">
              <ChatInterface
                initialQuery={initialQuery}
                initialFiles={chatData.files.map(file => file.filename)}
                chatId={params.id as string}
              />
            </div>
          )}
        </div>
      </div>

      {/* Tools Sidebar */}
      {isToolsSidebarOpen && (
        <CustomToolsSidebar
          tools={tools}
          onCollapse={() => setIsToolsSidebarOpen(false)}
          onDeleteTool={() => {}}
          chatId={params.id === 'new' ? null : params.id as string}
        />
      )}
    </div>
  );
} 