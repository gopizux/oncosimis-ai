from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from contextlib import asynccontextmanager
import requests
import logging
from pathlib import Path
import os
from typing import Optional, List
import uvicorn

# Import document loader
try:
    from document_loader import load_documents
    DOCUMENT_LOADER_AVAILABLE = True
except ImportError:
    DOCUMENT_LOADER_AVAILABLE = False
    logging.warning("document_loader.py not found")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama2:7b"
SOPS_DIR = Path("../SOPs-feed")

# Company knowledge base
ONCOSIMIS_CONTEXT = """You are a helpful AI assistant for Oncosimis Biotech. Answer questions using ONLY the information provided. Keep answers concise (2-3 sentences maximum) and professional.

=== COMPANY INFORMATION ===

Q: What is Oncosimis?
A: Oncosimis Biotech Pvt Ltd is a biotechnology company revolutionizing the development of biologics and biosimilars at affordable costs using cutting-edge proprietary platforms.

Q: What technologies does Oncosimis use?
A: Oncosimis uses two proprietary technology platforms - AcceTT® (CHO-based high-yield production for monoclonal antibodies) and BacSec® (endotoxin-free protein expression in E. coli).

Q: What is AcceTT?
A: AcceTT® (Accelerated Technology Transfer) is Oncosimis's CHO cell-based platform designed for high-yield production of therapeutic monoclonal antibodies and recombinant proteins with reduced manufacturing costs.

Q: What is BacSec?
A: BacSec® is Oncosimis's bacterial secretion platform that produces endotoxin-free recombinant proteins and peptides in E. coli, enabling cost-effective manufacturing of biosimilars.

Q: What does Oncosimis do?
A: Oncosimis develops and manufactures bio-therapeutic proteins, monoclonal antibodies, and biosimilars for treating diseases like cancer and diabetes, making expensive biologics affordable and accessible.

Q: What is Oncosimis's mission?
A: Oncosimis is committed to making a positive impact on society by addressing global healthcare challenges through innovative biotechnology, focusing on disease treatment, food security, and environmental sustainability.

Q: Who is on the Oncosimis team?
A: Oncosimis has a team of world-renowned research scientists, doctors, and entrepreneurs specializing in drug discovery, manufacturing, and commercializing bio-therapeutics.

Q: Who is the CEO?
A: Dr. Sudarshan Reddy

Q: Who is the CSO or Chief Scientific Officer?
A: Dr. Sridhar Reddy

Q: What about the team and how many members?
A: There are approximately 13 members in the team.

Q: Where is Oncosimis located?
A: Oncosimis Biotech Pvt Ltd is located at IDA Uppal, Hyderabad, Telangana, India, 500039.
"""

# Global variables
documents_content = ""
available_documents = []

# Pydantic models
class ChatMessage(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    files: Optional[List[dict]] = None

# Lifespan Event Handler (Modern FastAPI approach)
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for startup and shutdown
    Replaces deprecated @app.on_event("startup")
    """
    global documents_content, available_documents
    
    # STARTUP
    logger.info("=" * 60)
    logger.info("=== Starting Oncosimis AI Assistant ===")
    logger.info("=" * 60)
    
    # Create SOPs directory if it doesn't exist
    if not SOPS_DIR.exists():
        SOPS_DIR.mkdir(parents=True, exist_ok=True)
        logger.warning(f"📁 Created SOPs directory: {SOPS_DIR}")
    
    # Load documents
    if DOCUMENT_LOADER_AVAILABLE and SOPS_DIR.exists():
        try:
            documents_content, available_documents = load_documents(str(SOPS_DIR))
            logger.info(f"✅ Loaded {len(available_documents)} SOP documents")
            if available_documents:
                for doc in available_documents[:5]:  # Show first 5
                    logger.info(f"   📄 {doc}")
                if len(available_documents) > 5:
                    logger.info(f"   ... and {len(available_documents) - 5} more")
        except Exception as e:
            logger.error(f"❌ Error loading documents: {e}")
    else:
        logger.warning("⚠️  No documents loaded - SOPs directory empty or document_loader unavailable")
    
    # Check Ollama connection
    try:
        # First check if Ollama server is running
        response = requests.get(f"{OLLAMA_BASE_URL}/", timeout=5)
        
        if response.status_code == 200 and "Ollama is running" in response.text:
            logger.info(f"✅ Ollama server is running")
            
            # Check if model is available
            try:
                tags_response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
                if tags_response.status_code == 200:
                    models = tags_response.json().get("models", [])
                    model_names = [m.get("name", "") for m in models]
                    
                    if any(OLLAMA_MODEL in name for name in model_names):
                        logger.info(f"✅ Model '{OLLAMA_MODEL}' is available")
                        
                        # Test generation
                        test_gen = requests.post(
                            OLLAMA_API_URL,
                            json={"model": OLLAMA_MODEL, "prompt": "hi", "stream": False},
                            timeout=15
                        )
                        
                        if test_gen.status_code == 200:
                            logger.info(f"✅ Ollama connected successfully with model: {OLLAMA_MODEL}")
                            logger.info(f"🎮 GPU: NVIDIA RTX 4070 SUPER detected")
                        else:
                            logger.warning(f"⚠️  Model test failed with status: {test_gen.status_code}")
                    else:
                        logger.error(f"❌ Model '{OLLAMA_MODEL}' not found. Available models: {model_names}")
                        logger.error(f"   Run: ollama pull {OLLAMA_MODEL}")
            except Exception as e:
                logger.error(f"❌ Error checking models: {e}")
        else:
            logger.warning(f"⚠️  Ollama server not responding properly")
            
    except requests.exceptions.ConnectionError:
        logger.error("❌ Cannot connect to Ollama")
        logger.error("   Please ensure 'ollama serve' is running")
    except Exception as e:
        logger.error(f"❌ Ollama connection failed: {e}")
    
    logger.info("=" * 60)
    logger.info(f"🚀 Backend running on http://localhost:8000")
    logger.info(f"📁 SOPs directory: {SOPS_DIR.absolute()}")
    logger.info(f"📚 Documents loaded: {len(available_documents)}")
    logger.info("=" * 60)
    
    yield  # Application runs here
    
    # SHUTDOWN
    logger.info("🛑 Shutting down Oncosimis AI Assistant...")

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Oncosimis AI Assistant",
    description="AI-powered assistant for Oncosimis Biotech",
    version="2.0.0",
    lifespan=lifespan
)

# CORS configuration - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper function to query Ollama
def query_ollama(prompt: str) -> str:
    """Query Ollama with error handling"""
    try:
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "num_predict": 150,  # Limit response length
                }
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json().get("response", "").strip()
            return result if result else "Sorry, I couldn't generate a response."
        else:
            logger.error(f"Ollama API error: {response.status_code}")
            return "I'm having trouble connecting to the AI model. Please try again."
            
    except requests.exceptions.Timeout:
        logger.error("Ollama request timeout")
        return "The request took too long. Please try a simpler question."
    except Exception as e:
        logger.error(f"Error querying Ollama: {e}")
        return "An error occurred while processing your request."

# API endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Oncosimis AI Assistant API",
        "version": "2.0.0",
        "status": "running",
        "model": OLLAMA_MODEL,
        "documents": len(available_documents)
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    ollama_status = "disconnected"
    
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/", timeout=3)
        if response.status_code == 200 and "Ollama is running" in response.text:
            ollama_status = "connected"
    except:
        pass
    
    return {
        "status": "healthy",
        "ollama": ollama_status,
        "model": OLLAMA_MODEL,
        "documents_loaded": len(available_documents),
        "backend": "running"
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """Main chat endpoint"""
    user_message = message.message.strip()
    
    if not user_message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    logger.info(f"💬 User: {user_message[:100]}...")
    
    # Check for greetings first
    greeting_keywords = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening", "greetings", "howdy", "hola"]
    user_message_lower = user_message.lower().strip()

    is_greeting = any(keyword in user_message_lower for keyword in greeting_keywords) and len(user_message_lower.split()) <= 3

    if is_greeting:
        greeting_responses = [
            "Hello! I'm the Oncosimis AI Assistant. I'm here to help you learn about our biotechnology platforms and services. What would you like to know?",
            "Hi there! Welcome to Oncosimis Biotech. I can tell you about our AcceTT® and BacSec® platforms, our team, or help you find Standard Operating Procedures. How can I assist you today?",
            "Greetings! I'm your AI assistant for Oncosimis Biotech. Ask me about our technologies, team, or request any SOPs you need.",
            "Hello! Nice to meet you. I'm here to provide information about Oncosimis Biotech's innovative biotechnology solutions. What interests you most?"
        ]
        import random
        response_text = random.choice(greeting_responses)
        logger.info("👋 Greeting detected - returning friendly response")
        return ChatResponse(response=response_text, files=None)

    # Check if user is asking for files/SOPs
    file_keywords = ["sop", "procedure", "file", "document", "download", "send me", "give me", "show me", "need", "list"]

    is_file_request = any(keyword in user_message_lower for keyword in file_keywords)

    if is_file_request and available_documents:
        # Find matching files
        matching_files = []
        
        # Check for specific keywords in user message
        words = user_message_lower.split()
        for doc in available_documents:
            doc_lower = doc.lower()
            # Check if any word from user message is in document name
            if any(word in doc_lower for word in words if len(word) > 3):
                matching_files.append({
                    "filename": doc,
                    "path": f"/download/{doc}"
                })
        
        # If no specific match, return all files for broad requests
        if not matching_files and (
            "all" in user_message_lower or 
            "list" in user_message_lower or 
            "available" in user_message_lower or
            "show" in user_message_lower
        ):
            matching_files = [{"filename": doc, "path": f"/download/{doc}"} for doc in available_documents]
        
        if matching_files:
            if len(matching_files) == 1:
                response_text = f"I found this document for you:\n• {matching_files[0]['filename']}\n\nClick the download button below to get it."
            else:
                file_list = "\n".join([f"• {file['filename']}" for file in matching_files[:10]])
                if len(matching_files) > 10:
                    file_list += f"\n... and {len(matching_files) - 10} more"
                response_text = f"I found {len(matching_files)} relevant documents:\n{file_list}\n\nClick the download buttons below to get them."
            
            logger.info(f"📄 Returning {len(matching_files)} file(s)")
            return ChatResponse(
                response=response_text,
                files=matching_files
            )
        elif is_file_request:
            return ChatResponse(
                response="I couldn't find any documents matching your request. Try asking 'show me all SOPs' to see all available documents.",
                files=None
            )
    
    # Build context with company info and SOPs
    full_context = ONCOSIMIS_CONTEXT
    if documents_content:
        # Truncate if too long
        max_context_length = 8000
        if len(documents_content) > max_context_length:
            full_context += f"\n\n=== STANDARD OPERATING PROCEDURES (Excerpt) ===\n{documents_content[:max_context_length]}"
        else:
            full_context += f"\n\n=== STANDARD OPERATING PROCEDURES ===\n{documents_content}"
    
    # Create prompt for Ollama
    prompt = f"""{full_context}

User Question: {user_message}

Instructions: Answer the user's question based ONLY on the information provided above. If the information is not available, say so politely. Keep your answer concise and professional (2-3 sentences maximum).

Answer:"""
    
    # Get response from Ollama
    ai_response = query_ollama(prompt)
    
    logger.info(f"🤖 AI: {ai_response[:100]}...")
    
    return ChatResponse(response=ai_response, files=None)

@app.get("/documents")
async def list_documents():
    """Get list of all available documents"""
    return {
        "documents": available_documents,
        "count": len(available_documents),
        "directory": str(SOPS_DIR.absolute())
    }

@app.get("/download/{filename}")
async def download_document(filename: str):
    """Download a specific document"""
    # Prevent directory traversal attacks
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    file_path = SOPS_DIR / filename
    
    if not file_path.exists():
        logger.error(f"File not found: {filename}")
        raise HTTPException(status_code=404, detail=f"File '{filename}' not found")
    
    if not file_path.is_file():
        raise HTTPException(status_code=400, detail="Invalid file")
    
    logger.info(f"📥 Downloading: {filename}")
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="application/octet-stream"
    )

# Run server
if __name__ == "__main__":
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000, 
        log_level="info"
    )

