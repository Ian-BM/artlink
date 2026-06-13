import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

console.debug('[VirtualGallery] Three.js loaded successfully', { revision: THREE.REVISION });

/**
 * Virtual gallery runtime — plain ES modules + CDN (no bundler).
 */
export class VirtualGallery {
    constructor({
        canvas,
        artworks,
        onArtworkSelect,
        onProgress,
        onReady,
        onError,
    }) {
        this.canvas = canvas;
        this.artworks = artworks.slice(0, 13);
        this.onArtworkSelect = onArtworkSelect;
        this.onProgress = onProgress;
        this.onReady = onReady;
        this.onError = onError;

        console.debug('[VirtualGallery] Gallery initialized');
        console.debug('[VirtualGallery] Artwork count:', this.artworks.length);

        if (!this.artworks.length) {
            const error = new Error('No artworks available in this exhibition.');
            if (this.onError) {
                this.onError(error);
            }
            throw error;
        }

        this.movement = { forward: false, backward: false, left: false, right: false };
        this.velocity = new THREE.Vector3();
        this.direction = new THREE.Vector3();
        this.clock = new THREE.Clock();
        this.isMobile = window.matchMedia('(max-width: 780px)').matches;
        this.highlightedMesh = null;
        this.clickableArtworks = [];
        this.textureQueue = [...this.artworks];
        this.loadedCount = 0;
        this.isActive = true;
        this.failedTextures = 0;

        try {
            this._report('Loading Exhibition...');
            this._initScene();
            this._initRoom();
            this._initLights();
            this._initControls();
            this._initInput();
            this._initMobileJoystick();
            this._bindEvents();
            this._report('Loading Artworks...');
            this._scheduleTextureLoads();
            this._animate();
            this._markDirty();
        } catch (error) {
            console.error('[VirtualGallery] Initialization failed', error);
            if (this.onError) {
                this.onError(error);
            }
            throw error;
        }
    }

    _report(message) {
        if (this.onProgress) {
            this.onProgress({
                message,
                loaded: this.loadedCount,
                total: this.artworks.length,
                failedTextures: this.failedTextures,
            });
        }
    }

    _markDirty() {
        this.needsRender = true;
    }

    _initScene() {
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x1a1a1a);
        this.scene.fog = new THREE.Fog(0x1a1a1a, 14, 38);
        console.debug('[VirtualGallery] Scene created');

        this.camera = new THREE.PerspectiveCamera(58, 1, 0.1, 100);
        this.camera.position.set(0, 1.65, 7.5);
        console.debug('[VirtualGallery] Camera created');

        this.renderer = new THREE.WebGLRenderer({
            canvas: this.canvas,
            antialias: !this.isMobile,
            powerPreference: 'high-performance',
        });
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, this.isMobile ? 1.4 : 1.8));
        this.renderer.outputColorSpace = THREE.SRGBColorSpace;
        console.debug('[VirtualGallery] Renderer created');

        this.room = new THREE.Group();
        this.scene.add(this.room);
    }

    _initRoom() {
        const floorMaterial = new THREE.MeshStandardMaterial({ color: 0xd8d2c8, roughness: 0.78, metalness: 0.05 });
        const wallMaterial = new THREE.MeshStandardMaterial({ color: 0xf4f2f3, roughness: 0.9 });
        this.frameMaterial = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.45 });

        const floor = new THREE.Mesh(new THREE.PlaneGeometry(18, 18), floorMaterial);
        floor.rotation.x = -Math.PI / 2;
        this.room.add(floor);

        const ceiling = new THREE.Mesh(new THREE.PlaneGeometry(18, 18), wallMaterial);
        ceiling.rotation.x = Math.PI / 2;
        ceiling.position.y = 5;
        this.room.add(ceiling);

        this._makeWall(18, 5, 0, 2.5, -8.8, 0);
        this._makeWall(18, 5, -8.8, 2.5, 0, Math.PI / 2);
        this._makeWall(18, 5, 8.8, 2.5, 0, -Math.PI / 2);
    }

    _makeWall(width, height, x, y, z, rotY = 0) {
        const wallMaterial = new THREE.MeshStandardMaterial({ color: 0xf4f2f3, roughness: 0.9 });
        const wall = new THREE.Mesh(new THREE.PlaneGeometry(width, height), wallMaterial);
        wall.position.set(x, y, z);
        wall.rotation.y = rotY;
        this.room.add(wall);
    }

    _initLights() {
        this.scene.add(new THREE.AmbientLight(0xffffff, 0.45));
        this.scene.add(new THREE.HemisphereLight(0xffffff, 0x4f463d, 1.4));
        const keyLight = new THREE.DirectionalLight(0xffffff, 1.6);
        keyLight.position.set(0, 7, 4);
        this.scene.add(keyLight);
        const accentLight = new THREE.PointLight(0xefbf04, 1.4, 18);
        accentLight.position.set(0, 3.8, 2);
        this.scene.add(accentLight);
    }

    _initControls() {
        this.controls = new OrbitControls(this.camera, this.canvas);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.06;
        this.controls.target.set(0, 1.5, 0);
        this.controls.maxPolarAngle = Math.PI * 0.48;
        this.controls.minDistance = 2.5;
        this.controls.maxDistance = 14;
        this.controls.enablePan = true;
        this.controls.addEventListener('change', () => this._markDirty());
    }

    _initInput() {
        this._onKeyDown = (event) => this._setMovementKey(event.code, true);
        this._onKeyUp = (event) => this._setMovementKey(event.code, false);
        this._onInspect = (event) => {
            const clientX = event.clientX ?? event.changedTouches?.[0]?.clientX;
            const clientY = event.clientY ?? event.changedTouches?.[0]?.clientY;
            if (clientX == null || clientY == null) return;
            const hit = this._raycast(clientX, clientY);
            if (hit?.object?.userData?.artwork && this.onArtworkSelect) {
                this.onArtworkSelect(hit.object.userData.artwork);
            }
        };

        document.addEventListener('keydown', this._onKeyDown);
        document.addEventListener('keyup', this._onKeyUp);
        this.canvas.addEventListener('click', this._onInspect);
        this.canvas.addEventListener('touchend', this._onInspect, { passive: true });
    }

    _setMovementKey(code, active) {
        const map = {
            KeyW: 'forward',
            ArrowUp: 'forward',
            KeyS: 'backward',
            ArrowDown: 'backward',
            KeyA: 'left',
            ArrowLeft: 'left',
            KeyD: 'right',
            ArrowRight: 'right',
        };
        const key = map[code];
        if (key) {
            this.movement[key] = active;
            this._markDirty();
        }
    }

    _initMobileJoystick() {
        if (!this.isMobile) return;

        this.joystick = document.createElement('div');
        this.joystick.className = 'gallery-joystick';
        this.joystickKnob = document.createElement('div');
        this.joystickKnob.className = 'gallery-joystick-knob';
        this.joystick.appendChild(this.joystickKnob);
        this.canvas.parentElement.appendChild(this.joystick);

        const updateJoystick = (clientX, clientY) => {
            const rect = this.joystick.getBoundingClientRect();
            const centerX = rect.left + rect.width / 2;
            const centerY = rect.top + rect.height / 2;
            const dx = clientX - centerX;
            const dy = clientY - centerY;
            const distance = Math.min(Math.hypot(dx, dy), 36);
            const angle = Math.atan2(dy, dx);
            const offsetX = Math.cos(angle) * distance;
            const offsetY = Math.sin(angle) * distance;
            this.joystickKnob.style.transform = `translate(calc(-50% + ${offsetX}px), calc(-50% + ${offsetY}px))`;
            this.movement.forward = dy < -8;
            this.movement.backward = dy > 8;
            this.movement.left = dx < -8;
            this.movement.right = dx > 8;
            this._markDirty();
        };

        const resetJoystick = () => {
            this.movement = { forward: false, backward: false, left: false, right: false };
            this.joystickKnob.style.transform = 'translate(-50%, -50%)';
            this._markDirty();
        };

        this.joystick.addEventListener('touchstart', (event) => {
            updateJoystick(event.touches[0].clientX, event.touches[0].clientY);
        }, { passive: true });
        this.joystick.addEventListener('touchmove', (event) => {
            updateJoystick(event.touches[0].clientX, event.touches[0].clientY);
        }, { passive: true });
        this.joystick.addEventListener('touchend', resetJoystick, { passive: true });
    }

    _createFallbackTexture(label = 'ArtLink') {
        const fallback = document.createElement('canvas');
        fallback.width = 512;
        fallback.height = 640;
        const context = fallback.getContext('2d');
        context.fillStyle = '#f4f2f3';
        context.fillRect(0, 0, fallback.width, fallback.height);
        context.fillStyle = '#efbf04';
        context.fillRect(40, 40, fallback.width - 80, fallback.height - 80);
        context.fillStyle = '#111';
        context.font = 'bold 42px serif';
        context.textAlign = 'center';
        context.fillText(label, fallback.width / 2, fallback.height / 2);
        const texture = new THREE.CanvasTexture(fallback);
        texture.colorSpace = THREE.SRGBColorSpace;
        return texture;
    }

    _artworkPositions(index) {
        const backSlots = [-5.6, -2.8, 0, 2.8, 5.6];
        const sideSlots = [-5.2, -2.2, 1.2, 4.2];
        if (index < backSlots.length) {
            return { position: new THREE.Vector3(backSlots[index], 2.35, -8.72), rotation: new THREE.Euler(0, 0, 0) };
        }
        const sideIndex = index - backSlots.length;
        const leftSide = sideIndex % 2 === 0;
        const slot = sideSlots[Math.floor(sideIndex / 2) % sideSlots.length];
        return {
            position: new THREE.Vector3(leftSide ? -8.72 : 8.72, 2.35, slot),
            rotation: new THREE.Euler(0, leftSide ? Math.PI / 2 : -Math.PI / 2, 0),
        };
    }

    _installArtwork(artwork, index, texture) {
        const group = new THREE.Group();
        const placement = this._artworkPositions(index);
        group.position.copy(placement.position);
        group.rotation.copy(placement.rotation);

        const frame = new THREE.Mesh(new THREE.BoxGeometry(1.95, 2.45, 0.08), this.frameMaterial);
        frame.position.z = -0.04;
        group.add(frame);

        const material = new THREE.MeshStandardMaterial({ map: texture, roughness: 0.65 });
        const plane = new THREE.Mesh(new THREE.PlaneGeometry(1.72, 2.18), material);
        plane.position.z = 0.02;
        plane.userData.artwork = artwork;
        plane.userData.baseEmissive = new THREE.Color(0x000000);
        group.add(plane);
        this.clickableArtworks.push(plane);
        this.room.add(group);
        this._markDirty();
    }

    _scheduleTextureLoads() {
        const loader = new THREE.TextureLoader();
        loader.setCrossOrigin('anonymous');
        const fallback = this._createFallbackTexture();
        let activeLoads = 0;
        const maxConcurrent = this.isMobile ? 2 : 3;

        const maybeFinish = () => {
            if (this.loadedCount >= this.artworks.length) {
                console.debug('[VirtualGallery] Artworks loaded', {
                    loaded: this.loadedCount,
                    failedTextures: this.failedTextures,
                });
                this._report('Preparing Virtual Gallery...');
                window.setTimeout(() => {
                    if (this.onReady) {
                        this.onReady({
                            loaded: this.loadedCount,
                            total: this.artworks.length,
                            failedTextures: this.failedTextures,
                        });
                    }
                }, 350);
            }
        };

        const loadNext = () => {
            while (activeLoads < maxConcurrent && this.textureQueue.length) {
                const artwork = this.textureQueue.shift();
                const index = this.artworks.indexOf(artwork);
                activeLoads += 1;

                const finish = (texture, failed = false) => {
                    texture.colorSpace = THREE.SRGBColorSpace;
                    this._installArtwork(artwork, index, texture);
                    this.loadedCount += 1;
                    if (failed) {
                        this.failedTextures += 1;
                    }
                    this._report(`Loading Artworks... (${this.loadedCount}/${this.artworks.length})`);
                    activeLoads -= 1;
                    loadNext();
                    maybeFinish();
                };

                if (!artwork.imageUrl) {
                    finish(fallback, true);
                    continue;
                }

                loader.load(
                    artwork.imageUrl,
                    (texture) => finish(texture, false),
                    undefined,
                    () => finish(fallback, true),
                );
            }
        };

        loadNext();
    }

    _raycast(clientX, clientY) {
        const rect = this.renderer.domElement.getBoundingClientRect();
        const pointer = new THREE.Vector2(
            ((clientX - rect.left) / rect.width) * 2 - 1,
            -((clientY - rect.top) / rect.height) * 2 + 1,
        );
        const raycaster = new THREE.Raycaster();
        raycaster.setFromCamera(pointer, this.camera);
        return raycaster.intersectObjects(this.clickableArtworks, false)[0];
    }

    _updateMovement(delta) {
        this.velocity.x -= this.velocity.x * 8.0 * delta;
        this.velocity.z -= this.velocity.z * 8.0 * delta;
        this.direction.set(0, 0, 0);

        if (this.movement.forward) this.direction.z -= 1;
        if (this.movement.backward) this.direction.z += 1;
        if (this.movement.left) this.direction.x -= 1;
        if (this.movement.right) this.direction.x += 1;
        if (this.direction.lengthSq() === 0) {
            return;
        }
        this.direction.normalize();

        const speed = this.isMobile ? 16 : 22;
        const forward = new THREE.Vector3();
        this.camera.getWorldDirection(forward);
        forward.y = 0;
        forward.normalize();
        const right = new THREE.Vector3().crossVectors(forward, new THREE.Vector3(0, 1, 0)).normalize();

        if (this.movement.forward || this.movement.backward) {
            const sign = this.movement.forward ? 1 : -1;
            this.camera.position.addScaledVector(forward, sign * speed * delta);
            this.controls.target.addScaledVector(forward, sign * speed * delta);
        }
        if (this.movement.left || this.movement.right) {
            const sign = this.movement.right ? 1 : -1;
            this.camera.position.addScaledVector(right, sign * speed * delta);
            this.controls.target.addScaledVector(right, sign * speed * delta);
        }

        this.camera.position.y = 1.65;
        this.controls.target.y = 1.5;
        this.camera.position.x = THREE.MathUtils.clamp(this.camera.position.x, -7.5, 7.5);
        this.camera.position.z = THREE.MathUtils.clamp(this.camera.position.z, -7.5, 7.5);
        this._markDirty();
    }

    _updateHighlights() {
        let nearest = null;
        let nearestDistance = Infinity;
        const cameraPosition = this.camera.position;

        for (const mesh of this.clickableArtworks) {
            const distance = mesh.getWorldPosition(new THREE.Vector3()).distanceTo(cameraPosition);
            if (distance < nearestDistance) {
                nearestDistance = distance;
                nearest = mesh;
            }
        }

        if (this.highlightedMesh && this.highlightedMesh !== nearest) {
            this.highlightedMesh.material.emissive.copy(this.highlightedMesh.userData.baseEmissive);
            this.highlightedMesh.material.emissiveIntensity = 0;
            this.highlightedMesh.scale.set(1, 1, 1);
        }

        this.highlightedMesh = nearestDistance < 4.2 ? nearest : null;
        if (this.highlightedMesh) {
            this.highlightedMesh.material.emissive.setHex(0xefbf04);
            this.highlightedMesh.material.emissiveIntensity = 0.18;
            this.highlightedMesh.scale.set(1.03, 1.03, 1.03);
            this._markDirty();
        }
    }

    resetCamera() {
        this.camera.position.set(0, 1.65, 7.5);
        this.controls.target.set(0, 1.5, 0);
        this.controls.update();
        this._markDirty();
    }

    resize() {
        const width = this.canvas.clientWidth;
        const height = this.canvas.clientHeight;
        if (!width || !height) {
            return;
        }
        this.renderer.setSize(width, height, false);
        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        this._markDirty();
    }

    _bindEvents() {
        this._onResize = () => this.resize();
        window.addEventListener('resize', this._onResize);
        this.resize();
    }

    _animate() {
        if (!this.isActive) {
            return;
        }
        requestAnimationFrame(() => this._animate());
        const delta = Math.min(this.clock.getDelta(), 0.05);
        const moving = Object.values(this.movement).some(Boolean);
        if (moving) {
            this._updateMovement(delta);
        }
        this.controls.update();
        this._updateHighlights();
        this.renderer.render(this.scene, this.camera);
    }

    destroy() {
        this.isActive = false;
        document.removeEventListener('keydown', this._onKeyDown);
        document.removeEventListener('keyup', this._onKeyUp);
        window.removeEventListener('resize', this._onResize);
        this.controls.dispose();
        this.renderer.dispose();
    }
}
