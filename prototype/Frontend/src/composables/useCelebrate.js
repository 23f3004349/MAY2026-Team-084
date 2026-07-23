import { reactive } from 'vue'
import { engagement } from '../store/engagement'

// Shared, app-wide celebration + toast state. Rendered by <CelebrationHost/>.
export const celebrationState = reactive({
  toasts: [],
  confettiTick: 0,
})

let seq = 0

// Transient toast. kind: 'success' | 'info' | 'error' | 'reward'
export function toast(message, kind = 'info', opts = {}) {
  const id = ++seq
  celebrationState.toasts.push({ id, message, kind, icon: opts.icon || null, points: opts.points || null, title: opts.title || null })
  const ttl = kind === 'reward' ? 4200 : 3200
  setTimeout(() => {
    const i = celebrationState.toasts.findIndex(t => t.id === id)
    if (i !== -1) celebrationState.toasts.splice(i, 1)
  }, ttl)
  return id
}

// Big moment: confetti burst + a reward toast card.
export function celebrate(payload = {}) {
  celebrationState.confettiTick++
  toast(payload.subtitle || '', 'reward', {
    title: payload.title || 'Nice!',
    icon: payload.icon || 'fa-trophy',
    points: payload.points || null,
  })
}

// One-liner used by every feature: award NP + auto-celebrate on level-up.
export function reward(np, reason) {
  const res = engagement.award(np, reason)
  if (res.leveledUp) {
    celebrate({ title: 'Level up!', subtitle: `You’re now a ${res.level.name}`, icon: res.level.icon, points: np })
  } else {
    toast(reason, 'success', { icon: 'fa-star', points: np })
  }
  return res
}

export function useCelebrate() {
  return { celebrate, toast, reward }
}
