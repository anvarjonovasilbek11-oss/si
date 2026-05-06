// DOM References
const sidebar = document.getElementById('sidebar');
const sidebarToggle = document.getElementById('sidebarToggle');
const messagesContainer = document.getElementById('messagesContainer');
const chatInput = document.getElementById('chatInput');
const btnSend = document.getElementById('btnSend');
const modelSelect = document.getElementById('modelSelect');
const tempRange = document.getElementById('tempRange');
const tempValue = document.getElementById('tempValue');
const tokenRange = document.getElementById('tokenRange');
const tokenValue = document.getElementById('tokenValue');
const btnClearChat = document.getElementById('btnClearChat');
const emptyState = document.getElementById('emptyState');

// Chat State
let chatHistory = [];
const SYSTEM_PROMPT = 
    "Sizning ismingiz - Asilbek. Siz foydalanuvchilarga har qanday mavzuda yordam beradigan " +
    "juda aqlli, xushmuomala, muloyim va do'stona sun'iy intellekt yordamchisiz.\n\n" +
    "MUHIM MULOQOT QOIDALARI:\n" +
    "1. Siz FAQAT va FAQAT O'ZBEK TILIDA gapirishingiz shart. Boshqa tillarda yozilgan har qanday savolga ham " +
    "muloyimlik bilan faqat o'zbek tilida yordam bera olishingizni tushuntiring va muloqotni o'zbek tilida olib boring.\n" +
    "2. Foydalanuvchiga har doim hurmat bilan, 'Siz' deb muloqot qiling.\n" +
    "3. Javoblaringiz aniq, batafsil, imlo qoidalariga rioya qilgan holda va chiroyli formatlangan (Markdown jadvallari, " +
    "ro'yxatlari yoki kod bloklari orqali) bo'lishi lozim.\n" +
    "4. Hech qachon o'zingiz bilmagan ma'lumotlarni to'qimang.";

// Toggle mobile sidebar
sidebarToggle.addEventListener('click', (e) => {
    e.stopPropagation();
    sidebar.classList.toggle('active');
});

document.body.addEventListener('click', () => {
    sidebar.classList.remove('active');
});

sidebar.addEventListener('click', (e) => {
    e.stopPropagation();
});

// Update range indicators
tempRange.addEventListener('input', (e) => {
    tempValue.textContent = e.target.value;
});

tokenRange.addEventListener('input', (e) => {
    tokenValue.textContent = e.target.value;
});

// Input button state control
chatInput.addEventListener('input', (e) => {
    btnSend.disabled = e.target.value.trim().length === 0;
    // Auto resize input height
    e.target.style.height = 'auto';
    e.target.style.height = (e.target.scrollHeight) + 'px';
});

// Show/Hide Empty State Grid
function updateEmptyState() {
    if (chatHistory.length === 0) {
        emptyState.style.display = 'flex';
    } else {
        emptyState.style.display = 'none';
    }
}

// Clear chat (Safely preserving empty state block)
btnClearChat.addEventListener('click', () => {
    chatHistory = [];
    const rows = messagesContainer.querySelectorAll('.message-row');
    rows.forEach(row => row.remove());
    updateEmptyState();
    alert("Chat muvaffaqiyatli tozalandi!");
});

// Handle click on Suggestion Card
window.selectSuggestion = function(text) {
    chatInput.value = text;
    // Dispatch input event to enable button
    chatInput.dispatchEvent(new Event('input'));
    // Automatically submit message
    sendMessage();
};

// Render Message Helper
function appendMessage(role, text) {
    // Hide suggestions grid immediately when a message is added
    chatHistory.push({ role: role, content: text }); // update chat length
    updateEmptyState();
    // Remove from array since sendMessage handles adding it to state history
    chatHistory.pop(); 

    const row = document.createElement('div');
    row.className = `message-row ${role}`;
    
    const message = document.createElement('div');
    message.className = `chat-message ${role}`;
    
    const header = document.createElement('div');
    header.className = 'msg-header';
    
    if (role === 'user') {
        header.innerHTML = '<span class="msg-header-icon">👤</span> Siz';
    } else {
        header.innerHTML = '<span class="msg-header-icon">🤖</span> Asilbek AI';
    }
    
    const body = document.createElement('div');
    body.className = 'msg-text';
    
    // Format markdown using Marked.js
    body.innerHTML = marked.parse(text);
    
    message.appendChild(header);
    message.appendChild(body);
    row.appendChild(message);
    messagesContainer.appendChild(row);
    
    // Auto-scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Render Typing Loader
function showLoader() {
    const row = document.createElement('div');
    row.className = 'message-row assistant';
    row.id = 'loaderRow';
    
    const message = document.createElement('div');
    message.className = 'chat-message assistant';
    
    const header = document.createElement('div');
    header.className = 'msg-header';
    header.innerHTML = '<span class="msg-header-icon">🤖</span> Asilbek AI';
    
    const body = document.createElement('div');
    body.className = 'msg-text';
    body.innerHTML = `
        <div class="typing-loader">
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;
    
    message.appendChild(header);
    message.appendChild(body);
    row.appendChild(message);
    messagesContainer.appendChild(row);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function removeLoader() {
    const loader = document.getElementById('loaderRow');
    if (loader) loader.remove();
}

// Send message to Serverless API
async function sendMessage() {
    const text = chatInput.value.trim();
    if (!text) return;

    // Display user message and clear inputs
    appendMessage('user', text);
    chatInput.value = '';
    chatInput.style.height = '34px';
    btnSend.disabled = true;

    // Save to state history
    chatHistory.push({ role: "user", content: text });

    // Display typing animation
    showLoader();

    // Prepare API body
    const payloadMessages = [
        { role: "system", content: SYSTEM_PROMPT },
        ...chatHistory
    ];

    try {
        // Fetch response from Vercel Serverless api/chat
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                messages: payloadMessages,
                model: modelSelect.value,
                temperature: parseFloat(tempRange.value),
                max_tokens: parseInt(tokenRange.value)
            })
        });

        removeLoader();

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.error || "Server muloqotida muammo yuz berdi.");
        }

        const data = await response.json();
        const assistantReply = data.choices[0].message.content;

        // Show response
        appendMessage('assistant', assistantReply);
        chatHistory.push({ role: "assistant", content: assistantReply });

    } catch (error) {
        removeLoader();
        console.error(error);
        appendMessage('assistant', `⚠️ **Kechirasiz, xatolik yuz berdi:** ${error.message}\n\nIltimos, Vercel-da \`GROQ_API_KEY\` muhit o'zgaruvchisi to'g'ri o'rnatilganini va tarmoq ulanishingizni tekshiring.`);
    }
}

// Trigger Event Listeners
btnSend.addEventListener('click', sendMessage);

chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Initialize App (Suggestions are shown by default since chatHistory is empty)
updateEmptyState();
