chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "processMessages") {
        let messages = request.data;

        console.log("Messages received for analysis:", messages);

        // Send messages to Flask server for analysis
        fetch('http://localhost:5000/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ messages: messages })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok: ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            console.log('Data from /analyze:', data);
            const { counts } = data;

            // Determine the threat level based on word counts
            let threatLevel = 3; // Default: Level 3 (friendly/neutral)
            if (counts.non_friendly > counts.friendly && counts.non_friendly > counts.neutral) {
                threatLevel = 1; // Level 1: Non-friendly words dominate
            } else if (counts.non_friendly === counts.friendly || counts.non_friendly === counts.neutral) {
                threatLevel = 2; // Level 2: Balance between friendly/neutral and non-friendly
            }

            console.log(`Threat Level: ${threatLevel}`);

            // Collect all non-friendly words from analysis results
            let allNonFriendlyWords = [];
            data.results.forEach(result => {
                if (result.non_friendly_words.length > 0) {
                    allNonFriendlyWords.push(...result.non_friendly_words);
                }
            });

            // Send the threat level and non-friendly words to Flask as a notification
            fetch('http://localhost:5000/notify', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message_type: `Threat Level ${threatLevel}`,
                    messages: messages,
                    analysis: data.results,
                    non_friendly_words: allNonFriendlyWords // Send non-friendly words in the notification
                })
            })
            .then(notifyResponse => {
                if (!notifyResponse.ok) {
                    throw new Error('Notification failed: ' + notifyResponse.statusText);
                }
                return notifyResponse.json();
            })
            .then(notifyData => {
                console.log('Notification sent successfully:', notifyData);
            })
            .catch(error => {
                console.error('Error sending notification:', error);
            });

            sendResponse(data.results);
        })
        .catch(error => {
            console.error('Error analyzing messages:', error);
            sendResponse({ error: error.message });
        });

        return true;
    }
});
