# Agentic RAG - AI Chat Application

A modern chat interface built with Next.js that allows users to interact with AI models while managing custom tools and file uploads.

## Features

- 💬 Real-time chat interface with AI
- 🛠️ Custom tools management
- 📁 File upload and management
- 🎨 Modern UI with Tailwind CSS and shadcn/ui components
- 📱 Responsive design
- 🔧 Customizable sidebar with tools integration
- 🔄 Real-time updates and feedback system

## Tech Stack

- **Frontend:**
  - Next.js 15.0
  - React 19
  - TypeScript
  - Tailwind CSS
  - shadcn/ui components
  - Framer Motion for animations

- **Backend:**
  - FastAPI
  - SQLAlchemy
  - PostgreSQL
  - Python 3.10+

## Setup

1. Clone the repository 

```bash
git clone https://github.com/VectorNd/AgenticRAG.git 
cd AgenticRAG
```
2. Install frontend dependencies 

```bash
npm install
```

3. Setup environment variables in `backend/.env`

4. Install backend dependencies

```bash 
cd backend
pip install -r requirements.txt
```

5. Run the development server

Backend - 

```bash
cd backend
uvicorn main:app --reload
```

Frontend - 

```bash
npm run dev
```

6. Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## Project Structure

- `/app` - Next.js pages and routing
- `/components` - React components
- `/backend` - FastAPI server and database models
- `/types` - TypeScript type definitions
- `/lib` - Utility functions and shared code

## Features in Detail

### Chat Interface
- Real-time messaging with AI
- Message feedback system (thumbs up/down)
- Chat history management
- File attachment support

### Custom Tools
- Add and manage custom tools
- Tool description and metadata
- Per-chat tool management
- Searchable tools sidebar

### File Management
- File upload support
- File association with chats
- Multiple file types support