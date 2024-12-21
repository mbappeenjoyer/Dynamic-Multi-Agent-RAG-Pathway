'use client'

import React, { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent } from '@/components/ui/card'
import { ThumbsUp, ThumbsDown, Paperclip, PlusCircle, Smile, Frown } from 'lucide-react'
import { AddToolModal } from './AddToolModal'
import { LeftSidebar } from './leftsidebar';
import { useRouter } from 'next/navigation';
import { CustomToolsSidebar } from './custom-tools-sidebar';
import { CustomTool } from '@/types'
import { FeedbackModal } from './FeedbackModal';
import Image from 'next/image';

interface Message {
  role: 'user' | 'assistant'
  content: string
  feedback?: 'positive' | 'negative'
  detailedFeedback?: {
    description: string
    items: Array<{ word: string; meaning: string }>
  }
  isLoading?: boolean
}

interface FeedbackData {
  feedback: string;
  clarification: Array<{ word: string; meaning: string }>;
}

interface ChatInterfaceProps {
  initialQuery: string;
  initialFiles: string[];
  chatId: string;
}

interface FeedbackModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (feedbackData: FeedbackData) => void;
  onRerun: () => void;
}

export default function ChatInterface({ initialQuery, initialFiles, chatId: initialChatId }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  // const [relevantPages, setRelevantPages] = useState<RelevantPage[]>([]);
  const [input, setInput] = useState('')
  const [uploadedFiles, setUploadedFiles] = useState<string[]>(initialFiles);
  const [isAddToolModalOpen, setIsAddToolModalOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();
  const [chatId, setChatId] = useState<string | undefined>(initialChatId);
  const [isCustomToolsSidebarOpen, setIsCustomToolsSidebarOpen] = useState(false);
  const [customTools, setCustomTools] = useState<CustomTool[]>([]);
  const [uploadedFileIds, setUploadedFileIds] = useState<string[]>([]);
  const [activeFeedbackMessage, setActiveFeedbackMessage] = useState<number | null>(null);
  const [isRerunningQuestion, setIsRerunningQuestion] = useState(false);
  const [showToolPrompt, setShowToolPrompt] = useState(false);
  const [showDocstringPrompt, setShowDocstringPrompt] = useState(false);
  const [showDocstringInput, setShowDocstringInput] = useState(false);
  const [docstring, setDocstring] = useState('');
  const [lastQueryBeforeToolAdd, setLastQueryBeforeToolAdd] = useState<string>('');
  const [isAddingTool, setIsAddingTool] = useState(false);
  const [isGeneratingResponse, setIsGeneratingResponse] = useState(false);
  const [showFiles, setShowFiles] = useState(true);
  const [isFeedbackGood, setIsFeedbackGood] = useState<boolean | null>(null);
  const [jargonWords, setJargonWords] = useState<{ word: string; meaning: string }[]>([]);
  const [conversations, setConversations] = useState<[string, string][]>([]);
  const [hasLoadedConversations, setHasLoadedConversations] = useState(false);

  useEffect(() => {
    const handleInitialQuery = async () => {
      if (!initialQuery.trim() || messages.length > 0 || !chatId || chatId !== initialChatId) return;
  
      // Add user message immediately
      const userMessage: Message = { role: 'user', content: initialQuery.trim() };
      const loadingMessage: Message = {
        role: 'assistant',
        content: 'Generating response...',
        isLoading: true,
      };
  
      setMessages([loadingMessage, userMessage]);
  
      try {
        // Save initial user message to database
        if (chatId) {
          await fetch(`http://localhost:8000/chats/${chatId}/messages`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userMessage),
          });
        }
  
        // Simulate AI response
        const aiResponse = await RAGResponse(initialQuery.trim(), chatId || '');
        const assistantMessage: Message = { role: 'assistant', content: aiResponse };
  
        // Update state: replace the loading message with the assistant's response
        setMessages((prevMessages) =>
          prevMessages.map((msg) =>
            msg.isLoading ? assistantMessage : msg
          )
        );
  
        // Save AI response to database
        if (chatId) {
          await fetch(`http://localhost:8000/chats/${chatId}/messages`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(assistantMessage),
          });
        }
      } catch (error) {
        console.error("Error handling initial query:", error);
  
        // Remove the loading message and show error (optional: add an error message)
        setMessages((prevMessages) =>
          prevMessages.filter((msg) => !msg.isLoading)
        );
      }
    };
  
    handleInitialQuery();
  }, [chatId]);

  useEffect(() => {
    const fetchConversations = async () => {
      if (chatId) {
        try {
          const response = await fetch(`http://localhost:8000/chats/${chatId}/get_conversations`);
          const data = await response.json();
          setConversations(data.conversations || []);
          setHasLoadedConversations(true);
        } catch (error) {
          console.error('Error fetching conversations:', error);
        }
      }
    };

    fetchConversations();
  }, [chatId]);
  

  const RAGResponse = async (query: string, chatId: string) => {
    const response = await fetch(`http://localhost:8000/chats/${chatId}/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        text: query,
      }),
    });
    
    const data = await response.json();

    console.log(data.response)

    if(data.response.API_REFLEXTION_FLAG === true){
      setIsAddToolModalOpen(true);
      setLastQueryBeforeToolAdd(query);
    }
    
    if(data.response.RAG_FLAG === true){
      setActiveFeedbackMessage(messages.length - 1);
      setIsFeedbackGood(false);
      // Store jargon words if they exist
      if (data.response.Final_Answer[1].jargon) {
        setJargonWords(data.response.Final_Answer[1].jargon.map((item: any) => ({
          word: item.word,
          meaning: item.meaning || ''
        })));
      }
    }

    if(data.response.API_REFLEXTION_FLAG === false && data.response.RAG_FLAG ===false){
      // Return the value directly without JSON.stringify
      return data.response.Final_Answer;
    }
    if(data.response.API_REFLEXTION_FLAG === true && data.response.RAG_FLAG === false){
      return data.response.Final_Answer || "Sorry, We are unable to answer the question with the available tools. Please provide the tool";
    }
    if(data.response.API_REFLEXTION_FLAG === false && data.response.RAG_FLAG === true){
      return "Current RAG response : " + data.response.Final_Answer[1].func_response;
    }
  };

  const RAGToolResponse = async (query: string, chatId: string) => {
    const response = await fetch(`http://localhost:8000/chats/${chatId}/add_tools`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: query })
    });

    const data = await response.json();

    console.log(data.response)

    return JSON.stringify(data.response);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInput(e.target.value)
  }

  const handleFeedback = (index: number, type: 'positive' | 'negative') => {
    const updatedMessages = [...messages];
    updatedMessages[index].feedback = type;
    setMessages(updatedMessages);

    setIsFeedbackGood(type === 'positive');

   
    setActiveFeedbackMessage(index);
  };

  const handleDetailedFeedback = async (feedback: FeedbackData) => {
    if (!chatId || activeFeedbackMessage === null) return;

    try {
      const lastUserMessage = messages.slice(activeFeedbackMessage)
        .find(msg => msg.role === 'user');

      console.log(lastUserMessage);

      console.log(feedback);

      console.log(JSON.stringify({
        feedback: feedback.feedback,
        clarification: feedback.clarification,
        query: lastUserMessage?.content || '',
        re_evaluate: !isFeedbackGood
      }));

      const response = await fetch(`http://localhost:8000/chats/${chatId}/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          feedback: feedback.feedback,
          clarification: feedback.clarification,
          query: lastUserMessage?.content || '',
          re_evaluate: !isFeedbackGood ? true : false
        }),
      });
      
      console.log(response);
      if (!response.ok) throw new Error('Failed to process feedback');

      const newResponse = await response.json();

      console.log(newResponse.response);

      const updatedMessages = [...messages];
      updatedMessages[activeFeedbackMessage] = {
        ...updatedMessages[activeFeedbackMessage],
        content: JSON.stringify(newResponse.response['Final Answer'])
      };
      setMessages(updatedMessages);

      setActiveFeedbackMessage(null);
    } catch (error) {
      console.error('Error handling feedback:', error);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || !chatId) return;

    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(`http://localhost:8000/chats/${chatId}/upload`, {
                method: 'POST',
                body: formData,
            });
            const data = await response.json();
            
            if (response.ok) {
                setUploadedFiles(prev => [...prev, data.filename]);
            }
        } catch (error) {
            console.error('Error uploading file:', error);
        }
    }
  };

  useEffect(() => {
    const fetchChatFiles = async () => {
      if (!chatId) return;
      
      try {
        const response = await fetch(`http://localhost:8000/chats/${chatId}/files`);
        if (response.ok) {
          const files = await response.json();
          setUploadedFiles(files.map((f: any) => f.filename));
          setUploadedFileIds(files.map((f: any) => f.id));
        }
      } catch (error) {
        console.error('Error fetching chat files:', error);
      }
    };

    const fetchChatTools = async () => {
      if (!chatId) return;
      
      try {
        const response = await fetch(`http://localhost:8000/chats/${chatId}/tools`);
        if (response.ok) {
          const tools = await response.json();
          setCustomTools(tools);
        }
      } catch (error) {
        console.error('Error fetching chat tools:', error);
      }
    };

    fetchChatFiles();
    fetchChatTools();
  }, [chatId]);

  const removeUploadedFile = async (filename: string, index: number) => {
    if (!chatId) return;

    try {
      const fileId = uploadedFileIds[index];
      if (fileId) {
        const response = await fetch(`http://localhost:8000/chats/${chatId}/files/${fileId}`, {
          method: 'DELETE',
        });
        
        if (response.ok) {
          // Update state only if deletion was successful
          setUploadedFiles(prev => prev.filter((_, i) => i !== index));
          setUploadedFileIds(prev => prev.filter((_, i) => i !== index));
        } else {
          console.error('Failed to delete file');
        }
      }
    } catch (error) {
      console.error('Error removing file:', error);
    }
  };

  const handleToolAdded = async () => {
    // Refresh tools after adding a new one
    try {
      const response = await fetch(`http://localhost:8000/chats/${chatId}/tools`);
      if (response.ok) {
        const tools = await response.json();
        setCustomTools(tools);
      }
    } catch (error) {
      console.error('Error fetching tools:', error);
    }
  };

  const handleDeleteTool = async (id: string) => {
    if (!chatId) return;
    try {
      const response = await fetch(`http://localhost:8000/chats/${chatId}/tools/${id}`, {
        method: 'DELETE',
      });
      if (response.ok) {
        setCustomTools(prevTools => prevTools.filter(tool => tool.id !== id));
      } else {
        console.error('Failed to delete tool');
      }
    } catch (error) {
      console.error('Error deleting tool:', error);
    }
  };

  const handleToolPromptResponse = async (response: string) => {
    if (response.toLowerCase().includes('yes')) {
      setIsAddToolModalOpen(true);
    } else {
      setShowToolPrompt(false);
      setShowDocstringPrompt(true);
    }
  };

  const handleDocstringPromptResponse = async (response: string) => {
    if (response.toLowerCase().includes('yes')) {
      // Show docstring input field
      setShowDocstringInput(true);
    } else {
      setShowDocstringPrompt(false);
      // Show final message
      setMessages(prev => [{
        role: 'assistant',
        content: "Sorry, I won't be able to move forward without additional information."
      }, ...prev]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    if (showToolPrompt) {
      await handleToolPromptResponse(input);
      setInput('');
      return;
    }

    if (showDocstringPrompt) {
      await handleDocstringPromptResponse(input);
      setInput('');
      return;
    }

    const userMessage: Message = { role: 'user', content: input.trim() };
    
    // Add user message to state
    setMessages(prevMessages => [userMessage,...prevMessages]);

    // Add loading message
    setMessages(prevMessages => [{
      role: 'assistant',
      content: 'Generating response...',
      isLoading: true
    },...prevMessages]);

    // If no chatId, create new chat
    if (!chatId) {
      const response = await fetch('http://localhost:8000/chats', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          title: input.trim().slice(0, 50) // Use first 50 chars as title
        })
      });
      const chat = await response.json();
      setChatId(chat.id);
      router.push(`/chat/${chat.id}`);
    }

    // Save message to database
    await fetch(`http://localhost:8000/chats/${chatId}/messages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userMessage)
    });

    try {
      const aiResponse = await RAGResponse(input.trim(), chatId || '');
      const assistantMessage: Message = { role: 'assistant', content: aiResponse };

      // Remove loading message and add actual response
      setMessages(prevMessages => {
        const messagesWithoutLoading = prevMessages.filter(msg => !msg.isLoading);
        return [assistantMessage,...messagesWithoutLoading];
      });

      // Save AI response to database
      await fetch(`http://localhost:8000/chats/${chatId}/messages`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(assistantMessage)
      });
    } catch (error) {
      console.error('Error generating response:', error);
      // Remove loading message and show error
      setMessages(prevMessages => { 
        const messagesWithoutLoading = prevMessages.filter(msg => !msg.isLoading);
        return messagesWithoutLoading;
      });
    }

    setInput('');
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const toggleCustomToolsSidebar = () => {
    setIsCustomToolsSidebarOpen(!isCustomToolsSidebarOpen);
  };

  const handleNoToolsProvided = () => {
    setMessages(prev => [{
      role: 'assistant',
      content: "Sorry, I won't be able to move forward without any tool information. Would you like to try adding a tool again?"
    }, ...prev]);
  };

  const handleToolAddedAndRerun = async () => {
    if (lastQueryBeforeToolAdd && chatId) {
      setIsGeneratingResponse(true);
      setIsAddToolModalOpen(false);
      
      // Find the last assistant message index
      const lastAssistantIndex = messages.findIndex(msg => msg.role === 'assistant');
      
      // Update the existing assistant message with loading state
      if (lastAssistantIndex !== -1) {
        setMessages(prevMessages => {
          const updatedMessages = [...prevMessages];
          updatedMessages[lastAssistantIndex] = {
            role: 'assistant',
            content: 'Creating new tool...',
            isLoading: true
          };
          return updatedMessages;
        });
      }

      try {
        const aiResponse = await RAGToolResponse(lastQueryBeforeToolAdd, chatId);
        const parsedResponse = JSON.parse(aiResponse);

        console.log(parsedResponse);

        // Update the existing assistant message with the new response
        if (lastAssistantIndex !== -1) {
          setMessages(prevMessages => {
            const updatedMessages = [...prevMessages];
            
            if (parsedResponse === 'DOC_INVALID') {
              updatedMessages[lastAssistantIndex] = {
                role: 'assistant',
                content: 'Please provide the docstring for the tool.',
                isLoading: false
              };
              setIsAddToolModalOpen(true);
            } 
            else if (parsedResponse === 'NAME_INVALID') {
              updatedMessages[lastAssistantIndex] = {
                role: 'assistant',
                content: 'Please provide the name for the tool.',
                isLoading: false
              };
              setIsAddToolModalOpen(true);
            }
            else {
              updatedMessages[lastAssistantIndex] = {
                role: 'assistant',
                content: 'Tool added successfully. Please ask your query again.',
                isLoading: false
              };
              setLastQueryBeforeToolAdd('');
              setShowToolPrompt(false);
            }
            
            return updatedMessages;
          });

          // Save the updated message to the database
          await fetch(`http://localhost:8000/chats/${chatId}/messages`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              messageIndex: lastAssistantIndex,
              content: messages[lastAssistantIndex].content
            })
          });
        }
      } catch (error) {
        console.error('Error rerunning query:', error);
        
        // Update the existing message with error state
        if (lastAssistantIndex !== -1) {
          setMessages(prevMessages => {
            const updatedMessages = [...prevMessages];
            updatedMessages[lastAssistantIndex] = {
              role: 'assistant',
              content: 'Sorry, there was an error generating the response. Please try again.',
              isLoading: false
            };
            return updatedMessages;
          });
        }
      } finally {
        setIsGeneratingResponse(false);
      }
    }
  };

  // Add this function to determine if files should be shown for a message
  const shouldShowFiles = (index: number) => {
    // Only show files for the very first message
    return index === messages.length - 1 && messages.length === 1;
  };

  // Hide files after initial query is processed
  useEffect(() => {
    if (messages.length > 0) {
      setShowFiles(false);
    }
  }, [messages]);

  const MessageThread = ({ message, index, isConversation = false }: { message: Message, index: number, isConversation?: boolean }) => {
    return (
      <div className="mb-6">
        {/* File Display Section */}
        {showFiles && uploadedFiles.length > 0 && (
          <div className="mb-3">
            {uploadedFiles.map((file, fileIndex) => (
              <div 
                key={fileIndex} 
                className="inline-flex items-center bg-white rounded-lg p-3 mb-2 mr-2"
              >
                <div className="flex items-center gap-2">
                  <span className="text-blue-500 font-medium">{file}</span>
                  <div className="text-xs text-gray-500 px-2 py-1 bg-gray-100 rounded">
                    PDF
                  </div>
                </div>
                <button
                  onClick={() => removeUploadedFile(file, fileIndex)}
                  className="ml-2 text-gray-400 hover:text-gray-600"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Message Content */}
        {message.role === 'user' ? (
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-full bg-gray-800 flex items-center justify-center text-white">
              R
            </div>
            <div className="flex-1">
              <div className="bg-[#e9e5e0] rounded-2xl px-4 py-2 inline-block max-w-[80%]">
                <p className="text-gray-800">{message.content}</p>
              </div>
            </div>
          </div>
        ) : (
          <div className="flex items-start gap-3">
            <div className="w-8 h-8">
              <div className="w-8 h-8 rounded-sm bg-orange-100 flex items-center justify-center">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" fill="#FF6934"/>
                </svg>
              </div>
            </div>
            <div className="flex-1">
              <div className="bg-white rounded-2xl px-4 py-3 inline-block max-w-[80%]">
                {message.isLoading ? (
                  <div className="flex items-center gap-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-900"></div>
                    <p className="text-gray-800">{message.content}</p>
                  </div>
                ) : (
                  <p className="text-gray-800">{message.content}</p>
                )}
              </div>
              {!message.isLoading && !isConversation && (
                <div className="flex gap-2 mt-2">
                  <button 
                    onClick={() => handleFeedback(index, 'positive')}
                    className={`text-gray-500 hover:text-gray-700 p-1 rounded ${
                      message.feedback === 'positive' ? 'bg-green-50 text-green-600' : ''
                    }`}
                  >
                    <ThumbsUp className="h-4 w-4" />
                  </button>
                  <button 
                    onClick={() => handleFeedback(index, 'negative')}
                    className={`text-gray-500 hover:text-gray-700 p-1 rounded ${
                      message.feedback === 'negative' ? 'bg-red-50 text-red-600' : ''
                    }`}
                  >
                    <ThumbsDown className="h-4 w-4" />
                  </button>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="h-screen flex flex-col bg-[#f5f3f0]">
      <div className="flex-grow overflow-hidden flex flex-col m-4">
        <Card className="flex-grow overflow-hidden flex flex-col border border-gray-200 bg-white/50">
          <CardContent className="flex-grow overflow-y-auto flex flex-col-reverse p-6">
            <div ref={messagesEndRef} />
            {messages.map((message, index) => (
              <MessageThread key={index} message={message} index={index} />
            ))}
            {/* Add conversations at the bottom (will appear at top due to flex-col-reverse) */}
            {hasLoadedConversations && conversations.map(([userMessage, assistantMessage], index) => (
              <div key={`conv-${index}`}>
                <MessageThread 
                  message={{ role: 'user', content: userMessage }} 
                  index={-1} 
                  isConversation={true}
                />
                <MessageThread 
                  message={{ role: 'assistant', content: assistantMessage }} 
                  index={-1} 
                  isConversation={true}
                />
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      {/* Input Section */}
      <div className="border-t bg-white p-4">
        <div className="max-w-4xl mx-auto">
          <form onSubmit={handleSubmit} className="flex items-center gap-3">
            <Input
              value={input}
              onChange={handleInputChange}
              placeholder="Type your message..."
              className="flex-1 border-gray-200 focus:ring-2 focus:ring-blue-100"
            />
            <div className="flex gap-2">
              <Button
                type="button"
                variant="outline"
                onClick={() => fileInputRef.current?.click()}
                className="hover:bg-gray-50"
              >
                <Paperclip className="h-4 w-4" />
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => setIsAddToolModalOpen(true)}
                className="hover:bg-gray-50"
              >
                <PlusCircle className="h-4 w-4" />
              </Button>
              <Button 
                type="submit" 
                disabled={!input.trim()}
                className="bg-black hover:bg-gray-800 text-white transition-colors duration-200"
              >
                Send
              </Button>
            </div>
            <input
              type="file"
              ref={fileInputRef}
              className="hidden"
              onChange={handleFileUpload}
              multiple
            />
          </form>
        </div>
      </div>

      {/* Modals and Sidebars */}
      <AddToolModal 
        isOpen={isAddToolModalOpen}
        onClose={() => setIsAddToolModalOpen(false)}
        onToolAdded={handleToolAddedAndRerun}
        chatId={chatId}
      />
      {isCustomToolsSidebarOpen && (
        <CustomToolsSidebar
          tools={customTools}
          onCollapse={toggleCustomToolsSidebar}
          onDeleteTool={handleDeleteTool}
          chatId={chatId!}
        />
      )}

      {showToolPrompt && (
        <div className="p-4 bg-blue-50 rounded-lg mb-4">
          Would you like to add this as a custom tool? (Yes/No)
        </div>
      )}
      
      {showDocstringPrompt && (
        <div className="p-4 bg-blue-50 rounded-lg mb-4">
          Would you like to add a docstring? (Yes/No)
        </div>
      )}

      {activeFeedbackMessage !== null && (
        <FeedbackModal
          isOpen={true}
          onClose={() => setActiveFeedbackMessage(null)}
          onSaveFeedback={handleDetailedFeedback}
        />
      )}
    </div>
  );
}