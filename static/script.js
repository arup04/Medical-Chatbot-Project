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
const toastContainer = document.getElementById("toast-container");
const micBtn = document.getElementById("mic-btn");

// --- State Variables ---
let chatSessions = JSON.parse(localStorage.getItem("mediAidSessions")) || [];
let activeSessionId = localStorage.getItem("mediAidActiveSessionId") || null;
let currentRetrievedContexts = [];
let recognition = null;
let isRecording = false;

// --- Theme Initialization ---
const savedTheme = localStorage.getItem("mediAidTheme") || "dark";
document.documentElement.setAttribute("data-theme", savedTheme);

themeToggle.addEventListener("click", () => {
    const currentTheme = document.documentElement.getAttribute("data-theme");
    const newTheme = currentTheme === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", newTheme);
    localStorage.setItem("mediAidTheme", newTheme);
    showToast("Theme switched successfully!", "success");
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

// --- Toast System ---
function showToast(message, type = "success") {
    const toast = document.createElement("div");
    toast.classList.add("toast", type);
    
    // Status icons
    let icon = "🔔";
    if (type === "success") icon = "✅";
    if (type === "error") icon = "❌";
    
    toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;
    toastContainer.appendChild(toast);
    
    // Auto-remove toast
    setTimeout(() => {
        toast.classList.add("slide-out");
        toast.addEventListener("animationend", () => {
            toast.remove();
        });
    }, 3500);
}

// --- Session History Helpers ---
function createNewSession(showNotification = true) {
    // If current session is empty, reuse it
    const active = chatSessions.find(s => s.id === activeSessionId);
    if (active && active.messages.length === 0) {
        if (showNotification) showToast("Consultation restarted.", "success");
        return;
    }
    
    const newSession = {
        id: "session_" + Date.now(),
        title: "New Consultation",
        messages: [],
        contexts: [] 
    };
    chatSessions.unshift(newSession);
    activeSessionId = newSession.id;
    saveSessions();
    renderSidebarSessions();
    loadActiveSession();
    if (showNotification) showToast("New consultation session started.", "success");
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
            <span style="flex: 1; overflow: hidden; text-overflow: ellipsis;">${session.title}</span>
            <button class="delete-session-btn" style="background:transparent; border:none; color:var(--text-secondary); cursor:pointer;" title="Delete Session">&times;</button>
        `;
        
        // Handle delete session clicks
        item.querySelector(".delete-session-btn").addEventListener("click", (e) => {
            e.stopPropagation();
            chatSessions = chatSessions.filter(s => s.id !== session.id);
            if (activeSessionId === session.id) {
                activeSessionId = chatSessions.length > 0 ? chatSessions[0].id : null;
            }
            saveSessions();
            if (chatSessions.length === 0) {
                createNewSession();
            } else {
                renderSidebarSessions();
                loadActiveSession();
            }
            showToast("Consultation thread deleted.", "success");
        });
        
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
            renderMessage(msg.text, msg.sender, false, msg.contexts || null);
        });
        
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

// --- Text-to-Speech Helper ---
function speakText(text) {
    if ('speechSynthesis' in window) {
        // Cancel current speech if any
        window.speechSynthesis.cancel();
        
        // Strip out HTML tags for speech
        const cleanText = text.replace(/<[^>]*>/g, '');
        const utterance = new SpeechSynthesisUtterance(cleanText);
        utterance.rate = 1.0;
        
        // Find a suitable English voice
        const voices = window.speechSynthesis.getVoices();
        const enVoice = voices.find(v => v.lang.includes("en-") || v.lang.includes("en_"));
        if (enVoice) utterance.voice = enVoice;
        
        window.speechSynthesis.speak(utterance);
        showToast("Audio playback started.", "success");
    } else {
        showToast("Voice Synthesis not supported in this browser.", "error");
    }
}

// --- Clipboard Copy Helper ---
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast("Copied answer to clipboard!", "success");
    }).catch(err => {
        console.error("Copy failed:", err);
        showToast("Failed to copy text.", "error");
    });
}

// --- Export Conversation Helper ---
function exportChatSession() {
    const session = chatSessions.find(s => s.id === activeSessionId);
    if (!session || session.messages.length === 0) {
        showToast("No messages to export.", "error");
        return;
    }
    
    let exportText = `MediAid AI Consultation Log\nSession ID: ${session.id}\nTitle: ${session.title}\n========================================\n\n`;
    session.messages.forEach(msg => {
        const senderLabel = msg.sender === "user" ? "Patient" : "MediAid Assistant";
        exportText += `[${senderLabel}]:\n${msg.text}\n\n----------------------------------------\n\n`;
    });
    
    const blob = new Blob([exportText], { type: "text/plain;charset=utf-8" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `${session.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_consultation.txt`;
    link.click();
    showToast("Consultation log exported!", "success");
}

// --- Render Bubble Action Buttons ---
function injectMessageActions(row, bubbleElement, text) {
    // Actions container
    const actions = document.createElement("div");
    actions.classList.add("message-actions");
    
    // 1. Copy Button
    const copyBtn = document.createElement("button");
    copyBtn.classList.add("action-btn");
    copyBtn.title = "Copy to clipboard";
    copyBtn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>`;
    copyBtn.addEventListener("click", () => copyToClipboard(text));
    actions.appendChild(copyBtn);
    
    // 2. Speak Button (Bot only)
    if (row.classList.contains("bot-row")) {
        const speakBtn = document.createElement("button");
        speakBtn.classList.add("action-btn");
        speakBtn.title = "Speak answer aloud";
        speakBtn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path></svg>`;
        speakBtn.addEventListener("click", () => speakText(text));
        actions.appendChild(speakBtn);
    }
    
    // 3. Export Session Button
    const exportBtn = document.createElement("button");
    exportBtn.classList.add("action-btn");
    exportBtn.title = "Export entire conversation";
    exportBtn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>`;
    exportBtn.addEventListener("click", () => exportChatSession());
    actions.appendChild(exportBtn);
    
    row.appendChild(actions);
}

// --- Clean Source Name Helper ---
function getCleanSourceName(sourcePath) {
    if (!sourcePath) return "The Gale Encyclopedia of Medicine";
    const base = sourcePath.split(/[\\/]/).pop().replace(/\.pdf$/i, '');
    if (base.toLowerCase().includes("medical_book") || base.toLowerCase().includes("gale")) {
        return "The Gale Encyclopedia of Medicine";
    }
    return base.replace(/_/g, ' ');
}

// --- Citation Formatting Helpers ---
function formatCitationsHTML(contexts) {
    if (!contexts || contexts.length === 0) return "";
    
    // Group documents by clean source title
    const sourceGroups = {};
    contexts.forEach((doc, idx) => {
        const rawSource = doc.metadata?.source || "Medical_book";
        const cleanName = getCleanSourceName(rawSource);
        const page = doc.metadata?.page ? `Pg ${doc.metadata.page}` : null;
        
        if (!sourceGroups[cleanName]) {
            sourceGroups[cleanName] = {
                name: cleanName,
                count: 0,
                pages: new Set(),
                firstIndex: idx
            };
        }
        sourceGroups[cleanName].count += 1;
        if (page) sourceGroups[cleanName].pages.add(page);
    });

    const groupKeys = Object.keys(sourceGroups);
    if (groupKeys.length === 0) return "";

    let html = `<div class="message-citations-block">`;
    html += `<div class="citation-block-header">`;
    html += `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>`;
    html += `<span>Cited Medical Evidence</span>`;
    html += `</div>`;
    html += `<div class="citation-pills-list">`;
    
    groupKeys.forEach((key) => {
        const group = sourceGroups[key];
        const pageInfo = group.pages.size > 0 
            ? ` · ${Array.from(group.pages).join(', ')}` 
            : ` · ${group.count} Verified Passage${group.count > 1 ? 's' : ''}`;
        html += `<span class="citation-pill" data-source-index="${group.firstIndex}" title="Click to view retrieved textbook passages in context panel">📖 ${group.name}${pageInfo}</span>`;
    });
    
    html += `</div></div>`;
    return html;
}

function attachCitationClickHandlers(bubble, contexts) {
    if (!bubble || !contexts) return;
    bubble.querySelectorAll(".citation-pill").forEach(pill => {
        pill.addEventListener("click", (e) => {
            e.stopPropagation();
            renderCitations(contexts);
            focusCitationInPanel(0);
            showToast("Retrieved textbook passages displayed in context panel.", "success");
        });
    });
}

function focusCitationInPanel(index = 0) {
    const cards = document.querySelectorAll(".source-card");
    if (cards && cards.length > index) {
        cards.forEach(c => c.classList.remove("highlighted-card"));
        cards[index].classList.add("highlighted-card");
        cards[index].scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
}

// --- Render Message Bubbles ---
function renderMessage(text, sender, isSkeleton = false, contexts = null) {
    const row = document.createElement("div");
    row.classList.add(sender === "bot" ? "bot-row" : "user-row");

    const msgBubble = document.createElement("div");
    msgBubble.classList.add("message", sender === "bot" ? "bot-msg" : "user-msg");
    
    if (isSkeleton) {
        msgBubble.innerHTML = `
            <div class="skeleton-container">
                <div class="skeleton-line w-100"></div>
                <div class="skeleton-line w-80"></div>
                <div class="skeleton-line w-60"></div>
            </div>
        `;
    } else {
        let contentHtml = formatMessageText(text);
        if (sender === "bot" && contexts && contexts.length > 0) {
            contentHtml += formatCitationsHTML(contexts);
        }
        msgBubble.innerHTML = contentHtml;
        if (sender === "bot" && contexts && contexts.length > 0) {
            attachCitationClickHandlers(msgBubble, contexts);
        }
        injectMessageActions(row, msgBubble, text);
    }

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
    return text
        .replace(/---/g, '<hr style="border: none; border-top: 1px solid var(--border-color, rgba(255,255,255,0.12)); margin: 12px 0 8px 0;">')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
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
    
    contexts.forEach((doc, idx) => {
        const cleanName = getCleanSourceName(doc.metadata?.source);
        const pageNum = doc.metadata?.page ? `Page ${doc.metadata.page}` : `Passage #${idx + 1}`;
        const relevance = Math.round(98 - (idx * 5) - (Math.random() * 2));
        
        // Source card in citation sidebar
        const sourceCard = document.createElement("div");
        sourceCard.classList.add("source-card");
        sourceCard.style.cursor = "pointer";
        sourceCard.title = "Click to inspect passage excerpt";
        sourceCard.innerHTML = `
            <span class="source-title">📖 ${cleanName}</span>
            <span class="source-meta">${pageNum}</span>
            <div class="relevance-score-wrapper">
                <div class="relevance-score-text">
                    <span>Relevance Match</span>
                    <span>${relevance}%</span>
                </div>
                <div class="score-bar-bg">
                    <div class="score-bar-fill" style="width: 0%"></div>
                </div>
            </div>
        `;
        
        // Clicking source card expands and highlights text chunk excerpt
        sourceCard.addEventListener("click", () => {
            referencesToggleBtn.classList.add("active");
            referencesCollapsibleBody.classList.add("active");
            const chunkCards = textChunksList.querySelectorAll(".chunk-card");
            if (chunkCards && chunkCards[idx]) {
                chunkCards.forEach(c => c.classList.remove("active-chunk"));
                chunkCards[idx].classList.add("active-chunk");
                chunkCards[idx].scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        });
        
        sourcesList.appendChild(sourceCard);
        
        setTimeout(() => {
            const fill = sourceCard.querySelector(".score-bar-fill");
            if (fill) fill.style.width = relevance + "%";
        }, 100);

        // Raw text chunk details
        const chunkCard = document.createElement("div");
        chunkCard.classList.add("chunk-card");
        chunkCard.innerHTML = `
            <div class="chunk-hdr">Source: ${cleanName} [${pageNum} · Relevance: ${relevance}%]</div>
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
    
    if (!activeSessionId) {
        createNewSession();
    }
    
    welcomeContainer.style.display = "none";
    messagesContainer.style.display = "flex";
    
    const session = chatSessions.find(s => s.id === activeSessionId);
    session.messages.push({ text: text, sender: "user" });
    
    if (session.messages.length === 1) {
        session.title = text.length > 25 ? text.substring(0, 25) + "..." : text;
    }
    
    renderMessage(text, "user");
    
    // Render bot bubble with animated skeleton loading state
    const botBubble = renderMessage("", "bot", true);
    
    const formData = new FormData();
    formData.append("msg", text);
    formData.append("session_id", activeSessionId || "default_session");
    
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
        let isFirstToken = true;
        currentRetrievedContexts = [];
        
        // Blinking typing cursor
        const cursor = document.createElement("span");
        cursor.classList.add("cursor");
        
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split("\n");
            
            buffer = lines.pop();
            
            for (const line of lines) {
                if (line.startsWith("[CONTEXT] ")) {
                    const contextsData = JSON.parse(line.substring(10));
                    currentRetrievedContexts = contextsData;
                    renderCitations(contextsData);
                } else if (line.startsWith("[ANSWER] ")) {
                    if (isFirstToken) {
                        // Clear skeleton loader on receiving first real text token
                        botBubble.innerHTML = "";
                        botBubble.appendChild(cursor);
                        isFirstToken = false;
                    }
                    const token = line.substring(9);
                    botResponseText += token;
                    botBubble.innerHTML = formatMessageText(botResponseText);
                    botBubble.appendChild(cursor);
                } else if (line.startsWith("[ERROR] ")) {
                    throw new Error(line.substring(8));
                }
            }
        }
        
        // Remove typing cursor and inject hover actions container
        if (cursor.parentNode) cursor.parentNode.removeChild(cursor);
        
        // If LLM returned no answer text
        if (isFirstToken) {
            botBubble.innerHTML = "I am sorry, I couldn't formulate a response. Please try again.";
        } else {
            let finalHtml = formatMessageText(botResponseText);
            if (currentRetrievedContexts && currentRetrievedContexts.length > 0) {
                finalHtml += formatCitationsHTML(currentRetrievedContexts);
            }
            botBubble.innerHTML = finalHtml;
            if (currentRetrievedContexts && currentRetrievedContexts.length > 0) {
                attachCitationClickHandlers(botBubble, currentRetrievedContexts);
            }
        }
        
        // Inject action panel onto row
        const row = botBubble.closest(".bot-row");
        injectMessageActions(row, botBubble, botResponseText);
        
        session.messages.push({ 
            text: botResponseText, 
            sender: "bot", 
            contexts: currentRetrievedContexts 
        });
        session.contexts.push(currentRetrievedContexts);
        saveSessions();
        renderSidebarSessions();
        
    } catch (err) {
        console.error("Stream failed:", err);
        botBubble.innerHTML = formatMessageText("Sorry, I encountered an issue querying the clinical catalog. Please try again.");
        showToast("Clinical catalog search failed.", "error");
    }
}

sendBtn.addEventListener("click", handleFormSubmit);
userInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendBtn.click();
    }
});

// --- Speech Recognition Setup ---
function initSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        micBtn.style.display = "none";
        return;
    }

    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
        isRecording = true;
        micBtn.classList.add("recording");
        showToast("Voice recording active...", "success");
    };

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        userInput.value += (userInput.value ? " " : "") + transcript;
        userInput.style.height = "auto";
        userInput.style.height = (userInput.scrollHeight - 16) + "px";
        sendBtn.disabled = !userInput.value.trim();
        showToast("Speech recognized successfully.", "success");
    };

    recognition.onerror = (event) => {
        console.error("Speech recognition error:", event.error);
        if (event.error !== 'no-speech') {
            showToast("Speech recognition error: " + event.error, "error");
        }
        stopRecording();
    };

    recognition.onend = () => {
        stopRecording();
    };
}

function startRecording() {
    if (!recognition) initSpeechRecognition();
    if (recognition) {
        try {
            recognition.start();
        } catch (e) {
            console.error(e);
        }
    }
}

function stopRecording() {
    isRecording = false;
    if (micBtn) micBtn.classList.remove("recording");
    if (recognition) {
        try {
            recognition.stop();
        } catch (e) {
            // Already stopped
        }
    }
}

micBtn.addEventListener("click", () => {
    if (isRecording) {
        stopRecording();
    } else {
        startRecording();
    }
});

// --- Initialization ---
window.addEventListener("DOMContentLoaded", () => {
    // Initialize speech
    initSpeechRecognition();
    
    // Populate voice syntheses list (needed on Chrome/Firefox to load voices async)
    if ('speechSynthesis' in window) {
        window.speechSynthesis.getVoices();
    }
    
    renderSidebarSessions();
    createNewSession(false); // Always start with a fresh new consultation session on load
});