<template>
  <div class="rewards-page">

    <!-- ══ Profile hero ═══════════════════════════════════════ -->
    <section class="card hero-card mb-4">
      <div class="hero-main">
        <div class="hero-id">
          <div class="level-ring" :style="{ '--p': engagement.levelProgress }"
               :title="`Level progress: ${engagement.levelProgress}%`">
            <div class="se-avatar se-avatar--lg se-avatar--marigold">{{ user.initials }}</div>
            <span class="level-bubble" :title="engagement.level.name" aria-hidden="true">
              <i class="fas" :class="engagement.level.icon"></i>
            </span>
          </div>
          <div class="hero-who">
            <h2 class="hero-name">{{ user.name }}</h2>
            <div class="hero-level">
              <i class="fas" :class="engagement.level.icon" aria-hidden="true"></i>
              {{ engagement.level.name }}
              <span class="hero-flat">· Flat {{ user.flat }}</span>
            </div>
            <div class="hero-chips">
              <span class="se-chip se-chip--flame">🔥 {{ engagement.checkInStreak }}-day check-in</span>
              <span class="se-chip se-chip--teal">
                <i class="fas fa-calendar-check" aria-hidden="true"></i>{{ engagement.paymentStreak }}-month on-time
              </span>
            </div>
          </div>
        </div>

        <div class="hero-np">
          <div class="hero-np-value se-num">{{ fmt(engagement.points) }}</div>
          <div class="hero-np-label">Neighbour Points (NP)</div>
        </div>
      </div>

      <div class="hero-progress">
        <div class="hero-progress-meta">
          <span>Level progress</span>
          <span v-if="engagement.nextLevel" class="se-num">
            {{ fmt(engagement.npToNext) }} NP to {{ engagement.nextLevel.name }}
          </span>
          <span v-else>Max level!</span>
        </div>
        <div class="progress-bar-custom" role="progressbar" aria-label="Progress to next level"
             :aria-valuenow="engagement.levelProgress" aria-valuemin="0" aria-valuemax="100">
          <div class="progress-fill hero-fill" :style="{ width: engagement.levelProgress + '%' }"></div>
        </div>
      </div>

      <!-- Level ladder -->
      <div class="ladder-wrap">
        <div class="ladder-title">Level ladder</div>
        <ol class="ladder">
          <li v-for="(l, i) in LEVELS" :key="l.name" class="ladder-step"
              :class="{ 'is-done': i < currentLevelIdx, 'is-current': i === currentLevelIdx }">
            <div class="ladder-dot"><i class="fas" :class="l.icon" aria-hidden="true"></i></div>
            <div class="ladder-name">{{ l.name }}</div>
            <div class="ladder-min se-num">{{ fmt(l.min) }} NP</div>
          </li>
        </ol>
      </div>
    </section>

    <!-- ══ Badges ═════════════════════════════════════════════ -->
    <div class="se-page-actions">
      <h3 class="se-section-title">Badge collection</h3>
      <span class="se-chip se-chip--marigold">
        <i class="fas fa-medal" aria-hidden="true"></i>{{ earnedCount }} / {{ engagement.badges.length }} earned
      </span>
    </div>

    <div v-if="engagement.badges.length" class="badge-grid mb-4">
      <div v-for="b in engagement.badges" :key="b.id" class="badge-tile"
           :class="b.earned ? 'is-earned' : 'is-locked'" :title="b.desc">
        <div class="badge-ico">
          <i class="fas" :class="b.icon" aria-hidden="true"></i>
          <span v-if="!b.earned" class="badge-lock" aria-hidden="true"><i class="fas fa-lock"></i></span>
        </div>
        <div class="badge-name">{{ b.name }}<span v-if="!b.earned" class="visually-hidden"> (locked)</span></div>
        <div class="badge-desc">{{ b.desc }}</div>
      </div>
    </div>
    <div v-else class="card empty-state mb-4">
      <i class="fas fa-medal"></i>
      <p>No badges yet — get involved to start earning.</p>
    </div>

    <!-- ══ Recognition ════════════════════════════════════════ -->
    <div class="se-page-actions">
      <h3 class="se-section-title">Community standings</h3>
      <span class="se-chip se-chip--navy"><i class="fas fa-trophy" aria-hidden="true"></i>This quarter</span>
    </div>

    <div class="row g-3 align-items-stretch">
      <!-- Top Blocks -->
      <div class="col-md-6 col-lg-4">
        <div class="card h-100">
          <div class="card-header-custom"><i class="fas fa-building lb-head-ico" aria-hidden="true"></i>Top Blocks</div>
          <ol v-if="demo.leaderboard.blocks.length" class="lb-list">
            <li v-for="b in demo.leaderboard.blocks" :key="b.block" class="lb-row">
              <span class="lb-rank se-num" :class="rankClass(b.rank)">{{ b.rank }}</span>
              <span class="lb-who"><span class="lb-name">{{ b.block }}</span></span>
              <span class="lb-np se-num">{{ fmt(b.np) }}<small> NP</small></span>
            </li>
          </ol>
          <div v-else class="empty-state"><i class="fas fa-building"></i><p>No block standings yet.</p></div>
        </div>
      </div>

      <!-- Top Neighbours -->
      <div class="col-md-6 col-lg-4">
        <div class="card h-100">
          <div class="card-header-custom"><i class="fas fa-people-group lb-head-ico" aria-hidden="true"></i>Top Neighbours</div>
          <ol v-if="demo.leaderboard.flats.length" class="lb-list">
            <li v-for="f in demo.leaderboard.flats" :key="f.flat" class="lb-row" :class="{ 'is-you': f.you }">
              <span class="lb-rank se-num" :class="rankClass(f.rank)">{{ f.rank }}</span>
              <span class="se-avatar se-avatar--sm" :class="{ 'se-avatar--marigold': f.you }">{{ initialsOf(f.name) }}</span>
              <span class="lb-who">
                <span class="lb-name">{{ f.name }}<span v-if="f.you" class="you-tag">You</span></span>
                <span class="lb-sub">Flat {{ f.flat }}</span>
              </span>
              <span class="lb-np se-num">{{ fmt(f.np) }}<small> NP</small></span>
            </li>
          </ol>
          <div v-else class="empty-state"><i class="fas fa-people-group"></i><p>No neighbour standings yet.</p></div>
        </div>
      </div>

      <!-- Neighbour of the Month -->
      <div class="col-12 col-lg-4">
        <div class="card h-100 nom-card">
          <div class="card-header-custom"><i class="fas fa-crown lb-head-ico nom-head-ico" aria-hidden="true"></i>Neighbour of the Month</div>
          <div v-if="demo.neighbourOfMonth" class="nom-body">
            <div class="nom-avatar">
              <div class="se-avatar se-avatar--lg">{{ demo.neighbourOfMonth.initials }}</div>
              <span class="nom-ribbon" aria-hidden="true"><i class="fas fa-crown"></i></span>
            </div>
            <div class="nom-name">{{ demo.neighbourOfMonth.name }}</div>
            <div class="nom-sub">
              Flat {{ demo.neighbourOfMonth.flat }} ·
              <span class="se-num">{{ fmt(demo.neighbourOfMonth.np) }}</span> NP
            </div>
            <blockquote class="nom-quote">
              <i class="fas fa-quote-left" aria-hidden="true"></i>{{ demo.neighbourOfMonth.reason }}
            </blockquote>
          </div>
          <div v-else class="empty-state"><i class="fas fa-crown"></i><p>Nominations open soon.</p></div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { computed } from 'vue'
import { engagement, LEVELS } from '../store/engagement'
import { demo, me } from '../store/demo'

const user = computed(() => me())

const nf = new Intl.NumberFormat('en-IN')
const fmt = (n) => nf.format(n)

const currentLevelIdx = computed(() => LEVELS.findIndex(l => l.name === engagement.level.name))
const earnedCount = computed(() => engagement.badges.filter(b => b.earned).length)

const initialsOf = (name) => name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase()
const rankClass = (rank) => (rank === 1 ? 'is-gold' : rank === 2 ? 'is-silver' : rank === 3 ? 'is-bronze' : '')
</script>

<style scoped>
/* ── Profile hero ──────────────────────────────────────────── */
.hero-card {
  padding: var(--se-sp-6);
  background:
    radial-gradient(340px 200px at 100% 0, var(--se-marigold-50), transparent 70%),
    var(--se-surface);
}
.hero-main {
  display: flex;
  flex-wrap: wrap;
  gap: var(--se-sp-5);
  align-items: center;
  justify-content: space-between;
}
.hero-id {
  display: flex;
  gap: var(--se-sp-4);
  align-items: center;
  min-width: 0;
}

/* progress ring around the avatar (echoes the bar below) */
.level-ring {
  --p: 0;
  position: relative;
  flex-shrink: 0;
  padding: 5px;
  border-radius: 50%;
  background: conic-gradient(var(--se-marigold-400) calc(var(--p) * 1%), var(--se-sunken) 0);
}
.level-ring .se-avatar { border: 3px solid var(--se-surface); }
.level-bubble {
  position: absolute;
  right: -2px;
  bottom: -2px;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  font-size: var(--se-fs-2xs);
  background: var(--se-navy-600);
  color: #fff; /* matches global on-navy fills (.se-avatar) */
  border: 2px solid var(--se-surface);
}

.hero-name {
  font-family: var(--se-font-display);
  font-weight: 700;
  font-size: var(--se-fs-2xl);
  color: var(--se-ink);
  margin: 0 0 2px;
}
.hero-level {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  font-family: var(--se-font-display);
  font-weight: 600;
  font-size: var(--se-fs-md);
  color: var(--se-text);
}
.hero-level > i { color: var(--se-marigold-500); }
.hero-flat {
  font-family: var(--se-font-body);
  font-weight: 400;
  font-size: var(--se-fs-sm);
  color: var(--se-text-muted);
}
.hero-chips {
  display: flex;
  flex-wrap: wrap;
  gap: var(--se-sp-2);
  margin-top: var(--se-sp-3);
}

.hero-np { text-align: right; }
.hero-np-value {
  font-family: var(--se-font-display);
  font-size: var(--se-fs-3xl);
  font-weight: 800;
  line-height: 1.05;
  color: var(--se-ink);
}
.hero-np-label {
  font-size: var(--se-fs-2xs);
  font-weight: 600;
  letter-spacing: .04em;
  text-transform: uppercase;
  color: var(--se-text-muted);
  margin-top: 2px;
}

.hero-progress { margin-top: var(--se-sp-5); }
.hero-progress-meta {
  display: flex;
  justify-content: space-between;
  gap: var(--se-sp-3);
  font-size: var(--se-fs-xs);
  font-weight: 600;
  color: var(--se-text-muted);
  margin-bottom: 6px;
}
.hero-fill {
  background: var(--se-marigold-400);
  transition: width var(--se-t-slow) var(--se-ease-out);
}

/* ── Level ladder ──────────────────────────────────────────── */
.ladder-wrap {
  margin-top: var(--se-sp-5);
  padding-top: var(--se-sp-5);
  border-top: 1px dashed var(--se-border);
}
.ladder-title {
  font-size: var(--se-fs-2xs);
  font-weight: 600;
  letter-spacing: .04em;
  text-transform: uppercase;
  color: var(--se-text-muted);
  margin-bottom: var(--se-sp-3);
}
.ladder {
  list-style: none;
  margin: 0;
  padding: 0 0 var(--se-sp-1);
  display: flex;
  overflow-x: auto;
}
.ladder-step {
  flex: 1 0 104px;
  min-width: 104px;
  position: relative;
  text-align: center;
}
.ladder-step::before {
  content: "";
  position: absolute;
  top: 20px;
  left: -50%;
  width: 100%;
  height: 3px;
  border-radius: var(--se-r-pill);
  background: var(--se-border);
}
.ladder-step:first-child::before { display: none; }
.ladder-step.is-done::before,
.ladder-step.is-current::before { background: var(--se-teal-600); }
.ladder-dot {
  position: relative;
  z-index: 1;
  width: 42px;
  height: 42px;
  margin: 0 auto var(--se-sp-2);
  border-radius: 50%;
  display: grid;
  place-items: center;
  background: var(--se-sunken);
  color: var(--se-text-faint);
  border: 1px solid var(--se-border);
  transition: transform var(--se-t-fast) var(--se-ease-std);
}
.ladder-step:hover .ladder-dot { transform: translateY(-2px); }
.ladder-step.is-done .ladder-dot {
  background: var(--se-teal-600);
  border-color: var(--se-teal-600);
  color: #fff; /* matches global on-teal fills (.se-avatar--teal) */
}
.ladder-step.is-current .ladder-dot {
  background: var(--se-marigold-400);
  border-color: var(--se-marigold-400);
  color: var(--se-navy-800); /* marigold always carries navy ink */
  box-shadow: 0 0 0 4px var(--se-marigold-100);
}
.ladder-name {
  font-size: var(--se-fs-xs);
  font-weight: 600;
  color: var(--se-text);
}
.ladder-step.is-current .ladder-name { color: var(--se-ink); font-weight: 700; }
.ladder-min {
  font-size: var(--se-fs-2xs);
  color: var(--se-text-muted);
}

/* ── Badge grid ────────────────────────────────────────────── */
.badge-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: var(--se-sp-3);
}
.badge-tile {
  background: var(--se-surface);
  border: 1px solid var(--se-border);
  border-radius: var(--se-r-lg);
  padding: var(--se-sp-4);
  text-align: center;
  transition: transform var(--se-t-fast) var(--se-ease-std), box-shadow var(--se-t-fast) var(--se-ease-std);
}
.badge-tile.is-earned:hover {
  transform: translateY(-2px);
  box-shadow: var(--se-shadow-2);
}
.badge-tile.is-locked { border-style: dashed; }
.badge-ico {
  position: relative;
  width: 46px;
  height: 46px;
  margin: 0 auto var(--se-sp-2);
  border-radius: 50%;
  display: grid;
  place-items: center;
  font-size: var(--se-fs-lg);
}
.is-earned .badge-ico { background: var(--se-marigold-100); color: var(--se-marigold-600); }
.is-locked .badge-ico { background: var(--se-sunken); color: var(--se-text-faint); }
.badge-lock {
  position: absolute;
  right: -4px;
  bottom: -4px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  font-size: 9px;
  background: var(--se-text-muted);
  color: var(--se-surface);
  border: 2px solid var(--se-surface);
}
.badge-name {
  font-family: var(--se-font-display);
  font-weight: 600;
  font-size: var(--se-fs-sm);
  color: var(--se-ink);
}
.is-locked .badge-name { color: var(--se-text-muted); }
.badge-desc {
  font-size: var(--se-fs-2xs);
  color: var(--se-text-muted);
  margin-top: 2px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.is-locked .badge-desc { font-style: italic; color: var(--se-text-faint); }

/* ── Leaderboards ──────────────────────────────────────────── */
.lb-head-ico { color: var(--se-teal-600); }
.nom-head-ico { color: var(--se-marigold-500); }
.lb-list {
  list-style: none;
  margin: 0;
  padding: var(--se-sp-2);
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.lb-row {
  display: flex;
  align-items: center;
  gap: var(--se-sp-3);
  padding: 10px 12px;
  border-radius: var(--se-r-md);
  transition: background var(--se-t-fast) var(--se-ease-std);
}
.lb-row:not(.is-you):hover { background: var(--se-sunken); }
.lb-row.is-you {
  background: var(--se-navy-50);
  box-shadow: inset 3px 0 0 var(--se-navy-600);
}
.lb-rank {
  width: 26px;
  height: 26px;
  flex-shrink: 0;
  border-radius: 50%;
  display: grid;
  place-items: center;
  font-size: var(--se-fs-2xs);
  font-weight: 700;
  background: var(--se-sunken);
  color: var(--se-text-muted);
}
.lb-rank.is-gold { background: var(--se-marigold-100); color: var(--se-marigold-600); }
.lb-rank.is-silver { background: var(--se-navy-100); color: var(--se-ink); }
.lb-rank.is-bronze { background: var(--se-warn-100); color: var(--se-warn-ink); }
.lb-who {
  display: flex;
  flex-direction: column;
  min-width: 0;
}
.lb-name {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
  font-size: var(--se-fs-sm);
  color: var(--se-ink);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.lb-sub { font-size: var(--se-fs-2xs); color: var(--se-text-muted); }
.lb-np {
  margin-left: auto;
  font-weight: 700;
  font-size: var(--se-fs-sm);
  color: var(--se-ink);
  white-space: nowrap;
}
.lb-np small { font-size: var(--se-fs-2xs); font-weight: 600; color: var(--se-text-muted); }
.you-tag {
  flex-shrink: 0;
  padding: 2px 7px;
  border-radius: var(--se-r-pill);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: .03em;
  text-transform: uppercase;
  background: var(--se-navy-600);
  color: #fff; /* matches global on-navy fills */
}

/* ── Neighbour of the Month ────────────────────────────────── */
.nom-body {
  padding: var(--se-sp-5) var(--se-sp-5) var(--se-sp-6);
  text-align: center;
  background: radial-gradient(200px 120px at 50% 0, var(--se-marigold-50), transparent 75%);
}
.nom-avatar {
  position: relative;
  width: 72px;
  margin: var(--se-sp-2) auto var(--se-sp-3);
}
.nom-ribbon {
  position: absolute;
  top: -14px;
  left: -10px;
  transform: rotate(-24deg);
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  font-size: 13px;
  background: var(--se-marigold-400);
  color: var(--se-navy-800); /* marigold always carries navy ink */
  border: 2px solid var(--se-surface);
  box-shadow: var(--se-shadow-1);
}
.nom-name {
  font-family: var(--se-font-display);
  font-weight: 700;
  font-size: var(--se-fs-lg);
  color: var(--se-ink);
}
.nom-sub {
  font-size: var(--se-fs-sm);
  color: var(--se-text-muted);
  margin-top: 2px;
}
.nom-quote {
  position: relative;
  margin: var(--se-sp-4) auto 0;
  max-width: 34ch;
  padding: var(--se-sp-3) var(--se-sp-4);
  text-align: left;
  font-size: var(--se-fs-sm);
  font-style: italic;
  color: var(--se-text);
  background: var(--se-surface);
  border: 1px solid var(--se-border);
  border-left: 3px solid var(--se-marigold-400);
  border-radius: var(--se-r-md);
}
.nom-quote i {
  margin-right: 6px;
  font-size: var(--se-fs-2xs);
  color: var(--se-marigold-500);
}

/* ── Responsive ────────────────────────────────────────────── */
@media (max-width: 575.98px) {
  .hero-card { padding: var(--se-sp-5); }
  .hero-np { text-align: left; }
  .hero-np-value { font-size: var(--se-fs-2xl); }
  .hero-name { font-size: var(--se-fs-xl); }
}
</style>
