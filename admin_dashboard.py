import streamlit as st
import requests
import json
import uuid
import os

# Constants
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api")

# --- PAGE CONFIG (Premium Developer Minimalist Design) ---
st.set_page_config(
    page_title="Enterprise AI - Portal",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS (SaaS Premium & Minimalist Aesthetic) ---
st.markdown("""
<style>
    /* Global Reset & Typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
        background-color: #fafafa !important;
        color: #18181b !important;
    }
    
    /* Document Headers */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif !important;
        color: #09090b !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em !important;
    }
    
    /* Sidebar Styling - Premium Off-White Slate */
    section[data-testid="stSidebar"] {
        background-color: #fafafa !important;
        border-right: 1px solid #e4e4e7 !important;
    }
    
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #27272a !important;
    }
    
    /* Global Buttons Customization */
    .stButton > button {
        border-radius: 4px !important;
        padding: 6px 12px !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        border: 1px solid #e4e4e7 !important;
        background-color: #ffffff !important;
        color: #18181b !important;
        transition: all 0.15s ease !important;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.02) !important;
    }
    
    /* Sidebar Specific Button Refinements (VS Code / Git Tree style) */
    section[data-testid="stSidebar"] .stButton > button {
        background-color: transparent !important;
        border: 1px solid transparent !important;
        text-align: left !important;
        justify-content: flex-start !important;
        padding: 6px 12px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 13px !important;
        color: #52525b !important;
        box-shadow: none !important;
        margin-bottom: 3px !important;
        border-radius: 4px !important;
        width: 100% !important;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background-color: #f4f4f5 !important;
        color: #09090b !important;
        border-color: #e4e4e7 !important;
    }
    
    /* Sidebar Primary Action Buttons (Tạo phiên mới / Active Session) */
    section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background-color: #18181b !important;
        border: 1px solid #18181b !important;
        text-align: left !important;
        justify-content: flex-start !important;
        padding: 6px 12px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 13px !important;
        border-radius: 4px !important;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05) !important;
    }
    section[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
        background-color: #000000 !important;
        border-color: #000000 !important;
    }
    /* Force white text inside active primary buttons in sidebar */
    section[data-testid="stSidebar"] .stButton > button[kind="primary"] * {
        color: #ffffff !important;
        font-weight: 500 !important;
    }
    
    /* Main Content Action Buttons */
    .stButton > button[kind="primary"] {
        background-color: #18181b !important;
        color: #ffffff !important;
        border: 1px solid #18181b !important;
        border-radius: 4px !important;
        padding: 6px 12px !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #09090b !important;
        border-color: #09090b !important;
        color: #ffffff !important;
    }
    
    /* Streamlit File Uploader Box Styling */
    section[data-testid="stFileUploadDropzone"] {
        border: 1px dashed #d4d4d8 !important;
        background-color: #ffffff !important;
        border-radius: 4px !important;
        padding: 20px !important;
        transition: border-color 0.15s ease !important;
    }
    section[data-testid="stFileUploadDropzone"]:hover {
        border-color: #18181b !important;
    }
    
    /* Chat System Custom Containers */
    .stChatMessage {
        border-radius: 4px !important;
        padding: 14px 16px !important;
        margin-bottom: 12px !important;
        border: 1px solid #e4e4e7 !important;
        background-color: #ffffff !important;
    }
    
    /* User Message Bubble */
    .stChatMessage[data-testid="chat-message-user"] {
        background-color: #f4f4f5 !important;
        border-color: #e4e4e7 !important;
    }
    
    /* Assistant Message Bubble */
    .stChatMessage[data-testid="chat-message-assistant"] {
        background-color: #ffffff !important;
        border-left: 3px solid #18181b !important;
    }
    
    /* Divider lines refinement */
    hr {
        margin: 16px 0 !important;
        border-color: #e4e4e7 !important;
    }
    
    /* Custom Alerts info box */
    .stAlert {
        border-radius: 4px !important;
        font-size: 13px !important;
        border: 1px solid #e4e4e7 !important;
        background-color: #ffffff !important;
        color: #27272a !important;
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
    <div style='margin-bottom: 24px; padding-top: 8px;'>
        <p style='font-size: 10px; font-weight: 600; color: #a1a1aa; letter-spacing: 0.15em; text-transform: uppercase; margin: 0;'>SYSTEM CORE</p>
        <h2 style='font-size: 18px; font-weight: 700; color: #09090b; margin: 2px 0 0 0; letter-spacing: -0.02em;'>Enterprise AI</h2>
        <p style='font-size: 12px; color: #71717a; margin: 2px 0 0 0;'>RAG & Multi-Tool Engine</p>
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

    # 1. New Chat Button - Prominent, clean, primary styling (left-aligned)
    if st.button("+ Tạo phiên mới", use_container_width=True, type="primary"):
        st.session_state.session_id = str(uuid.uuid4())
        st.query_params["session_id"] = st.session_state.session_id
        if "messages" in st.session_state:
            st.session_state.messages = []
        if "active_sessions" in st.session_state:
            del st.session_state.active_sessions
        st.rerun()

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 10px; font-weight: 700; color: #a1a1aa; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px;'>HỘI THOẠI HOẠT ĐỘNG</p>", unsafe_allow_html=True)

    # 2. Render list of sessions (ChatGPT style)
    # Render at most the latest 8 sessions to keep sidebar neat
    for sess in active_sessions[:8]:
        is_current = (sess == st.session_state.session_id)
        short_id = sess[:8].lower()
        
        # Premium visual indicators
        if is_current:
            btn_label = f"• session-{short_id} (active)"
            btn_type = "primary"
        else:
            btn_label = f"  session-{short_id}"
            btn_type = "secondary"
            
        if st.button(btn_label, key=f"sess_btn_{sess}", use_container_width=True, type=btn_type):
            if sess != st.session_state.session_id:
                st.session_state.session_id = sess
                st.query_params["session_id"] = sess
                if "messages" in st.session_state:
                    del st.session_state.messages
                st.rerun()

    if len(active_sessions) > 8:
        st.markdown(f"<p style='font-size: 11px; color: #71717a; text-align: center; font-style: italic; margin-top: 5px;'>Và {len(active_sessions) - 8} phiên khác...</p>", unsafe_allow_html=True)

    st.divider()

    # 3. Clean and neat "Xóa phiên hiện tại" at the bottom
    if st.button("× Xóa phiên hiện tại", use_container_width=True, type="secondary"):
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

# --- BREADCRUMBS & HEADER ---
st.markdown("""
<div style='margin-bottom: 24px; padding-top: 6px;'>
    <p style='font-size: 10px; font-weight: 600; color: #a1a1aa; letter-spacing: 0.15em; text-transform: uppercase; margin: 0;'>SYSTEMS / RAG ENGINE / WORKSPACE</p>
    <h1 style='color: #09090b; margin: 4px 0 0 0; font-size: 26px; font-weight: 700; letter-spacing: -0.03em;'>Enterprise RAG Platform</h1>
    <p style='color: #71717a; margin: 4px 0 0 0; font-size: 13px; font-weight: 400;'>Hệ thống quản lý tri thức và mô phỏng tác vụ AI Agent nâng cao dành cho doanh nghiệp.</p>
</div>
""", unsafe_allow_html=True)


# --- SESSION-STATE PERSISTENT TABS ---
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Knowledge Base"

# Render tab button columns (Styled like flat segmented controls)
nav_col1, nav_col2, _ = st.columns([1, 1, 2])
with nav_col1:
    if st.button("Cơ sở tri thức (Knowledge Base)", use_container_width=True, type="primary" if st.session_state.active_tab == "Knowledge Base" else "secondary"):
        st.session_state.active_tab = "Knowledge Base"
        st.rerun()
with nav_col2:
    if st.button("Tương tác AI (Agent Sandbox)", use_container_width=True, type="primary" if st.session_state.active_tab == "AI Sandbox & Chat" else "secondary"):
        st.session_state.active_tab = "AI Sandbox & Chat"
        st.rerun()

st.divider()

if st.session_state.active_tab == "Knowledge Base":
    st.markdown("<h3 style='margin-top: 10px; margin-bottom: 4px; font-size: 16px; font-weight: 600;'>Tải lên dữ liệu doanh nghiệp</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #71717a; font-size: 13px; margin-bottom: 20px;'>Hỗ trợ các định dạng PDF, XLSX, XLS và TXT. Văn bản sẽ được phân tích, chia nhỏ đoạn ngữ cảnh và lập chỉ mục vào cơ sở dữ liệu Vector.</p>", unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Chọn tệp tài liệu nguồn", type=["pdf", "xlsx", "xls", "txt"], label_visibility="collapsed")
    
    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    if st.button("Lập chỉ mục tài liệu (Indexing)", type="primary"):
        if uploaded_file is not None:
            with st.spinner("Đang xử lý tài liệu vào VectorDB..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    response = requests.post(f"{API_BASE_URL}/upload", files=files)
                    
                    if response.status_code == 200:
                        res_data = response.json()
                        st.toast(f"Đã xử lý {res_data.get('chunks_indexed', 0)} đoạn văn bản.")
                        st.success(f"Tài liệu '{uploaded_file.name}' đã được phân tích thành {res_data.get('chunks_indexed', 0)} đoạn ngữ cảnh và lưu trữ vào VectorDB.")
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
    st.markdown("<h3 style='margin-bottom: 4px; font-size: 16px; font-weight: 600;'>Cơ sở dữ liệu tri thức hiện tại</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #71717a; font-size: 13px; margin-bottom: 20px;'>Danh sách các tài liệu hiện có trong VectorDB phục vụ cho tác vụ RAG.</p>", unsafe_allow_html=True)
    
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
            # Show a clean minimalist developer row
            st.markdown(f"""
            <div style='background-color: #ffffff; padding: 10px 14px; border-radius: 4px; border: 1px solid #e4e4e7; margin-bottom: 6px; display: flex; align-items: center; justify-content: space-between;'>
                <div style='display: flex; align-items: center; gap: 8px;'>
                    <span style='font-size: 12px; color: #71717a; font-family: monospace;'>[{idx+1:02d}]</span>
                    <span style='font-size: 13px; font-weight: 500; color: #09090b; font-family: monospace;'>{doc}</span>
                </div>
                <div style='display: flex; align-items: center; gap: 6px;'>
                    <span style='background-color: #10b981; width: 5px; height: 5px; border-radius: 50%; display: inline-block;'></span>
                    <span style='color: #10b981; font-size: 11px; font-family: monospace; font-weight: 500;'>INDEXED</span>
                </div>
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
        st.markdown("<p style='color: #71717a; font-size: 13px; font-style: italic;'>Chưa có tài liệu nào được lập chỉ mục trong hệ thống.</p>", unsafe_allow_html=True)


else:
    st.markdown("<h3 style='margin-top: 10px; margin-bottom: 4px; font-size: 16px; font-weight: 600;'>AI Sandbox & Agent Simulator</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #71717a; font-size: 13px; margin-bottom: 20px;'>Kiểm thử trực tiếp cơ chế Tool-Calling và khả năng tự quyết định (Orchestration) của AI Agent.</p>", unsafe_allow_html=True)
    
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
        <div style='margin-top: 10px; margin-bottom: 12px;'>
            <p style='color: #71717a; font-size: 11px; font-family: monospace; margin: 0;'>[RECOMMENDED TEST QUERIES]</p>
        </div>
        """, unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("$ run-query --topic corporate-travel-policy", use_container_width=True, key="sug_policy"):
                suggestion_clicked = "Chính sách thanh toán công tác phí và hỗ trợ lưu trú của công ty quy định như thế nào?"
            if st.button("$ run-query --topic resume-skills-analysis", use_container_width=True, key="sug_cv"):
                suggestion_clicked = "Phân tích các kỹ năng chuyên môn cốt lõi và các dự án tiêu biểu được đề cập trong hồ sơ năng lực của tôi."
        with col2:
            if st.button("$ run-query --topic web-market-research", use_container_width=True, key="sug_market"):
                suggestion_clicked = "Tìm kiếm thông tin trực tuyến và tóm tắt những diễn biến mới nhất về thị trường trí tuệ nhân tạo (AI) tuần này."
            if st.button("$ run-query --topic cross-tool-benchmarking", use_container_width=True, key="sug_benchmark"):
                suggestion_clicked = "So sánh định hướng công nghệ trong tài liệu giới thiệu nội bộ với xu hướng công nghệ thực tế hiện nay trên thị trường."

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
            
            with st.spinner("AI Agent đang phân tích..."):
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
                                        action_text = content.strip()
                                        action_container.markdown(f"""
                                        <div style='background-color: #f4f4f5; padding: 10px 14px; border-radius: 4px; border-left: 3px solid #18181b; font-family: monospace; font-size: 12px; color: #18181b; margin-bottom: 12px;'>
                                            <span style='color: #71717a;'>[EXECUTE_ACTION]</span> {action_text}
                                        </div>
                                        """, unsafe_allow_html=True)
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
                                        action_container.markdown(f"""
                                        <div style='background-color: #f4f4f5; padding: 10px 14px; border-radius: 4px; border-left: 3px solid #18181b; font-family: monospace; font-size: 12px; color: #18181b; margin-bottom: 12px;'>
                                            <span style='color: #71717a;'>[EXECUTE_ACTION]</span> {action_text}
                                        </div>
                                        """, unsafe_allow_html=True)
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
