import { reactive, computed } from 'vue'

// ── Levels (NP thresholds → identity) ─────────────────────────
export const LEVELS = [
  { name: 'Newcomer',        min: 0,    icon: 'fa-seedling' },
  { name: 'Neighbour',       min: 100,  icon: 'fa-user-group' },
  { name: 'Good Neighbour',  min: 300,  icon: 'fa-hand-holding-heart' },
  { name: 'Community Star',  min: 700,  icon: 'fa-star' },
  { name: 'Society Legend',  min: 1500, icon: 'fa-crown' },
]

// ── Badge catalogue (earned flag lives in state) ──────────────
const BADGE_CATALOG = [
  { id: 'first_post',  name: 'First Post',          icon: 'fa-pen-nib',       desc: 'Shared your first post on the wall' },
  { id: 'voter',       name: 'Voice of the Society', icon: 'fa-check-to-slot', desc: 'Cast a vote in a poll' },
  { id: 'rsvp',        name: 'Party Starter',        icon: 'fa-champagne-glasses', desc: 'RSVP’d to a society event' },
  { id: 'booker',      name: 'Regular',              icon: 'fa-dumbbell',      desc: 'Booked a society amenity' },
  { id: 'streak7',     name: 'Week Warrior',         icon: 'fa-fire',          desc: 'Kept a 7-day check-in streak' },
  { id: 'peacemaker',  name: 'Peacemaker',           icon: 'fa-handshake',     desc: 'Used the Conflict Resolver' },
  { id: 'social',      name: 'Social Butterfly',     icon: 'fa-heart',         desc: 'Reacted to 10 posts' },
  { id: 'full_house',  name: 'Full House',           icon: 'fa-id-card',       desc: 'Completed your profile' },
  { id: 'legend',      name: 'Society Legend',       icon: 'fa-crown',         desc: 'Reached the top level' },
]

const KEY = 'se_engagement_v1'
const todayStr = () => new Date().toISOString().slice(0, 10)
const yesterdayStr = () => new Date(Date.now() - 864e5).toISOString().slice(0, 10)

// ── Seed (used only on first ever load) ───────────────────────
function seed() {
  return {
    points: 285,               // 15 NP from "Good Neighbour" — a single vote levels up (demo)
    checkInStreak: 11,
    paymentStreak: 5,
    lastCheckIn: yesterdayStr(),
    reactionCount: 6,
    earned: ['voter', 'streak7', 'social'],
    notifications: [
      { id: 1, icon: 'fa-comment', text: 'Ravi replied to your post “Anyone up for morning badminton?”', time: '2h ago', read: false },
      { id: 2, icon: 'fa-poll',    text: 'Poll “Solar panels on the terrace” closes tonight — add your vote', time: '4h ago', read: false },
      { id: 3, icon: 'fa-calendar-check', text: '18 neighbours are going to the Diwali celebration', time: '1d ago', read: true },
    ],
  }
}

function load() {
  try {
    const raw = localStorage.getItem(KEY)
    if (raw) return { ...seed(), ...JSON.parse(raw) }
  } catch { /* ignore */ }
  return seed()
}

const s = load()

export const engagement = reactive({
  points: s.points,
  checkInStreak: s.checkInStreak,
  paymentStreak: s.paymentStreak,
  lastCheckIn: s.lastCheckIn,
  reactionCount: s.reactionCount,
  earned: s.earned,
  notifications: s.notifications,

  // ── derived ──
  get level() {
    let lvl = LEVELS[0]
    for (const l of LEVELS) if (this.points >= l.min) lvl = l
    return lvl
  },
  get nextLevel() {
    return LEVELS.find(l => l.min > this.points) || null
  },
  get levelProgress() {
    const cur = this.level, nxt = this.nextLevel
    if (!nxt) return 100
    return Math.round(((this.points - cur.min) / (nxt.min - cur.min)) * 100)
  },
  get npToNext() {
    return this.nextLevel ? this.nextLevel.min - this.points : 0
  },
  get badges() {
    return BADGE_CATALOG.map(b => ({ ...b, earned: this.earned.includes(b.id) }))
  },
  get unreadCount() {
    return this.notifications.filter(n => !n.read).length
  },
  get hasCheckedInToday() {
    return this.lastCheckIn === todayStr()
  },

  // ── mutations ──  (return info so callers can celebrate)
  award(np, reason) {
    const before = this.level.name
    this.points += np
    const leveledUp = this.level.name !== before
    if (leveledUp) {
      this.notify({ icon: this.level.icon, text: `Level up! You’re now a ${this.level.name} 🎉` })
      if (this.level.name === 'Society Legend') this.unlock('legend')
    }
    this.save()
    return { gained: np, reason, leveledUp, level: this.level }
  },
  checkIn() {
    if (this.hasCheckedInToday) return { already: true, streak: this.checkInStreak }
    this.checkInStreak = this.lastCheckIn === yesterdayStr() ? this.checkInStreak + 1 : 1
    this.lastCheckIn = todayStr()
    if (this.checkInStreak >= 7) this.unlock('streak7')
    const bonus = 5 + Math.min(this.checkInStreak, 10)   // streak-escalating reward
    const res = this.award(bonus, 'Daily check-in')
    return { already: false, streak: this.checkInStreak, gained: bonus, ...res }
  },
  unlock(id) {
    if (this.earned.includes(id)) return false
    this.earned.push(id)
    const b = BADGE_CATALOG.find(x => x.id === id)
    if (b) this.notify({ icon: b.icon, text: `Badge unlocked: ${b.name}` })
    this.save()
    return b || true
  },
  react() {
    this.reactionCount += 1
    if (this.reactionCount >= 10) this.unlock('social')
    this.save()
  },
  notify(n) {
    this.notifications.unshift({
      id: Date.now() + Math.random(),
      icon: n.icon || 'fa-bell',
      text: n.text,
      time: 'just now',
      read: false,
    })
    if (this.notifications.length > 30) this.notifications.pop()
    this.save()
  },
  markAllRead() {
    this.notifications.forEach(n => (n.read = true))
    this.save()
  },
  save() {
    try {
      localStorage.setItem(KEY, JSON.stringify({
        points: this.points, checkInStreak: this.checkInStreak, paymentStreak: this.paymentStreak,
        lastCheckIn: this.lastCheckIn, reactionCount: this.reactionCount,
        earned: this.earned, notifications: this.notifications,
      }))
    } catch { /* ignore */ }
  },
})
