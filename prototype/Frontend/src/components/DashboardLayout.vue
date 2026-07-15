<template>
  <div style="display:flex;">
    <!-- SIDEBAR (desktop) -->
    <aside class="sidebar">
      <div class="sidebar-brand">
        <h4><i class="fas fa-building me-2" style="color:#F2A541;"></i>SocietyEase</h4>
        <small>{{ authStore.user?.role }}</small>
      </div>
      <nav class="sidebar-nav">
        <template v-for="(sec, i) in sections" :key="i">
          <div v-if="sec.title" class="nav-section">{{ sec.title }}</div>
          <router-link v-for="item in sec.items" :key="item.to" class="nav-item" :to="item.to">
            <i class="fas" :class="item.icon"></i> {{ item.label }}
          </router-link>
        </template>
      </nav>
      <div class="sidebar-footer">
        <router-link to="/app/rewards" class="sidebar-you">
          <div class="se-avatar se-avatar--sm se-avatar--marigold">{{ initials }}</div>
          <div class="sidebar-you-meta">
            <div class="sidebar-you-name">{{ authStore.user?.name }}</div>
            <div class="sidebar-you-sub">{{ engagement.level.name }} · {{ engagement.points }} NP</div>
          </div>
        </router-link>
        <button @click="logout" class="sidebar-logout"><i class="fas fa-sign-out-alt me-2"></i>Logout</button>
      </div>
    </aside>

    <!-- MAIN CONTENT -->
    <div class="main-content">
      <div class="topbar">
        <h5 style="margin:0;font-weight:600;color:var(--se-ink);">{{ pageTitle }}</h5>
        <div class="topbar-right">
          <router-link to="/app/rewards" class="np-chip" title="Your Neighbour Points">
            <i class="fas" :class="engagement.level.icon"></i>
            <span class="np-value se-num">{{ engagement.points }}</span><span class="np-unit">NP</span>
            <span class="np-streak"><i class="fas fa-fire"></i>{{ engagement.checkInStreak }}</span>
          </router-link>
          <button class="icon-btn" @click="toggleTheme" :title="isDark ? 'Light mode' : 'Dark mode'">
            <i class="fas" :class="isDark ? 'fa-sun' : 'fa-moon'"></i>
          </button>
          <div class="bell-wrap">
            <button class="icon-btn" @click="bellOpen = !bellOpen" title="Notifications">
              <i class="fas fa-bell"></i>
              <span v-if="engagement.unreadCount" class="bell-badge">{{ engagement.unreadCount }}</span>
            </button>
            <div v-if="bellOpen" class="bell-backdrop" @click="bellOpen = false"></div>
            <div v-if="bellOpen" class="bell-dropdown">
              <div class="bell-head"><span>Notifications</span><button class="bell-clear" @click="engagement.markAllRead()">Mark all read</button></div>
              <div v-if="engagement.notifications.length === 0" class="bell-empty">You're all caught up 🎉</div>
              <div v-for="n in engagement.notifications.slice(0,8)" :key="n.id" class="bell-item" :class="{ unread: !n.read }">
                <div class="bell-item-icon"><i class="fas" :class="n.icon"></i></div>
                <div><div class="bell-item-text">{{ n.text }}</div><div class="bell-item-time">{{ n.time }}</div></div>
              </div>
            </div>
          </div>
          <button class="icon-btn icon-btn--logout" @click="logout" title="Logout"><i class="fas fa-sign-out-alt"></i></button>
          <div class="topbar-date"><i class="fas fa-calendar me-1"></i>{{ today }}</div>
        </div>
      </div>

      <div class="page-content">
        <router-view v-slot="{ Component }">
          <transition name="page" mode="out-in"><component :is="Component" /></transition>
        </router-view>
      </div>
    </div>

    <!-- BOTTOM NAV (mobile) -->
    <nav class="bottom-nav">
      <router-link v-for="item in bottomPrimary" :key="item.to" class="bottom-item" :to="item.to">
        <i class="fas" :class="item.icon"></i><span>{{ item.short || item.label }}</span>
      </router-link>
      <button class="bottom-item" :class="{ 'is-active': moreOpen }" @click="moreOpen = true">
        <i class="fas fa-ellipsis"></i><span>More</span>
      </button>
    </nav>

    <!-- MORE SHEET (mobile) -->
    <div v-if="moreOpen" class="more-backdrop" @click="moreOpen = false"></div>
    <div v-if="moreOpen" class="more-sheet">
      <div class="more-grab"></div>
      <div class="more-head">More</div>
      <div class="more-grid">
        <router-link v-for="item in moreItems" :key="item.to" class="more-tile" :to="item.to" @click="moreOpen = false">
          <i class="fas" :class="item.icon"></i><span>{{ item.label }}</span>
        </router-link>
      </div>
      <button class="more-logout" @click="logout"><i class="fas fa-sign-out-alt me-2"></i>Logout</button>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { authStore } from '../store/auth'
import { engagement } from '../store/engagement'
import { me } from '../store/demo'

const route = useRoute()
const router = useRouter()

const today = new Date().toLocaleDateString('en-IN', { weekday: 'long', month: 'long', day: 'numeric' })
const initials = computed(() => me().initials)
const bellOpen = ref(false)
const moreOpen = ref(false)
const isDark = ref(document.documentElement.getAttribute('data-theme') === 'dark')

function toggleTheme() {
  isDark.value = !isDark.value
  const theme = isDark.value ? 'dark' : 'light'
  document.documentElement.setAttribute('data-theme', theme)
  localStorage.setItem('se_theme', theme)
}

// nav catalogue
const I = {
  dashboard: { to: '/app/dashboard', icon: 'fa-chart-pie', label: 'Dashboard', short: 'Home' },
  home: { to: '/app/home', icon: 'fa-house', label: 'For You', short: 'Home' },
  worker: { to: '/app/worker', icon: 'fa-hard-hat', label: 'My Tasks', short: 'Tasks' },
  community: { to: '/app/community', icon: 'fa-comments', label: 'Community', short: 'Wall' },
  events: { to: '/app/events', icon: 'fa-calendar-day', label: 'Events', short: 'Events' },
  amenities: { to: '/app/amenities', icon: 'fa-dumbbell', label: 'Amenities', short: 'Book' },
  marketplace: { to: '/app/marketplace', icon: 'fa-store', label: 'Marketplace', short: 'Market' },
  rewards: { to: '/app/rewards', icon: 'fa-trophy', label: 'Rewards', short: 'Rewards' },
  payR: { to: '/app/invoices', icon: 'fa-wallet', label: 'Pay Dues', short: 'Pay' },
  payA: { to: '/app/invoices', icon: 'fa-file-invoice', label: 'Payments', short: 'Pay' },
  complaints: { to: '/app/complaints', icon: 'fa-screwdriver-wrench', label: 'Complaints', short: 'Fix' },
  notices: { to: '/app/notices', icon: 'fa-bullhorn', label: 'Notices', short: 'Notices' },
  polls: { to: '/app/polls', icon: 'fa-square-poll-vertical', label: 'Polls', short: 'Polls' },
  conflicts: { to: '/app/conflicts', icon: 'fa-handshake', label: 'Conflict Resolver', short: 'Resolve' },
  parking: { to: '/app/parking', icon: 'fa-square-parking', label: 'Parking', short: 'Parking' },
  members: { to: '/app/members', icon: 'fa-users', label: 'Members', short: 'Members' },
  expenses: { to: '/app/expenses', icon: 'fa-receipt', label: 'Expenses', short: 'Expenses' },
  maintenance: { to: '/app/maintenance', icon: 'fa-toolbox', label: 'Maintenance', short: 'Upkeep' },
  equipment: { to: '/app/equipment', icon: 'fa-gears', label: 'Equipment', short: 'Assets' },
  health: { to: '/app/health', icon: 'fa-heart-pulse', label: 'Health Score', short: 'Health' },
}

const sections = computed(() => {
  if (authStore.isAdmin) return [
    { items: [I.dashboard] },
    { title: 'Community', items: [I.community, I.events, I.amenities, I.marketplace, I.rewards] },
    { title: 'Operations', items: [I.payA, I.complaints, I.notices, I.polls, I.conflicts, I.parking] },
    { title: 'Manage', items: [I.members, I.expenses, I.maintenance, I.equipment, I.health] },
  ]
  if (authStore.user?.role === 'WORKER') return [
    { items: [I.worker] },
    { title: 'Community', items: [I.community, I.events, I.rewards] },
    { title: 'Work', items: [I.complaints, I.notices, I.parking] },
  ]
  return [
    { items: [I.home] },
    { title: 'Community', items: [I.community, I.events, I.amenities, I.marketplace, I.rewards] },
    { title: 'Services', items: [I.payR, I.complaints, I.notices, I.polls, I.conflicts, I.parking] },
  ]
})

const bottomTos = computed(() => {
  if (authStore.isAdmin) return ['/app/dashboard', '/app/community', '/app/invoices', '/app/complaints']
  if (authStore.user?.role === 'WORKER') return ['/app/worker', '/app/community', '/app/complaints']
  return ['/app/home', '/app/community', '/app/invoices', '/app/complaints']
})
const allItems = computed(() => sections.value.flatMap(s => s.items))
const bottomPrimary = computed(() => bottomTos.value.map(t => allItems.value.find(i => i.to === t)).filter(Boolean))
const moreItems = computed(() => allItems.value.filter(i => !bottomTos.value.includes(i.to)))

const titles = {
  '/app/dashboard': 'Dashboard', '/app/home': 'For You', '/app/worker': 'My Assigned Tasks',
  '/app/community': 'Community', '/app/events': 'Events', '/app/amenities': 'Book Amenities',
  '/app/marketplace': 'Marketplace', '/app/rewards': 'You', '/app/invoices': 'Pay & Dues',
  '/app/complaints': 'Complaints', '/app/notices': 'Notice Board', '/app/polls': 'Polls & Voting',
  '/app/conflicts': 'Conflict Resolver', '/app/parking': 'Visitor Parking', '/app/members': 'Member Management',
  '/app/expenses': 'Expense Tracker', '/app/maintenance': 'Maintenance Tasks',
  '/app/equipment': 'Smart Maintenance Predictor', '/app/health': 'Society Health Score',
}
const pageTitle = computed(() => titles[route.path] || 'SocietyEase')

function logout() { authStore.logout(); router.push('/login') }
</script>

<style scoped>
.nav-section {
  padding: 16px 20px 6px; font-size: 10px; font-weight: 700; letter-spacing: .09em;
  text-transform: uppercase; color: rgba(255,255,255,.4);
}
.sidebar-you { display: flex; align-items: center; gap: 10px; padding: 8px; border-radius: var(--se-r-md); text-decoration: none; margin-bottom: 8px; transition: background var(--se-t-fast); }
.sidebar-you:hover { background: rgba(255,255,255,.08); }
.sidebar-you-name { color: #fff; font-size: var(--se-fs-sm); font-weight: 600; }
.sidebar-you-sub { color: rgba(255,255,255,.6); font-size: var(--se-fs-2xs); }
.sidebar-logout { width: 100%; background: rgba(255,255,255,.1); color: #fff; border: none; padding: 9px 14px; border-radius: var(--se-r-md); font-size: var(--se-fs-xs); cursor: pointer; transition: background var(--se-t-fast); }
.sidebar-logout:hover { background: rgba(255,255,255,.18); }

.topbar-right { display: flex; align-items: center; gap: 10px; }
.np-chip { display: inline-flex; align-items: center; gap: 6px; padding: 5px 10px 5px 8px; border-radius: var(--se-r-pill); background: var(--se-navy-50); color: var(--se-navy-700); font-weight: 700; font-size: var(--se-fs-xs); text-decoration: none; transition: transform var(--se-t-fast), background var(--se-t-fast); }
.np-chip:hover { transform: translateY(-1px); background: var(--se-navy-100); }
.np-chip .np-unit { opacity: .7; font-weight: 600; }
.np-chip .np-streak { display: inline-flex; align-items: center; gap: 3px; margin-left: 4px; padding: 2px 8px; border-radius: var(--se-r-pill); background: var(--se-marigold-100); color: var(--se-marigold-600); }
[data-theme="dark"] .np-chip { color: #AEC4EE; }
[data-theme="dark"] .np-chip .np-streak { color: #F3C27A; }
.icon-btn { position: relative; width: 38px; height: 38px; border-radius: 50%; border: 1px solid var(--se-border); background: var(--se-surface); color: var(--se-text-muted); cursor: pointer; display: grid; place-items: center; font-size: 15px; transition: background var(--se-t-fast), color var(--se-t-fast); }
.icon-btn:hover { background: var(--se-sunken); color: var(--se-ink); }
.icon-btn--logout { display: none; }
.bell-badge { position: absolute; top: -3px; right: -3px; min-width: 18px; height: 18px; padding: 0 5px; border-radius: var(--se-r-pill); background: var(--se-danger-600); color: #fff; font-size: 10px; font-weight: 700; display: grid; place-items: center; }
.bell-wrap { position: relative; }
.bell-backdrop { position: fixed; inset: 0; z-index: 40; }
.bell-dropdown { position: absolute; right: 0; top: 46px; width: 340px; z-index: 50; background: var(--se-surface); border: 1px solid var(--se-border); border-radius: var(--se-r-lg); box-shadow: var(--se-shadow-3); overflow: hidden; }
.bell-head { display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; border-bottom: 1px solid var(--se-border); font-weight: 600; color: var(--se-ink); }
.bell-clear { background: none; border: 0; color: var(--se-navy-600); font-size: var(--se-fs-xs); font-weight: 600; cursor: pointer; }
.bell-empty { padding: 24px; text-align: center; color: var(--se-text-muted); font-size: var(--se-fs-sm); }
.bell-item { display: flex; gap: 10px; padding: 12px 16px; border-bottom: 1px solid var(--se-border); }
.bell-item:last-child { border-bottom: 0; }
.bell-item.unread { background: var(--se-navy-50); }
.bell-item-icon { width: 32px; height: 32px; border-radius: 50%; flex-shrink: 0; display: grid; place-items: center; background: var(--se-navy-100); color: var(--se-navy-700); font-size: 13px; }
.bell-item-text { font-size: var(--se-fs-sm); color: var(--se-text); line-height: 1.35; }
.bell-item-time { font-size: var(--se-fs-2xs); color: var(--se-text-faint); margin-top: 2px; }
.topbar-date { font-size: var(--se-fs-xs); color: var(--se-text-muted); }

.page-enter-from { opacity: 0; transform: translateY(6px); }
.page-leave-to { opacity: 0; }
.page-enter-active, .page-leave-active { transition: all var(--se-t-med) var(--se-ease-out); }

/* bottom nav + more sheet (mobile) */
.bottom-nav { display: none; position: fixed; bottom: 0; left: 0; right: 0; z-index: 60; background: var(--se-surface); border-top: 1px solid var(--se-border); padding: 6px 4px calc(6px + env(safe-area-inset-bottom)); justify-content: space-around; box-shadow: 0 -4px 16px rgba(22,35,63,.06); }
.bottom-item { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 3px; padding: 6px 2px; border: 0; background: none; border-radius: var(--se-r-md); text-decoration: none; color: var(--se-text-muted); font-size: 11px; font-weight: 600; min-width: 0; cursor: pointer; transition: color var(--se-t-fast); }
.bottom-item i { font-size: 18px; }
.bottom-item.router-link-active, .bottom-item.is-active { color: var(--se-navy-700); }
[data-theme="dark"] .bottom-item.router-link-active, [data-theme="dark"] .bottom-item.is-active { color: #AEC4EE; }

.more-backdrop { display: none; position: fixed; inset: 0; background: rgba(16,23,38,.5); z-index: 70; }
.more-sheet { display: none; position: fixed; left: 0; right: 0; bottom: 0; z-index: 80; background: var(--se-surface); border-radius: var(--se-r-lg) var(--se-r-lg) 0 0; box-shadow: var(--se-shadow-3); padding: 10px 16px calc(20px + env(safe-area-inset-bottom)); animation: sheet-up var(--se-t-slow) var(--se-ease-out); }
.more-grab { width: 40px; height: 4px; border-radius: 2px; background: var(--se-border-strong); margin: 4px auto 12px; }
.more-head { font-family: var(--se-font-display); font-weight: 700; color: var(--se-ink); margin-bottom: 12px; }
.more-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }
.more-tile { display: flex; flex-direction: column; align-items: center; gap: 6px; padding: 14px 6px; border-radius: var(--se-r-md); text-decoration: none; color: var(--se-text); background: var(--se-sunken); font-size: 11px; font-weight: 600; text-align: center; }
.more-tile i { font-size: 18px; color: var(--se-navy-600); }
.more-tile.router-link-active { background: var(--se-navy-50); color: var(--se-navy-700); }
.more-logout { width: 100%; margin-top: 14px; background: var(--se-sunken); color: var(--se-danger-600); border: 0; padding: 12px; border-radius: var(--se-r-md); font-weight: 600; cursor: pointer; }
@keyframes sheet-up { from { transform: translateY(100%); } to { transform: none; } }

@media (max-width: 991.98px) {
  .bottom-nav { display: flex; }
  .more-backdrop, .more-sheet { display: block; }
  .icon-btn--logout { display: grid; }
  .topbar-date { display: none; }
  .np-chip .np-unit { display: none; }
}
</style>
