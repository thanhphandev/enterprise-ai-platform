(function() {
    // 1. Core configurations
    const API_BASE = "http://localhost:8000/api";
    const SESSION_KEY = "enterprise_ai_widget_session";
    
    // Generate or retrieve session ID
    let sessionId = localStorage.getItem(SESSION_KEY);
    if (!sessionId) {
        sessionId = "sess_" + Math.random().toString(36).substring(2, 15);
        localStorage.setItem(SESSION_KEY, sessionId);
    }

    // 2. Inject Google Fonts & Styles
    const fontLink = document.createElement("link");
    fontLink.rel = "stylesheet";
    fontLink.href = "https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap";
    document.head.appendChild(fontLink);

    const style = document.createElement("style");
    style.textContent = `
        /* Premium Standalone Reset */
        .ai-widget-wrapper {
            font-family: 'Outfit', sans-serif;
            position: fixed;
            bottom: 24px;
            right: 24px;
            z-index: 999999;
            display: flex;
            flex-direction: column;
            align-items: flex-end;
        }

        /* Floating Bubble with Pulsing Ring */
        .ai-widget-bubble {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%);
            box-shadow: 0 8px 32px rgba(79, 70, 229, 0.4);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            position: relative;
        }

        .ai-widget-bubble:hover {
            transform: scale(1.1) rotate(5deg);
            box-shadow: 0 12px 40px rgba(79, 70, 229, 0.6);
        }

        .ai-widget-bubble::after {
            content: '';
            position: absolute;
            width: 100%;
            height: 100%;
            border-radius: 50%;
            border: 2px solid #4f46e5;
            top: 0;
            left: 0;
            animation: ai-bubble-pulse 2s infinite;
            opacity: 0;
            pointer-events: none;
        }

        @keyframes ai-bubble-pulse {
            0% { transform: scale(1); opacity: 0.6; }
            100% { transform: scale(1.4); opacity: 0; }
        }

        .ai-widget-bubble svg {
            width: 28px;
            height: 28px;
            fill: white;
            transition: all 0.3s ease;
        }

        /* Elegant Chat Window with Glassmorphism */
        .ai-widget-window {
            width: 380px;
            height: 580px;
            border-radius: 24px;
            background: rgba(15, 23, 42, 0.95);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            margin-bottom: 16px;
            transform: scale(0.9) translateY(20px);
            opacity: 0;
            pointer-events: none;
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            transform-origin: bottom right;
        }

        .ai-widget-window.open {
            transform: scale(1) translateY(0);
            opacity: 1;
            pointer-events: auto;
        }

        /* Premium Header */
        .ai-widget-header {
            padding: 20px;
            background: linear-gradient(135deg, rgba(79, 70, 229, 0.1) 0%, rgba(6, 116, 212, 0.05) 100%);
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .ai-widget-header-info {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .ai-widget-header-avatar {
            width: 40px;
            height: 40px;
            border-radius: 12px;
            background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
        }

        .ai-widget-header-title {
            color: #f8fafc;
            font-size: 16px;
            font-weight: 600;
            margin: 0;
        }

        .ai-widget-header-subtitle {
            color: #94a3b8;
            font-size: 11px;
            margin: 2px 0 0 0;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .ai-widget-status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #10b981;
            box-shadow: 0 0 8px #10b981;
            display: inline-block;
            animation: ai-dot-pulse 1.5s infinite;
        }

        @keyframes ai-dot-pulse {
            0% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.2); opacity: 0.5; }
            100% { transform: scale(1); opacity: 1; }
        }

        .ai-widget-close {
            background: none;
            border: none;
            color: #94a3b8;
            cursor: pointer;
            padding: 4px;
            border-radius: 8px;
            transition: all 0.2s ease;
        }

        .ai-widget-close:hover {
            color: #f1f5f9;
            background: rgba(255, 255, 255, 0.05);
        }

        /* Message Display Container */
        .ai-widget-body {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 16px;
            scroll-behavior: smooth;
        }

        .ai-widget-body::-webkit-scrollbar {
            width: 4px;
        }

        .ai-widget-body::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 2px;
        }

        /* Message Bubbles */
        .ai-widget-msg {
            max-width: 80%;
            padding: 12px 16px;
            border-radius: 16px;
            font-size: 14px;
            line-height: 1.5;
            color: #e2e8f0;
            word-wrap: break-word;
            animation: ai-fade-in 0.3s ease forwards;
        }

        @keyframes ai-fade-in {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .ai-widget-msg.user {
            background: #4f46e5;
            color: white;
            align-self: flex-end;
            border-bottom-right-radius: 4px;
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.25);
        }

        .ai-widget-msg.bot {
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.04);
            align-self: flex-start;
            border-bottom-left-radius: 4px;
        }

        /* Tool Action Log Pulse */
        .ai-widget-action {
            display: flex;
            align-items: center;
            gap: 8px;
            background: rgba(245, 158, 11, 0.08);
            border: 1px dashed rgba(245, 158, 11, 0.2);
            color: #fbbf24;
            padding: 10px 14px;
            border-radius: 12px;
            font-size: 12px;
            align-self: flex-start;
            animation: ai-fade-in 0.3s ease forwards;
            max-width: 85%;
        }

        .ai-widget-action-icon {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #fbbf24;
            box-shadow: 0 0 8px #fbbf24;
            animation: ai-dot-pulse 1s infinite;
        }

        /* Message Styles for Lists & Code */
        .ai-widget-msg ul, .ai-widget-msg ol {
            margin: 6px 0;
            padding-left: 20px;
        }

        .ai-widget-msg li {
            margin-bottom: 4px;
        }

        .ai-widget-msg strong {
            color: white;
            font-weight: 600;
        }

        .ai-widget-msg code {
            font-family: monospace;
            background: rgba(255, 255, 255, 0.1);
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 12px;
        }

        /* Input Controls */
        .ai-widget-footer {
            padding: 16px;
            background: rgba(15, 23, 42, 0.8);
            border-top: 1px solid rgba(255, 255, 255, 0.05);
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .ai-widget-input-wrapper {
            display: flex;
            align-items: center;
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 14px;
            padding: 4px 8px 4px 14px;
            transition: all 0.2s ease;
        }

        .ai-widget-input-wrapper:focus-within {
            border-color: #4f46e5;
            background: rgba(255, 255, 255, 0.05);
            box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.2);
        }

        .ai-widget-input {
            flex: 1;
            background: none;
            border: none;
            outline: none;
            color: #f1f5f9;
            font-size: 14px;
            padding: 8px 0;
            font-family: inherit;
        }

        .ai-widget-input::placeholder {
            color: #475569;
        }

        .ai-widget-send {
            width: 36px;
            height: 36px;
            border-radius: 10px;
            background: #4f46e5;
            border: none;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s ease;
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.2);
        }

        .ai-widget-send:hover {
            background: #4338ca;
            transform: scale(1.05);
        }

        .ai-widget-send svg {
            width: 16px;
            height: 16px;
            fill: white;
        }

        .ai-widget-send:disabled {
            background: rgba(255, 255, 255, 0.05);
            box-shadow: none;
            cursor: not-allowed;
        }

        .ai-widget-brand {
            font-size: 10px;
            color: #475569;
            text-align: center;
            margin: 0;
        }

        .ai-widget-brand a {
            color: #64748b;
            text-decoration: none;
            transition: color 0.2s ease;
        }

        .ai-widget-brand a:hover {
            color: #94a3b8;
        }
    `;
    document.head.appendChild(style);

    // 3. Create DOM Layout
    const wrapper = document.createElement("div");
    wrapper.className = "ai-widget-wrapper";

    wrapper.innerHTML = `
        <div class="ai-widget-window" id="aiWidgetWindow">
            <div class="ai-widget-header">
                <div class="ai-widget-header-info">
                    <div class="ai-widget-header-avatar">
                        <svg viewBox="0 0 24 24" width="20" height="20">
                            <path d="M12 2C6.48 2 2 6.48 2 12c0 3.06 1.4 5.75 3.57 7.55-.26-.81-.37-1.63-.37-2.55 0-3.31 2.69-6 6-6h.5v-1.5c0-.83.67-1.5 1.5-1.5s1.5.67 1.5 1.5v1.5h.5c3.31 0 6 2.69 6 6 0 .92-.11 1.74-.37 2.55C20.6 17.75 22 15.06 22 12c0-5.52-4.48-10-10-10zm2.5 14c-.83 0-1.5-.67-1.5-1.5v-1.5h-2v1.5c0 .83-.67 1.5-1.5 1.5s-1.5-.67-1.5-1.5V13c0-.55-.45-1-1-1s-1 .45-1 1v1.5c0 2.48 2.02 4.5 4.5 4.5h4c2.48 0 4.5-2.02 4.5-4.5V13c0-.55-.45-1-1-1s-1 .45-1 1v1.5c0 .83-.67 1.5-1.5 1.5z"/>
                        </svg>
                    </div>
                    <div>
                        <h4 class="ai-widget-header-title">Enterprise AI Assistant</h4>
                        <p class="ai-widget-header-subtitle">
                            <span class="ai-widget-status-dot"></span> Sẵn sàng phản hồi
                        </p>
                    </div>
                </div>
                <button class="ai-widget-close" id="aiWidgetClose" title="Thu nhỏ">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </button>
            </div>
            <div class="ai-widget-body" id="aiWidgetBody">
                <div class="ai-widget-msg bot">
                    Xin chào! Tôi là **Trợ lý AI Doanh nghiệp**. Bạn cần tôi giúp gì về tài liệu, quy định, hay các thắc mắc chuyên sâu hôm nay?
                </div>
            </div>
            <div class="ai-widget-footer">
                <div class="ai-widget-input-wrapper">
                    <input type="text" class="ai-widget-input" id="aiWidgetInput" placeholder="Nhập câu hỏi tại đây..." autocomplete="off">
                    <button class="ai-widget-send" id="aiWidgetSend">
                        <svg viewBox="0 0 24 24">
                            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                        </svg>
                    </button>
                </div>
                <p class="ai-widget-brand">Powered by <a href="#" target="_blank">Enterprise AI Agent</a></p>
            </div>
        </div>
        
        <div class="ai-widget-bubble" id="aiWidgetBubble" title="Chat với AI Assistant">
            <svg viewBox="0 0 24 24" id="aiBubbleIcon">
                <path d="M20 2H4c-1.1 0-1.99.9-1.99 2L2 22l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zM6 9h12v2H6V9zm8 5H6v-2h8v2zm4-6H6V6h12v2z"/>
            </svg>
        </div>
    `;

    document.body.appendChild(wrapper);

    // 4. Element Selectors
    const bubble = document.getElementById("aiWidgetBubble");
    const windowEl = document.getElementById("aiWidgetWindow");
    const closeBtn = document.getElementById("aiWidgetClose");
    const bodyEl = document.getElementById("aiWidgetBody");
    const inputEl = document.getElementById("aiWidgetInput");
    const sendBtn = document.getElementById("aiWidgetSend");
    const bubbleIcon = document.getElementById("aiBubbleIcon");

    // Toggle Chat Window
    function toggleChat() {
        const isOpen = windowEl.classList.toggle("open");
        if (isOpen) {
            inputEl.focus();
            // Morph icon to a down chevron on open
            bubbleIcon.innerHTML = `<path d="M7.41 8.59L12 13.17l4.59-4.58L18 10l-6 6-6-6 1.41-1.41z"/>`;
        } else {
            // Morph back to comment icon
            bubbleIcon.innerHTML = `<path d="M20 2H4c-1.1 0-1.99.9-1.99 2L2 22l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zM6 9h12v2H6V9zm8 5H6v-2h8v2zm4-6H6V6h12v2z"/>`;
        }
    }

    bubble.addEventListener("click", toggleChat);
    closeBtn.addEventListener("click", toggleChat);

    // Dynamic message creation
    function appendMessage(role, text) {
        const msgDiv = document.createElement("div");
        msgDiv.className = `ai-widget-msg ${role}`;
        
        // Basic parser for minimal markdown (bold and bullets)
        let parsedText = text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/^\s*-\s+(.*?)$/gm, '<li>$1</li>');
            
        if (parsedText.includes("<li>")) {
            // Group lists
            parsedText = parsedText.replace(/(<li>.*?<\/li>)/gs, '<ul>$1</ul>');
        }
        
        msgDiv.innerHTML = parsedText;
        bodyEl.appendChild(msgDiv);
        bodyEl.scrollTop = bodyEl.scrollHeight;
        return msgDiv;
    }

    function appendActionBadge(actionText) {
        const badge = document.createElement("div");
        badge.className = "ai-widget-action";
        badge.innerHTML = `<span class="ai-widget-action-icon"></span> ${actionText}`;
        bodyEl.appendChild(badge);
        bodyEl.scrollTop = bodyEl.scrollHeight;
        return badge;
    }

    // Call API with custom Real-time Reader for SSE Streams
    async function sendChatQuery(queryText) {
        // Disable controls
        inputEl.disabled = true;
        sendBtn.disabled = true;
        inputEl.placeholder = "AI đang suy nghĩ...";

        // Append User Message
        appendMessage("user", queryText);
        
        // Prep stream receiver elements
        let botMsgDiv = null;
        let activeActionBadge = null;
        let botReplyText = "";

        try {
            const response = await fetch(`${API_BASE}/chat/stream`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    message: queryText,
                    session_id: sessionId
                })
            });

            if (!response.ok) {
                throw new Error(`Server returned HTTP ${response.status}`);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder("utf-8");
            let buffer = "";

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split("\n");
                buffer = lines.pop(); // Keep incomplete lines in the buffer

                for (const line of lines) {
                    const cleanLine = line.trim();
                    if (!cleanLine.startsWith("data: ")) continue;

                    const dataStr = cleanLine.substring(6);
                    try {
                        const data = JSON.parse(dataStr);
                        
                        if (data.type === "action") {
                            // Render glowing action indicator badge
                            if (activeActionBadge) activeActionBadge.remove();
                            activeActionBadge = appendActionBadge(data.content);
                        } 
                        else if (data.type === "content") {
                            // If an action was running, remove the badge when content arrives
                            if (activeActionBadge) {
                                activeActionBadge.remove();
                                activeActionBadge = null;
                            }
                            
                            // Initialize bot bubble if not already present
                            if (!botMsgDiv) {
                                botMsgDiv = appendMessage("bot", "");
                            }
                            
                            botReplyText += data.content;
                            
                            // Format response and update bubble
                            let parsed = botReplyText
                                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                                .replace(/`(.*?)`/g, '<code>$1</code>')
                                .replace(/^\s*-\s+(.*?)$/gm, '<li>$1</li>');
                                
                            if (parsed.includes("<li>")) {
                                parsed = parsed.replace(/(<li>.*?<\/li>)/gs, '<ul>$1</ul>');
                            }
                            botMsgDiv.innerHTML = parsed;
                            bodyEl.scrollTop = bodyEl.scrollHeight;
                        }
                        else if (data.type === "done") {
                            if (activeActionBadge) {
                                activeActionBadge.remove();
                                activeActionBadge = null;
                            }
                        }
                        else if (data.type === "error") {
                            throw new Error(data.content);
                        }
                    } catch (e) {
                        // Suppress JSON parse exceptions for partial buffers
                    }
                }
            }

        } catch (err) {
            console.error("Chat Widget Streaming Error:", err);
            if (activeActionBadge) activeActionBadge.remove();
            appendMessage("bot", `❌ **Lỗi:** Không thể kết nối với dịch vụ AI Agent. Chi tiết: _${err.message}_`);
        } finally {
            // Restore Controls
            inputEl.disabled = false;
            sendBtn.disabled = false;
            inputEl.placeholder = "Nhập câu hỏi tại đây...";
            inputEl.focus();
        }
    }

    // Event Handlers
    function handleSubmit() {
        const text = inputEl.value.trim();
        if (!text) return;
        inputEl.value = "";
        sendChatQuery(text);
    }

    sendBtn.addEventListener("click", handleSubmit);
    inputEl.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            handleSubmit();
        }
    });

})();
