document.addEventListener('DOMContentLoaded', () => {
    const gameContainer = document.getElementById('game-container');
    const gameList = document.getElementById('game-list');
    const closeBtn = document.getElementById('close-game');
    const emulatorFrame = document.getElementById('emulator-frame');
    const fileInput = document.getElementById('file-upload');

    // Function to open game
    window.playGame = function(gameId, title) {
        // Hide list, show game
        gameList.style.display = 'none';
        document.getElementById('controls').style.display = 'none';
        gameContainer.style.display = 'block';
        
        // Scroll to top
        window.scrollTo(0, 0);

        // Load game in iframe
        emulatorFrame.src = `player.html?game=${gameId}`;
        console.log(`Starting game: ${title} (${gameId})`);
    };

    // Close game
    closeBtn.addEventListener('click', () => {
        // Stop emulator by clearing src
        emulatorFrame.src = '';
        
        gameContainer.style.display = 'none';
        gameList.style.display = 'grid';
        document.getElementById('controls').style.display = 'block';
    });

    // File upload handler
    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (!file) return;

        // Create object URL
        const objectUrl = URL.createObjectURL(file);
        
        // Hide list, show game
        gameList.style.display = 'none';
        document.getElementById('controls').style.display = 'none';
        gameContainer.style.display = 'block';

        // Load with custom URL
        emulatorFrame.src = `player.html?url=${encodeURIComponent(objectUrl)}`;
        console.log(`Loading local file: ${file.name}`);
    });

    // Fullscreen button logic
    document.getElementById('fullscreen-game').addEventListener('click', () => {
        const docEl = emulatorFrame;
        const requestFullScreen = docEl.requestFullscreen || docEl.mozRequestFullScreen || docEl.webkitRequestFullScreen || docEl.msRequestFullscreen;
        
        if (requestFullScreen) {
            requestFullScreen.call(docEl);
        } else {
            const lang = localStorage.getItem('language') || 'ru';
            const msg = translations[lang] ? translations[lang].alert_fullscreen_error : translations['ru'].alert_fullscreen_error;
            alert(msg);
        }
    });

    // Try to get local IP from server
    fetch('/api/ip')
        .then(res => res.json())
        .then(data => {
            if (data.ip) {
                const url = `http://${data.ip}:8080`;
                document.getElementById('local-ip').textContent = url;
                
                // Generate QR Code
                if (typeof QRCode !== 'undefined') {
                    document.getElementById('qrcode').innerHTML = ''; // Clear previous
                    new QRCode(document.getElementById("qrcode"), {
                        text: url,
                        width: 128,
                        height: 128,
                        colorDark : "#000000",
                        colorLight : "#ffffff",
                        correctLevel : QRCode.CorrectLevel.H
                    });
                }
            }
        })
        .catch(e => console.log('Could not fetch IP'));
});
