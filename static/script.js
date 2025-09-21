const chatBody = document.getElementById("chat-body");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");

function addMessage(text, sender) {
    // Create a row container for each message
    const row = document.createElement("div");

    // Create the message bubble
    const msgBubble = document.createElement("div");
    msgBubble.classList.add("message");
    msgBubble.textContent = text;

    if (sender === "bot") {
        row.classList.add("bot-row");
        msgBubble.classList.add("bot-msg");

        // Create the bot avatar image
        const avatar = document.createElement("img");
        avatar.src = "/static/app.png";
        avatar.alt = "Bot";
        // Use the correct class name from your CSS
        avatar.classList.add("bot-avatar");

        // Add the avatar and then the message bubble to the row
        row.appendChild(avatar);
        row.appendChild(msgBubble);

    } else {
        row.classList.add("user-row");
        msgBubble.classList.add("user-msg");

        // Add just the message bubble to the row
        row.appendChild(msgBubble);
    }

    // Add the completed row to the chat body
    chatBody.appendChild(row);
    chatBody.scrollTop = chatBody.scrollHeight;
}


async function sendMessage(text) {
    addMessage(text, "user");

    const formData = new FormData();
    formData.append("msg", text);

    try {
        const response = await fetch("/get", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();
        addMessage(data.answer, "bot");

    } catch (error) {
        console.error("Failed to get response:", error);
        addMessage("Sorry, something went wrong. Please try again.", "bot");
    }
}

sendBtn.addEventListener("click", () => {
    const text = userInput.value.trim();
    if (!text) return;
    userInput.value = "";
    sendMessage(text);
});

userInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendBtn.click();
});

// Add a welcome message
window.addEventListener("load", () => {
    addMessage("Hello! I am MedAid. How can I assist you today?", "bot");
});