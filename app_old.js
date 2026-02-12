class JarvisAssistant {
    constructor() {
        this.initializeElements();
        this.initializeState();
        this.bindEvents();
        this.initializeSpeechRecognition();
        this.initializeSpeechSynthesis();
        this.loadChatHistory();
        this.loadUserSession();
        
        // Show initial welcome message
        this.showWelcomeMessage();
    }

    initializeElements() {
        // Sidebar elements
        this.sidebar = document.getElementById('sidebar');
        this.sidebarToggle = document.getElementById('sidebarToggle');
        this.sidebarClose = document.getElementById('sidebarClose');
        this.sidebarOverlay = document.getElementById('sidebarOverlay');
        this.chatHistory = document.getElementById('chatHistory');
        this.newChatBtn = document.getElementById('newChatBtn');
        this.loginBtn = document.getElementById('loginBtn');
        this.logoutBtn = document.getElementById('logoutBtn');
        this.userName = document.getElementById('userName');
        
        // Chat elements
        this.chatArea = document.getElementById('chatArea');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.micButton = document.getElementById('micButton');
        
        // Phase indicator elements
        this.phaseIndicator = document.getElementById('phaseIndicator');
        this.phaseIcon = document.getElementById('phaseIcon');
        this.phaseText = document.getElementById('phaseText');
        
        // Shortcut buttons
        this.shortcutBtns = document.querySelectorAll('.shortcut-btn');
    }

    initializeState() {
        this.isListening = false;
        this.isProcessing = false;
        this.currentPhase = 'ready';
        this.recognition = null;
        this.synthesis = window.speechSynthesis;
        this.currentVoice = null;
        this.conversationHistory = [];
        this.currentChatId = null;
        this.isLoggedIn = false;
        this.currentUser = 'Guest User';
        
        // Show initializing phase
        this.setPhase('initializing');
        
        // Initialize UI state after a delay
        setTimeout(() => {
            this.setPhase('ready');
            this.updateSendButtonState();
        }, 1500);
    }

    bindEvents() {
        // Sidebar events
        this.sidebarToggle.addEventListener('click', (e) => {
            e.preventDefault();
            this.toggleSidebar();
        });
        this.sidebarClose.addEventListener('click', (e) => {
            e.preventDefault();
            this.closeSidebar();
        });
        this.sidebarOverlay.addEventListener('click', (e) => {
            e.preventDefault();
            this.closeSidebar();
        });
        this.newChatBtn.addEventListener('click', (e) => {
            e.preventDefault();
            this.startNewChat();
        });
        this.loginBtn.addEventListener('click', (e) => {
            e.preventDefault();
            this.handleLogin();
        });
        this.logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            this.handleLogout();
        });
        
        // Input events
        this.messageInput.addEventListener('input', () => {
            this.handleInputChange();
            this.autoResizeTextarea();
        });
        this.messageInput.addEventListener('keydown', (e) => this.handleKeyDown(e));
        
        // Button events
        this.sendButton.addEventListener('click', (e) => {
            e.preventDefault();
            this.sendMessage();
        });
        this.micButton.addEventListener('click', (e) => {
            e.preventDefault();
            this.toggleVoiceRecognition();
        });
        
        // Shortcut button events
        this.shortcutBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const url = btn.dataset.url;
                const name = btn.dataset.name;
                this.openShortcut(url, name);
            });
        });
    }

    initializeSpeechRecognition() {
        if ('webkitSpeechRecognition' in window) {
            this.recognition = new webkitSpeechRecognition();
        } else if ('SpeechRecognition' in window) {
            this.recognition = new SpeechRecognition();
        }

        if (this.recognition) {
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = 'en-US';

            this.recognition.onstart = () => {
                console.log('Speech recognition started');
                this.isListening = true;
                this.setPhase('listening');
                this.micButton.classList.add('listening');
            };

            this.recognition.onresult = (event) => {
                console.log('Speech result received:', event);
                this.handleSpeechResult(event);
            };

            this.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                this.stopListening();
                if (event.error === 'not-allowed') {
                    this.addMessage('jarvis', 'Microphone access denied. Please enable microphone permissions.');
                }
            };

            this.recognition.onend = () => {
                console.log('Speech recognition ended');
                this.stopListening();
            };
        }
    }

    initializeSpeechSynthesis() {
        if (this.synthesis) {
            if (this.synthesis.getVoices().length === 0) {
                this.synthesis.onvoiceschanged = () => {
                    this.selectVoice();
                };
            } else {
                this.selectVoice();
            }
        }
    }

    selectVoice() {
        const voices = this.synthesis.getVoices();
        this.currentVoice = voices.find(voice => 
            voice.lang.includes('en') && voice.name.toLowerCase().includes('male')
        ) || voices.find(voice => voice.lang.includes('en')) || voices[0];
    }

    showWelcomeMessage() {
        // Clear any existing content
        this.chatArea.innerHTML = '';
        
        // Add welcome message
        const welcomeDiv = document.createElement('div');
        welcomeDiv.className = 'welcome-message';
        welcomeDiv.innerHTML = `
            <div class="jarvis-message">
                <div class="message-bubble jarvis-bubble">
                    <p>Hello! I'm Jarvis, your AI assistant. How can I help you today?</p>
                    <ul>
                        <li>Type your message below or use voice commands</li>
                        <li>Click shortcuts for quick actions</li>
                        <li>Access chat history from the sidebar</li>
                    </ul>
                </div>
                <div class="message-timestamp">Just now</div>
            </div>
        `;
        this.chatArea.appendChild(welcomeDiv);
    }

    toggleSidebar() {
        if (this.sidebar.classList.contains('open')) {
            this.closeSidebar();
        } else {
            this.openSidebar();
        }
    }

    openSidebar() {
        this.sidebar.classList.add('open');
        this.sidebarOverlay.classList.add('show');
        document.body.style.overflow = 'hidden';
    }

    closeSidebar() {
        this.sidebar.classList.remove('open');
        this.sidebarOverlay.classList.remove('show');
        document.body.style.overflow = '';
    }

    setPhase(phase) {
        console.log('Setting phase to:', phase);
        this.currentPhase = phase;
        
        // Hide all phase icons
        const icons = this.phaseIcon.querySelectorAll('svg, .icon-processing');
        icons.forEach(icon => icon.classList.add('hidden'));
        
        // Remove phase classes
        this.phaseIcon.classList.remove('listening', 'processing', 'speaking');
        
        // Show appropriate icon and set text
        switch (phase) {
            case 'initializing':
                const processingIcon1 = this.phaseIcon.querySelector('.icon-processing');
                if (processingIcon1) processingIcon1.classList.remove('hidden');
                this.phaseIcon.classList.add('processing');
                this.phaseText.textContent = 'Initializing...';
                break;
            case 'listening':
                const listeningIcon = this.phaseIcon.querySelector('.icon-listening');
                if (listeningIcon) listeningIcon.classList.remove('hidden');
                this.phaseIcon.classList.add('listening');
                this.phaseText.textContent = 'Listening...';
                break;
            case 'processing':
                const processingIcon2 = this.phaseIcon.querySelector('.icon-processing');
                if (processingIcon2) processingIcon2.classList.remove('hidden');
                this.phaseIcon.classList.add('processing');
                this.phaseText.textContent = 'Processing...';
                break;
            case 'speaking':
                const speakingIcon = this.phaseIcon.querySelector('.icon-speaking');
                if (speakingIcon) speakingIcon.classList.remove('hidden');
                this.phaseIcon.classList.add('speaking');
                this.phaseText.textContent = 'Speaking...';
                break;
            default:
                const readyIcon = this.phaseIcon.querySelector('.icon-ready');
                if (readyIcon) readyIcon.classList.remove('hidden');
                this.phaseText.textContent = 'Ready';
        }
    }

    handleSpeechResult(event) {
        let transcript = '';
        
        for (let i = 0; i < event.results.length; i++) {
            transcript += event.results[i][0].transcript;
        }

        console.log('Transcript:', transcript);
        
        if (transcript.trim()) {
            this.processVoiceCommand(transcript.trim());
        }
    }

    toggleVoiceRecognition() {
        if (this.recognition) {
            if (this.isListening) {
                this.recognition.stop();
            } else {
                try {
                    this.recognition.start();
                } catch (error) {
                    console.error('Error starting speech recognition:', error);
                    this.addMessage('jarvis', 'Speech recognition is not available or permission was denied.');
                }
            }
        } else {
            this.addMessage('jarvis', 'Speech recognition is not supported in this browser.');
        }
    }

    stopListening() {
        this.isListening = false;
        this.micButton.classList.remove('listening');
        this.setPhase('ready');
    }

    handleInputChange() {
        this.updateSendButtonState();
    }

    updateSendButtonState() {
        const hasText = this.messageInput.value.trim().length > 0;
        this.sendButton.disabled = !hasText || this.isProcessing;
    }

    handleKeyDown(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            this.sendMessage();
        }
    }

    autoResizeTextarea() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || this.isProcessing) {
            return;
        }

        console.log('Sending message:', message);
        
        // Clear input
        this.messageInput.value = '';
        this.autoResizeTextarea();
        this.updateSendButtonState();

        // Add user message
        this.addMessage('user', message);

        // Process the message
        await this.processMessage(message);
    }

    async processVoiceCommand(command) {
        console.log('Processing voice command:', command);
        this.addMessage('user', command);
        await this.processMessage(command);
    }

    async processMessage(message) {
        this.isProcessing = true;
        this.setPhase('processing');
        this.updateSendButtonState();

        try {
            // Simulate processing delay
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            const response = await this.generateResponse(message);
            this.addMessage('jarvis', response);
            
            // Speak the response
            setTimeout(() => {
                this.speak(response);
            }, 500);
            
        } catch (error) {
            console.error('Error processing message:', error);
            const errorResponse = "I'm sorry, I encountered an error processing your request.";
            this.addMessage('jarvis', errorResponse);
        } finally {
            this.isProcessing = false;
            this.setPhase('ready');
            this.updateSendButtonState();
        }
    }

    async generateResponse(message) {
        const lowerMessage = message.toLowerCase();

        // Website opening commands
        if (lowerMessage.includes('open google') || lowerMessage.includes('google')) {
            window.open('https://www.google.com', '_blank');
            return "Opening Google for you.";
        }
        
        if (lowerMessage.includes('open youtube') || lowerMessage.includes('youtube')) {
            window.open('https://www.youtube.com', '_blank');
            return "Opening YouTube for you.";
        }
        
        if (lowerMessage.includes('open instagram') || lowerMessage.includes('instagram')) {
            window.open('https://www.instagram.com', '_blank');
            return "Opening Instagram for you.";
        }
        
        if (lowerMessage.includes('open linkedin') || lowerMessage.includes('linkedin')) {
            window.open('https://www.linkedin.com', '_blank');
            return "Opening LinkedIn for you.";
        }

        // Music search commands
        if (lowerMessage.includes('play') || lowerMessage.includes('music')) {
            const songMatch = lowerMessage.match(/(?:play|music)\s+(.+?)(?:\s+song|\s+music|$)/);
            const songName = songMatch ? songMatch[1] : 'songs';
            window.open(`https://www.youtube.com/results?search_query=${encodeURIComponent(songName)}`, '_blank');
            return `Searching for "${songName}" on YouTube for you.`;
        }

        // News command
        if (lowerMessage.includes('news')) {
            window.open('https://news.google.com', '_blank');
            return "Opening Google News for the latest updates.";
        }

        // Time query
        if (lowerMessage.includes('time')) {
            const now = new Date();
            const timeString = now.toLocaleTimeString();
            return `The current time is ${timeString}.`;
        }

        // Date query
        if (lowerMessage.includes('date') || lowerMessage.includes('today')) {
            const now = new Date();
            const dateString = now.toLocaleDateString('en-US', { 
                weekday: 'long', 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
            });
            return `Today is ${dateString}.`;
        }

        // Weather query
        if (lowerMessage.includes('weather')) {
            return "I don't have access to real-time weather data, but I can help you open a weather website if you'd like.";
        }

        // Greetings
        if (lowerMessage.includes('hello') || lowerMessage.includes('hi') || lowerMessage.includes('hey')) {
            return "Hello! How can I assist you today? I can help you open websites, search for content, or answer questions.";
        }

        // Thank you
        if (lowerMessage.includes('thank') || lowerMessage.includes('thanks')) {
            return "You're welcome! Is there anything else I can help you with?";
        }

        // Help command
        if (lowerMessage.includes('help')) {
            return "I can help you with: Opening websites (Google, YouTube, Instagram, LinkedIn), Searching for music on YouTube, Getting news updates, Telling you the time and date, Managing your chat history. Try using the shortcut buttons below for quick actions!";
        }

        // Default response
        return this.generateGenericResponse(message);
    }

    generateGenericResponse(message) {
        const responses = [
            "That's an interesting question. I'd be happy to help you search for more information online.",
            "I understand what you're asking about. Would you like me to open Google so you can search for detailed information?",
            "That's a good question! I can help you find resources to learn more about this topic.",
            "I appreciate your question. Let me know if you'd like me to open any websites to help you find the information you need.",
            "Interesting topic! For comprehensive information, I can help you access relevant websites or search engines."
        ];
        
        return responses[Math.floor(Math.random() * responses.length)];
    }

    addMessage(sender, content) {
        console.log('Adding message:', { sender, content });
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `${sender}-message`;

        const bubble = document.createElement('div');
        bubble.className = `message-bubble ${sender}-bubble`;
        
        const paragraph = document.createElement('p');
        paragraph.textContent = content;
        paragraph.style.margin = '0';
        bubble.appendChild(paragraph);

        const timestamp = document.createElement('div');
        timestamp.className = 'message-timestamp';
        timestamp.textContent = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});

        messageDiv.appendChild(bubble);
        messageDiv.appendChild(timestamp);
        
        // Add to chat area
        this.chatArea.appendChild(messageDiv);
        this.scrollToBottom();

        // Store in conversation history
        const messageObj = {
            sender,
            content,
            timestamp: new Date().toISOString()
        };
        
        this.conversationHistory.push(messageObj);
        this.saveChatMessage(messageObj);
        
        console.log('Message added successfully');
    }

    speak(text) {
        if (this.synthesis && this.currentVoice) {
            this.synthesis.cancel();
            
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.voice = this.currentVoice;
            utterance.rate = 0.9;
            utterance.pitch = 1;
            utterance.volume = 0.8;

            utterance.onstart = () => {
                this.setPhase('speaking');
            };

            utterance.onend = () => {
                this.setPhase('ready');
            };

            utterance.onerror = (event) => {
                console.error('Speech synthesis error:', event);
                this.setPhase('ready');
            };

            this.synthesis.speak(utterance);
        }
    }

    openShortcut(url, name) {
        console.log('Opening shortcut:', name, url);
        window.open(url, '_blank');
        this.addMessage('jarvis', `Opening ${name} for you.`);
    }

    // Chat History Management
    saveChatMessage(message) {
        try {
            let chats = JSON.parse(localStorage.getItem('jarvis_chats') || '[]');
            
            if (!this.currentChatId) {
                this.currentChatId = 'chat_' + Date.now();
                const newChat = {
                    id: this.currentChatId,
                    title: message.content.substring(0, 50) + (message.content.length > 50 ? '...' : ''),
                    timestamp: new Date().toISOString(),
                    messages: []
                };
                chats.unshift(newChat);
            }
            
            const currentChat = chats.find(chat => chat.id === this.currentChatId);
            if (currentChat) {
                currentChat.messages.push(message);
                currentChat.timestamp = new Date().toISOString();
            }
            
            // Keep only last 50 conversations
            if (chats.length > 50) {
                chats = chats.slice(0, 50);
            }
            
            localStorage.setItem('jarvis_chats', JSON.stringify(chats));
            this.updateChatHistoryUI();
        } catch (error) {
            console.error('Error saving chat:', error);
        }
    }

    loadChatHistory() {
        this.updateChatHistoryUI();
    }

    updateChatHistoryUI() {
        try {
            const chats = JSON.parse(localStorage.getItem('jarvis_chats') || '[]');
            this.chatHistory.innerHTML = '';
            
            if (chats.length === 0) {
                this.chatHistory.innerHTML = '<div style="text-align: center; color: var(--color-text-secondary); font-size: var(--font-size-sm); padding: var(--space-16);">No chat history yet</div>';
                return;
            }
            
            chats.forEach(chat => {
                const chatItem = document.createElement('div');
                chatItem.className = 'chat-history-item';
                chatItem.innerHTML = `
                    <div class="chat-title">${chat.title}</div>
                    <div class="chat-preview">${chat.messages.length} messages</div>
                    <div class="chat-timestamp">${new Date(chat.timestamp).toLocaleDateString()}</div>
                `;
                
                chatItem.addEventListener('click', () => {
                    this.loadChat(chat.id);
                    this.closeSidebar();
                });
                
                this.chatHistory.appendChild(chatItem);
            });
        } catch (error) {
            console.error('Error updating chat history UI:', error);
        }
    }

    loadChat(chatId) {
        try {
            const chats = JSON.parse(localStorage.getItem('jarvis_chats') || '[]');
            const chat = chats.find(c => c.id === chatId);
            
            if (chat) {
                this.currentChatId = chatId;
                this.chatArea.innerHTML = '';
                this.conversationHistory = [];
                
                chat.messages.forEach(message => {
                    this.addMessage(message.sender, message.content);
                });
            }
        } catch (error) {
            console.error('Error loading chat:', error);
        }
    }

    startNewChat() {
        this.currentChatId = null;
        this.conversationHistory = [];
        this.showWelcomeMessage();
        this.closeSidebar();
    }

    // User Session Management
    loadUserSession() {
        try {
            const session = JSON.parse(localStorage.getItem('jarvis_session') || '{}');
            if (session.isLoggedIn) {
                this.isLoggedIn = true;
                this.currentUser = session.userName || 'User';
            }
            this.updateUserUI();
        } catch (error) {
            console.error('Error loading user session:', error);
            this.updateUserUI();
        }
    }

    handleLogin() {
        const name = prompt('Enter your name:');
        if (name && name.trim()) {
            this.isLoggedIn = true;
            this.currentUser = name.trim();
            this.saveUserSession();
            this.updateUserUI();
            this.addMessage('jarvis', `Welcome back, ${this.currentUser}!`);
        }
    }

    handleLogout() {
        this.isLoggedIn = false;
        this.currentUser = 'Guest User';
        this.saveUserSession();
        this.updateUserUI();
        this.addMessage('jarvis', 'You have been logged out.');
    }

    saveUserSession() {
        try {
            const session = {
                isLoggedIn: this.isLoggedIn,
                userName: this.currentUser
            };
            localStorage.setItem('jarvis_session', JSON.stringify(session));
        } catch (error) {
            console.error('Error saving user session:', error);
        }
    }

    updateUserUI() {
        if (this.userName) {
            this.userName.textContent = this.currentUser;
        }
        
        const userStatus = document.querySelector('.user-status');
        if (userStatus) {
            userStatus.textContent = this.isLoggedIn ? 'Logged in' : 'Not logged in';
        }
        
        if (this.loginBtn && this.logoutBtn) {
            if (this.isLoggedIn) {
                this.loginBtn.classList.add('hidden');
                this.logoutBtn.classList.remove('hidden');
            } else {
                this.loginBtn.classList.remove('hidden');
                this.logoutBtn.classList.add('hidden');
            }
        }
    }

    scrollToBottom() {
        setTimeout(() => {
            this.chatArea.scrollTop = this.chatArea.scrollHeight;
        }, 100);
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing Jarvis Assistant');
    window.jarvisApp = new JarvisAssistant();
});