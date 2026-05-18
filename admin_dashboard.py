import streamlit as st
import requests
import json
import uuid
import os

# Constants
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api")

# --- PAGE CONFIG (Premium Enterprise Minimalist Design) ---
st.set_page_config(
    page_title="Enterprise AI - Admin Portal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS (SaaS Premium & Minimalist Aesthetic) ---
st.markdown("""
<style>
    /* Global Reset & Typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
        background-color: #f8fafc !important;
        color: #0f172a !important;
    }
    
    /* Document Headers */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif !important;
        color: #0f172a !important;
        font-weight: 600 !important;
        letter-spacing: -0.01em !important;
    }
    
    /* Sidebar Styling - Premium Corporate Slate */
    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e2e8f0 !important;
    }
    
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #334155 !important;
    }
    
    /* Button Customization - Professional Corporate Slate & Blue */
    .stButton > button {
        border-radius: 6px !important;
        padding: 8px 16px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease-in-out !important;
    }
    
    /* Primary Buttons (Action triggers) */
    .stButton > button[kind="primary"] {
        background-color: #2563eb !important;
        color: #ffffff !important;
        border: 1px solid #2563eb !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05) !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #1d4ed8 !important;
        border-color: #1d4ed8 !important;
        color: #ffffff !important;
    }
    .stButton > button[kind="primary"]:active {
        background-color: #1e40af !important;
        border-color: #1e40af !important;
    }
    
    /* Secondary Buttons (Tab navigation / defaults) */
    .stButton > button[kind="secondary"] {
        background-color: #ffffff !important;
        color: #334155 !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05) !important;
    }
    .stButton > button[kind="secondary"]:hover {
        background-color: #f8fafc !important;
        color: #0f172a !important;
        border-color: #cbd5e1 !important;
    }
    .stButton > button[kind="secondary"]:active {
        background-color: #f1f5f9 !important;
        border-color: #cbd5e1 !important;
    }
    
    /* Streamlit File Uploader Box Styling */
    section[data-testid="stFileUploadDropzone"] {
        border: 1px dashed #cbd5e1 !important;
        background-color: #ffffff !important;
        border-radius: 8px !important;
        padding: 24px !important;
        transition: border-color 0.2s ease !important;
    }
    section[data-testid="stFileUploadDropzone"]:hover {
        border-color: #2563eb !important;
    }
    
    /* Chat System Custom Containers */
    .stChatMessage {
        border-radius: 8px !important;
        padding: 16px !important;
        margin-bottom: 16px !important;
        border: 1px solid #e2e8f0 !important;
        background-color: #ffffff !important;
    }
    
    /* User Message Bubble */
    .stChatMessage[data-testid="chat-message-user"] {
        background-color: #f1f5f9 !important;
        border-color: #e2e8f0 !important;
    }
    .stChatMessage[data-testid="chat-message-user"] p,
    .stChatMessage[data-testid="chat-message-user"] li,
    .stChatMessage[data-testid="chat-message-user"] strong {
        color: #0f172a !important;
    }
    
    /* Assistant Message Bubble */
    .stChatMessage[data-testid="chat-message-assistant"] {
        background-color: #ffffff !important;
        border-left: 4px solid #2563eb !important;
    }
    
    /* Custom Alerts info box */
    .stAlert {
        border-radius: 6px !important;
        font-size: 14px !important;
        border: 1px solid #e2e8f0 !important;
        background-color: #f8fafc !important;
        color: #334155 !important;
        box-shadow: none !important;
    }
    
    /* Remove default Streamlit decoration line */
    header {
        visibility: hidden;
    }
    #MainMenu {
        visibility: hidden;
    }
    footer {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR (Session Management) ---
with st.sidebar:
    st.markdown("""
    <div style='display: flex; align-items: center; gap: 12px; margin-top: 5px; margin-bottom: 15px;'>
        <div style='background-color: #0f172a; width: 36px; height: 36px; border-radius: 6px; display: flex; align-items: center; justify-content: center; color: white; font-weight: 800; font-size: 18px; font-family: "Inter", sans-serif;'>E</div>
        <div style='display: flex; flex-direction: column;'>
            <span style='font-size: 16px; font-weight: 700; color: #0f172a; line-height: 1.2;'>Enterprise AI</span>
            <span style='font-size: 11px; color: #64748b;'>Admin & Agent Portal</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # --- SESSION MANAGEMENT CONFIG ---
    if "session_id" not in st.session_state:
        q_params = st.query_params
        if "session_id" in q_params:
            st.session_state.session_id = q_params["session_id"]
        else:
            st.session_state.session_id = str(uuid.uuid4())
            st.query_params["session_id"] = st.session_state.session_id

    # Fetch all active sessions from SQLite via Backend API (Cached)
    if "active_sessions" not in st.session_state:
        try:
            sess_response = requests.get(f"{API_BASE_URL}/sessions")
            if sess_response.status_code == 200:
                st.session_state.active_sessions = sess_response.json().get("sessions", [])
            else:
                st.session_state.active_sessions = []
        except Exception:
            st.session_state.active_sessions = []
            
    active_sessions = st.session_state.active_sessions

    # Ensure current session is in the list
    if st.session_state.session_id not in active_sessions:
        active_sessions.insert(0, st.session_state.session_id)

    # 1. New Chat Button - Prominent, clean, primary styling
    if st.button("➕ Tạo phiên Chat mới", use_container_width=True, type="primary"):
        st.session_state.session_id = str(uuid.uuid4())
        st.query_params["session_id"] = st.session_state.session_id
        if "messages" in st.session_state:
            st.session_state.messages = []
        if "active_sessions" in st.session_state:
            del st.session_state.active_sessions
        st.rerun()

    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px;'>Lịch sử hội thoại</p>", unsafe_allow_html=True)

    # 2. Render list of sessions (ChatGPT style)
    # Render at most the latest 8 sessions to keep sidebar neat
    for sess in active_sessions[:8]:
        is_current = (sess == st.session_state.session_id)
        short_id = sess[:8].upper()
        
        # Premium visual indicators
        if is_current:
            btn_label = f"✨ Phiên {short_id} (Hiện tại)"
            btn_type = "primary"
        else:
            btn_label = f"💬 Phiên {short_id}"
            btn_type = "secondary"
            
        if st.button(btn_label, key=f"sess_btn_{sess}", use_container_width=True, type=btn_type):
            if sess != st.session_state.session_id:
                st.session_state.session_id = sess
                st.query_params["session_id"] = sess
                if "messages" in st.session_state:
                    del st.session_state.messages
                st.rerun()

    if len(active_sessions) > 8:
        st.markdown(f"<p style='font-size: 11px; color: #94a3b8; text-align: center; font-style: italic; margin-top: 5px;'>Và {len(active_sessions) - 8} phiên khác...</p>", unsafe_allow_html=True)

    st.divider()

    # 3. Clean and neat "Xóa phiên hiện tại" at the bottom
    if st.button("🗑️ Xóa phiên hiện tại", use_container_width=True):
        try:
            # Send DELETE request to FastAPI to clear session history
            del_sess_resp = requests.delete(f"{API_BASE_URL}/history/{st.session_state.session_id}")
            if del_sess_resp.status_code == 200:
                st.toast("Đã xóa phiên chat thành công!")
            
            # Switch to a new session
            st.session_state.session_id = str(uuid.uuid4())
            st.query_params["session_id"] = st.session_state.session_id
            if "messages" in st.session_state:
                st.session_state.messages = []
            if "active_sessions" in st.session_state:
                del st.session_state.active_sessions
            st.rerun()
        except Exception as e:
            st.error(f"Lỗi: {str(e)}")

# --- HERO SECTION ---
st.markdown("""
<div style='background-color: #ffffff; padding: 28px 32px; border-radius: 8px; border: 1px solid #e2e8f0; border-left: 5px solid #0f172a; margin-bottom: 24px;'>
    <h1 style='color: #0f172a; margin: 0; font-size: 2.0rem; font-weight: 700; letter-spacing: -0.02em;'>Enterprise AI Platform</h1>
    <p style='color: #475569; margin: 6px 0 0 0; font-size: 1.05rem; font-weight: 400;'>Hệ thống quản trị tri thức RAG & Multi-Tool AI Agent doanh nghiệp.</p>
</div>
""", unsafe_allow_html=True)

# --- KPI METRICS ---
m_col1, m_col2, m_col3 = st.columns(3)
with m_col1:
    st.markdown("""
    <div style='background-color: #ffffff; padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0; border-top: 3px solid #0f172a;'>
        <h5 style='color: #64748b; margin: 0; font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600;'>Vector Database</h5>
        <h3 style='color: #0f172a; margin: 8px 0 0 0; font-size: 20px; font-weight: 700;'>ChromaDB</h3>
        <p style='color: #16a34a; margin: 6px 0 0 0; font-size: 12px; font-weight: 500;'>Persisted & Embedded</p>
    </div>
    """, unsafe_allow_html=True)
with m_col2:
    st.markdown("""
    <div style='background-color: #ffffff; padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0; border-top: 3px solid #2563eb;'>
        <h5 style='color: #64748b; margin: 0; font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600;'>Short-term Memory</h5>
        <h3 style='color: #0f172a; margin: 8px 0 0 0; font-size: 20px; font-weight: 700;'>SQLite Database</h3>
        <p style='color: #2563eb; margin: 6px 0 0 0; font-size: 12px; font-weight: 500;'>Auto-sync Chat History</p>
    </div>
    """, unsafe_allow_html=True)
with m_col3:
    st.markdown(f"""
    <div style='background-color: #ffffff; padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0; border-top: 3px solid #475569;'>
        <h5 style='color: #64748b; margin: 0; font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600;'>System Status</h5>
        <h3 style='color: #0f172a; margin: 8px 0 0 0; font-size: 20px; font-weight: 700;'>Agent Active</h3>
        <p style='color: #64748b; margin: 6px 0 0 0; font-size: 12px; font-weight: 500;'>Tool-Calling Enabled</p>
    </div>
    """, unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Knowledge Base"

# Styled custom tab navigation bar
nav_col1, nav_col2, _ = st.columns([1, 1, 2])
with nav_col1:
    if st.button("Knowledge Base", use_container_width=True, type="primary" if st.session_state.active_tab == "Knowledge Base" else "secondary"):
        st.session_state.active_tab = "Knowledge Base"
        st.rerun()
with nav_col2:
    if st.button("AI Sandbox & Chat", use_container_width=True, type="primary" if st.session_state.active_tab == "AI Sandbox & Chat" else "secondary"):
        st.session_state.active_tab = "AI Sandbox & Chat"
        st.rerun()

st.divider()

if st.session_state.active_tab == "Knowledge Base":
    st.markdown("<h3 style='margin-bottom: 8px;'>Tải lên dữ liệu doanh nghiệp</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; font-size: 14px; margin-bottom: 20px;'>Hệ thống hỗ trợ các định dạng PDF, XLSX, XLS và TXT. Tài liệu sau khi tải lên sẽ được phân tích, sinh vector nhúng và lưu trữ vào cơ sở dữ liệu tri thức nội bộ.</p>", unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Chọn tệp tài liệu nguồn", type=["pdf", "xlsx", "xls", "txt"])
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Bắt đầu lập chỉ mục (Indexing)", type="primary"):
        if uploaded_file is not None:
            with st.spinner("Đang tải lên và xử lý tài liệu vào VectorDB..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    response = requests.post(f"{API_BASE_URL}/upload", files=files)
                    
                    if response.status_code == 200:
                        res_data = response.json()
                        st.toast(f"Tải lên thành công! Đã xử lý {res_data.get('chunks_indexed', 0)} đoạn văn bản.")
                        st.success(f"**Thành công:** Tài liệu '{uploaded_file.name}' đã được phân tích thành {res_data.get('chunks_indexed', 0)} đoạn ngữ cảnh và lưu trữ vào VectorDB thành công!")
                        if "indexed_docs" in st.session_state:
                            del st.session_state.indexed_docs
                        st.rerun()
                    else:
                        st.error(f"Lỗi khi xử lý: {response.text}")
                except Exception as e:
                    st.error(f"Lỗi kết nối tới Server: {str(e)}")
        else:
            st.warning("Vui lòng chọn một tệp hợp lệ trước khi bắt đầu!")

    st.divider()
    st.markdown("<h3 style='margin-bottom: 8px;'>Cơ sở dữ liệu tri thức hiện tại</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; font-size: 14px; margin-bottom: 20px;'>Danh sách các tài liệu đã được VectorDB lưu trữ và lập chỉ mục vĩnh viễn.</p>", unsafe_allow_html=True)
    
    # Fetch and cache indexed documents to prevent blocking HTTP requests on every chat rerun
    if "indexed_docs" not in st.session_state:
        try:
            doc_response = requests.get(f"{API_BASE_URL}/documents")
            if doc_response.status_code == 200:
                st.session_state.indexed_docs = doc_response.json().get("documents", [])
            else:
                st.session_state.indexed_docs = []
        except Exception:
            st.session_state.indexed_docs = []
            
    docs = st.session_state.indexed_docs

    if docs:
        for idx, doc in enumerate(docs):
            # Show a very clean minimalist card for each document
            st.markdown(f"""
            <div style='background-color: #ffffff; padding: 12px 16px; border-radius: 6px; border: 1px solid #e2e8f0; margin-bottom: 8px; display: flex; align-items: center; justify-content: space-between;'>
                <div style='display: flex; align-items: center; gap: 10px;'>
                    <span style='font-size: 16px;'>📄</span>
                    <span style='font-size: 14px; font-weight: 500; color: #0f172a;'>{doc}</span>
                </div>
                <span style='background-color: #dcfce7; color: #16a34a; font-size: 11px; padding: 2px 8px; border-radius: 12px; font-weight: 600;'>Đã chỉ mục</span>
            </div>
            """, unsafe_allow_html=True)
        
        # Show a delete all button
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        if st.button("Xóa toàn bộ cơ sở tri thức", type="secondary"):
            with st.spinner("Đang xóa dữ liệu..."):
                try:
                    del_response = requests.delete(f"{API_BASE_URL}/documents")
                    if del_response.status_code == 200:
                        st.toast("Đã xóa toàn bộ tài liệu thành công!")
                        if "indexed_docs" in st.session_state:
                            del st.session_state.indexed_docs
                        st.rerun()
                    else:
                        st.error("Lỗi khi xóa tài liệu.")
                except Exception as e:
                    st.error(f"Lỗi kết nối tới Server: {str(e)}")
    else:
        st.markdown("<p style='color: #64748b; font-size: 14px; font-style: italic;'>Chưa có tài liệu nào được lập chỉ mục trong hệ thống.</p>", unsafe_allow_html=True)


else:
    st.markdown("<h3 style='margin-bottom: 8px;'>AI Sandbox & Agent Simulator</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; font-size: 14px; margin-bottom: 20px;'>Kiểm thử trực tiếp cơ chế Tool Calling của Agent. Agent tự động nhận thức khi nào cần tìm kiếm dữ liệu nội bộ (RAG), khi nào cần tra cứu trực tuyến (Web Search), và khi nào cần phản hồi trực tiếp.</p>", unsafe_allow_html=True)
    
    # Load history from SQLite memory on startup/refresh
    if "messages" not in st.session_state:
        try:
            response = requests.get(f"{API_BASE_URL}/history/{st.session_state.session_id}")
            if response.status_code == 200:
                st.session_state.messages = response.json().get("history", [])
            else:
                st.session_state.messages = []
        except Exception:
            st.session_state.messages = []

    # Display Suggestions Grid ONLY when there are no messages
    suggestion_clicked = None
    if not st.session_state.messages:
        st.markdown("""
        <div style='text-align: center; margin-top: 25px; margin-bottom: 15px;'>
            <p style='color: #64748b; font-size: 14px; font-weight: 500;'>Gợi ý câu hỏi kiểm thử hệ thống:</p>
        </div>
        """, unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Tra cứu quy chế nghỉ phép của doanh nghiệp", use_container_width=True, key="sug_policy"):
                suggestion_clicked = "Quy định nghỉ phép của công ty là gì?"
            if st.button("Trò chuyện xã giao thông thường (Chitchat)", use_container_width=True, key="sug_hi"):
                suggestion_clicked = "Chào bạn! Rất vui được gặp bạn."
        with col2:
            if st.button("Hỏi đáp thông tin trên CV / Hồ sơ năng lực", use_container_width=True, key="sug_cv"):
                suggestion_clicked = "Nội dung CV của tôi có gì nổi bật?"
            if st.button("Tìm kiếm thông tin thời tiết trực tuyến (Web Search)", use_container_width=True, key="sug_weather"):
                suggestion_clicked = "Thời tiết Hà Nội hôm nay thế nào?"

    # Render Chat History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input and Suggestion Action Handler
    prompt = None
    chat_prompt = st.chat_input("Nhập câu hỏi tại đây...")
    
    if chat_prompt:
        prompt = chat_prompt
    elif suggestion_clicked:
        prompt = suggestion_clicked

    if prompt:
        # Append User Message immediately and rerun to display it
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()

    # Generation Block
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        user_prompt = st.session_state.messages[-1]["content"]
        
        with st.chat_message("assistant"):
            action_container = st.empty()
            message_placeholder = st.empty()
            full_response = ""
            
            with st.spinner("AI Agent đang lập kế hoạch..."):
                try:
                    req_payload = {
                        "message": user_prompt,
                        "session_id": st.session_state.session_id
                    }
                    response = requests.post(f"{API_BASE_URL}/chat/stream", json=req_payload, stream=True)
                    
                    for line in response.iter_lines():
                        if line:
                            decoded_line = line.decode("utf-8")
                            if decoded_line.startswith("data: "):
                                data_str = decoded_line.replace("data: ", "")
                                try:
                                    # Try parsing as JSON to safely handle escaped newlines
                                    data_json = json.loads(data_str)
                                    msg_type = data_json.get("type")
                                    content = data_json.get("content", "")
                                    
                                    if msg_type == "done":
                                        break
                                    elif msg_type == "error":
                                        full_response += f"\n\n**Lỗi:** {content}"
                                        break
                                    elif msg_type == "action":
                                        action_container.info(f"⚙️ **Agent Action:** {content.strip()}")
                                    elif msg_type == "content":
                                        full_response += content
                                        message_placeholder.markdown(full_response + "▌")
                                except Exception:
                                    # Fallback for legacy plain text SSE chunks
                                    if data_str == "[DONE]":
                                        break
                                    elif data_str.startswith("[ERROR]"):
                                        full_response += f"\n\n**Lỗi:** {data_str}"
                                        break
                                    elif data_str.startswith("⚙️ [ACTION]"):
                                        action_text = data_str.replace("⚙️ [ACTION] ", "").strip()
                                        action_container.info(f"⚙️ **Agent Action:** {action_text}")
                                    else:
                                        full_response += data_str
                                        message_placeholder.markdown(full_response + "▌")
                                    
                    message_placeholder.markdown(full_response)
                except Exception as e:
                    full_response = f"Lỗi kết nối tới Server: {str(e)}"
                    message_placeholder.error(full_response)
                    
        # Save response to history and rerun to lock the state
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.rerun()
