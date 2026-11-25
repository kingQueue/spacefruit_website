const garden = document.querySelector('#spacefruit-garden');
const container = document.querySelector('#garden-scene');
const status = document.querySelector('#scene-status');
const reset = document.querySelector('#scene-reset');
const fullscreen = document.querySelector('#scene-fullscreen');
let initialized = false;
let loaded = false;
reset.disabled = true;
async function initializeGarden() {
  if (initialized) return;
  initialized = true;
  try {
    await import('./assets/vendor/model-viewer.min.js');
  } catch {
    status.textContent = 'The 3D view could not load. Please refresh to try again.';
    initialized = false;
  }
}
garden.addEventListener('load', () => {
  loaded = true;
  status.hidden = true;
  reset.disabled = false;
});
garden.addEventListener('error', () => {
  loaded = false;
  reset.disabled = true;
  status.hidden = false;
  status.textContent = 'The 3D view could not load. Please refresh to try again.';
});
reset.addEventListener('click', () => {
  if (!loaded) return;
  garden.cameraOrbit = '35deg 65deg 115%';
  garden.cameraTarget = '0m 0.6m 0m';
  garden.fieldOfView = '32deg';
  garden.jumpCameraToGoal();
});
if (!container.requestFullscreen) fullscreen.hidden = true;
fullscreen.addEventListener('click', async () => {
  try {
    if (document.fullscreenElement) await document.exitFullscreen();
    else await container.requestFullscreen();
  } catch {
    status.hidden = false;
    status.textContent = 'Fullscreen is unavailable in this browser. You can still rotate and zoom here.';
  }
});
document.addEventListener('fullscreenchange', () => {
  fullscreen.textContent = document.fullscreenElement === container ? 'Exit fullscreen' : 'Fullscreen';
});
if ('IntersectionObserver' in window) {
  const observer = new IntersectionObserver(entries => {
    if (entries.some(entry => entry.isIntersecting)) {
      initializeGarden();
      observer.disconnect();
    }
  }, {rootMargin:'400px'});
  observer.observe(container);
} else initializeGarden();
