// Function to extract chat messages
function getChatMessages() {
    let messages = [];
    let messageElements = document.querySelectorAll('.message-in .selectable-text');

    messageElements.forEach((element) => {
        messages.push(element.innerText);
    });

    return messages;
}

// Function to send messages to background script for processing
function sendMessagesToBackground(messages) {
    chrome.runtime.sendMessage({ action: "processMessages", data: messages });
}

// Extract chat messages and send them to background script
let chatMessages = getChatMessages();
sendMessagesToBackground(chatMessages);

// Listen for new messages
let chatObserver = new MutationObserver(() => {
    let newMessages = getChatMessages();
    sendMessagesToBackground(newMessages);
});

let chatHistory = document.querySelector('.chat-history');
if (chatHistory) {
    chatObserver.observe(chatHistory, { childList: true, subtree: true });
} else {
    console.error('Chat history element not found');
}



