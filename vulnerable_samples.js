// JavaScript security vulnerabilities demonstration

// Cross-site Scripting (XSS) vulnerability
function displayUserContent(userInput) {
    // Vulnerable: Direct insertion of user input into DOM
    document.getElementById('content').innerHTML = userInput;
}

// Safer alternative
function displayUserContentSafely(userInput) {
    const safeContent = document.createTextNode(userInput);
    document.getElementById('content').appendChild(safeContent);
}

// Prototype pollution
function mergeObjects(target, source) {
    for (let key in source) {
        // Vulnerable: No hasOwnProperty check
        target[key] = source[key];
    }
    return target;
}

// DOM-based XSS from URL parameters
function loadContent() {
    const urlParams = new URLSearchParams(window.location.search);
    const message = urlParams.get('message');
    
    // Vulnerable: XSS risk
    document.querySelector('.message-box').innerHTML = message;
}

// Insecure use of eval
function calculateExpression(expression) {
    // Vulnerable: RCE risk
    return eval(expression);
} 