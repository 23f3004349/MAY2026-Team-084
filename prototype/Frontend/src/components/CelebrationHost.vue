<template>
  <div class="celebration-host">
    <canvas ref="canvas" class="confetti-canvas"></canvas>
    <div class="toast-stack">
      <transition-group name="toast">
        <div v-for="t in state.toasts" :key="t.id" class="toast" :class="`toast--${t.kind}`">
          <div v-if="t.kind === 'reward'" class="toast-reward">
            <div class="toast-reward-icon"><i class="fas" :class="t.icon"></i></div>
            <div>
              <div class="toast-reward-title">{{ t.title }}</div>
              <div v-if="t.message" class="toast-reward-sub">{{ t.message }}</div>
            </div>
            <div v-if="t.points" class="toast-reward-np">+{{ t.points }} NP</div>
          </div>
          <template v-else>
            <i class="fas" :class="t.icon || kindIcon(t.kind)"></i>
            <span>{{ t.message }}</span>
          </template>
        </div>
      </transition-group>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { celebrationState } from '../composables/useCelebrate'

const state = celebrationState
const canvas = ref(null)

function kindIcon(kind) {
  return { success: 'fa-circle-check', error: 'fa-circle-exclamation', info: 'fa-circle-info' }[kind] || 'fa-circle-info'
}

const COLORS = ['#1B2A4A', '#0E7C7B', '#F2A541', '#DC2626', '#30497F', '#E8941F']

function burst() {
  if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return
  const cv = canvas.value; if (!cv) return
  const ctx = cv.getContext('2d')
  cv.width = window.innerWidth; cv.height = window.innerHeight
  const N = 140
  const parts = Array.from({ length: N }, () => ({
    x: cv.width / 2 + (Math.random() - 0.5) * 220,
    y: cv.height * 0.30 + (Math.random() - 0.5) * 60,
    vx: (Math.random() - 0.5) * 14,
    vy: Math.random() * -12 - 4,
    g: 0.32 + Math.random() * 0.2,
    size: 5 + Math.random() * 7,
    color: COLORS[(Math.random() * COLORS.length) | 0],
    rot: Math.random() * Math.PI, vr: (Math.random() - 0.5) * 0.3,
    life: 0,
  }))
  const start = performance.now()
  function frame(t) {
    const elapsed = t - start
    ctx.clearRect(0, 0, cv.width, cv.height)
    for (const p of parts) {
      p.vy += p.g; p.x += p.vx; p.y += p.vy; p.rot += p.vr; p.life = elapsed
      ctx.save()
      ctx.globalAlpha = Math.max(0, 1 - elapsed / 1800)
      ctx.translate(p.x, p.y); ctx.rotate(p.rot)
      ctx.fillStyle = p.color
      ctx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size * 0.6)
      ctx.restore()
    }
    if (elapsed < 1800) requestAnimationFrame(frame)
    else ctx.clearRect(0, 0, cv.width, cv.height)
  }
  requestAnimationFrame(frame)
}

watch(() => state.confettiTick, () => burst())
onMounted(() => { window.addEventListener('resize', () => { if (canvas.value) { canvas.value.width = innerWidth; canvas.value.height = innerHeight } }) })
</script>

<style scoped>
.confetti-canvas {
  position: fixed; inset: 0; pointer-events: none; z-index: 9999;
}
.toast-stack {
  position: fixed; bottom: 24px; right: 24px; z-index: 10000;
  display: flex; flex-direction: column; gap: 10px; align-items: flex-end;
}
.toast {
  display: flex; align-items: center; gap: 10px;
  background: var(--se-surface); color: var(--se-text);
  border: 1px solid var(--se-border); border-left: 4px solid var(--se-navy-600);
  border-radius: var(--se-r-md); box-shadow: var(--se-shadow-3);
  padding: 12px 16px; font-size: var(--se-fs-sm); max-width: 340px;
}
.toast--success { border-left-color: var(--se-teal-600); }
.toast--success i { color: var(--se-teal-600); }
.toast--error { border-left-color: var(--se-danger-600); }
.toast--error i { color: var(--se-danger-600); }
.toast--info i { color: var(--se-navy-600); }
.toast--reward {
  border-left-color: var(--se-marigold-400);
  background: linear-gradient(120deg, var(--se-marigold-50), var(--se-surface));
  padding: 14px 18px;
}
.toast-reward { display: flex; align-items: center; gap: 12px; }
.toast-reward-icon {
  width: 40px; height: 40px; border-radius: 50%; flex-shrink: 0;
  display: grid; place-items: center; color: var(--se-navy-800);
  background: var(--se-marigold-400); font-size: 1.1rem;
}
.toast-reward-title { font-weight: 700; color: var(--se-ink); font-family: var(--se-font-display); }
.toast-reward-sub { font-size: var(--se-fs-xs); color: var(--se-text-muted); }
.toast-reward-np {
  margin-left: 8px; font-weight: 700; color: var(--se-teal-700);
  background: var(--se-teal-50); padding: 4px 10px; border-radius: var(--se-r-pill); font-size: var(--se-fs-xs);
}
.toast-enter-from { opacity: 0; transform: translateY(12px); }
.toast-leave-to { opacity: 0; transform: translateX(20px); }
.toast-enter-active, .toast-leave-active { transition: all var(--se-t-slow) var(--se-ease-out); }
</style>
