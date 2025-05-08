from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import requests
import aiohttp
import os
from lite_llm import LiteLLM

app = FastAPI(title="Web-based Chat Assistant")

# Initialize the LLM model (assuming LiteLLM supports model selection)
llm_models = {
    "default": "gpt-3.5-turbo",
    "advanced": "gpt-4"
}
current_model_name = "default"
llm = LiteLLM(model_name=llm_models[current_model_name])

# In-memory storage for conversation context per user/session
# For simplicity, using a dict; in production, consider persistent storage
conversation_contexts = {}

class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    user_id: str
    message: str
    model: Optional[str] = None  # Optional model selection
    reset: Optional[bool] = False  # Reset context if True

class ChatResponse(BaseModel):
    reply: str
    context: List[Message]

@app.post("/set_model")
async def set_model(model_name: str = Form(...)):
    """
    Endpoint to change the model used by the LLM.
    """
    if model_name not in llm_models:
        raise HTTPException(status_code=400, detail="Model not supported.")
    global llm, current_model_name
    current_model_name = model_name
    llm = LiteLLM(model_name=llm_models[current_model_name])
    return {"status": "Model updated", "model": current_model_name}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Handle user messages, maintain context, and generate responses.
    """
    user_id = request.user_id
    message = request.message
    model_name = request.model or current_model_name
    reset = request.reset

    # Initialize context if not present
    if user_id not in conversation_contexts or reset:
        conversation_contexts[user_id] = []

    context = conversation_contexts[user_id]

    # Append user message to context
    context.append(Message(role="user", content=message))

    # Prepare prompt with context
    prompt = ""
    for msg in context:
        role = "User" if msg.role == "user" else "Assistant"
        prompt += f"{role}: {msg.content}\n"
    prompt += "Assistant:"

    try:
        # Generate response from LLM
        response_text = await generate_response(prompt, model_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

    # Append assistant response to context
    context.append(Message(role="assistant", content=response_text))
    # Keep only last 10 messages for context
    if len(context) > 20:
        context = context[-20:]
        conversation_contexts[user_id] = context

    return ChatResponse(reply=response_text, context=context)

async def generate_response(prompt: str, model_name: str) -> str:
    """
    Generate a response from the LLM given a prompt.
    """
    # Assuming LiteLLM has an async method 'generate'
    # If not, adapt accordingly
    # For demonstration, using a placeholder implementation
    # Replace with actual LiteLLM API call
    # Example:
    # response = await llm.generate(prompt)
    # return response
    # Placeholder implementation:
    async with aiohttp.ClientSession() as session:
        # Replace with actual API endpoint if needed
        # For now, simulate response
        await asyncio.sleep(0.5)  # simulate delay
        return "This is a placeholder response."

@app.post("/upload_media")
async def upload_media(file: UploadFile = File(...)):
    """
    Endpoint to handle multimedia uploads.
    """
    try:
        contents = await file.read()
        save_path = os.path.join("uploads", file.filename)
        os.makedirs("uploads", exist_ok=True)
        with open(save_path, "wb") as f:
            f.write(contents)
        return {"status": "File uploaded", "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)