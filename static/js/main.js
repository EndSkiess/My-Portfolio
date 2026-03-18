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
