document.addEventListener('DOMContentLoaded', () => {
    const messageList = document.getElementById('message-list');
    const messageForm = document.getElementById('message-form');
    const userInput = document.getElementById('user-input');
    const contentInput = document.getElementById('content-input');
    const sendButton = document.getElementById('send-button');

    // Fetch initial messages
    fetchMessages();

    // Handle form submission
    messageForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const user = userInput.value.trim();
        const content = contentInput.value.trim();

        if (!user || !content) return;

        // Disable UI
        setLoadingState(true);

        try {
            const response = await fetch('/api/messages', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ user, content }),
            });

            if (response.ok) {
                contentInput.value = '';
                await fetchMessages();
            } else {
                console.error('Failed to send message');
            }
        } catch (error) {
            console.error('Error:', error);
        } finally {
            setLoadingState(false);
        }
    });

    async function fetchMessages() {
        try {
            const response = await fetch('/api/messages');
            const messages = await response.json();
            renderMessages(messages);
        } catch (error) {
            console.error('Error fetching messages:', error);
            messageList.innerHTML = '<div class="loading">Connection lost to nebula.</div>';
        }
    }

    function renderMessages(messages) {
        if (messages.length === 0) {
            messageList.innerHTML = '<div class="loading">No transmissions yet. Start the conversation!</div>';
            return;
        }

        messageList.innerHTML = messages.map(msg => `
            <div class="message-item">
                <div class="message-header">
                    <span class="message-user">${escapeHtml(msg.user)}</span>
                    <span class="message-id">#${msg.id}</span>
                </div>
                <div class="message-content">${escapeHtml(msg.content)}</div>
            </div>
        `).join('');

        // Scroll to bottom
        const container = document.getElementById('message-list-container');
        container.scrollTop = container.scrollHeight;
    }

    function setLoadingState(isLoading) {
        sendButton.disabled = isLoading;
        sendButton.style.opacity = isLoading ? '0.7' : '1';
        sendButton.querySelector('span').textContent = isLoading ? 'Sending...' : 'Send';
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Auto-refresh every 5 seconds (simple polling)
    setInterval(fetchMessages, 5000);
});
