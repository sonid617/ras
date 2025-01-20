document.getElementById('analyzeButton').addEventListener('click', () => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        chrome.scripting.executeScript(
            {
                target: { tabId: tabs[0].id },
                func: () => {
                    let messages = [];
                    let messageElements = document.querySelectorAll('.message-in .selectable-text');
                    messageElements.forEach((element) => {
                        messages.push(element.innerText);
                    });
                    return messages;
                }
            },
            (results) => {
                if (results && results[0]) {
                    const messages = results[0].result;
                    chrome.runtime.sendMessage({ action: "processMessages", data: messages }, (response) => {
                        if (response && !response.error) {
                            displayResults(response); // Ensure displayResults is defined before calling
                            renderPieChart(response);
                            checkAndNotify(response); // Assuming you want to keep the notification check
                        } else {
                            displayError(response ? response.error : 'Unknown error');
                        }
                    });
                }
            }
        );
    });
});

function displayResults(results) {
    const resultsContainer = document.getElementById('results');
    resultsContainer.innerHTML = '';

    results.forEach((result) => {
        const messageElement = document.createElement('div');
        messageElement.innerHTML = `
            <p><strong>Message:</strong> ${result.message}</p>
            <p><strong>Sentiment:</strong> ${result.sentiment}</p>
            <p><strong>Behavior:</strong> ${result.behavior}</p>
            <hr>
        `;
        resultsContainer.appendChild(messageElement);
    });
}

function displayError(error) {
    const resultsContainer = document.getElementById('results');
    resultsContainer.innerHTML = `<p>Error: ${error}</p>`;
}

function renderPieChart(results) {
    const ctx = document.getElementById('sentimentChart').getContext('2d');
    const sentiments = results.map(result => result.behavior); // Use behavior for the chart
    const sentimentCounts = {
        friendly: sentiments.filter(s => s === 'friendly').length,
        neutral: sentiments.filter(s => s === 'neutral').length,
        non_friendly: sentiments.filter(s => s === 'non-friendly').length,
        potential_non_friendly: sentiments.filter(s => s === 'potential non-friendly').length,
    };

    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Friendly', 'Neutral', 'Non-Friendly', 'Potential Non-Friendly'],
            datasets: [{
                data: [
                    sentimentCounts.friendly,
                    sentimentCounts.neutral,
                    sentimentCounts.non_friendly,
                    sentimentCounts.potential_non_friendly
                ],
                backgroundColor: ['#4caf50', '#ffeb3b', '#f44336', '#ff9800'], // Color coding
            }]
        },
        options: {
            responsive: true,
        }
    });
}

function checkAndNotify(results) {
    let nonFriendlyCount = 0;
    let potentialNonFriendlyCount = 0;

    results.forEach(result => {
        if (result.behavior === 'non-friendly') {
            nonFriendlyCount++;
        } else if (result.behavior === 'potential non-friendly') {
            potentialNonFriendlyCount++;
        }
    });

    const NOTIFICATION_THRESHOLD = 5;

    if (nonFriendlyCount >= NOTIFICATION_THRESHOLD) {
        sendNotification('Non-Friendly Messages', `You have ${nonFriendlyCount} non-friendly messages.`);
    }

    if (potentialNonFriendlyCount >= NOTIFICATION_THRESHOLD) {
        sendNotification('Potential Non-Friendly Messages', `You have ${potentialNonFriendlyCount} potential non-friendly messages.`);
    }
}

function sendNotification(title, message) {
    chrome.notifications.create({
        type: 'basic',
        iconUrl: 'icon.', // Update with your icon path
        title: title,
        message: message,
        priority: 2
    });
}
