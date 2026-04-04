const canvas = document.getElementById('matrix-canvas');

if (canvas) {
    const ctx = canvas.getContext('2d');

    // Make canvas full screen
    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();

    const chars = '01'; // Binary code only
    const fontSize = 16;
    let columns = Math.floor(canvas.width / fontSize);
    let drops = [];

    // Initialize drop positions
    for (let x = 0; x < columns; x++) {
        drops[x] = Math.random() * -100; // Start at random negative y offsets
    }

    // Update columns on resize seamlessly
    window.addEventListener('resize', () => {
        let newColumns = Math.floor(window.innerWidth / fontSize);
        if (newColumns > columns) {
            for (let x = columns; x < newColumns; x++) {
                drops[x] = Math.random() * -100;
            }
        }
        columns = newColumns;
    });

    // Theme Colors: Green, White, Purple
    // We weight the array to make Green the most common color (80s hacker primary)
    const colors = [
        '#00ff00', '#00ff00', '#00ff00', '#00ff00', '#00ff00', 
        '#ffffff', // White
        '#9900ff'  // Purple
    ];

    function draw() {
        // Semi-transparent true black background to create the fading trail effect
        ctx.fillStyle = 'rgba(0, 0, 0, 0.08)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        ctx.font = fontSize + 'px "VT323", monospace';

        for (let i = 0; i < drops.length; i++) {
            // Pick a random 0 or 1
            const text = chars.charAt(Math.floor(Math.random() * chars.length));
            
            // Randomly select a color from the weighted pool
            ctx.fillStyle = colors[Math.floor(Math.random() * colors.length)];
            
            // Draw character
            ctx.fillText(text, i * fontSize, drops[i] * fontSize);

            // Send drop back to the top randomly once it exceeds the screen
            if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
                drops[i] = 0;
            }

            // Move drop down
            drops[i]++;
        }
    }

    // Run animation
    setInterval(draw, 50);
}
