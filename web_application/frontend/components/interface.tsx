"use client"

import React, { useState , useRef , useEffect} from 'react';
import { PlusCircle, Paperclip, ArrowUp , X, PenToolIcon as Tool, ChevronLeft,ChevronRight, MessageCircle, FileText, Loader2} from 'lucide-react';
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import ChatInterface from './chatinterface';
import { CustomToolsSidebar } from './custom-tools-sidebar';
import { LeftSidebar } from './leftsidebar';
import { AddToolModal } from './AddToolModal';
import { useRouter } from 'next/navigation';

interface CustomTool {
  id: string;
  name: string;
  description: string;
}

const AgentRAG: React.FC = () => {
  const [inputValue, setInputValue] = useState('');
  const [isLeftSidebarOpen, setIsLeftSidebarOpen] = useState(true);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [isCustomToolsSidebarOpen, setIsCustomToolsSidebarOpen] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([]);
  const [showChatInterface, setShowChatInterface] = useState(false);
  const [customTools, setCustomTools] = useState<CustomTool[]>([]);
  const [toolToDelete, setToolToDelete] = useState<string | null>(null);
  const [showToolsSection, setShowToolsSection] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isLeftSidebarExpanded, setIsLeftSidebarExpanded] = useState(false);
  const [isAddToolModalOpen, setIsAddToolModalOpen] = useState(false);
  const router = useRouter();
  const [chatId, setChatId] = useState<string | null>(null);
  const [uploadingFiles, setUploadingFiles] = useState<Set<string>>(new Set());

  useEffect(() => {
    const createInitialChat = async () => {
      try {
        const response = await fetch('http://localhost:8000/chats', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            title: 'New Chat' // Default title
          })
        });
        
        const chat = await response.json();
        setChatId(chat.id);
      } catch (error) {
        console.error('Error creating initial chat:', error);
      }
    };

    createInitialChat();
  }, []); 

  const fetchCustomTools = async () => {
    if (!chatId) return;
    try {
      const response = await fetch(`http://localhost:8000/chats/${chatId}/tools`);
      if (response.ok) {
        const tools = await response.json();
        setCustomTools(tools);
      } else {
        console.error('Failed to fetch custom tools');
      }
    } catch (error) {
      console.error('Error fetching custom tools:', error);
    }
  };

  const handleDeleteTool = async (id: string) => {
    if (!chatId) return;
    try {
      const response = await fetch(`http://localhost:8000/chats/${chatId}/tools/${id}`, {
        method: 'DELETE',
      });
      if (response.ok) {
        setCustomTools(customTools.filter(tool => tool.id !== id));
      } else {
        console.error('Failed to delete custom tool');
      }
    } catch (error) {
      console.error('Error deleting custom tool:', error);
    }
  };

  const handleSubmit = async () => {
    if (inputValue.trim() && chatId) {
      try {
        router.push(`/chat/${chatId}?query=${encodeURIComponent(inputValue)}`);
      } catch (error) {
        console.error('Error:', error);
      }
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && chatId) {
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        setUploadingFiles(prev => new Set(prev).add(file.name));

        const formData = new FormData();
        formData.append('file', file);

        try {
          // Upload file to storage
          const response = await fetch(`http://localhost:8000/chats/${chatId}/upload`, {
            method: 'POST',
            body: formData,
          });
          const data = await response.json();
  
          // Store file reference in database
          const fileData = {
            filename: data.filename,
            original_filename: file.name,
            file_url: data.file_url
          };
          
          const dbResponse = await fetch(`http://localhost:8000/chats/${chatId}/files`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(fileData),
          });
  
          if (dbResponse.ok) {
            setUploadedFiles(prev => [...prev, data.filename]);
          }
  
          setUploadingFiles(prev => {
            const newSet = new Set(prev);
            newSet.delete(file.name);
            return newSet;
          });
        } catch (error) {
          console.error('Error uploading file:', error);
          setUploadingFiles(prev => {
            const newSet = new Set(prev);
            newSet.delete(file.name);
            return newSet;
          });
        }
      }
    }
  };

  const removeUploadedFile = async (filename: string) => {
    if (!chatId) return;
    try {
      const response = await fetch(`http://localhost:8000/chats/${chatId}/files/${filename}`, {
        method: 'DELETE',
      });
      if (response.ok) {
        setUploadedFiles(prev => prev.filter(file => file !== filename));
      } else {
        console.error('Failed to delete file');
      }
    } catch (error) {
      console.error('Error deleting file:', error);
    }
  };

  const handleNewChat = () => {
    setShowChatInterface(false);
    setInputValue('');
    setUploadedFiles([]);
    setCustomTools([]);
    setIsCustomToolsSidebarOpen(false);
    setShowToolsSection(false);
  };

  const toggleLeftSidebar = () => {
    setIsLeftSidebarOpen(!isLeftSidebarOpen);
    setIsLeftSidebarExpanded(!isLeftSidebarExpanded);
  };

  const toggleCustomToolsSidebar = () => {
    setIsCustomToolsSidebarOpen(!isCustomToolsSidebarOpen);
  };

  const handleToolAdded = () => {
    fetchCustomTools();
  };

  return (
    <div className="flex h-screen bg-white text-gray-900">
      <LeftSidebar
        onNewChat={handleNewChat}
        onToggleToolbox={toggleCustomToolsSidebar}
        isToolboxOpen={isCustomToolsSidebarOpen}
        onToggleSidebar={toggleLeftSidebar}
        currentChatId={chatId}
        onChatSelect={() => {}}
      />

      <div className={`flex-1 flex flex-col justify-center transition-all duration-200 ${
      isLeftSidebarExpanded ? 'ml-48' : isLeftSidebarOpen ? 'ml-16' : 'ml-0'
       }`}>
          <main className="flex-1 overflow-y-auto p-8">
            <h1 className="text-4xl font-bold mb-8 text-center">What can I help you answer?</h1>
            
            <div className="max-w-3xl mx-auto">
              <div className="bg-white border border-gray-200 rounded-lg shadow-sm">
                <div className="p-4">
                  <Input
                    type="text"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    placeholder="Ask a question..."
                    className="w-full text-lg"
                  />
                </div>
                <div className="flex items-center justify-between border-t border-gray-200 p-2">
                  <div className="flex items-center space-x-2">
                    <input
                      type="file"
                      ref={fileInputRef}
                      className="hidden"
                      onChange={handleFileUpload}
                      multiple
                    />
                    <Button variant="ghost" size="icon" onClick={() => fileInputRef.current?.click()}>
                      <Paperclip className="h-5 w-5" />
                    </Button>
                    <Button 
                    onClick={() => setIsAddToolModalOpen(true)}
                    variant="ghost"
                    className="flex items-center gap-3 px-4 py-6 w-full text-gray-600 hover:text-gray-800 hover:bg-gray-50 "
                  >
                    <PlusCircle className="h-5 w-5" />
                    <span className="text-sm font-medium">Add Tool</span>
                  </Button>
                  </div>
                  <Button 
                    variant="default" 
                    size="icon" 
                    className="rounded-full" 
                    onClick={handleSubmit}
                    disabled={!inputValue.trim() || uploadedFiles.length === 0}
                  >
                    <ArrowUp className="h-5 w-5" />
                  </Button>
                </div>
                {(uploadedFiles.length > 0 || uploadingFiles.size > 0) && (
                  <div className="p-4 border-t border-gray-200">
                    <p className="text-sm font-medium text-gray-700 mb-3">Attached files</p>
                    <div className="grid grid-cols-1 gap-2">
                      {/* Loading Files */}
                      {Array.from(uploadingFiles).map((filename) => (
                        <div 
                          key={filename}
                          className="flex items-center justify-between bg-gray-50 rounded-lg p-3"
                        >
                          <div className="flex items-center space-x-3 flex-1">
                            <div className="bg-blue-100 p-2 rounded">
                              <FileText className="h-6 w-6 text-blue-600" />
                            </div>
                            <div className="flex flex-col flex-1">
                              <span className="text-sm font-medium text-gray-700">{filename}</span>
                              <div className="w-full bg-gray-200 rounded-full h-1.5 mt-2">
                                <div className="bg-blue-600 h-1.5 rounded-full animate-pulse w-full"></div>
                              </div>
                            </div>
                            <Loader2 className="h-5 w-5 animate-spin text-blue-600" />
                          </div>
                        </div>
                      ))}
                      
                      {/* Uploaded Files */}
                      {uploadedFiles.map((file, index) => (
                        <div 
                          key={index}
                          className="flex items-center justify-between bg-gray-50 rounded-lg p-3 hover:bg-gray-100 transition-colors"
                        >
                          <div className="flex items-center space-x-3 flex-1">
                            <div className="bg-blue-100 p-2 rounded">
                              <FileText className="h-6 w-6 text-blue-600" />
                            </div>
                            <div className="flex flex-col">
                              <span className="text-sm font-medium text-gray-700">{file}</span>
                              <span className="text-xs text-gray-500">PDF</span>
                            </div>
                          </div>
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            className="hover:bg-gray-200 rounded-full h-8 w-8 p-0"
                            onClick={() => removeUploadedFile(file)}
                          >
                            <X className="h-4 w-4 text-gray-500" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </main>
      </div>
      {isCustomToolsSidebarOpen && (
        <CustomToolsSidebar
          tools={customTools}
          onCollapse={toggleCustomToolsSidebar}
          onDeleteTool={handleDeleteTool}
          chatId={chatId}
        />
      )}
      <AddToolModal 
        isOpen={isAddToolModalOpen}
        onClose={() => setIsAddToolModalOpen(false)}
        onToolAdded={handleToolAdded}
        chatId={chatId}
      />
    </div>
  );
};

export default AgentRAG;

