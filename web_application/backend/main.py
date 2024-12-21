from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
from typing import List , Optional
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
from sqlalchemy.orm import Session
import models
import db
from datetime import datetime
from uuid import UUID
from s3_utils import upload_file_to_s3 , delete_file_from_s3
import requests
import json

app = FastAPI()
backend_url = "http://localhost:5000"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FeedbackData(BaseModel):
    feedback: str
    clarification: List[dict]
    query: str
    re_evaluate: bool

class Tool(BaseModel):
    id: Optional[str] = None
    name: str
    description: str

class Query(BaseModel):
    text: str

class ChatCreate(BaseModel):
    title: str

class ChatResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    messages: List[dict]
    tools: List[dict]
    files: List[dict]

    class Config:
        from_attributes = True

class ToolCreate(BaseModel):
    name: str
    description: str
    python_code: str | None = None

class ChatToolResponse(BaseModel):
    id: str
    chat_id: str
    name: str
    description: str
    python_code: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True

class ChatFileResponse(BaseModel):
    id: str
    chat_id: str
    filename: str
    original_filename: str
    created_at: datetime

    class Config:
        from_attributes = True

tools: List[Tool] = []
UPLOAD_DIR = "uploads"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def _get_request_headers():
    request_headers = {"accept": "*/*", "Content-Type": "application/json"}
    return request_headers

@app.get("/")
async def read_root():
    return {"message": "Welcome to v0 API"}

@app.get("/tools", response_model=List[Tool])
async def get_tools():
    return tools

@app.post("/tools", response_model=Tool)
async def add_tool(tool: Tool):
    new_tool = Tool(id=str(uuid.uuid4()), name=tool.name, description=tool.description)
    tools.append(new_tool)
    return new_tool

@app.delete("/tools/{tool_id}")
async def delete_tool(tool_id: str):
    for tool in tools:
        if tool.id == tool_id:
            tools.remove(tool)
            return {"message": f"Tool {tool_id} deleted"}
    raise HTTPException(status_code=404, detail="Tool not found")

@app.get("/chats/history")
async def get_history():
    try:
        # Replace this with your actual database query
        # This is just example data
        history = requests.get(url=f"{backend_url}/1/get_history",timeout=900)
        print(history.json())
        return history.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/chats/{chat_id}/get_conversations")
async def get_conversations(chat_id: str):
    try:
        conversations = requests.get(url=f"{backend_url}/1/{chat_id}/get_conversations",timeout=900)
        print(conversations.json())
        return conversations.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chats", response_model=List[ChatResponse])
async def get_chats(db: Session = Depends(db.get_db)):
    chats = db.query(models.Chat).order_by(models.Chat.created_at.desc()).all()
    return chats

@app.get("/chats/{chat_id}", response_model=ChatResponse)
async def get_chat(chat_id: str, db: Session = Depends(db.get_db)):
    chat = db.query(models.Chat).filter(models.Chat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    messages = db.query(models.Message)\
        .filter(models.Message.chat_id == chat_id)\
        .order_by(models.Message.created_at.asc())\
        .all()
    
    tools = db.query(models.ChatTool)\
        .filter(models.ChatTool.chat_id == chat_id)\
        .all()
    
    files = db.query(models.ChatFile)\
        .filter(models.ChatFile.chat_id == chat_id)\
        .all()
    
    return {
        "id": str(chat.id),
        "title": chat.title,
        "created_at": chat.created_at,
        "messages": [{"role": msg.role, "content": msg.content, "feedback": msg.feedback} 
                    for msg in messages],
        "tools": [{"id": str(tool.id), "name": tool.name, "description": tool.description, "python_code": tool.python_code} 
                 for tool in tools],
        "files": [{"filename": file.filename, "original_filename": file.original_filename} 
                 for file in files]
    }

@app.post("/chats", response_model=ChatResponse)
async def create_chat(chat: ChatCreate, db: Session = Depends(db.get_db)):
    db_chat = models.Chat(title=chat.title)
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return {
        "id": str(db_chat.id),
        "title": db_chat.title,
        "created_at": db_chat.created_at,
        "messages": [],  # Empty list for new chat
        "tools": [],    # Empty list for new chat
        "files": []     # Empty list for new chat
    }

@app.post("/chats/{chat_id}/messages")
async def add_message(
    chat_id: str,
    message: dict,
    db: Session = Depends(db.get_db)
):
    # Validate chat_id is a valid UUID
    try:
        # Convert string to UUID to validate format
        chat_uuid = UUID(chat_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid chat_id format. Must be a valid UUID"
        )

    # First verify that the chat exists
    chat = db.query(models.Chat).filter(models.Chat.id == str(chat_uuid)).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    try:
        # Check if identical message already exists
        existing_message = db.query(models.Message).filter(
            models.Message.chat_id == str(chat_uuid),
            models.Message.role == message.get("role"),
            models.Message.content == message.get("content")
        ).first()

        if not existing_message:
            # Create the message if it doesn't exist
            db_message = models.Message(
                chat_id=str(chat_uuid),
                role=message.get("role"),
                content=message.get("content")
            )
            db.add(db_message)
            db.commit()

            return {"status": "success", "message_id": str(db_message.id)}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/chats/{chat_id}/tools", response_model=ChatResponse)
async def add_tool_to_chat(
    chat_id: str,
    tool: ToolCreate,
    db: Session = Depends(db.get_db)
):
    try:
        chat_uuid = UUID(chat_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid chat_id format. Must be a valid UUID"
        )

    chat = db.query(models.Chat).filter(models.Chat.id == str(chat_uuid)).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Check if tool with same name already exists for this chat
    existing_tool = db.query(models.ChatTool).filter(
        models.ChatTool.chat_id == str(chat_uuid),
        models.ChatTool.name == tool.name
    ).first()

    if not existing_tool:  # Only add if tool doesn't exist
        new_tool = models.ChatTool(
            chat_id=str(chat_uuid),
            name=tool.name,
            description=tool.description,
            python_code=tool.python_code
        )
        db.add(new_tool)
        db.commit()
        db.refresh(new_tool)

    return await get_chat(chat_id, db)

@app.get("/chats/{chat_id}/tools", response_model=List[ChatToolResponse])
async def get_chat_tools(
    chat_id: str,
    db: Session = Depends(db.get_db)
):
    try:
        chat_uuid = UUID(chat_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid chat_id format. Must be a valid UUID"
        )

    tools = db.query(models.ChatTool).filter(models.ChatTool.chat_id == str(chat_uuid)).all()
    return tools

@app.post("/chats/{chat_id}/files")
async def add_file_to_chat(
    chat_id: str,
    file_data: dict,
    db: Session = Depends(db.get_db)
):
    try:
        chat_uuid = UUID(chat_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid chat_id format. Must be a valid UUID"
        )

    chat = db.query(models.Chat).filter(models.Chat.id == str(chat_uuid)).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    try:
        db_file = models.ChatFile(
            chat_id=str(chat_uuid),
            filename=file_data.get("filename"),
            original_filename=file_data.get("original_filename"),
            file_url=file_data.get("file_url")
        )
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        return {"status": "success", "file_id": str(db_file.id)}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/chats/{chat_id}/files")
async def get_chat_files(
    chat_id: str,
    db: Session = Depends(db.get_db)
):
    try:
        chat_uuid = UUID(chat_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid chat_id format. Must be a valid UUID"
        )

    files = db.query(models.ChatFile).filter(models.ChatFile.chat_id == str(chat_uuid)).all()
    return [{"id": str(file.id), "filename": file.filename, "original_filename": file.original_filename, "file_url": file.file_url} for file in files]

@app.delete("/chats/{chat_id}/tools/{tool_id}")
async def delete_chat_tool(
    chat_id: str,
    tool_id: str,
    db: Session = Depends(db.get_db)
):
    try:
        # Validate UUIDs
        chat_uuid = UUID(chat_id)
        tool_uuid = UUID(tool_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid UUID format for chat_id or tool_id"
        )

    # First verify that the chat exists
    chat = db.query(models.Chat).filter(models.Chat.id == str(chat_uuid)).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Find and delete the tool
    tool = db.query(models.ChatTool).filter(
        models.ChatTool.id == str(tool_uuid),
        models.ChatTool.chat_id == str(chat_uuid)
    ).first()

    if not tool:
        raise HTTPException(
            status_code=404, 
            detail="Tool not found or doesn't belong to this chat"
        )

    try:
        db.delete(tool)
        db.commit()
        return {"message": f"Tool {tool_id} deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting tool: {str(e)}"
        )

@app.delete("/chats/{chat_id}/files/{file_id}")
async def delete_chat_file(
    chat_id: str,
    file_id: str,
    db: Session = Depends(db.get_db)
):
    try:
        chat_uuid = UUID(chat_id)
        file_uuid = UUID(file_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid UUID format"
        )

    file = db.query(models.ChatFile).filter(
        models.ChatFile.id == str(file_uuid),
        models.ChatFile.chat_id == str(chat_uuid)
    ).first()

    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    try:
        # Delete the file from S3
        delete_file_from_s3(file.filename)

        # Delete the file record from the database
        db.delete(file)
        db.commit()
        return {"status": "success"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    
@app.post("/chats/{chat_id}/feedback")
async def process_feedback(chat_id: str, feedback: FeedbackData, db: Session = Depends(db.get_db)):
    chat_uuid = UUID(chat_id)
    print(chat_uuid)
    print(feedback)
    files = db.query(models.ChatFile).filter(models.ChatFile.chat_id == str(chat_uuid)).all()
    file_urls = [file.file_url for file in files]

    print(type(feedback.re_evaluate))   
    print(type(feedback.feedback))
    print(type(feedback.clarification))
    print(type(feedback.query))
    print(file_urls[0])
    response = requests.post(f"{backend_url}/1/{chat_id}/clarify_rag", 
                    data=json.dumps({
                        "re_evaluate": feedback.re_evaluate,
                        "feedback": feedback.feedback, 
                        "clarification": list(feedback.clarification),
                        "query": feedback.query,
                        "url": file_urls[0]
                    }),
                    headers=_get_request_headers(),
                    timeout=900
                    )
    
    print(response)
    
    return response.json()

@app.post("/chats/{chat_id}/add_tools")
async def process_add_tools(chat_id: str, query: Query, db: Session = Depends(db.get_db)):
    chat_uuid = UUID(chat_id)
    print(chat_uuid)
    # Get file URLs from chat_files table
    files = db.query(models.ChatFile).filter(models.ChatFile.chat_id == str(chat_uuid)).all()
    file_urls = [file.file_url for file in files] 
    
    tools = db.query(models.ChatTool).filter(models.ChatTool.chat_id == str(chat_uuid)).all()
    python_codes = [tool.python_code for tool in tools]
    descriptions = [tool.description for tool in tools]
    names = [tool.name for tool in tools]

    if python_codes[-1] is not None:
        url = f"{backend_url}/1/{chat_id}/add_tool"
        
        try:
            response = requests.post(
                url,
                data=json.dumps({"query": query.text , "url" : file_urls[0], 
                                    "user_code" : python_codes[-1]}),
                headers=_get_request_headers(),
                timeout=900
            )
            print(response.json())
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    else:
        url = f"{backend_url}/1/{chat_id}/add_tool_desc" 

        try:
            response = requests.post(
                url=url,
                data=json.dumps({"query": query.text , "url" : file_urls[0], 
                                    "user_desc" : descriptions[-1] , "func_name" : names[-1]}),
                headers=_get_request_headers(),
                timeout=900 
            )
            print(response.json())
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.post("/chats/{chat_id}/query")
async def process_query(chat_id: str, query: Query, db: Session = Depends(db.get_db)):
    chat_uuid = UUID(chat_id)
    print(chat_uuid)
    # Get file URLs from chat_files table
    files = db.query(models.ChatFile).filter(models.ChatFile.chat_id == str(chat_uuid)).all()
    file_urls = [file.file_url for file in files] 
    
    tools = db.query(models.ChatTool).filter(models.ChatTool.chat_id == str(chat_uuid)).all()
    python_codes = [tool.python_code for tool in tools]

    print(python_codes)
        

    url = f"{backend_url}/1/{chat_id}/query"
    print(url)

    print(file_urls[0])

    try:
        response = requests.post(
            url = url,
            data=json.dumps({"query": query.text , "url" : file_urls[0]}),
            headers=_get_request_headers(),
            timeout=900
        )
        print(response.json())
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chats/{chat_id}/upload")
async def upload_file(
    chat_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(db.get_db)
):
    try:
        chat_uuid = UUID(chat_id)
        chat = db.query(models.Chat).filter(models.Chat.id == str(chat_uuid)).first()
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")

        file_content = await file.read()
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Upload to S3 and get URL
        file_url = upload_file_to_s3(file_content, unique_filename)
        
        return {
            "filename": unique_filename,
            "file_url": file_url,
            "original_filename": file.filename,
            "message": "File uploaded successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

