document.addEventListener('DOMContentLoaded', () => {
    // Game State
    let state = {
        hype: 50,
        tactica: 50,
        sorpresa: 50,
        logistica: 50
    };

    const MAX_VAL = 100;
    const MIN_VAL = 0;

    // Dummy Cards Data
    const CARDS = [
        {
            title: "Argentina vs Francia",
            desc: "La revancha de Qatar 2022. ¿Querés ver a Messi vs Mbappé una vez más?",
            swipeRight: { hype: 25, tactica: 10, sorpresa: -15, logistica: -5 },
            swipeLeft: { hype: -20, tactica: -5, sorpresa: 10, logistica: 5 }
        },
        {
            title: "Japón vs Senegal",
            desc: "Un choque de estilos completamente diferentes. Pura velocidad y contraataque.",
            swipeRight: { hype: 5, tactica: 20, sorpresa: 15, logistica: 10 },
            swipeLeft: { hype: -5, tactica: -10, sorpresa: -15, logistica: 0 }
        },
        {
            title: "Marruecos vs España",
            desc: "Un derbi del estrecho. Alta tensión táctica y clima infernal.",
            swipeRight: { hype: 15, tactica: 15, sorpresa: 10, logistica: -10 },
            swipeLeft: { hype: -10, tactica: -10, sorpresa: -5, logistica: 5 }
        },
        {
            title: "USA vs México",
            desc: "El clásico de CONCACAF en suelo norteamericano.",
            swipeRight: { hype: 20, tactica: -5, sorpresa: -10, logistica: 20 },
            swipeLeft: { hype: -15, tactica: 5, sorpresa: 10, logistica: -15 }
        },
        {
            title: "Brasil vs Alemania",
            desc: "Fantasmas del 7-1. ¿Habrá redención o nueva humillación?",
            swipeRight: { hype: 30, tactica: 10, sorpresa: -5, logistica: -5 },
            swipeLeft: { hype: -25, tactica: -5, sorpresa: 5, logistica: 5 }
        }
    ];

    let currentCardIndex = 0;

    const deckEl = document.getElementById('deck');
    const bgOverlay = document.getElementById('background-overlay');

    // Init Meters
    updateMeters();
    renderTopCard();

    function renderTopCard() {
        if (currentCardIndex >= CARDS.length) {
            // Loop
            currentCardIndex = 0; 
        }

        const cardData = CARDS[currentCardIndex];
        
        const cardEl = document.createElement('div');
        cardEl.className = 'swipe-card';
        cardEl.innerHTML = `
            <div class="card-indicator indicator-like">SÍ</div>
            <div class="card-indicator indicator-nope">NO</div>
            <h2 class="card-title">${cardData.title}</h2>
            <p class="card-desc">${cardData.desc}</p>
        `;

        deckEl.appendChild(cardEl);
        initDrag(cardEl, cardData);
    }

    function updateMeters() {
        document.getElementById('bar-hype').style.width = `${state.hype}%`;
        document.getElementById('bar-tactica').style.width = `${state.tactica}%`;
        document.getElementById('bar-sorpresa').style.width = `${state.sorpresa}%`;
        document.getElementById('bar-logistica').style.width = `${state.logistica}%`;

        checkWinCondition();
    }

    function applyImpact(impacts) {
        state.hype = Math.max(MIN_VAL, Math.min(MAX_VAL, state.hype + impacts.hype));
        state.tactica = Math.max(MIN_VAL, Math.min(MAX_VAL, state.tactica + impacts.tactica));
        state.sorpresa = Math.max(MIN_VAL, Math.min(MAX_VAL, state.sorpresa + impacts.sorpresa));
        state.logistica = Math.max(MIN_VAL, Math.min(MAX_VAL, state.logistica + impacts.logistica));
        updateMeters();
    }

    function checkWinCondition() {
        if (state.hype >= 100 || state.tactica >= 100 || state.sorpresa >= 100 || state.logistica >= 100) {
            // Glitch Effect Win
            setTimeout(() => {
                document.getElementById('match-found-screen').classList.remove('hidden');
                document.getElementById('match-found-details').innerText = `Tu partido ideal: ${CARDS[currentCardIndex===0 ? CARDS.length-1 : currentCardIndex-1].title}`;
            }, 300);
        }
    }

    // Drag Logic
    function initDrag(card, data) {
        let isDragging = false;
        let startX = 0, startY = 0;
        let currentX = 0, currentY = 0;

        const likeIndicator = card.querySelector('.indicator-like');
        const nopeIndicator = card.querySelector('.indicator-nope');

        const onStart = (e) => {
            isDragging = true;
            startX = e.type.includes('mouse') ? e.clientX : e.touches[0].clientX;
            startY = e.type.includes('mouse') ? e.clientY : e.touches[0].clientY;
            card.style.transition = 'none';
        };

        const onMove = (e) => {
            if (!isDragging) return;
            const x = e.type.includes('mouse') ? e.clientX : e.touches[0].clientX;
            const y = e.type.includes('mouse') ? e.clientY : e.touches[0].clientY;
            
            currentX = x - startX;
            currentY = y - startY;

            const rotate = currentX * 0.05;
            card.style.transform = `translate(${currentX}px, ${currentY}px) rotate(${rotate}deg)`;

            // Visual feedback background
            const intensity = Math.min(Math.abs(currentX) / 200, 1) * 0.4;
            if (currentX > 0) {
                bgOverlay.style.backgroundColor = `rgba(57, 255, 20, ${intensity})`; // Green
                likeIndicator.style.opacity = intensity * 2;
                nopeIndicator.style.opacity = 0;
            } else {
                bgOverlay.style.backgroundColor = `rgba(255, 0, 127, ${intensity})`; // Pink/Red
                nopeIndicator.style.opacity = intensity * 2;
                likeIndicator.style.opacity = 0;
            }
        };

        const onEnd = () => {
            if (!isDragging) return;
            isDragging = false;
            
            const threshold = 100;
            card.style.transition = 'transform 0.3s ease-out, opacity 0.3s ease-out';
            
            if (currentX > threshold) {
                // Swipe Right
                card.style.transform = `translate(1000px, ${currentY}px) rotate(30deg)`;
                card.style.opacity = 0;
                applyImpact(data.swipeRight);
                nextCard(card);
            } else if (currentX < -threshold) {
                // Swipe Left
                card.style.transform = `translate(-1000px, ${currentY}px) rotate(-30deg)`;
                card.style.opacity = 0;
                applyImpact(data.swipeLeft);
                nextCard(card);
            } else {
                // Return to center
                card.style.transform = `translate(0px, 0px) rotate(0deg)`;
                bgOverlay.style.backgroundColor = `transparent`;
                likeIndicator.style.opacity = 0;
                nopeIndicator.style.opacity = 0;
            }
        };

        const nextCard = (cardToRemove) => {
            bgOverlay.style.backgroundColor = `transparent`;
            setTimeout(() => {
                cardToRemove.remove();
                currentCardIndex++;
                renderTopCard();
            }, 300);
        };

        // Events
        card.addEventListener('mousedown', onStart);
        card.addEventListener('touchstart', onStart);
        
        window.addEventListener('mousemove', onMove);
        window.addEventListener('touchmove', onMove);

        window.addEventListener('mouseup', onEnd);
        window.addEventListener('touchend', onEnd);
    }
});
