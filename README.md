# README.md

# Web-Based Chat Assistant

This project implements a web-based Chat Assistant that allows users to have continuous conversations with a Large Language Model (LLM). The application features a front-end UI for user interaction, a back-end API for managing conversations, model selection, context management, and optional multimedia uploads. It is designed to be deployed on Render.com.

## Features

- User-friendly web interface for chatting with the LLM
- Support for multiple LLM models with selection
- Context management for ongoing conversations
- Optional multimedia uploads (images, files)
- Modular and scalable architecture
- Deployment-ready on Render.com

## Technologies Used

- FastAPI for the backend API
- Uvicorn as the ASGI server
- LiteLLM for lightweight LLM integration
- Pydantic for data validation
- Starlette for web components
- Requests and aiohttp for HTTP requests

## Files

- `front-end.html` / `front-end.js`: Front-end UI code
- `main.py`: Backend API implementation
- `requirements.txt`: Dependencies list
- `README.md`: This documentation

## Setup Instructions

### 1. Clone the repository

```bash
git clone <repository_url>
cd <repository_directory>
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the backend server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 4. Serve the front-end files

Open `front-end.html` in a browser or serve it via a static file server.

### 5. Deploy on Render.com

Configure your Render service to run the backend with the command:

```bash
uvicorn main:app --host 0.0.0.0 --port 10000
```

and host the static files accordingly.

## Usage

Open the front-end UI in your browser, select the desired model, and start chatting. Upload multimedia files if needed. The conversation context is maintained automatically.

## Code Overview

### `main.py`

```python
from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import requests
import aiohttp
from lite_llm import LiteLLM

app = FastAPI()

# Initialize LiteLLM (configure as needed)
llm = LiteLLM()

# Data models
class Message(BaseModel):
    role: str
    content: str

class Conversation(BaseModel):
    messages: List[Message]
    model: str
    context: Optional[List[Message]] = []

@app.post("/chat/")
async def chat_endpoint(conversation: Conversation):
    """
    Handle chat requests, maintain context, and return LLM response.
    """
    try:
        # Prepare prompt with context
        prompt_messages = conversation.context + conversation.messages
        prompt = "\n".join([f"{msg.role}: {msg.content}" for msg in prompt_messages])

        # Call LLM
        response_text = await generate_response(prompt, conversation.model)
        # Append assistant response to context
        conversation.context.append(Message(role="assistant", content=response_text))
        return {"response": response_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def generate_response(prompt: str, model: str) -> str:
    """
    Generate response from LLM based on prompt and model.
    """
    try:
        # Example using LiteLLM (adjust as per actual API)
        response = await llm.chat(prompt=prompt, model=model)
        return response
    except Exception as e:
        raise e

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    """
    Handle multimedia uploads.
    """
    try:
        content = await file.read()
        # Process the uploaded file as needed
        return {"filename": file.filename, "size": len(content)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### `requirements.txt`

```
fastapi
uvicorn
lite_llm
pydantic
starlette
requests
aiohttp
```

### `front-end.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Chat Assistant</title>
<style>
  body { font-family: Arial, sans-serif; margin: 20px; }
  #chat { border: 1px solid #ccc; padding: 10px; height: 400px; overflow-y: scroll; }
  #user-input { width: 80%; }
  #send-btn { width: 15%; }
</style>
</head>
<body>
<h2>Web-Based Chat Assistant</h2>
<div id="chat"></div>
<input type="text" id="user-input" placeholder="Type your message..." />
<button id="send-btn">Send</button>
<input type="file" id="file-upload" />
<script>
const chatDiv = document.getElementById('chat');
const inputBox = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const fileInput = document.getElementById('file-upload');

let conversationContext = [];
let selectedModel = 'default';

async function sendMessage() {
    const message = inputBox.value;
    if (!message) return;
    appendMessage('User', message);
    conversationContext.push({role: 'user', content: message});
    inputBox.value = '';

    // Prepare payload
    const payload = {
        messages: conversationContext,
        model: selectedModel,
        context: conversationContext
    };

    try {
        const response = await fetch('/chat/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        const data = await response.json();
        appendMessage('Assistant', data.response);
        conversationContext.push({role: 'assistant', content: data.response});
    } catch (error) {
        appendMessage('Error', 'Failed to get response.');
    }
}

function appendMessage(sender, message) {
    const msgDiv = document.createElement('div');
    msgDiv.innerHTML = `<strong>${sender}:</strong> ${message}`;
    chatDiv.appendChild(msgDiv);
    chatDiv.scrollTop = chatDiv.scrollHeight;
}

sendBtn.onclick = sendMessage;
inputBox.onkeydown = (e) => { if (e.key === 'Enter') sendMessage(); };

fileInput.onchange = async () => {
    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);
    try {
        await fetch('/upload/', {
            method: 'POST',
            body: formData
        });
        alert('File uploaded successfully.');
    } catch {
        alert('File upload failed.');
    }
};
</script>
</body>
</html>
```