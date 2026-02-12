
// Enhanced frontend to work with the Python backend
class JarvisAssistant {
    constructor() {
        this.initializeElements();
        this.initializeState();
        this.bindEvents();
        this.initializeSpeechRecognition();
        this.initializeSpeechSynthesis();
        this.loadChatHistory();
        this.loadUserSession();

        // Connect to backend
        this.connectToBackend();

        // Show initial welcome message
        this.showWelcomeMessage();
    }

    initializeElements() {
        // Your existing element initialization code stays the same
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

        // Backend connection
        this.websocket = null;
        this.isConnectedToBackend = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;

        // Show initializing phase
        this.setPhase('initializing');

        // Initialize UI state after a delay
        setTimeout(() => {
            if (!this.isConnectedToBackend) {
                this.setPhase('ready');
            }
            this.updateSendButtonState();
        }, 3000);
    }

    // Backend Connection Methods
    connectToBackend() {
        console.log('🔌 Attempting to connect to Jarvis backend...');

        try {
            this.websocket = new WebSocket('ws://localhost:8765');

            this.websocket.onopen = () => {
                console.log('✅ Connected to Jarvis backend!');
                this.isConnectedToBackend = true;
                this.reconnectAttempts = 0;
                this.setPhase('ready');

                // Send connection test
                this.sendToBackend({
                    type: 'ping',
                    timestamp: new Date().toISOString()
                });
            };

            this.websocket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleBackendMessage(data);
                } catch (error) {
                    console.error('Error parsing backend message:', error);
                }
            };

            this.websocket.onclose = () => {
                console.log('❌ Disconnected from backend');
                this.isConnectedToBackend = false;
                this.setPhase('ready');

                // Attempt to reconnect
                if (this.reconnectAttempts < this.maxReconnectAttempts) {
                    this.reconnectAttempts++;
                    console.log(`🔄 Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
                    setTimeout(() => this.connectToBackend(), 3000 * this.reconnectAttempts);
                } else {
                    this.addMessage('jarvis', 'Lost connection to backend. Voice features are disabled. Please restart the Python server and refresh the page.');
                }
            };

            this.websocket.onerror = (error) => {
                console.error('❌ WebSocket error:', error);
                this.isConnectedToBackend = false;
                this.setPhase('ready');
            };

        } catch (error) {
            console.error('Failed to create WebSocket connection:', error);
            this.isConnectedToBackend = false;
            this.setPhase('ready');
            this.addMessage('jarvis', 'Could not connect to backend. Please make sure to run: python jarvis_backend_complete.py');
        }
    }

    sendToBackend(data) {
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.send(JSON.stringify(data));
            return true;
        } else {
            console.warn('Backend not connected. Message not sent:', data);
            return false;
        }
    }

    handleBackendMessage(data) {
        const { type, phase, message, content } = data;

        switch (type) {
            case 'phase_update':
                this.setPhase(phase);
                if (phase === 'listening') {
                    this.micButton.classList.add('listening');
                } else {
                    this.micButton.classList.remove('listening');
                }
                break;

            case 'jarvis_message':
            case 'jarvis_response':
                this.addMessage('jarvis', content);
                break;

            case 'voice_user_message':
                this.addMessage('user', content);
                break;

            case 'status_update':
                // Handle status updates
                console.log('Status:', message);
                break;

            case 'pong':
                console.log('🏓 Backend connection confirmed');
                break;

            default:
                console.log('Unknown message type from backend:', type, data);
        }
    }

    // Your existing methods with backend integration
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
                this.handleShortcut(name);
            });
        });
    }

    handleShortcut(name) {
        if (this.isConnectedToBackend) {
            // Send to backend for processing
            this.sendToBackend({
                type: 'text_command',
                message: `open ${name.toLowerCase()}`,
                timestamp: new Date().toISOString()
            });
        } else {
            // Fallback to local handling
            this.openShortcut(this.getUrlForShortcut(name), name);
        }
    }

    getUrlForShortcut(name) {
        const urls = {
            'Google': 'https://www.google.com',
            'YouTube': 'https://www.youtube.com',
            'Instagram': 'https://www.instagram.com',
            'LinkedIn': 'https://www.linkedin.com'
        };
        return urls[name] || 'https://www.google.com';
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
                console.log('Local speech recognition started');
                this.isListening = true;
                this.setPhase('listening');
                this.micButton.classList.add('listening');
            };

            this.recognition.onresult = (event) => {
                console.log('Local speech result received:', event);
                this.handleSpeechResult(event);
            };

            this.recognition.onerror = (event) => {
                console.error('Local speech recognition error:', event.error);
                this.stopListening();
                if (event.error === 'not-allowed') {
                    this.addMessage('jarvis', 'Microphone access denied. Please enable microphone permissions.');
                }
            };

            this.recognition.onend = () => {
                console.log('Local speech recognition ended');
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
                    <p>Hello! I'm Jarvis, your AI assistant.</p>
                    <ul>
                        <li><strong>Backend Connection:</strong> ${this.isConnectedToBackend ? 'Connected ✅' : 'Connecting... 🔄'}</li>
                        <li><strong>Voice Commands:</strong> Click the microphone or type messages</li>
                        <li><strong>Quick Actions:</strong> Use the shortcut buttons below</li>
                        <li><strong>Chat History:</strong> Access previous conversations from the sidebar</li>
                    </ul>
                    <p>How can I help you today?</p>
                </div>
                <div class="message-timestamp">Just now</div>
            </div>
        `;
        this.chatArea.appendChild(welcomeDiv);
    }

    toggleVoiceRecognition() {
        if (this.isConnectedToBackend) {
            // Use backend speech recognition
            this.sendToBackend({
                type: 'voice_request',
                timestamp: new Date().toISOString()
            });
        } else {
            // Fallback to local speech recognition
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

        // Send to backend if connected, otherwise process locally
        if (this.isConnectedToBackend) {
            this.sendToBackend({
                type: 'text_command',
                message: message,
                timestamp: new Date().toISOString()
            });
        } else {
            // Fallback to local processing
            await this.processMessage(message);
        }
    }

    // Keep all your existing methods (setPhase, addMessage, etc.)
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
                this.phaseText.textContent = this.isConnectedToBackend ? 'Ready (Backend Connected)' : 'Ready (Local Mode)';
        }
    }

    // Keep all your other existing methods...
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

    async processVoiceCommand(command) {
        console.log('Processing voice command:', command);
        this.addMessage('user', command);

        if (this.isConnectedToBackend) {
            this.sendToBackend({
                type: 'text_command',
                message: command,
                timestamp: new Date().toISOString()
            });
        } else {
            await this.processMessage(command);
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

    async processMessage(message) {
        this.isProcessing = true;
        this.setPhase('processing');
        this.updateSendButtonState();

        try {
            await new Promise(resolve => setTimeout(resolve, 1000));
            const response = await this.generateResponse(message);
            this.addMessage('jarvis', response);
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
        // Fallback local responses (kept from your original code)
        const lowerMessage = message.toLowerCase();

        if (lowerMessage.includes('open google') || lowerMessage.includes('google')) {
            window.open('https://www.google.com', '_blank');
            return "Opening Google for you.";
        }
        // ... keep all your other response logic

        return "I understand. For full functionality, please connect to the Python backend by running 'python jarvis_backend_complete.py'";
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

        this.chatArea.appendChild(messageDiv);
        this.scrollToBottom();

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
        if (this.synthesis && this.currentVoice && !this.isConnectedToBackend) {
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
        // If connected to backend, speech is handled by backend
    }

    openShortcut(url, name) {
        console.log('Opening shortcut:', name, url);
        window.open(url, '_blank');
        this.addMessage('jarvis', `Opening ${name} for you.`);
    }

    // Keep all your existing chat history and user session methods...
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
    console.log('DOM loaded, initializing Jarvis Assistant with Backend Connection');
    window.jarvisApp = new JarvisAssistant();
});
