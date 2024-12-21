import React, { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { PlusCircle, PenToolIcon as Tool, ChevronRight, Trash2, Search } from 'lucide-react';
import { Input } from "@/components/ui/input";
import { AddToolModal } from './AddToolModal';

interface CustomTool {
  id: string;
  name: string;
  description: string;
}

interface CustomToolsSidebarProps {
  tools: CustomTool[];
  onCollapse: () => void;
  onDeleteTool: (id: string) => void;
  chatId?: string | null;
}

export const CustomToolsSidebar: React.FC<CustomToolsSidebarProps> = ({
  tools: initialTools,
  onCollapse,
  onDeleteTool,
  chatId
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [hoveredTool, setHoveredTool] = useState<string | null>(null);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [tools, setTools] = useState<CustomTool[]>(initialTools);

  useEffect(() => {
    if (chatId) {
      fetchChatTools();
    }
  }, [chatId]);

  const fetchChatTools = async () => {
    try {
      const response = await fetch(`http://localhost:8000/chats/${chatId}/tools`);
      if (response.ok) {
        const fetchedTools = await response.json();
        setTools(fetchedTools);
      }
    } catch (error) {
      console.error('Error fetching tools:', error);
    }
  };

  const handleToolAdded = async () => {
    if (chatId) {
      await fetchChatTools();
    }
    setIsAddModalOpen(false);
  };

  const handleDeleteTool = async (id: string) => {
    if (chatId) {
      try {
        const response = await fetch(`http://localhost:8000/chats/${chatId}/tools/${id}`, {
          method: 'DELETE',
        });
        if (response.ok) {
          setTools(tools.filter(tool => tool.id !== id));
        }
      } catch (error) {
        console.error('Error deleting tool:', error);
      }
    }
    onDeleteTool(id);
  };

  const filteredTools = tools.filter(tool => 
    tool.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    tool.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="w-80 h-full bg-white border-l border-gray-200 flex flex-col shadow-lg transition-all duration-300">
      <div className="p-6 border-b border-gray-100">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-800">Custom Tools</h2>
          <Button 
            variant="ghost" 
            size="icon" 
            onClick={onCollapse}
            className="hover:bg-gray-100 rounded-full transition-colors duration-200"
          >
            <ChevronRight className="h-5 w-5 text-gray-600" />
          </Button>
        </div>
        
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            type="text"
            placeholder="Search tools..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10 w-full bg-gray-50 border-gray-200 focus:border-blue-300 focus:ring-blue-200 transition-all duration-200"
          />
        </div>
      </div>

      <ScrollArea className="flex-1 px-4">
        <div key={filteredTools.length} className="py-4 space-y-2">
          {filteredTools.map((tool) => (
            <div
              key={tool.id}
              className="relative group"
              onMouseEnter={() => setHoveredTool(tool.id)}
              onMouseLeave={() => setHoveredTool(null)}
            >
              <div className={`
                p-4 rounded-lg
                transition-all duration-200
                ${hoveredTool === tool.id ? 'bg-blue-50' : 'bg-gray-50'}
                hover:shadow-md
                cursor-pointer
              `}>
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-3">
                    <Tool className={`
                      h-5 w-5 transition-colors duration-200
                      ${hoveredTool === tool.id ? 'text-blue-500' : 'text-gray-500'}
                    `} />
                    <div>
                      <h3 className="font-medium text-gray-800">{tool.name}</h3>
                      <p className="text-sm text-gray-500 mt-1">{tool.description}</p>
                    </div>
                  </div>
                  
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleDeleteTool(tool.id)}
                    className={`
                      opacity-0 group-hover:opacity-100
                      transition-opacity duration-200
                      hover:bg-red-100 hover:text-red-600
                      rounded-full
                    `}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </ScrollArea>

      <div className="p-4 border-t border-gray-100">
        <Button 
          onClick={() => setIsAddModalOpen(true)}
          className="w-full bg-gray-900 hover:bg-gray-800 text-white transition-colors duration-200"
        >
          <div className="flex items-center justify-center gap-2">
            <PlusCircle className="h-5 w-5" />
            <span>Add New Tool</span>
          </div>
        </Button>
      </div>

      <AddToolModal 
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        onToolAdded={handleToolAdded}
        chatId={chatId}
        initialTool={false}
      />
    </div>
  );
};