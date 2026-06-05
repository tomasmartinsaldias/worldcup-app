
    window.window.appState = 'homepage'; // 'homepage', 'transition', 'spectator', 'quiz'

    function startExperience() {
      if (window.appState !== 'homepage') return;
      window.appState = 'transition';

      // Ocultar UI inicial
      document.querySelector('.hero-ui').classList.add('fade-out');
      document.querySelector('.scroll-indicator').classList.add('fade-out');
      
      // Mostrar Tarjetas
      setTimeout(() => {
        document.getElementById('spectator-selection').classList.add('visible');
        window.appState = 'spectator';
      }, 500);
    }

    function returnToHomepage() {
      if (window.appState === 'homepage') return;
      
      window.appState = 'transition';

      document.getElementById('spectator-selection').classList.remove('visible');
      
      const rec = document.getElementById('recommendations-overlay');
      if (rec) rec.classList.remove('visible');
      
      const survey = document.getElementById('antigravity-survey');
      if (survey) {
        survey.classList.remove('visible');
        setTimeout(() => survey.classList.add('hidden'), 500);
      }
      
      // Obsolete overlays (already removed from HTML)

      const futDraft = document.getElementById('draft-template');
      if (futDraft) {
        futDraft.classList.remove('visible');
        futDraft.classList.add('hidden');
      }

      const draft = document.getElementById('draft-overlay');
      if (draft) {
        draft.classList.remove('visible');
        draft.classList.add('hidden');
      }

      setTimeout(() => {
        document.querySelector('.hero-ui').classList.remove('fade-out');
        document.querySelector('.scroll-indicator').classList.remove('fade-out');
        window.appState = 'homepage';
      }, 500);
    }

    // Event listener para el scroll (rueda del mouse o trackpad)
    window.addEventListener('wheel', (event) => {
      if (window.window.appState === 'homepage' && event.deltaY > 10) {
        startExperience();
      } else if (window.window.appState === 'spectator' && event.deltaY < -10) {
        returnToHomepage();
      }
    });

    