import logging
from typing import AsyncGenerator
from .document_loader import DocumentLoader
from .text_splitter import TextSplitterService
from .vector_store import VectorStoreService
from .memory import SqliteMemoryManager
from .web_search import WebSearchService

from ..llm.schemas import ChatCompletionRequest, ChatMessage, Role
from ..llm.base import BaseLLMProvider
from ..llm.config import llm_settings

logger = logging.getLogger(__name__)

class RAGPipeline:
    """
    Orchestrates the Retrieval-Augmented Generation (RAG) process.
    Connects the Vector Store (ChromaDB) with our Custom LLM Router and Memory.
    """
    def __init__(self, llm_provider: BaseLLMProvider):
        self.llm_provider = llm_provider
        self.loader = DocumentLoader()
        self.splitter = TextSplitterService()
        self.vector_store = VectorStoreService()
        self.memory = SqliteMemoryManager()
        self.web_search = WebSearchService()

    def process_and_index_file(self, file_path: str):
        """
        End-to-end pipeline: Load -> Split -> Embed -> Store
        """
        import os
        logger.info(f"--- Starting Data Ingestion Pipeline for {file_path} ---")
        
        # 1. Load Document
        raw_docs = self.loader.load_document(file_path)
        
        # 2. Split Text
        chunks = self.splitter.split_documents(raw_docs)
        
        # Prepend filename to each chunk to enhance semantic retrieval by filename keywords
        filename = os.path.basename(file_path)
        for chunk in chunks:
            chunk.page_content = f"[Tài liệu: {filename}]\n{chunk.page_content}"
        
        # 3. Store in VectorDB
        self.vector_store.add_documents(chunks)
        
        logger.info("--- Data Ingestion Pipeline Completed Successfully ---")
        return {"status": "success", "chunks_indexed": len(chunks)}

    async def _rewrite_query(self, query: str, session_id: str) -> str:
        """
        Using LLM to rewrite a follow-up query into a standalone query
        based on recent chat history. Saves token and increases DB search accuracy.
        """
        history = self.memory.get_history(session_id)
        if not history:
            return query  # No history, no need to rewrite

        # We only need the last 4 messages for rewriting to save tokens
        recent_history = history[-4:]
        history_str = ""
        for msg in recent_history:
            role_label = "User" if msg["role"] == "user" else "Assistant"
            history_str += f"{role_label}: {msg['content']}\n"

        prompt = f"""Given the following conversation history and a follow-up question, rewrite the follow-up question to be a standalone question that can be understood without the conversation history.
Do NOT answer the question. Just rewrite it. If it is already standalone, return it exactly as is.

Chat History:
{history_str}
Follow-up Question: {query}
Standalone Question:"""

        request = ChatCompletionRequest(
            model=llm_settings.DEFAULT_MODEL,
            messages=[ChatMessage(role=Role.USER, content=prompt)],
            temperature=0.0,
            stream=False
        )
        try:
            response = await self.llm_provider.generate_chat(request)
            rewritten = response.choices[0].message.content.strip()
            logger.info(f"Query Rewrite: '{query}' -> '{rewritten}'")
            return rewritten
        except Exception as e:
            logger.error(f"Failed to rewrite query: {e}. Falling back to original.")
            return query

    def _build_rag_prompt(self, context_docs: list) -> str:
        """
        Format the prompt with retrieved context and strict enterprise rules.
        Optimized for high accuracy and minimal token usage.
        """
        context_str = "\n\n".join([doc.page_content for doc in context_docs])
        
        prompt = f"""You are an elite, highly precise enterprise AI assistant.
Answer the user's question based ONLY on the provided context below.

[RULES]
1. Strict Factualness: Answer using ONLY the facts explicitly mentioned in the context.
2. No Hallucination: If the context does not contain the answer, say exactly: "Tôi không tìm thấy thông tin này trong tài liệu nội bộ." - Do NOT attempt to make up an answer.
3. High Readability & Executive Formatting (CRITICAL):
   - Always format your answer beautifully using clean, professional Markdown.
   - Use bold text (`**term**`) to highlight key terms, technologies, and achievements.
   - Organize information using brief headings (`### Section Name`) and clean, standard bullet points (`-`).
   - Avoid messy, colorful, or childish emojis. Keep it clean, executive, and highly professional.
   - Never output big, raw blocks of text. Break them into clean paragraphs or lists.
4. Language: Always reply in the same language as the user's question.

<context>
{context_str}
</context>"""
        return prompt

    def _prepare_messages(self, session_id: str, query: str, docs: list) -> list[ChatMessage]:
        # Build System Prompt with retrieved context
        system_prompt = self._build_rag_prompt(docs)
        messages = [ChatMessage(role=Role.SYSTEM, content=system_prompt)]
        
        # Inject Chat History (Truncated to last 4 messages to save Input Tokens)
        history = self.memory.get_history(session_id)
        recent_history = history[-4:]
        for msg in recent_history:
            messages.append(ChatMessage(role=Role(msg["role"]), content=msg["content"]))
        
        # Append current user query
        messages.append(ChatMessage(role=Role.USER, content=query))
        return messages

    def _build_web_search_prompt(self, context_str: str) -> str:
        prompt = f"""You are an elite, highly precise enterprise AI assistant.
Answer the user's question based on the web search results provided below.

[RULES]
1. Factual and Objective: Answer using the facts mentioned in the web search results. Cite sources or links if present.
2. High Readability & Executive Formatting (CRITICAL):
   - Always format your answer beautifully using clean, professional Markdown.
   - Use bold text (`**term**`) to highlight key terms, technologies, and achievements.
   - Organize information using brief headings (`### Section Name`) and clean, standard bullet points (`-`).
   - Avoid messy, colorful, or childish emojis. Keep it clean, executive, and highly professional.
   - Never output big, raw blocks of text. Break them into clean paragraphs or lists.
3. Language: Always reply in the same language as the user's question.

<web_search_results>
{context_str}
</web_search_results>"""
        return prompt

    def _prepare_agent_messages(self, session_id: str, query: str) -> list[ChatMessage]:
        # Get list of currently indexed files to help the agent make highly precise search queries
        filenames = []
        try:
            collection = self.vector_store.vector_store._collection
            results = collection.get(include=["metadatas"])
            metadatas = results.get("metadatas", [])
            file_set = set()
            for meta in metadatas:
                if meta and "source" in meta:
                    import os
                    file_set.add(os.path.basename(meta["source"]))
                elif meta and "filename" in meta:
                    file_set.add(meta["filename"])
            filenames = sorted(list(file_set))
        except Exception:
            pass

        files_context = ""
        if filenames:
            files_context = "\nCurrently indexed files in the internal knowledge base:\n" + "\n".join([f"- {f}" for f in filenames]) + "\n"

        system_prompt = (
            "You are an elite, highly intelligent enterprise AI assistant. You have access to TWO distinct tools:\n"
            "1. 'search_knowledge': Use this tool ONLY when the user asks about internal company files, policies, regulations, "
            "documents uploaded, or user's private CV and records.\n"
            "2. 'search_web': Use this tool ONLY when the user asks about external general knowledge, current events, recent news, "
            "weather, real-time facts, programming, software technical errors, or general internet searches.\n\n"
            f"{files_context}"
            "\nCRITICAL INSTRUCTIONS:\n"
            "- For general greetings, chitchat, thank-yous, or basic mathematical calculations, do NOT call any tools. Reply directly "
            "using your general knowledge.\n"
            "- If the user's message is a follow-up, use the chat history to resolve pronouns (e.g., 'nó', 'họ', 'ở đâu') "
            "and generate a fully self-contained standalone search query for the correct tool.\n"
            "- When calling 'search_knowledge', generate the 'query' parameter as a direct, natural keyword phrase or natural question "
            "likely to match the actual content of the documents. Do NOT generate generic or meta-descriptions like 'Tên của CV của người dùng' "
            "or 'tài liệu của người dùng'. Instead, write queries using exact keywords related to the indexed filenames or topics (e.g., "
            "'Phan Văn Thành Backend Developer', 'Phan Văn Thành SEO', 'Học tài liệu đi', 'chính sách nghỉ phép').\n"
            "- When calling 'search_web', generate a clean, highly optimized, non-conversational keyword search query for DuckDuckGo. "
            "Strip all conversational filler, question marks, polite phrasing, and long sentences. Use only 2-5 high-impact search keywords "
            "(e.g., instead of 'diễn biến mới nhất về thị trường trí tuệ nhân tạo AI tuần này', generate 'thị trường AI mới nhất' or 'tin tức trí tuệ nhân tạo'; "
            "instead of 'hãy cho tôi biết thời tiết Hà Nội ngày hôm nay thế nào', generate 'thời tiết Hà Nội').\n"
            "- Executive Formatting: Always format your direct replies and final answers beautifully in markdown, using clear bullet points, bold markers, and clean line breaks. Avoid raw, unformatted text blocks or childish emojis."
        )
        messages = [ChatMessage(role=Role.SYSTEM, content=system_prompt)]
        
        # Truncate history to save tokens
        history = self.memory.get_history(session_id)
        recent_history = history[-4:]
        for msg in recent_history:
            messages.append(ChatMessage(role=Role(msg["role"]), content=msg["content"]))
            
        messages.append(ChatMessage(role=Role.USER, content=query))
        return messages

    async def chat(self, query: str, session_id: str = "default") -> str:
        """
        AI Agent Chat using Tool Calling. 
        Falls back gracefully to standard RAG if tools are not supported.
        """
        agent_messages = self._prepare_agent_messages(session_id, query)
        
        from ..llm.schemas import Tool, ToolType, FunctionDefinition
        search_knowledge_tool = Tool(
            type=ToolType.FUNCTION,
            function=FunctionDefinition(
                name="search_knowledge",
                description="Tìm kiếm trong tài liệu, quy định, chính sách, và thông tin nội bộ của công ty.",
                parameters={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Từ khóa hoặc câu hỏi trực tiếp để tra cứu tài liệu (ví dụ: 'Phan Văn Thành', 'CV Phan Văn Thành', 'chính sách nghỉ phép', tránh dùng từ chung chung mô tả như 'Tên của CV của người dùng')."
                        }
                    },
                    "required": ["query"]
                }
            )
        )
        
        search_web_tool = Tool(
            type=ToolType.FUNCTION,
            function=FunctionDefinition(
                name="search_web",
                description="Tìm kiếm thông tin thời gian thực ngoài Internet như tin tức, thời tiết, sự kiện xã hội, lập trình, công nghệ, hoặc kiến thức thế giới.",
                parameters={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Từ khóa tìm kiếm rút gọn, tối ưu hóa tối đa cho DuckDuckGo, không chứa câu hỏi hay từ ngữ hội thoại dài dòng (ví dụ: thay vì 'hãy tìm tin tức mới nhất về AI tuần này', chỉ truyền 'tin tức AI mới nhất' hoặc 'thị trường trí tuệ nhân tạo')."
                        }
                    },
                    "required": ["query"]
                }
            )
        )
        
        use_fallback = False
        tool_call_name = None
        search_query = query
        direct_reply = ""
        
        try:
            request = ChatCompletionRequest(
                model=llm_settings.DEFAULT_MODEL,
                messages=agent_messages,
                temperature=0.0,
                tools=[search_knowledge_tool, search_web_tool],
                stream=False
            )
            response = await self.llm_provider.generate_chat(request)
            message = response.choices[0].message
            
            if message.tool_calls:
                tool_call = message.tool_calls[0]
                tool_call_name = tool_call.function.name
                import json
                try:
                    args = json.loads(tool_call.function.arguments)
                    search_query = args.get("query", query)
                except Exception:
                    search_query = query
            else:
                direct_reply = message.content or ""
                
        except Exception as e:
            logger.warning(f"Agent: Tool calling failed ({e}). Falling back to traditional RAG.")
            use_fallback = True
            
        if use_fallback:
            search_query = await self._rewrite_query(query, session_id)
            docs = self.vector_store.similarity_search(search_query, k=6)
            final_messages = self._prepare_messages(session_id, query, docs)
            request = ChatCompletionRequest(
                model=llm_settings.DEFAULT_MODEL,
                messages=final_messages,
                temperature=0.0,
                stream=False
            )
            response = await self.llm_provider.generate_chat(request)
            reply = response.choices[0].message.content
        elif tool_call_name == "search_knowledge":
            logger.info(f"Agent: Decided to search knowledge base for: '{search_query}'")
            docs = self.vector_store.similarity_search(search_query, k=6)
            rag_system_prompt = self._build_rag_prompt(docs)
            
            final_messages = [ChatMessage(role=Role.SYSTEM, content=rag_system_prompt)]
            history = self.memory.get_history(session_id)
            for msg in history[-4:]:
                final_messages.append(ChatMessage(role=Role(msg["role"]), content=msg["content"]))
            final_messages.append(ChatMessage(role=Role.USER, content=query))
            
            request = ChatCompletionRequest(
                model=llm_settings.DEFAULT_MODEL,
                messages=final_messages,
                temperature=0.0,
                stream=False
            )
            response = await self.llm_provider.generate_chat(request)
            reply = response.choices[0].message.content
        elif tool_call_name == "search_web":
            logger.info(f"Agent: Decided to search web for: '{search_query}'")
            web_results = self.web_search.search(search_query, max_results=5)
            web_system_prompt = self._build_web_search_prompt(web_results)
            
            final_messages = [ChatMessage(role=Role.SYSTEM, content=web_system_prompt)]
            history = self.memory.get_history(session_id)
            for msg in history[-4:]:
                final_messages.append(ChatMessage(role=Role(msg["role"]), content=msg["content"]))
            final_messages.append(ChatMessage(role=Role.USER, content=query))
            
            request = ChatCompletionRequest(
                model=llm_settings.DEFAULT_MODEL,
                messages=final_messages,
                temperature=0.0,
                stream=False
            )
            response = await self.llm_provider.generate_chat(request)
            reply = response.choices[0].message.content
        else:
            logger.info("Agent: Decided to reply directly (No search tool used)")
            reply = direct_reply
            
        self.memory.add_message(session_id, "user", query)
        self.memory.add_message(session_id, "assistant", reply)
        return reply

    async def stream_chat(self, query: str, session_id: str = "default") -> AsyncGenerator[str, None]:
        """
        AI Agent Chat with Streaming and Multi-Tool support.
        """
        agent_messages = self._prepare_agent_messages(session_id, query)
        
        from ..llm.schemas import Tool, ToolType, FunctionDefinition
        search_knowledge_tool = Tool(
            type=ToolType.FUNCTION,
            function=FunctionDefinition(
                name="search_knowledge",
                description="Tìm kiếm trong tài liệu, quy định, chính sách, và thông tin nội bộ của công ty.",
                parameters={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Từ khóa hoặc câu hỏi trực tiếp để tra cứu tài liệu (ví dụ: 'Phan Văn Thành', 'CV Phan Văn Thành', 'chính sách nghỉ phép', tránh dùng từ chung chung mô tả như 'Tên của CV của người dùng')."
                        }
                    },
                    "required": ["query"]
                }
            )
        )
        
        search_web_tool = Tool(
            type=ToolType.FUNCTION,
            function=FunctionDefinition(
                name="search_web",
                description="Tìm kiếm thông tin thời gian thực ngoài Internet như tin tức, thời tiết, sự kiện xã hội, lập trình, công nghệ, hoặc kiến thức thế giới.",
                parameters={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Từ khóa tìm kiếm rút gọn, tối ưu hóa tối đa cho DuckDuckGo, không chứa câu hỏi hay từ ngữ hội thoại dài dòng (ví dụ: thay vì 'hãy tìm tin tức mới nhất về AI tuần này', chỉ truyền 'tin tức AI mới nhất' hoặc 'thị trường trí tuệ nhân tạo')."
                        }
                    },
                    "required": ["query"]
                }
            )
        )
        
        use_fallback = False
        tool_call_name = None
        search_query = query
        direct_reply = ""
        
        try:
            request = ChatCompletionRequest(
                model=llm_settings.DEFAULT_MODEL,
                messages=agent_messages,
                temperature=0.0,
                tools=[search_knowledge_tool, search_web_tool],
                stream=False
            )
            response = await self.llm_provider.generate_chat(request)
            message = response.choices[0].message
            
            if message.tool_calls:
                tool_call = message.tool_calls[0]
                tool_call_name = tool_call.function.name
                import json
                try:
                    args = json.loads(tool_call.function.arguments)
                    search_query = args.get("query", query)
                except Exception:
                    search_query = query
            else:
                direct_reply = message.content or ""
                
        except Exception as e:
            logger.warning(f"Agent: Tool calling failed ({e}). Falling back to traditional RAG.")
            use_fallback = True
            
        self.memory.add_message(session_id, "user", query)
        full_reply = ""
        
        if use_fallback:
            search_query = await self._rewrite_query(query, session_id)
            docs = self.vector_store.similarity_search(search_query, k=6)
            final_messages = self._prepare_messages(session_id, query, docs)
            
            request = ChatCompletionRequest(
                model=llm_settings.DEFAULT_MODEL,
                messages=final_messages,
                temperature=0.0,
                stream=True
            )
            generator = self.llm_provider.stream_chat(request)
            async for chunk in generator:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_reply += content
                    yield content
                    
        elif tool_call_name == "search_knowledge":
            logger.info(f"Agent: Decided to search knowledge base for: '{search_query}'")
            yield f"⚙️ [ACTION] Đang tra cứu tài liệu nội bộ với từ khóa: '{search_query}'...\n\n"
            docs = self.vector_store.similarity_search(search_query, k=6)
            rag_system_prompt = self._build_rag_prompt(docs)
            
            final_messages = [ChatMessage(role=Role.SYSTEM, content=rag_system_prompt)]
            history = self.memory.get_history(session_id)
            for msg in history[-5:-1]:
                final_messages.append(ChatMessage(role=Role(msg["role"]), content=msg["content"]))
            final_messages.append(ChatMessage(role=Role.USER, content=query))
            
            request = ChatCompletionRequest(
                model=llm_settings.DEFAULT_MODEL,
                messages=final_messages,
                temperature=0.0,
                stream=True
            )
            generator = self.llm_provider.stream_chat(request)
            async for chunk in generator:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_reply += content
                    yield content
                    
        elif tool_call_name == "search_web":
            logger.info(f"Agent: Decided to search web for: '{search_query}'")
            yield f"⚙️ [ACTION] Đang quét mạng Internet tìm kiếm: '{search_query}'...\n\n"
            
            # Execute web search
            web_results = self.web_search.search(search_query, max_results=5)
            web_system_prompt = self._build_web_search_prompt(web_results)
            
            final_messages = [ChatMessage(role=Role.SYSTEM, content=web_system_prompt)]
            history = self.memory.get_history(session_id)
            for msg in history[-5:-1]:
                final_messages.append(ChatMessage(role=Role(msg["role"]), content=msg["content"]))
            final_messages.append(ChatMessage(role=Role.USER, content=query))
            
            request = ChatCompletionRequest(
                model=llm_settings.DEFAULT_MODEL,
                messages=final_messages,
                temperature=0.0,
                stream=True
            )
            generator = self.llm_provider.stream_chat(request)
            async for chunk in generator:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_reply += content
                    yield content
        else:
            logger.info("Agent: Decided to reply directly (No search tool used)")
            import asyncio
            chunk_size = 4
            for i in range(0, len(direct_reply), chunk_size):
                chunk = direct_reply[i:i+chunk_size]
                full_reply += chunk
                yield chunk
                await asyncio.sleep(0.01)
                
        self.memory.add_message(session_id, "assistant", full_reply)
