document.addEventListener('DOMContentLoaded', () => {
    fetchDiscordProfile();
});

async function fetchDiscordProfile() {
    const profileContainer = document.getElementById('discord-profile');
    
    try {
        const response = await fetch('/api/discord');
        const data = await response.json();
        
        if (response.ok) {
            // Check if backend warned us about tokens (using dummy data fallback)
            let profile = data;
            if (data.error && data.dummy_data) {
                console.warn(data.error + " - Using dummy data");
                profile = data.dummy_data;
            } else if (data.error) {
                throw new Error(data.error);
            }

            renderProfile(profileContainer, profile);
        } else {
            throw new Error(data.error || "Failed to load profile");
        }
    } catch (error) {
        profileContainer.innerHTML = `<div class="error" style="color: var(--text-neon-pink);">> ERROR: ${error.message}</div>`;
    }
}

function renderProfile(container, data) {
    container.innerHTML = `
        <div class="avatar-container">
            <img src="${data.avatar_url}" alt="Discord Avatar" class="avatar">
        </div>
        <div class="user-details">
            <div class="display-name">${data.display_name}</div>
            <div class="username">@${data.username}</div>
        </div>
    `;
}

// -----------------------------------------
// INTRO SEQUENCE LOGIC
// -----------------------------------------
const introOverlay = document.getElementById('intro-overlay');
const scannerContainer = document.getElementById('scanner-container');
const fingerprintBtn = document.getElementById('fingerprint-btn');
const progressContainer = document.getElementById('scan-progress-container');
const progressBar = document.getElementById('scan-progress');
const scanStatus = document.getElementById('scan-status');
const bootSequence = document.getElementById('boot-sequence');
const bootLog = document.getElementById('boot-log');

let holdTimer;
let holdProgress = 0;
const HOLD_DURATION = 2000; // Time in milliseconds required to hold

// Check if already authenticated this session so we don't repeat the intro every refresh
if (sessionStorage.getItem('authenticated') === 'true') {
    introOverlay.style.display = 'none';
    typeTitle(); // Start typing right away since intro is skipped
} else {
    // Hide main scrollbar while in intro
    document.body.style.overflow = 'hidden';
}

function startScanning(e) {
    if (e.type === 'touchstart') e.preventDefault();
    holdProgress = 0;
    scanStatus.innerText = "> SCANNING BIOMETRICS...";
    scanStatus.classList.remove('blink-slow');
    progressContainer.classList.remove('hidden');
    progressBar.style.width = '0%';
    progressBar.style.backgroundColor = 'var(--text-neon-cyan)';
    
    const intervalTime = 50; 
    
    holdTimer = setInterval(() => {
        holdProgress += intervalTime;
        const width = (holdProgress / HOLD_DURATION) * 100;
        progressBar.style.width = `${width}%`;
        
        if (holdProgress >= HOLD_DURATION) {
            clearInterval(holdTimer);
            handleSuccess();
        }
    }, intervalTime);
}

function stopScanning(e) {
    if (e.type === 'touchend') e.preventDefault();
    if (holdProgress < HOLD_DURATION) {
        clearInterval(holdTimer);
        progressBar.style.width = '0%';
        progressContainer.classList.add('hidden');
        scanStatus.innerText = "> AUTHENTICATION FAILED. HOLD LONGER.";
        scanStatus.style.color = "var(--text-neon-pink)";
        
        setTimeout(() => {
            if (scanStatus.innerText.includes("FAILED")) {
                scanStatus.innerText = ">>> AWAITING AUTHENTICATION <<<";
                scanStatus.style.color = "var(--text-primary)";
                scanStatus.classList.add('blink-slow');
            }
        }, 2000);
    }
}

// Event listeners for holding the button
fingerprintBtn.addEventListener('mousedown', startScanning);
fingerprintBtn.addEventListener('mouseup', stopScanning);
fingerprintBtn.addEventListener('mouseleave', stopScanning);
fingerprintBtn.addEventListener('touchstart', startScanning);
fingerprintBtn.addEventListener('touchend', stopScanning);

function handleSuccess() {
    scanStatus.innerText = "> ACCESS GRANTED";
    scanStatus.style.color = "var(--text-primary)";
    progressBar.style.backgroundColor = "var(--text-primary)";
    
    // Disable hovering/clicking again
    fingerprintBtn.style.pointerEvents = 'none';
    
    setTimeout(() => {
        scannerContainer.style.display = 'none';
        bootSequence.classList.remove('hidden');
        runBootSequence();
    }, 1500);
}

const bootLines = [
    "> ESTABLISHING SECURE CONNECTION...",
    "> DECRYPTING USER DATABANKS (RSA-4096)...",
    "> LOADING PORTFOLIO.SYS...",
    "> BYPASSING MAINFRAME FIREWALL...",
    "> SYSTEM READY."
];

function runBootSequence() {
    let i = 0;
    const interval = setInterval(() => {
        if (i < bootLines.length) {
            const li = document.createElement('li');
            li.innerHTML = `<span class="prompt">root@system:~#</span> ${bootLines[i]}`;
            bootLog.appendChild(li);
            // Quick scroll to bottom if needed
            window.scrollTo(0, document.body.scrollHeight);
            i++;
        } else {
            clearInterval(interval);
            const finalCursor = document.getElementById('final-cursor');
            if (finalCursor) finalCursor.classList.remove('hidden');
            
            setTimeout(() => {
                introOverlay.classList.add('hidden'); // Fades out due to CSS transition
                document.body.style.overflow = 'auto'; // Restore scrolling
                sessionStorage.setItem('authenticated', 'true');
                
                typeTitle(); // Type out the portfolio title when revealing
                
                setTimeout(() => introOverlay.remove(), 1000); // Clean up DOM
            }, 1500);
        }
    }, 700); // Delay between each text line
}

// -----------------------------------------
// TYPING TITLE LOGIC
// -----------------------------------------
function typeTitle() {
    const titleElement = document.getElementById('main-title');
    const targetText = "WELCOME BACK AGENT-Q";
    let titleIndex = 0;
    
    titleElement.textContent = "\u00A0"; // Prevent height collapse 
    titleElement.style.borderRight = "4px solid var(--text-primary)";
    titleElement.style.paddingRight = "5px";
    
    // Animate character by character
    const typeInterval = setInterval(() => {
        if (titleIndex === 0) titleElement.textContent = ""; // Clear initial space
        
        titleElement.textContent += targetText[titleIndex];
        titleElement.setAttribute('data-text', titleElement.textContent); // Update glitch attribute
        titleIndex++;
        
        if (titleIndex === targetText.length) {
            clearInterval(typeInterval);
            // Optionally blink the cursor infinitely
            titleElement.classList.add('blink-slow');
        }
    }, 120); // 120ms per character for satisfying retro typing speed
}
