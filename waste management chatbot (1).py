from flask import Flask, request, jsonify, Response

app = Flask(__name__)

# --- HTML Template ---
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vijayawada Waste Management Chatbot</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        /* --- CSS styles are embedded here --- */
        body {
            font-family: 'Inter', sans-serif;
        }

        .chat-btn {
            background-color: white;
            border: 1px solid #0d9488;
            color: #0d9488;
            padding: 8px 16px;
            border-radius: 9999px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
            margin-top: 8px;
            margin-right: 8px;
        }

        .chat-btn:hover {
            background-color: #0d9488;
            color: white;
        }

        .typing-indicator {
            display: flex;
            align-items: center;
        }

        .typing-indicator span {
            height: 8px;
            width: 8px;
            margin: 0 2px;
            background-color: #14b8a6;
            border-radius: 50%;
            display: inline-block;
            animation: bounce 1.4s infinite ease-in-out both;
        }

        .typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
        .typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

        @keyframes bounce {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1.0); }
        }
        
        @keyframes fade-in {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .animate-fade-in {
            animation: fade-in 0.3s ease-out forwards;
        }
    </style>
</head>
<body class="bg-gray-100 flex items-center justify-center h-screen">
    <div class="w-full max-w-lg bg-white rounded-2xl shadow-2xl flex flex-col h-[90vh]">
        <div class="bg-teal-600 text-white p-6 rounded-t-2xl shadow-lg flex items-center justify-between">
            <div>
                <h1 class="text-2xl font-bold">Vijayawada Waste Assistant</h1>
                <p class="text-sm opacity-90">Your guide to a cleaner city</p>
            </div>
            <div class="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
            </div>
        </div>
        <div id="chat-window" class="flex-1 p-6 overflow-y-auto">
            </div>
        <div class="p-6 bg-gray-50 rounded-b-2xl border-t border-gray-200">
            <div class="flex">
                <input type="text" id="user-input" class="flex-1 p-4 border border-gray-300 rounded-l-lg focus:outline-none focus:ring-2 focus:ring-teal-500" placeholder="Ask about schedules, bins, recycling...">
                <button id="send-btn" class="bg-teal-600 text-white px-6 py-4 rounded-r-lg hover:bg-teal-700 focus:outline-none focus:ring-2 focus:ring-teal-500 font-semibold">Send</button>
            </div>
        </div>
    </div>

    <script>
        // --- JavaScript is embedded here ---
        document.addEventListener("DOMContentLoaded", () => {
            const chatWindow = document.getElementById('chat-window');
            const userInput = document.getElementById('user-input');
            const sendBtn = document.getElementById('send-btn');

            const displayMessage = (message, sender) => {
                const messageDiv = document.createElement('div');
                messageDiv.classList.add('flex', 'mb-4', 'animate-fade-in');
                const messageBubble = document.createElement('div');
                messageBubble.classList.add('p-4', 'rounded-lg', 'max-w-md', 'shadow-md');

                if (sender === 'user') {
                    messageDiv.classList.add('justify-end');
                    messageBubble.classList.add('bg-gray-200', 'text-gray-800');
                    messageBubble.innerHTML = `<p>${message}</p>`;
                } else { // Bot
                    messageDiv.classList.add('justify-start');
                    messageBubble.classList.add('bg-teal-100', 'text-teal-800');
                    
                    if (message.includes('[BUTTONS]')) {
                        const parts = message.split('[BUTTONS]');
                        messageBubble.innerHTML = `<p>${parts[0]}</p>`;
                        const buttonLabels = parts[1].split('|');
                        const buttonContainer = document.createElement('div');
                        buttonContainer.classList.add('mt-2');

                        buttonLabels.forEach(label => {
                            const button = document.createElement('button');
                            button.textContent = label;
                            button.classList.add('chat-btn');
                            button.onclick = () => {
                                handleSend(label);
                                buttonContainer.querySelectorAll('.chat-btn').forEach(btn => {
                                    btn.disabled = true;
                                    btn.style.cursor = 'not-allowed';
                                    btn.style.opacity = '0.6';
                                });
                            };
                            buttonContainer.appendChild(button);
                        });
                        messageBubble.appendChild(buttonContainer);
                    } else {
                        messageBubble.innerHTML = `<p>${message}</p>`;
                    }
                }
                
                messageDiv.appendChild(messageBubble);
                chatWindow.appendChild(messageDiv);
                chatWindow.scrollTop = chatWindow.scrollHeight;
            };

            const showTypingIndicator = () => {
                const typingDiv = document.createElement('div');
                typingDiv.id = 'typing-indicator';
                typingDiv.classList.add('flex', 'justify-start', 'mb-4');
                typingDiv.innerHTML = `
                    <div class="bg-teal-100 text-teal-800 p-4 rounded-lg shadow-md typing-indicator">
                        <span></span><span></span><span></span>
                    </div>
                `;
                chatWindow.appendChild(typingDiv);
                chatWindow.scrollTop = chatWindow.scrollHeight;
            };

            const hideTypingIndicator = () => {
                const indicator = document.getElementById('typing-indicator');
                if (indicator) {
                    indicator.remove();
                }
            };

            const handleSend = async (prefilledInput = null) => {
                const userInputText = prefilledInput || userInput.value.trim();
                if (userInputText) {
                    displayMessage(userInputText, 'user');
                    userInput.value = '';
                    showTypingIndicator();

                    try {
                        const response = await fetch('/ask', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ message: userInputText })
                        });

                        const data = await response.json();
                        const botResponse = data.answer;

                        setTimeout(() => {
                            hideTypingIndicator();
                            displayMessage(botResponse, 'bot');
                        }, 500);

                    } catch (error) {
                        hideTypingIndicator();
                        displayMessage("Sorry, something went wrong. Please try again.", 'bot');
                        console.error("Error:", error);
                    }
                }
            };

            sendBtn.addEventListener('click', () => handleSend());
            userInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    handleSend();
                }
            });
            
            const welcomeMessage = "Hello! I'm the Vijayawada Waste Management Assistant. How can I help you today? [BUTTONS]Garbage Collection Schedule|How to Segregate Waste|Contact VMC";
            setTimeout(() => displayMessage(welcomeMessage, 'bot'), 500);
        });
    </script>
</body>
</html>
"""

# --- Backend Logic (Chatbot Brain) ---
knowledge_base = [
    {
        "id": 'greeting',
        "keywords": ['hello', 'hi', 'hey', 'yo', 'good morning', 'good afternoon'],
        "response": "Hi there! How can I assist you with waste management in Vijayawada today? [BUTTONS]Collection Schedule|Waste Segregation|Contact VMC"
    },
    {
        "id": 'help',
        "keywords": ['help', 'menu', 'options', 'what can you do'],
        "response": "I can help with the following topics. Just ask me, or click a button below! [BUTTONS]Garbage Collection|Waste Segregation|Recycling Centers|E-Waste|Report a Problem"
    },
    {
        "id": 'collection_schedule',
        "keywords": ['garbage', 'collection', 'schedule', 'timing', 'when', 'pickup', 'truck'],
        "response": "The Vijayawada Municipal Corporation (VMC) handles door-to-door garbage collection. Schedules can sometimes vary by ward. For the most accurate schedule in your area, it's best to contact the VMC directly or check the 'Puraseva' app."
    },
    {
        "id": 'segregation',
        "keywords": ['segregation', 'separate', 'divide', 'sort', 'bins', 'wet', 'dry', 'green', 'blue', 'color', 'codes', 'trash'],
        "response": "Waste segregation is crucial! Please use two bins:<br> • <strong>Green Bin:</strong> For wet waste (kitchen scraps, food leftovers, vegetable peels).<br> • <strong>Blue Bin:</strong> For dry waste (plastic, paper, metal, glass)."
    },
    {
        "id": 'recycling',
        "keywords": ['recycling', 'recycle', 'centers', 'scrap', 'aakri', 'paper', 'plastic', 'glass'],
        "response": "You can find several recycling centers in Vijayawada. A convenient option is the 'AAKRI' app, which lets you schedule a pickup for recyclable scrap from your doorstep. Local services include Greenstakes Recycling and Darji Go Green Recycling."
    },
    {
        "id": 'ewaste',
        "keywords": ['e-waste', 'electronic', 'computer', 'mobile', 'phone', 'batteries', 'tv'],
        "response": "Electronic waste (e-waste) is hazardous and should NOT be mixed with regular garbage. Please drop off old electronics, batteries, and CFL bulbs at designated VMC e-waste collection points or contact a certified e-waste recycler."
    },
    {
        "id": 'contact',
        "keywords": ['vmc', 'contact', 'number', 'phone', 'email', 'helpline', 'information'],
        "response": "You can contact the Vijayawada Municipal Corporation (VMC) at:<br> • <strong>Phone:</strong> 0866-2427 485 or 0866-2422 400<br> • <strong>Email:</strong> ourvmc@yahoo.com<br>You can also use the 'Puraseva' app to register grievances."
    },
    {
        "id": 'report',
        "keywords": ['report', 'problem', 'issue', 'complaint', 'grievance', 'garbage not collected'],
        "response": "To report an issue with garbage collection or sanitation, the fastest way is to use the **'Puraseva'** mobile app. Alternatively, you can call the VMC helpline numbers directly."
    },
    {
        "id": 'default',
        "keywords": [],
        "response": "I'm sorry, I don't have information on that. Please try rephrasing, or type 'help' to see what I can assist with. [BUTTONS]Help Menu"
    }
]

def get_nlu_response(user_input):
    lower_input = user_input.lower()
    best_match = {'id': 'default', 'score': 0}

    for topic in knowledge_base:
        score = 0
        for keyword in topic['keywords']:
            if keyword in lower_input:
                score += 1
        if score > best_match['score']:
            best_match = {'id': topic['id'], 'score': score}

    if best_match['score'] > 0:
        for topic in knowledge_base:
            if topic['id'] == best_match['id']:
                return topic['response']

    for topic in knowledge_base:
        if topic['id'] == 'default':
            return topic['response']

# --- API Routes ---
@app.route("/")
def index():
    """Serves the HTML page."""
    return Response(html_template, mimetype='text/html')

@app.route("/ask", methods=['POST'])
def ask():
    """Handles chat messages."""
    data = request.get_json()
    user_message = data.get("message")

    if not user_message:
        return jsonify({"answer": "Error: No message received."})

    bot_response = get_nlu_response(user_message)
    return jsonify({"answer": bot_response})

if __name__ == "__main__":
    # The port has been changed from 5000 to 5001
    app.run(debug=True, port=5001)