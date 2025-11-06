// Configuration
const API_BASE_URL = 'http://localhost:8000'; // Update this with your production backend URL

// DOM Elements
const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');
const statusIndicator = document.getElementById('status');
const statusDot = statusIndicator.querySelector('.status-dot');
const statusText = statusIndicator.querySelector('.status-text');
const clearBtn = document.getElementById('clearBtn');

// State
let isConnected = false;

// ====================================================================
// INITIALIZATION
// ====================================================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Oncosimis AI Assistant Initialized');
    setupEventListeners();
    checkBackendStatus();
});

// ====================================================================
// EVENT LISTENERS
// ====================================================================

function setupEventListeners() {
    sendButton.addEventListener('click', handleSendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    });

    // Auto-resize textarea
    userInput.addEventListener('input', adjustTextareaHeight);

    // Clear chat button
    clearBtn.addEventListener('click', clearChat);

    // Focus input on load
    userInput.focus();
}

// ====================================================================
// BACKEND STATUS CHECKING
// ====================================================================

async function checkBackendStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`, {
            method: 'GET',
            headers: {
                'ngrok-skip-browser-warning': '69420'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        if (data.status === 'healthy' && data.ollama === 'connected') {
            updateStatus('online', 'Connected');
            isConnected = true;
        } else if (data.status === 'healthy') {
            updateStatus('offline', 'Ollama Disconnected');
            isConnected = false;
        } else {
            updateStatus('offline', 'Backend Issues');
            isConnected = false;
        }
    } catch (error) {
        updateStatus('offline', 'Backend Offline');
        isConnected = false;
        console.error('❌ Connection error:', error);
    }

    // Recheck every 10 seconds
    setTimeout(checkBackendStatus, 10000);
}

function updateStatus(status, text) {
    statusIndicator.className = `status-indicator ${status}`;
    statusText.textContent = text;
}

// ====================================================================
// MESSAGE HANDLING
// ====================================================================

async function handleSendMessage() {
    const message = userInput.value.trim();

    if (!message) return;

    if (!isConnected) {
        addMessage('⚠️ Backend is not connected. Please wait or check if the server is running.', 'bot');
        return;
    }

    // Clear input
    userInput.value = '';
    adjustTextareaHeight();

    // Remove welcome message if it exists
    const welcomeMsg = document.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.style.opacity = '0';
        setTimeout(() => welcomeMsg.remove(), 300);
    }

    // Add user message
    addMessage(message, 'user');

    // Show typing indicator
    const typingDiv = addTypingIndicator();

    // Disable send button
    sendButton.disabled = true;

    try {
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'ngrok-skip-browser-warning': '69420'
            },
            body: JSON.stringify({ message: message })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();

        // Remove typing indicator
        removeTypingIndicator(typingDiv);

        // Add bot response
        addMessage(data.response, 'bot');

        // Handle files if present
        if (data.files && data.files.length > 0) {
            displayFiles(data.files);
        }

    } catch (error) {
        console.error('❌ Chat error:', error);
        removeTypingIndicator(typingDiv);

        let errorMsg = 'Sorry, I encountered an error processing your request.';

        if (error.message.includes('Failed to fetch')) {
            errorMsg = '🔌 Connection error. Please check if the backend is running.';
        } else if (error.message.includes('404')) {
            errorMsg = '🔍 Endpoint not found. Please check your backend configuration.';
        } else if (error.message.includes('500')) {
            errorMsg = '⚠️ Server error. Please check the backend logs.';
        }

        addMessage(errorMsg, 'bot');
    } finally {
        // Re-enable send button
        sendButton.disabled = false;
        userInput.focus();
    }
}

// ====================================================================
// UI HELPERS
// ====================================================================

function adjustTextareaHeight() {
    userInput.style.height = 'auto';
    userInput.style.height = Math.min(userInput.scrollHeight, 120) + 'px';
}

function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// ====================================================================
// CHAT MANAGEMENT
// ====================================================================

function clearChat() {
    // Keep only the first AI welcome message
    const firstMessage = chatMessages.querySelector('.message.ai:first-child');
    chatMessages.innerHTML = '';
    if (firstMessage) {
        chatMessages.appendChild(firstMessage);
    }
}

// ====================================================================
// QUICK QUESTIONS
// ====================================================================

function askQuestion(question) {
    userInput.value = question;
    handleSendMessage();
}

// ====================================================================
// MESSAGE DISPLAY
// ====================================================================

function addMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender === 'user' ? 'user' : 'ai'}`;

    const avatar = document.createElement('div');
    avatar.className = 'avatar';

    if (sender === 'user') {
        avatar.textContent = 'U';
    } else {
        // Use logo image for AI messages
        const logoImg = document.createElement('img');
        logoImg.src = 'assets/osb_logo.png';
        logoImg.alt = 'Oncosimis AI';
        logoImg.style.width = '100%';
        logoImg.style.height = '100%';
        logoImg.style.borderRadius = '50%';
        logoImg.style.objectFit = 'cover';
        avatar.appendChild(logoImg);
    }

    const textBubble = document.createElement('div');
    textBubble.className = 'text-bubble';
    textBubble.innerHTML = text.replace(/\n/g, '<br>');

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(textBubble);
    chatMessages.appendChild(messageDiv);

    scrollToBottom();
}

function addTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message ai typing';
    typingDiv.id = 'typing-indicator';

    const avatar = document.createElement('div');
    avatar.className = 'avatar';

    // Use logo image for typing indicator
    const logoImg = document.createElement('img');
    logoImg.src = 'assets/osb_logo.png';
    logoImg.alt = 'Oncosimis AI';
    logoImg.style.width = '100%';
    logoImg.style.height = '100%';
    logoImg.style.borderRadius = '50%';
    logoImg.style.objectFit = 'cover';
    avatar.appendChild(logoImg);

    const textBubble = document.createElement('div');
    textBubble.className = 'text-bubble';
    textBubble.innerHTML = '<span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span>';

    typingDiv.appendChild(avatar);
    typingDiv.appendChild(textBubble);
    chatMessages.appendChild(typingDiv);

    scrollToBottom();
    return typingDiv;
}

function removeTypingIndicator(typingDiv) {
    if (typingDiv && typingDiv.parentNode) {
        typingDiv.parentNode.removeChild(typingDiv);
    }
}

function displayFiles(files) {
    files.forEach(file => {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message ai';

        const avatar = document.createElement('div');
        avatar.className = 'avatar';

        // Use logo image for file messages
        const logoImg = document.createElement('img');
        logoImg.src = 'assets/osb_logo.png';
        logoImg.alt = 'Oncosimis AI';
        logoImg.style.width = '100%';
        logoImg.style.height = '100%';
        logoImg.style.borderRadius = '50%';
        logoImg.style.objectFit = 'cover';
        avatar.appendChild(logoImg);

        const textBubble = document.createElement('div');
        textBubble.className = 'text-bubble';

        const fileInfo = document.createElement('div');
        fileInfo.innerHTML = `<strong>File available:</strong> ${file.filename}`;

        const downloadBtn = document.createElement('button');
        downloadBtn.className = 'download-btn';
        downloadBtn.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M21 15V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M7 10L12 15L17 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M12 15V3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            Download
        `;
        downloadBtn.onclick = () => downloadFile(file.filename);

        textBubble.appendChild(fileInfo);
        textBubble.appendChild(downloadBtn);
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(textBubble);
        chatMessages.appendChild(messageDiv);
    });

    scrollToBottom();
}

async function downloadFile(filename) {
    try {
        console.log('📥 Downloading file:', filename);

        const response = await fetch(`${API_BASE_URL}/download/${encodeURIComponent(filename)}`, {
            method: 'GET',
            headers: {
                'ngrok-skip-browser-warning': '69420'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const blob = await response.blob();

        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.style.display = 'none';

        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);

        window.URL.revokeObjectURL(url);

        console.log('✅ Download complete:', filename);

    } catch (error) {
        console.error('❌ Download error:', error);
        addMessage(`❌ Failed to download ${filename}: ${error.message}`, 'bot');
    }
}