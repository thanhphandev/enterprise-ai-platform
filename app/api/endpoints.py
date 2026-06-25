import os
import shutil
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import StreamingResponse

from .schemas import ChatRequest, ChatResponse, UploadResponse, HistoryResponse, MessageItem
from .dependencies import get_rag_pipeline
from app.core.rag import RAGPipeline

router = APIRouter()

UPLOAD_DIR = "./temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    rag: RAGPipeline = Depends(get_rag_pipeline)
):
    """
    Upload a document (PDF, Excel, TXT) and index it into the VectorDB.
    """
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        # Save file temporarily
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Trigger RAG pipeline ingestion
        result = rag.process_and_index_file(file_path)
        
        return UploadResponse(
            status="success",
            filename=file.filename,
            chunks_indexed=result.get("chunks_indexed", 0)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup temporary file
        if os.path.exists(file_path):
            os.remove(file_path)

@router.post("/chat")
async def chat_with_bot(
    request: ChatRequest,
    rag: RAGPipeline = Depends(get_rag_pipeline)
):
    """
    Standard chat response (Non-streaming).
    """
    try:
        reply = await rag.chat(request.message, session_id=request.session_id)
        return ChatResponse(reply=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/stream")
async def chat_with_bot_stream(
    request: ChatRequest,
    rag: RAGPipeline = Depends(get_rag_pipeline)
):
    """
    Streaming chat response for real-time typewriter effect.
    Returns Server-Sent Events (SSE) stream.
    """
    async def event_generator():
        try:
            async for chunk in rag.stream_chat(request.message, session_id=request.session_id):
                import json
                if chunk.startswith("⚙️ [ACTION]"):
                    action_text = chunk.replace("⚙️ [ACTION] ", "")
                    yield f"data: {json.dumps({'type': 'action', 'content': action_text})}\n\n"
                else:
                    yield f"data: {json.dumps({'type': 'content', 'content': chunk})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        except Exception as e:
            import json
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.get("/history/{session_id}", response_model=HistoryResponse)
async def get_chat_history(
    session_id: str,
    rag: RAGPipeline = Depends(get_rag_pipeline)
):
    """
    Retrieve chat history for a given session.
    """
    try:
        history = rag.memory.get_history(session_id)
        return HistoryResponse(
            session_id=session_id,
            history=[MessageItem(role=msg["role"], content=msg["content"]) for msg in history]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/history/{session_id}")
async def clear_chat_history(
    session_id: str,
    rag: RAGPipeline = Depends(get_rag_pipeline)
):
    """
    Clear chat history for a given session.
    """
    try:
        rag.memory.clear_history(session_id)
        return {"status": "success", "message": "History cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents")
async def list_documents(
    rag: RAGPipeline = Depends(get_rag_pipeline)
):
    """
    List all unique document filenames indexed in ChromaDB.
    """
    try:
        collection = rag.vector_store.vector_store._collection
        results = collection.get(include=["metadatas"])
        metadatas = results.get("metadatas", [])
        
        filenames = set()
        for meta in metadatas:
            if meta and "source" in meta:
                # Extract clean filename from source path
                import os
                filenames.add(os.path.basename(meta["source"]))
            elif meta and "filename" in meta:
                filenames.add(meta["filename"])
                
        return {"documents": sorted(list(filenames))}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/documents")
async def clear_all_documents(
    rag: RAGPipeline = Depends(get_rag_pipeline)
):
    """
    Clear all indexed documents from ChromaDB.
    """
    try:
        collection = rag.vector_store.vector_store._collection
        results = collection.get(include=[])
        ids = results.get("ids", [])
        if ids:
            collection.delete(ids=ids)
        return {"status": "success", "message": "All documents cleared from VectorDB"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions")
async def list_chat_sessions(
    rag: RAGPipeline = Depends(get_rag_pipeline)
):
    """
    List all unique active chat session IDs.
    """
    try:
        sessions = rag.memory.get_all_sessions()
        return {"sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


