// HR Assistant WebApp JavaScript

// Initialize Telegram WebApp
const tg = window.Telegram.WebApp;
tg.expand();

// Get user info from Telegram
const user = tg.initDataUnsafe?.user || { id: 123456789 }; // Fallback for testing
const telegramId = user.id;
const userLang = user.language_code || 'en';

// DOM elements
const chatContainer = document.getElementById('chatContainer');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const loading = document.getElementById('loading');
const subtitle = document.getElementById('subtitle');
const welcomeMessage = document.getElementById('welcomeMessage');

// Translations
const translations = {
    en: {
        subtitle: "Ask me anything about HR!",
        welcome: "Hello! I'm your HR assistant. How can I help you today?",
        placeholder: "Type your question...",
        error: "Sorry, something went wrong. Please try again."
    },
    ru: {
        subtitle: "Задайте мне любой вопрос по HR!",
        welcome: "Здравствуйте! Я ваш HR-ассистент. Чем могу помочь?",
        placeholder: "Введите ваш вопрос...",
        error: "Извините, произошла ошибка. Пожалуйста, попробуйте еще раз."
    },
    uz: {
        subtitle: "Menga HR bo'yicha har qanday savol bering!",
        welcome: "Salom! Men sizning HR yordamchingizman. Sizga qanday yordam bera olaman?",
        placeholder: "Savolingizni yozing...",
        error: "Kechirasiz, xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring."
    }
};

// Get translation
function t(key) {
    const lang = ['uz', 'ru', 'en'].includes(userLang) ? userLang : 'en';
    return translations[lang][key] || translations['en'][key];
}

// Set initial translations
subtitle.textContent = t('subtitle');
welcomeMessage.textContent = t('welcome');
messageInput.placeholder = t('placeholder');

// Auto-resize textarea
messageInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
});

// Add message to chat
function addMessage(text, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const p = document.createElement('p');
    p.textContent = text;
    
    contentDiv.appendChild(p);
    messageDiv.appendChild(contentDiv);
    chatContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Show/hide loading
function setLoading(show) {
    loading.style.display = show ? 'block' : 'none';
    sendButton.disabled = show;
    messageInput.disabled = show;
}

// Send message to API
async function sendMessage(question) {
    try {
        setLoading(true);
        
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                telegram_id: telegramId,
                question: question
            })
        });
        
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        
        const data = await response.json();
        
        // Add bot response
        addMessage(data.answer, false);
        
        // Haptic feedback
        if (tg.HapticFeedback) {
            tg.HapticFeedback.notificationOccurred('success');
        }
        
    } catch (error) {
        console.error('Error:', error);
        addMessage(t('error'), false);
        
        // Haptic feedback for error
        if (tg.HapticFeedback) {
            tg.HapticFeedback.notificationOccurred('error');
        }
    } finally {
        setLoading(false);
    }
}

// Handle send button click
sendButton.addEventListener('click', async () => {
    const question = messageInput.value.trim();
    
    if (!question) return;
    
    // Add user message
    addMessage(question, true);
    
    // Clear input
    messageInput.value = '';
    messageInput.style.height = 'auto';
    
    // Send to API
    await sendMessage(question);
});

// Handle Enter key (without Shift)
messageInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendButton.click();
    }
});

// Load chat history on startup
async function loadHistory() {
    try {
        const response = await fetch(`/api/history/${telegramId}?limit=5`);
        
        if (response.ok) {
            const data = await response.json();
            
            if (data.messages && data.messages.length > 0) {
                // Clear welcome message
                chatContainer.innerHTML = '';
                
                // Add history messages
                data.messages.forEach(msg => {
                    addMessage(msg.question, true);
                    addMessage(msg.answer, false);
                });
            }
        }
    } catch (error) {
        console.error('Error loading history:', error);
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Set Telegram theme colors
    document.body.style.setProperty('--tg-theme-bg-color', tg.themeParams.bg_color || '#ffffff');
    document.body.style.setProperty('--tg-theme-text-color', tg.themeParams.text_color || '#000000');
    document.body.style.setProperty('--tg-theme-hint-color', tg.themeParams.hint_color || '#999999');
    document.body.style.setProperty('--tg-theme-button-color', tg.themeParams.button_color || '#3390ec');
    document.body.style.setProperty('--tg-theme-button-text-color', tg.themeParams.button_text_color || '#ffffff');
    document.body.style.setProperty('--tg-theme-secondary-bg-color', tg.themeParams.secondary_bg_color || '#f0f0f0');
    
    // Load history
    loadHistory();
    
    // Focus input
    messageInput.focus();
    
    // Tell Telegram the WebApp is ready
    tg.ready();
});

// Handle back button
tg.BackButton.onClick(() => {
    tg.close();
});
