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
// -----------------------------------------
// INTRO SEQUENCE LOGIC
// -----------------------------------------
const introOverlay = document.getElementById('intro-overlay');
const cmdContainer = document.getElementById('cmd-container');
const cmdInput = document.getElementById('cmd-input');
const cmdContent = document.getElementById('cmd-content');
const bootSequence = document.getElementById('boot-sequence');
const bootLog = document.getElementById('boot-log');

// Check if already authenticated this session
if (sessionStorage.getItem('authenticated') === 'true') {
    introOverlay.style.display = 'none';
    typeTitle(); // Start typing right away since intro is skipped
} else {
    // Hide main scrollbar while in intro
    document.body.style.overflow = 'hidden';
    if (cmdInput) {
        cmdInput.focus();
        
        // Ensure input stays focused if user clicks anywhere inside the terminal
        document.addEventListener('click', (e) => {
            if (introOverlay && introOverlay.style.display !== 'none') {
                 cmdInput.focus();
            }
        });

        cmdInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                const val = this.value.trim().toLowerCase();
                
                // Echo the command visually
                const echoLine = document.createElement('p');
                echoLine.textContent = `C:\\root\\access> ${this.value}`;
                cmdContent.insertBefore(echoLine, cmdInput.parentElement);
                
                this.value = ''; // clear input

                if (val === 'yes') {
                    handleSuccess();
                } else if (val === 'no') {
                    // Navigate to the coming soon page
                    window.location.href = '/coming-soon';
                } else {
                    const errorMsg = document.createElement('p');
                    errorMsg.className = 'error-text';
                    errorMsg.textContent = `'${val}' is not recognized. Please type 'yes' or 'no'.`;
                    cmdContent.insertBefore(errorMsg, cmdInput.parentElement);
                    cmdContent.scrollTop = cmdContent.scrollHeight;
                }
            }
        });
    }
}

function handleSuccess() {
    // Disable input
    cmdInput.disabled = true;
    
    // Quick pause then start real boot sequence
    setTimeout(() => {
        cmdContainer.style.display = 'none';
        bootSequence.classList.remove('hidden');
        runBootSequence();
    }, 800);
}

const bootLines = [
    "> Establishing secure connection...",
    "> Decrypting user databanks (RSA-4096)...",
    "> Loading portfolio.sys...",
    "> Bypassing mainframe firewall...",
    "> System ready."
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
    const targetText = "Welcome back Agent-Q";
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
