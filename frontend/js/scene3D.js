
    // 1. CONFIGURACIÓN BÁSICA DE THREE.JS
    const container = document.getElementById('canvas-container');
    const scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x030303, 0.035); // Niebla oscura para fundir el fondo hacia los bordes

    const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 100);
    camera.position.set(0, 0, 15);

    const renderer = new THREE.WebGLRenderer({ antialias: false, alpha: true, powerPreference: "high-performance" });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);

    // 2. ILUMINACIÓN ÉPICA (DARK + RIM LIGHT)
    // Luz ambiental extremadamente tenue
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.15);
    scene.add(ambientLight);

    // RIM LIGHT 1 (Izquierda - Plateado/Blanco frío) - Delinea el borde izquierdo
    const rimLightLeft = new THREE.PointLight(0xffffff, 6, 50);
    rimLightLeft.position.set(-6, 2, -4);
    scene.add(rimLightLeft);

    // RIM LIGHT 2 (Derecha - Dorado épico) - Delinea el borde derecho
    const rimLightRight = new THREE.PointLight(0xf5d061, 8, 50);
    rimLightRight.position.set(6, -1, -4);
    scene.add(rimLightRight);

    // 3. CARGA DEL MODELO 3D (GLB)
    const loader = new THREE.GLTFLoader();
    let trophyGroup = new THREE.Group();
    scene.add(trophyGroup);

    // Inclinación ligera hacia adelante majestuosa
    trophyGroup.rotation.x = 0.12;

    loader.load(
      'copa.glb', // <--- PLACEHOLDER DEL MODELO
      function (gltf) {
        const trophy = gltf.scene;

        // Centrado exacto matemático
        const box = new THREE.Box3().setFromObject(trophy);
        const center = box.getCenter(new THREE.Vector3());
        const size = box.getSize(new THREE.Vector3()).length();

        trophy.position.set(-center.x, -center.y, -center.z);

        // Escala responsiva basada en el tamaño real del modelo
        const scale = window.innerWidth < 900 ? 5.5 / size : 8.5 / size;
        trophyGroup.scale.setScalar(scale);

        // Modificamos el material para que sea un "espejo oscuro" que atrapa las luces laterales
        trophy.traverse((child) => {
          if (child.isMesh) {
            // Reemplazamos los materiales para forzar la silueta épica
            child.material = new THREE.MeshStandardMaterial({
              color: 0x050505,       // Casi negro absoluto
              metalness: 1.0,        // Metal puro
              roughness: 0.35,       // Ligeramente pulido para que la luz rebote en los bordes
            });
          }
        });

        trophyGroup.add(trophy);

        // Hide loader once 3D model is ready
        const loaderEl = document.getElementById('global-loader');
        if (loaderEl) {
            loaderEl.classList.add('fade-out');
            setTimeout(() => loaderEl.remove(), 800);
        }
      },
      undefined,
      function (error) {
        console.error('Error cargando el modelo 3D:', error);
        
        // Hide loader even on error so user isn't stuck
        const loaderEl = document.getElementById('global-loader');
        if (loaderEl) {
            loaderEl.classList.add('fade-out');
            setTimeout(() => loaderEl.remove(), 800);
        }
      }
    );

    // 4. SISTEMA DE PARTÍCULAS INTERACTIVAS (NIEBLA ORB)
    const particleCount = 180;
    const particlesGeometry = new THREE.BufferGeometry();
    const particlesPositions = new Float32Array(particleCount * 3);
    const particlesVelocities = [];

    for (let i = 0; i < particleCount * 3; i += 3) {
      // Esparcir partículas a lo ancho y profundo
      particlesPositions[i] = (Math.random() - 0.5) * 35; // x
      particlesPositions[i + 1] = (Math.random() - 0.5) * 20; // y
      particlesPositions[i + 2] = (Math.random() - 0.5) * 20 - 4; // z
      
      particlesVelocities.push({
        x: (Math.random() - 0.5) * 0.008,
        y: Math.random() * 0.015 + 0.005, // Flotan hacia arriba como niebla densa
        z: (Math.random() - 0.5) * 0.008
      });
    }

    particlesGeometry.setAttribute('position', new THREE.BufferAttribute(particlesPositions, 3));

    // Crear textura procedimental de "Niebla / Orbe"
    const canvasP = document.createElement('canvas');
    canvasP.width = 64; canvasP.height = 64;
    const ctxP = canvasP.getContext('2d');
    
    // Gradiente radial: Núcleo blanco -> Borde gris -> Transparente
    const gradient = ctxP.createRadialGradient(32, 32, 0, 32, 32, 32);
    gradient.addColorStop(0, 'rgba(255, 255, 255, 0.9)');
    gradient.addColorStop(0.15, 'rgba(150, 150, 150, 0.6)');
    gradient.addColorStop(0.7, 'rgba(50, 50, 50, 0.2)');
    gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');
    
    ctxP.fillStyle = gradient;
    ctxP.fillRect(0, 0, 64, 64);
    const particleTexture = new THREE.CanvasTexture(canvasP);

    const particlesMaterial = new THREE.PointsMaterial({
      size: 0.8,
      map: particleTexture,
      transparent: true,
      opacity: 0.6,
      blending: THREE.AdditiveBlending, // Mezcla aditiva para brillo etéreo
      depthWrite: false
    });

    const particleSystem = new THREE.Points(particlesGeometry, particlesMaterial);
    scene.add(particleSystem);

    // 5. INTERACCIONES DEL MOUSE Y PARALLAX
    const mouse = new THREE.Vector2(0, 0);
    const targetMouse = new THREE.Vector2(0, 0);

    window.addEventListener('mousemove', (event) => {
      targetMouse.x = (event.clientX / window.innerWidth) * 2 - 1;
      targetMouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
    });

    // Raycaster para detectar la posición del mouse en el plano 3D (para repeler partículas)
    const raycaster = new THREE.Raycaster();
    const planeZ = new THREE.Plane(new THREE.Vector3(0, 0, 1), 0);
    const mousePos3D = new THREE.Vector3();

    // 6. BUCLE DE ANIMACIÓN
    const clock = new THREE.Clock();

    function animate() {
      requestAnimationFrame(animate);

      // PAUSE RENDER LOOP IF NOT ON HOMEPAGE TO SAVE CPU/GPU
      if (window.appState && window.appState !== 'homepage' && window.appState !== 'transition') {
          return;
      }

      const elapsedTime = clock.getElapsedTime();

      // Suavizado del movimiento del mouse (Lerp)
      mouse.x += (targetMouse.x - mouse.x) * 0.05;
      mouse.y += (targetMouse.y - mouse.y) * 0.05;

      // Parallax sutil de la cámara
      camera.position.x = mouse.x * 1.5;
      camera.position.y = mouse.y * 1.5;
      camera.lookAt(0, 0, 0);

      // Rotación constante del trofeo
      trophyGroup.rotation.y = elapsedTime * 0.15;

      // Proyectar mouse al plano Z=0 para interactuar con partículas
      raycaster.setFromCamera(mouse, camera);
      raycaster.ray.intersectPlane(planeZ, mousePos3D);

      // Animar partículas
      const positions = particleSystem.geometry.attributes.position.array;
      
      for (let i = 0; i < particleCount; i++) {
        let i3 = i * 3;
        
        // Movimiento base flotante
        positions[i3] += particlesVelocities[i].x;
        positions[i3 + 1] += particlesVelocities[i].y;
        positions[i3 + 2] += particlesVelocities[i].z;

        // Resetear partícula si sube demasiado
        if (positions[i3 + 1] > 12) {
          positions[i3 + 1] = -12;
          positions[i3] = (Math.random() - 0.5) * 35; // Nueva posición X aleatoria
        }

        // FÍSICA: Repulsión con el cursor del mouse
        const dx = positions[i3] - mousePos3D.x;
        const dy = positions[i3 + 1] - mousePos3D.y;
        const dist = Math.sqrt(dx*dx + dy*dy);

        if (dist < 3.5) { // Si está a menos de 3.5 unidades del mouse
          const force = (3.5 - dist) * 0.03;
          positions[i3] += (dx / dist) * force;     // Empuja en X
          positions[i3 + 1] += (dy / dist) * force; // Empuja en Y
        }
      }
      
      particleSystem.geometry.attributes.position.needsUpdate = true;
      renderer.render(scene, camera);
    }

    animate();

    // 7. RESPONSIVE
    window.addEventListener('resize', () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

      if (trophyGroup.children.length > 0) {
        const box = new THREE.Box3().setFromObject(trophyGroup.children[0]);
        const size = box.getSize(new THREE.Vector3()).length();
        const scale = window.innerWidth < 900 ? 5.5 / size : 8.5 / size;
        trophyGroup.scale.setScalar(scale);
      }
    });

    // =========================================================================
    // 8. NUEVA CAPA DE EFECTOS VISUALES 3D Y 2D (ANFITRIONES)
    // =========================================================================
    (function() {
      // --- A. LUCES 3D (ROJO Y VERDE - Canadá y México) ---
      const redLight = new THREE.PointLight(0xff0000, 0, 50);
      const greenLight = new THREE.PointLight(0x00ff66, 0, 50);
      scene.add(redLight);
      scene.add(greenLight);

      let active3DEffect = null;
      let effectStartTime = 0;

      // --- B. CANVAS 2D (ESTRELLAS AZULES - USA) ---
      const fxCanvas = document.createElement('canvas');
      fxCanvas.id = 'fx-canvas';
      fxCanvas.style.position = 'absolute';
      fxCanvas.style.top = '0';
      fxCanvas.style.left = '0';
      fxCanvas.style.width = '100vw';
      fxCanvas.style.height = '100vh';
      fxCanvas.style.zIndex = '0'; // Detrás de la copa 3D y su niebla
      fxCanvas.style.pointerEvents = 'none'; // No interfiere con la interacción
      document.body.insertBefore(fxCanvas, document.getElementById('canvas-container'));

      const ctx = fxCanvas.getContext('2d');
      let width, height;

      function resize() {
        width = window.innerWidth;
        height = window.innerHeight;
        fxCanvas.width = width;
        fxCanvas.height = height;
      }
      window.addEventListener('resize', resize);
      resize();

      let blueStars = [];

      // --- LÓGICA 3D ---
      function trigger3DEffect(variant) {
        active3DEffect = variant;
        effectStartTime = performance.now();
        
        if (variant === 1) { // Barrido cruzado
          redLight.position.set(-15, 2, 3);
          greenLight.position.set(15, -2, 3);
        } else if (variant === 2) { // Destello sup/inf
          redLight.position.set(0, -10, 4);
          greenLight.position.set(0, 10, 4);
        } else { // Pulsación misterio
          redLight.position.set(-5, 0, -10);
          greenLight.position.set(5, 0, -10);
        }
      }

      function update3DLights(time) {
        if (!active3DEffect) return;
        const elapsed = (time - effectStartTime) / 1000; // segundos
        const duration = 4; // Duración base de los efectos 3D

        if (elapsed > duration) {
          redLight.intensity = 0;
          greenLight.intensity = 0;
          active3DEffect = null;
          return;
        }

        // Fade in/out suave
        let fade = 1;
        if (elapsed < 1) fade = elapsed;
        else if (elapsed > duration - 1) fade = duration - elapsed;

        const maxInt = 15; // Intensidad máxima ajustada para no quemar el modelo

        if (active3DEffect === 1) { // Barrido cruzado
          redLight.position.x = -15 + (elapsed * 7.5);
          greenLight.position.x = 15 - (elapsed * 7.5);
          redLight.intensity = maxInt * fade;
          greenLight.intensity = maxInt * fade;
        } else if (active3DEffect === 2) { // Destello (secuencial)
          if (elapsed < 2) {
            redLight.intensity = maxInt * Math.sin((elapsed/2) * Math.PI);
            greenLight.intensity = 0;
          } else {
            redLight.intensity = 0;
            greenLight.intensity = maxInt * Math.sin(((elapsed-2)/2) * Math.PI);
          }
        } else if (active3DEffect === 3) { // Pulsación de atrás hacia adelante
          redLight.position.z = -10 + (elapsed * 4);
          greenLight.position.z = -10 + (elapsed * 4);
          redLight.intensity = (maxInt - 5) * fade * (0.6 + 0.4 * Math.sin(elapsed * 6));
          greenLight.intensity = (maxInt - 5) * fade * (0.6 + 0.4 * Math.sin(elapsed * 6 + Math.PI));
        }
      }

      // --- LÓGICA 2D (AZUL) ---
      class BlueStar {
        constructor(variant) {
          this.variant = variant;
          this.life = 0;
          if (variant === 1) { // Constelación estática
            this.x = width * 0.1 + Math.random() * width * 0.8;
            this.y = height * 0.1 + Math.random() * height * 0.8;
            this.maxLife = 80 + Math.random() * 40;
            this.size = Math.random() * 2 + 1.5;
          } else if (variant === 2) { // Fugaz masiva
            this.x = Math.random() > 0.5 ? -100 : width + 100;
            this.y = Math.random() * height * 0.6;
            this.vx = (this.x < 0 ? 1 : -1) * (18 + Math.random() * 12);
            this.vy = 8 + Math.random() * 6;
            this.maxLife = 60;
            this.size = 3.5 + Math.random() * 2;
          } else { // Destello central (Lens Flare)
            this.x = width / 2;
            this.y = height / 2;
            this.maxLife = 120;
            this.size = 0;
          }
        }
        update() {
          if (this.variant === 2) {
            this.x += this.vx;
            this.y += this.vy;
          }
          this.life++;
          return this.life >= this.maxLife;
        }
        draw(ctx) {
          let progress = this.life / this.maxLife;
          let alpha = Math.sin(progress * Math.PI);
          
          if (this.variant === 1) { // Constelación
            alpha *= (0.3 + 0.7 * Math.sin(this.life * 0.4)); // Parpadeo agresivo
            this.drawGlow(ctx, this.x, this.y, this.size, alpha, 25);
          } else if (this.variant === 2) { // Fugaz
            ctx.beginPath();
            ctx.moveTo(this.x, this.y);
            ctx.lineTo(this.x - this.vx * 4, this.y - this.vy * 4);
            ctx.strokeStyle = `rgba(150, 220, 255, ${alpha})`;
            ctx.lineWidth = this.size;
            ctx.shadowBlur = 25;
            ctx.shadowColor = '#0088ff';
            ctx.stroke();
            ctx.shadowBlur = 0;
          } else if (this.variant === 3) { // Lens Flare
            // Expansión rápida, desvanecimiento lento
            const s = progress < 0.15 ? progress * 600 : (1 - progress) * 150;
            this.drawGlow(ctx, this.x, this.y, s * 0.3, alpha * 0.9, s);
            
            // Rayo horizontal
            ctx.fillStyle = `rgba(150, 220, 255, ${alpha * 0.6})`;
            ctx.shadowBlur = 10;
            ctx.shadowColor = '#00aaff';
            ctx.fillRect(this.x - s*1.5, this.y - 1.5, s*3, 3);
            ctx.shadowBlur = 0;
          }
        }
        drawGlow(ctx, x, y, size, alpha, blur) {
          // OPTIMIZACIÓN: Se usa createRadialGradient en lugar de shadowBlur, que causa caída masiva de FPS en radios grandes.
          if (blur > 0) {
            const radius = Math.max(0.1, size + blur);
            const grad = ctx.createRadialGradient(x, y, Math.max(0, size * 0.2), x, y, radius);
            grad.addColorStop(0, `rgba(255, 255, 255, ${alpha})`);
            grad.addColorStop(0.35, `rgba(0, 150, 255, ${alpha * 0.7})`);
            grad.addColorStop(1, `rgba(0, 150, 255, 0)`);
            
            ctx.beginPath();
            ctx.arc(x, y, radius, 0, Math.PI * 2);
            ctx.fillStyle = grad;
            ctx.fill();
          } else {
            ctx.beginPath();
            ctx.arc(x, y, Math.max(0, size), 0, Math.PI * 2);
            ctx.fillStyle = `rgba(255, 255, 255, ${alpha})`;
            ctx.fill();
          }
        }
      }

      function triggerBlue(variant) {
        if (variant === 1) {
          for(let i=0; i<6; i++) {
            setTimeout(() => blueStars.push(new BlueStar(1)), Math.random() * 800);
          }
        } else {
          blueStars.push(new BlueStar(variant));
        }
      }

      // --- BUCLE DE ANIMACIÓN SECUNDARIO ---
      let fxNeedsClear = false;

      function fxLoop(time) {
        // 1. Actualizar luces 3D
        update3DLights(time);

        // 2. Actualizar Canvas 2D solo si hay elementos (ahorra 90% de GPU)
        if (blueStars.length > 0) {
          ctx.clearRect(0, 0, width, height);
          ctx.globalCompositeOperation = 'screen';
          
          for (let i = blueStars.length - 1; i >= 0; i--) {
            let dead = blueStars[i].update();
            blueStars[i].draw(ctx);
            if (dead) blueStars.splice(i, 1);
          }
          fxNeedsClear = true;
        } else if (fxNeedsClear) {
          ctx.clearRect(0, 0, width, height);
          fxNeedsClear = false;
        }
        
        requestAnimationFrame(fxLoop);
      }
      requestAnimationFrame(fxLoop);

      // --- PROGRAMADOR PRINCIPAL ---
      function scheduleNext() {
        const delay = 8000 + Math.random() * 7000; // 8 a 15 segundos
        setTimeout(() => {
          // Decidir si es luz 3D (Rojo/Verde) o Canvas 2D (Azul)
          const is3D = Math.random() > 0.5;
          const variant = Math.floor(Math.random() * 3) + 1;
          
          if (is3D) trigger3DEffect(variant);
          else triggerBlue(variant);
          
          scheduleNext();
        }, delay);
      }
      
      // Lanzar primer efecto rápido (A los 2.5 segs, una luz 3D para asombrar)
      setTimeout(() => {
        trigger3DEffect(1);
        scheduleNext();
      }, 2500);
    })();
