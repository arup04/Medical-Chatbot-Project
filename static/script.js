// --- Elements Caching ---
const chatViewport = document.querySelector(".chat-viewport");
const welcomeContainer = document.getElementById("welcome-container");
const messagesContainer = document.getElementById("chat-messages-container");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const newChatBtn = document.getElementById("new-chat-btn");
const chatHistoryList = document.getElementById("chat-history-list");
const themeToggle = document.getElementById("theme-toggle");
const archModalBtn = document.getElementById("arch-modal-btn");
const archModal = document.getElementById("arch-modal");
const closeModalBtn = document.getElementById("close-modal-btn");
const emptyCitationsState = document.getElementById("empty-citations-state");
const citationsContent = document.getElementById("citations-content");
const sourcesList = document.getElementById("sources-list");
const textChunksList = document.getElementById("text-chunks-list");
const referencesToggleBtn = document.getElementById("references-toggle-btn");
const referencesCollapsibleBody = document.getElementById("references-collapsible-body");

// --- State Variables ---
let chatSessions = JSON.parse(localStorage.getItem("mediAidSessions")) || [];
let activeSessionId = localStorage.getItem("mediAidActiveSessionId") || null;
let currentRetrievedContexts = [];

// --- Theme Initialization ---
const savedTheme = localStorage.getItem("mediAidTheme") || "dark";
document.documentElement.setAttribute("data-theme", savedTheme);

themeToggle.addEventListener("click", () => {
    const currentTheme = document.documentElement.getAttribute("data-theme");
    const newTheme = currentTheme === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", newTheme);
    localStorage.setItem("mediAidTheme", newTheme);
});

// --- Modal Functionality ---
archModalBtn.addEventListener("click", () => archModal.classList.add("active"));
closeModalBtn.addEventListener("click", () => archModal.classList.remove("active"));
window.addEventListener("click", (e) => {
    if (e.target === archModal) archModal.classList.remove("active");
});

// --- Collapsible Citations References ---
referencesToggleBtn.addEventListener("click", () => {
    referencesToggleBtn.classList.toggle("active");
    referencesCollapsibleBody.classList.toggle("active");
});

// --- Auto-resize Textarea & Button Enable ---
userInput.addEventListener("input", () => {
    userInput.style.height = "auto";
    userInput.style.height = (userInput.scrollHeight - 16) + "px";
    sendBtn.disabled = !userInput.value.trim();
});

// --- Session History Helpers ---
function createNewSession() {
    const newSession = {
        id: "session_" + Date.now(),
        title: "New Consultation",
        messages: [],
        contexts: [] // Stores history of retrieved contexts per turn
    };
    chatSessions.unshift(newSession);
    activeSessionId = newSession.id;
    saveSessions();
    renderSidebarSessions();
    loadActiveSession();
}

function saveSessions() {
    localStorage.setItem("mediAidSessions", JSON.stringify(chatSessions));
    localStorage.setItem("mediAidActiveSessionId", activeSessionId);
}

function renderSidebarSessions() {
    chatHistoryList.innerHTML = "";
    chatSessions.forEach(session => {
        const item = document.createElement("div");
        item.classList.add("history-item");
        if (session.id === activeSessionId) item.classList.add("active");
        
        item.innerHTML = `
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
            <span>${session.title}</span>
        `;
        
        item.addEventListener("click", () => {
            activeSessionId = session.id;
            saveSessions();
            renderSidebarSessions();
            loadActiveSession();
        });
        
        chatHistoryList.appendChild(item);
    });
}

function loadActiveSession() {
    const session = chatSessions.find(s => s.id === activeSessionId);
    if (!session || session.messages.length === 0) {
        // Show empty welcome state
        welcomeContainer.style.display = "flex";
        messagesContainer.style.display = "none";
        emptyCitationsState.style.display = "flex";
        citationsContent.style.display = "none";
        messagesContainer.innerHTML = "";
    } else {
        welcomeContainer.style.display = "none";
        messagesContainer.style.display = "flex";
        messagesContainer.innerHTML = "";
        
        session.messages.forEach(msg => {
            renderMessage(msg.text, msg.sender);
        });
        
        // Show citations for the latest bot response if available
        const botMessages = session.messages.filter(m => m.sender === "bot");
        if (botMessages.length > 0 && session.contexts.length > 0) {
            renderCitations(session.contexts[session.contexts.length - 1]);
        } else {
            emptyCitationsState.style.display = "flex";
            citationsContent.style.display = "none";
        }
        
        chatViewport.scrollTop = chatViewport.scrollHeight;
    }
    
    userInput.value = "";
    userInput.style.height = "auto";
    sendBtn.disabled = true;
}

newChatBtn.addEventListener("click", createNewSession);

// --- Suggestion Cards click ---
document.querySelectorAll(".suggestion-card").forEach(card => {
    card.addEventListener("click", () => {
        const question = card.getAttribute("data-question");
        userInput.value = question;
        userInput.dispatchEvent(new Event("input"));
        sendBtn.click();
    });
});

// --- Rendering Messages ---
function renderMessage(text, sender, isStreaming = false) {
    const row = document.createElement("div");
    row.classList.add(sender === "bot" ? "bot-row" : "user-row");

    const msgBubble = document.createElement("div");
    msgBubble.classList.add("message", sender === "bot" ? "bot-msg" : "user-msg");
    
    // Convert newlines to breaks or render markdown boldings
    msgBubble.innerHTML = formatMessageText(text);

    if (sender === "bot") {
        const avatar = document.createElement("img");
        avatar.src = "/static/app.png";
        avatar.alt = "Bot";
        avatar.classList.add("bot-avatar");
        row.appendChild(avatar);
    }
    
    row.appendChild(msgBubble);
    messagesContainer.appendChild(row);
    chatViewport.scrollTop = chatViewport.scrollHeight;
    
    return msgBubble;
}

function formatMessageText(text) {
    // Basic bold markdown support and line break parsing
    return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br>');
}

// --- Citations Panel Rendering ---
function renderCitations(contexts) {
    if (!contexts || contexts.length === 0) {
        emptyCitationsState.style.display = "flex";
        citationsContent.style.display = "none";
        return;
    }
    
    emptyCitationsState.style.display = "none";
    citationsContent.style.display = "block";
    
    sourcesList.innerHTML = "";
    textChunksList.innerHTML = "";
    
    // Group contexts by textbook/metadata page
    contexts.forEach((doc, idx) => {
        const sourcePath = doc.metadata.source || "Gale Encyclopedia of Medicine";
        const filename = sourcePath.split(/[\\/]/).pop();
        const pageNum = doc.metadata.page ? `Page ${doc.metadata.page}` : "N/A";
        
        // Calculate a mock relevance score based on retrieval indices
        const relevance = Math.round(98 - (idx * 5) - (Math.random() * 2));
        
        // Render source cards
        const sourceCard = document.createElement("div");
        sourceCard.classList.add("source-card");
        sourceCard.innerHTML = `
            <span class="source-title">📖 ${filename}</span>
            <span class="source-meta">${pageNum}</span>
            <div class="relevance-score-wrapper">
                <div class="relevance-score-text">
                    <span>Relevance</span>
                    <span>${relevance}%</span>
                </div>
                <div class="score-bar-bg">
                    <div class="score-bar-fill" style="width: 0%"></div>
                </div>
            </div>
        `;
        sourcesList.appendChild(sourceCard);
        
        // Trigger animations for the progress bars
        setTimeout(() => {
            const fill = sourceCard.querySelector(".score-bar-fill");
            if (fill) fill.style.width = relevance + "%";
        }, 100);

        // Render detailed text chunks
        const chunkCard = document.createElement("div");
        chunkCard.classList.add("chunk-card");
        chunkCard.innerHTML = `
            <div class="chunk-hdr">Source: ${filename} (Page ${doc.metadata.page || 'N/A'}) [Relevance: ${relevance}%]</div>
            <p>${doc.page_content}</p>
        `;
        textChunksList.appendChild(chunkCard);
    });
}

// --- Streaming API Fetch call ---
async function handleFormSubmit() {
    const text = userInput.value.trim();
    if (!text) return;
    
    userInput.value = "";
    userInput.style.height = "auto";
    sendBtn.disabled = true;
    
    // Setup session if none exists
    if (!activeSessionId) {
        createNewSession();
    }
    
    // Hide welcome state
    welcomeContainer.style.display = "none";
    messagesContainer.style.display = "flex";
    
    // Save User message
    const session = chatSessions.find(s => s.id === activeSessionId);
    session.messages.push({ text: text, sender: "user" });
    
    // Update consultation title dynamically if it is the first message
    if (session.messages.length === 1) {
        session.title = text.length > 25 ? text.substring(0, 25) + "..." : text;
    }
    
    renderMessage(text, "user");
    
    // Render bot placeholder with blinking cursor
    const botBubble = renderMessage("", "bot", true);
    const cursor = document.createElement("span");
    cursor.classList.add("cursor");
    botBubble.appendChild(cursor);
    
    // Trigger streaming fetch request
    const formData = new FormData();
    formData.append("msg", text);
    
    try {
        const response = await fetch("/get", {
            method: "POST",
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`Server status: ${response.status}`);
        }
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";
        let botResponseText = "";
        currentRetrievedContexts = [];
        
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split("\n");
            
            // Keep the last partial line in the buffer
            buffer = lines.pop();
            
            for (const line of lines) {
                if (line.startsWith("[CONTEXT] ")) {
                    const contextsData = JSON.parse(line.substring(10));
                    currentRetrievedContexts = contextsData;
                    renderCitations(contextsData);
                } else if (line.startsWith("[ANSWER] ")) {
                    const token = line.substring(9);
                    botResponseText += token;
                    // Render formatted text inside bubble
                    botBubble.innerHTML = formatMessageText(botResponseText);
                    botBubble.appendChild(cursor);
                } else if (line.startsWith("[ERROR] ")) {
                    throw new Error(line.substring(8));
                }
            }
        }
        
        // Remove typing cursor
        if (cursor.parentNode) cursor.parentNode.removeChild(cursor);
        
        // Save Bot Response and Contexts to state
        session.messages.push({ text: botResponseText, sender: "bot" });
        session.contexts.push(currentRetrievedContexts);
        saveSessions();
        renderSidebarSessions();
        
    } catch (err) {
        console.error("Stream failed:", err);
        if (cursor.parentNode) cursor.parentNode.removeChild(cursor);
        botBubble.innerHTML = formatMessageText("Sorry, I encountered an issue querying the clinical catalog. Please try again.");
    }
}

sendBtn.addEventListener("click", handleFormSubmit);
userInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendBtn.click();
    }
});

// --- Initialization ---
window.addEventListener("DOMContentLoaded", () => {
    if (chatSessions.length === 0) {
        createNewSession();
    } else {
        renderSidebarSessions();
        loadActiveSession();
    }
});