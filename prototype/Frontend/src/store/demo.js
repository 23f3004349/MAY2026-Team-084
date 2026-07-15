import { reactive } from 'vue'
import { authStore } from './auth'

// current user helpers (fall back to a friendly demo identity)
export function me() {
  return {
    name: authStore.user?.name || 'You',
    flat: authStore.user?.flat_number || 'A-101',
    initials: (authStore.user?.name || 'You').split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase(),
  }
}

const now = Date.now()
const ago = (h) => `${h}h ago`

export const demo = reactive({
  // ── COMMUNITY WALL ──────────────────────────────────────────
  wallPosts: [
    { id: 1, author: 'Meera Iyer', flat: 'B-204', initials: 'MI', category: 'Help',
      time: ago(1), text: 'Water supply will be off in B-block 10am–1pm today for tank cleaning. Please store water! 🙏',
      reactions: { like: 8, love: 0, celebrate: 0, pray: 12 }, myReaction: null,
      comments: [{ author: 'Ravi K', flat: 'B-207', text: 'Thanks for the heads up!', time: ago(1) }] },
    { id: 2, author: 'Arjun Nair', flat: 'C-101', initials: 'AN', category: 'Recommend',
      time: ago(3), text: 'Found a fantastic electrician who fixed our whole DB board in 30 mins. DM me for the number — reasonable rates. ⚡',
      reactions: { like: 15, love: 4, celebrate: 0, pray: 0 }, myReaction: 'like',
      comments: [] },
    { id: 3, author: 'Priya Sharma', flat: 'A-101', initials: 'PS', category: 'Celebration',
      time: ago(6), text: 'Our society won the “Cleanest Community” award from the municipality this year! 🎉 Thank you to everyone who helped.',
      reactions: { like: 22, love: 18, celebrate: 31, pray: 0 }, myReaction: null,
      comments: [{ author: 'Meera Iyer', flat: 'B-204', text: 'So proud of us all! 👏', time: ago(5) },
                 { author: 'Sanjay G', flat: 'D-302', text: 'Well deserved 🙌', time: ago(4) }] },
    { id: 4, author: 'Sanjay Gupta', flat: 'D-302', initials: 'SG', category: 'Lost & Found',
      time: ago(9), text: 'Found a set of car keys near the C-block parking. Collect from the security desk. 🔑',
      reactions: { like: 6, love: 0, celebrate: 0, pray: 2 }, myReaction: null, comments: [] },
  ],
  addPost(text, category) {
    const u = me()
    this.wallPosts.unshift({
      id: now + Math.random(), author: u.name, flat: u.flat, initials: u.initials,
      category: category || 'Announcement', time: 'just now', text,
      reactions: { like: 0, love: 0, celebrate: 0, pray: 0 }, myReaction: null, comments: [],
    })
  },
  toggleReaction(postId, kind) {
    const p = this.wallPosts.find(x => x.id === postId); if (!p) return
    if (p.myReaction === kind) { p.reactions[kind]--; p.myReaction = null }
    else { if (p.myReaction) p.reactions[p.myReaction]--; p.reactions[kind]++; p.myReaction = kind }
  },
  addComment(postId, text) {
    const p = this.wallPosts.find(x => x.id === postId); if (!p) return
    const u = me(); p.comments.push({ author: u.name, flat: u.flat, text, time: 'just now' })
  },

  // ── EVENTS ──────────────────────────────────────────────────
  events: [
    { id: 1, title: 'Diwali Celebration & Potluck', emoji: '🪔', accent: '#F2A541',
      date: '2026-07-25', time: '6:00 PM', venue: 'Community Hall', goingCount: 18, imAttending: false,
      going: ['Priya', 'Meera', 'Arjun', 'Ravi'], desc: 'Lights, food, music and rangoli competition. Bring a dish to share!' },
    { id: 2, title: 'Society General Body Meeting', emoji: '🗣️', accent: '#1B2A4A',
      date: '2026-07-20', time: '11:00 AM', venue: 'Clubhouse', goingCount: 34, imAttending: true,
      going: ['You', 'Sanjay', 'Meera'], desc: 'Quarterly accounts, upcoming projects and the terrace-solar proposal.' },
    { id: 3, title: 'Kids Summer Sports Day', emoji: '⚽', accent: '#0E7C7B',
      date: '2026-07-28', time: '4:30 PM', venue: 'Play Area', goingCount: 12, imAttending: false,
      going: ['Arjun', 'Deepa'], desc: 'Races, football and prizes for all the little champions of the society.' },
  ],
  toggleRSVP(id) {
    const e = this.events.find(x => x.id === id); if (!e) return
    e.imAttending = !e.imAttending
    e.goingCount += e.imAttending ? 1 : -1
    if (e.imAttending && !e.going.includes('You')) e.going.unshift('You')
    else e.going = e.going.filter(n => n !== 'You')
    return e.imAttending
  },

  // ── AMENITIES ───────────────────────────────────────────────
  amenities: [
    { id: 1, name: 'Gymnasium', icon: 'fa-dumbbell', desc: 'Fully equipped · 8 people/slot',
      slots: [{ time: '6:00 AM', status: 'available' }, { time: '7:00 AM', status: 'mine' }, { time: '8:00 AM', status: 'booked' }, { time: '6:00 PM', status: 'available' }, { time: '7:00 PM', status: 'available' }] },
    { id: 2, name: 'Swimming Pool', icon: 'fa-person-swimming', desc: 'Lap + kids pool · lifeguard on duty',
      slots: [{ time: '6:00 AM', status: 'available' }, { time: '7:00 AM', status: 'booked' }, { time: '5:00 PM', status: 'available' }, { time: '6:00 PM', status: 'available' }] },
    { id: 3, name: 'Clubhouse', icon: 'fa-couch', desc: 'Lounge, TV & indoor games',
      slots: [{ time: '10:00 AM', status: 'available' }, { time: '2:00 PM', status: 'available' }, { time: '6:00 PM', status: 'booked' }] },
    { id: 4, name: 'Party Hall', icon: 'fa-champagne-glasses', desc: 'Up to 60 guests · A/C',
      slots: [{ time: 'Morning', status: 'available' }, { time: 'Evening', status: 'booked' }] },
    { id: 5, name: 'Tennis Court', icon: 'fa-table-tennis-paddle-ball', desc: 'Floodlit · racquets available',
      slots: [{ time: '6:00 AM', status: 'available' }, { time: '7:00 AM', status: 'available' }, { time: '7:00 PM', status: 'mine' }] },
    { id: 6, name: 'Co-work Lounge', icon: 'fa-laptop', desc: 'Wi-Fi · quiet zone · 6 desks',
      slots: [{ time: '9:00 AM', status: 'available' }, { time: '12:00 PM', status: 'available' }, { time: '3:00 PM', status: 'booked' }] },
  ],
  bookSlot(amenityId, time) {
    const a = this.amenities.find(x => x.id === amenityId); if (!a) return false
    const slot = a.slots.find(s => s.time === time); if (!slot || slot.status === 'booked') return false
    slot.status = slot.status === 'mine' ? 'available' : 'mine'
    return slot.status === 'mine'
  },

  // ── LEADERBOARD (Rewards) ───────────────────────────────────
  leaderboard: {
    blocks: [
      { block: 'A-Block', np: 4820, rank: 1 },
      { block: 'B-Block', np: 4780, rank: 2 },
      { block: 'C-Block', np: 3960, rank: 3 },
      { block: 'D-Block', np: 3510, rank: 4 },
    ],
    flats: [
      { flat: 'B-204', name: 'Meera Iyer', np: 640, rank: 1 },
      { flat: 'C-101', name: 'Arjun Nair', np: 590, rank: 2 },
      { flat: 'A-101', name: 'You', np: 285, rank: 7, you: true },
      { flat: 'D-302', name: 'Sanjay Gupta', np: 240, rank: 9 },
    ],
  },
  neighbourOfMonth: { name: 'Meera Iyer', flat: 'B-204', np: 640, initials: 'MI',
    reason: 'Most active on the wall, never missed a payment, and organised the tree-planting drive.' },

  // ── MARKETPLACE ─────────────────────────────────────────────
  marketplace: [
    { id: 1, title: 'Kids’ bicycle (age 6–9)', price: 1500, category: 'For Sale', emoji: '🚲', condition: 'Barely used', seller: 'Arjun Nair', flat: 'C-101', time: ago(2) },
    { id: 2, title: 'Study table + chair', price: 3200, category: 'For Sale', emoji: '🪑', condition: 'Good', seller: 'Priya Sharma', flat: 'A-101', time: ago(8) },
    { id: 3, title: 'Free: moving boxes (x12)', price: 0, category: 'Giveaway', emoji: '📦', condition: 'Reusable', seller: 'Sanjay Gupta', flat: 'D-302', time: ago(20) },
    { id: 4, title: 'Home-baked cakes on order', price: 450, category: 'Service', emoji: '🎂', condition: 'Eggless available', seller: 'Deepa Rao', flat: 'B-110', time: ago(30) },
  ],
  addListing(title, price, category) {
    const u = me()
    this.marketplace.unshift({ id: now + Math.random(), title, price: Number(price) || 0, category: category || 'For Sale',
      emoji: '🏷️', condition: 'New listing', seller: u.name, flat: u.flat, time: 'just now' })
  },
})
