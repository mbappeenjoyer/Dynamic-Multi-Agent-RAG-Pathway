// types.ts
export interface ChatHistory {
    id: string;
    title: string; // First few words of the initial message
    timestamp: string;
    messages: Message[];
    tools: CustomTool[];
    files: string[];
  }
  
  export interface Message {
    role: 'user' | 'assistant';
    content: string;
    feedback?: 'positive' | 'negative';
  }
  
  export interface CustomTool {
    id: string;
    name: string;
    description: string;
  }