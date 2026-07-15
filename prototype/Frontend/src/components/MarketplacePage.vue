<template>
  <div class="market">
    <!-- ── Header: one clear primary action ─────────────────── -->
    <div class="se-page-actions">
      <div>
        <h1 class="se-section-title">Marketplace</h1>
        <p class="page-sub">Buy, sell, give away — it all stays inside the society.</p>
      </div>
      <button
        type="button"
        class="btn-primary-custom market__toggle"
        :aria-expanded="composing"
        aria-controls="listing-form"
        @click="toggleCompose"
      >
        <i class="fas" :class="composing ? 'fa-xmark' : 'fa-plus'" aria-hidden="true"></i>
        {{ composing ? 'Close' : 'Post a listing' }}
      </button>
    </div>

    <!-- ── Inline compose card ──────────────────────────────── -->
    <Transition name="sheet">
      <section v-if="composing" id="listing-form" class="card compose" aria-label="Post a new listing">
        <form @submit.prevent="publish">
          <div class="form-group">
            <label class="form-label" for="mk-title">What are you listing?</label>
            <input
              id="mk-title"
              ref="titleEl"
              v-model="form.title"
              type="text"
              class="form-control-custom"
              maxlength="80"
              placeholder="e.g. Kids’ cycle, sofa set, tiffin service…"
            />
          </div>

          <div class="compose__grid">
            <div class="form-group">
              <label class="form-label" for="mk-price">Price (₹)</label>
              <div class="price-wrap">
                <span class="price-wrap__symbol" aria-hidden="true">₹</span>
                <input
                  id="mk-price"
                  v-model.number="form.price"
                  type="number"
                  class="form-control-custom price-wrap__input"
                  min="0"
                  step="1"
                  inputmode="numeric"
                  placeholder="0 = free"
                />
              </div>
            </div>
            <div class="form-group">
              <label class="form-label" for="mk-category">Category</label>
              <select id="mk-category" v-model="form.category" class="form-control-custom">
                <option v-for="c in CATEGORIES" :key="c.name" :value="c.name">{{ c.name }}</option>
              </select>
            </div>
          </div>

          <div class="compose__foot">
            <p class="compose__hint">Neighbours reach you directly · earns <span class="se-num">+10</span> NP</p>
            <button type="submit" class="btn-primary-custom compose__submit">
              <i class="fas fa-paper-plane" aria-hidden="true"></i>Publish listing
            </button>
          </div>
        </form>
      </section>
    </Transition>

    <!-- ── Category filters ─────────────────────────────────── -->
    <div class="chip-row" role="group" aria-label="Filter listings by category">
      <button
        type="button"
        class="pick-chip"
        :class="{ 'is-on': filter === 'All' }"
        :aria-pressed="filter === 'All'"
        @click="filter = 'All'"
      >
        <i class="fas fa-layer-group" aria-hidden="true"></i>All
        <span class="pick-chip__count se-num">{{ demo.marketplace.length }}</span>
      </button>
      <button
        v-for="c in CATEGORIES"
        :key="c.name"
        type="button"
        class="pick-chip"
        :class="{ 'is-on': filter === c.name }"
        :aria-pressed="filter === c.name"
        @click="filter = c.name"
      >
        <i class="fas" :class="c.icon" aria-hidden="true"></i>{{ c.name }}
        <span class="pick-chip__count se-num">{{ countFor(c.name) }}</span>
      </button>
    </div>

    <!-- ── Listings grid ────────────────────────────────────── -->
    <TransitionGroup name="grid" tag="div" appear class="row g-3 g-lg-4 listing-grid">
      <div
        v-for="(l, idx) in filtered"
        :key="l.id"
        class="col-md-6 col-lg-4"
        :style="{ '--stagger': Math.min(idx, 6) * 40 + 'ms' }"
      >
        <article class="card listing">
          <div class="listing__thumb">
            <span class="listing__emoji" aria-hidden="true">{{ l.emoji }}</span>
            <span class="badge-custom listing__cat" :class="badgeFor(l.category)">{{ l.category }}</span>
          </div>

          <div class="listing__body">
            <h3 class="listing__title">{{ l.title }}</h3>

            <div class="listing__pricing">
              <span v-if="l.price > 0" class="listing__price se-num">₹{{ nf.format(l.price) }}</span>
              <span v-else class="badge-custom badge-green listing__free">Free</span>
              <span class="listing__cond">
                <i class="fas fa-circle-check" aria-hidden="true"></i>{{ l.condition }}
              </span>
            </div>

            <div class="listing__seller">
              <div class="se-avatar se-avatar--sm" :class="avatarTone(initialsOf(l.seller) + l.flat)">
                {{ initialsOf(l.seller) }}
              </div>
              <div class="listing__who">
                <span class="listing__name">{{ l.seller }}</span>
                <span class="listing__flat">{{ l.flat }}</span>
              </div>
              <span class="listing__time">{{ l.time }}</span>
            </div>

            <button
              v-if="!isMine(l)"
              type="button"
              class="listing__contact"
              :class="{ 'is-sent': contacted.has(l.id) }"
              :aria-label="`Contact ${l.seller} about ${l.title}`"
              @click="contact(l)"
            >
              <i class="fas" :class="contacted.has(l.id) ? 'fa-circle-check' : 'fa-comment-dots'" aria-hidden="true"></i>
              {{ contacted.has(l.id) ? 'Request sent' : 'Contact' }}
            </button>
            <div v-else class="listing__own">
              <i class="fas fa-circle-user" aria-hidden="true"></i>Your listing
            </div>
          </div>
        </article>
      </div>
    </TransitionGroup>

    <!-- ── Empty state (per filter) ─────────────────────────── -->
    <div v-if="filtered.length === 0" class="card empty-state market__empty">
      <i class="fas fa-box-open" aria-hidden="true"></i>
      <p>{{ emptyMessage }}</p>
      <button type="button" class="btn-accent market__empty-cta" @click="startListing">
        <i class="fas fa-pen-nib me-2" aria-hidden="true"></i>Post the first listing
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, reactive, ref } from 'vue'
import { demo, me } from '../store/demo'
import { useCelebrate } from '../composables/useCelebrate'

const { reward, toast } = useCelebrate()

const user = me()
const nf = new Intl.NumberFormat('en-IN')

const CATEGORIES = [
  { name: 'For Sale', icon: 'fa-tag',                badge: 'badge-open' },
  { name: 'Giveaway', icon: 'fa-gift',               badge: 'badge-green' },
  { name: 'Wanted',   icon: 'fa-magnifying-glass',   badge: 'badge-medium' },
  { name: 'Service',  icon: 'fa-screwdriver-wrench', badge: 'badge-service' },
]

const EMPTY_COPY = {
  'All':      'The marketplace is quiet — post the first listing and get the bazaar going!',
  'For Sale': 'Nothing for sale right now — got something gathering dust at home?',
  'Giveaway': 'No giveaways yet — one neighbour’s clutter is another’s treasure.',
  'Wanted':   'Nobody has asked for anything yet — looking for something? Just ask!',
  'Service':  'No services on offer yet — bake, tutor, or repair? Put it up!',
}

const composing = ref(false)
const filter = ref('All')
const titleEl = ref(null)
const form = reactive({ title: '', price: '', category: 'For Sale' })
const contacted = reactive(new Set())

const filtered = computed(() =>
  filter.value === 'All' ? demo.marketplace : demo.marketplace.filter(l => l.category === filter.value)
)

const emptyMessage = computed(() => EMPTY_COPY[filter.value] || EMPTY_COPY['All'])

const countFor = (name) => demo.marketplace.filter(l => l.category === name).length
const badgeFor = (name) => CATEGORIES.find(c => c.name === name)?.badge || 'badge-low'
const isMine = (l) => l.seller === user.name

const initialsOf = (name) => name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase()

// Deterministic avatar tint — same recipe as the wall, so each
// neighbour keeps a stable colour across screens.
const TONES = ['', 'se-avatar--teal', 'se-avatar--marigold']
function avatarTone(seed) {
  let h = 0
  for (const ch of seed) h = (h * 31 + ch.charCodeAt(0)) % 997
  return TONES[h % TONES.length]
}

function toggleCompose() {
  composing.value = !composing.value
  if (composing.value) nextTick(() => titleEl.value?.focus())
}

function startListing() {
  if (filter.value !== 'All') form.category = filter.value
  composing.value = true
  nextTick(() => {
    titleEl.value?.scrollIntoView({ behavior: 'smooth', block: 'center' })
    titleEl.value?.focus({ preventScroll: true })
  })
}

function publish() {
  const title = form.title.trim()
  if (!title) {
    toast('Give your listing a title first', 'error')
    titleEl.value?.focus()
    return
  }
  const price = Math.max(0, Number(form.price) || 0)
  demo.addListing(title, price, form.category)
  reward(10, 'Posted a listing')
  // Make sure the poster sees their fresh card.
  if (filter.value !== 'All' && filter.value !== form.category) filter.value = 'All'
  composing.value = false
  Object.assign(form, { title: '', price: '', category: 'For Sale' })
}

function contact(l) {
  toast('Request sent to ' + l.seller, 'success')
  contacted.add(l.id)
}
</script>

<style scoped>
/* ── Header ─────────────────────────────────────────────────── */
.page-sub {
  margin: var(--se-sp-1) 0 0;
  font-size: var(--se-fs-sm);
  color: var(--se-text-muted);
}

/* ── Compose card ───────────────────────────────────────────── */
.compose {
  padding: var(--se-sp-5);
  margin-bottom: var(--se-sp-5);
}
.compose__grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0 var(--se-sp-4);
}
.price-wrap {
  position: relative;
}
.price-wrap__symbol {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  font-weight: 600;
  font-size: var(--se-fs-sm);
  color: var(--se-text-muted);
  pointer-events: none;
}
.price-wrap__input {
  padding-left: 30px;
}
.compose__foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--se-sp-3);
  flex-wrap: wrap;
}
.compose__hint {
  margin: 0;
  font-size: var(--se-fs-2xs);
  color: var(--se-text-faint);
}
.compose__submit {
  margin-left: auto;
}

/* compose card slides open/shut */
.sheet-enter-active,
.sheet-leave-active {
  transition:
    opacity var(--se-t-slow) var(--se-ease-out),
    transform var(--se-t-slow) var(--se-ease-out);
}
.sheet-enter-from,
.sheet-leave-to {
  opacity: 0;
  transform: translateY(-8px) scale(0.99);
}

/* ── Filter chips ───────────────────────────────────────────── */
.chip-row {
  display: flex;
  flex-wrap: wrap;
  gap: var(--se-sp-2);
  margin-bottom: var(--se-sp-5);
}
.pick-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 12px;
  min-height: 32px;
  border: 1px solid var(--se-border-strong);
  border-radius: var(--se-r-pill);
  background: var(--se-surface);
  color: var(--se-text-muted);
  font-family: var(--se-font-body);
  font-size: var(--se-fs-xs);
  font-weight: 600;
  cursor: pointer;
  transition:
    color var(--se-t-fast) var(--se-ease-std),
    background var(--se-t-fast) var(--se-ease-std),
    border-color var(--se-t-fast) var(--se-ease-std),
    transform var(--se-t-fast) var(--se-ease-std);
}
.pick-chip:hover {
  color: var(--se-ink);
  border-color: var(--se-navy-500);
  transform: translateY(-1px);
}
.pick-chip.is-on {
  background: var(--se-ink);
  border-color: var(--se-ink);
  color: var(--se-surface);
}
.pick-chip__count {
  font-size: var(--se-fs-2xs);
  opacity: 0.75;
}

/* ── Listing cards ──────────────────────────────────────────── */
.listing-grid {
  position: relative; /* anchors absolute leave transitions */
}
.listing {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}
.listing:hover {
  transform: translateY(-3px);
  box-shadow: var(--se-shadow-2);
}
.listing__thumb {
  position: relative;
  display: grid;
  place-items: center;
  height: 132px;
  background:
    radial-gradient(140px 90px at 50% 45%, var(--se-navy-50), transparent),
    var(--se-sunken);
  border-bottom: 1px solid var(--se-border);
}
.listing__emoji {
  font-size: 54px;
  line-height: 1;
  filter: drop-shadow(0 6px 8px rgba(22, 35, 63, 0.16));
  transition: transform var(--se-t-slow) var(--se-ease-out);
}
.listing:hover .listing__emoji {
  transform: translateY(-3px) scale(1.08) rotate(-3deg);
}
.listing__cat {
  position: absolute;
  top: var(--se-sp-3);
  left: var(--se-sp-3);
}

.listing__body {
  display: flex;
  flex-direction: column;
  gap: var(--se-sp-3);
  padding: var(--se-sp-4);
  flex: 1;
}
.listing__title {
  margin: 0;
  font-family: var(--se-font-display);
  font-size: var(--se-fs-md);
  font-weight: 700;
  color: var(--se-ink);
  line-height: 1.35;
  min-height: calc(2 * 1.35em); /* keeps price rows aligned across the grid */
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.listing__pricing {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--se-sp-2);
  flex-wrap: wrap;
}
.listing__price {
  font-family: var(--se-font-display);
  font-size: var(--se-fs-xl);
  font-weight: 700;
  color: var(--se-ink);
}
.listing__free {
  font-size: var(--se-fs-xs);
  padding: 5px 12px;
}
.listing__cond {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: var(--se-fs-2xs);
  color: var(--se-text-muted);
}
.listing__cond i {
  font-size: 11px;
  color: var(--se-teal-600);
}

.listing__seller {
  display: flex;
  align-items: center;
  gap: var(--se-sp-2);
  margin-top: auto;
  padding-top: var(--se-sp-3);
  border-top: 1px dashed var(--se-border);
}
.listing__who {
  display: flex;
  flex-direction: column;
  min-width: 0;
  line-height: 1.25;
}
.listing__name {
  font-size: var(--se-fs-xs);
  font-weight: 600;
  color: var(--se-ink);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.listing__flat {
  font-size: var(--se-fs-2xs);
  color: var(--se-text-muted);
}
.listing__time {
  margin-left: auto;
  font-size: var(--se-fs-2xs);
  color: var(--se-text-faint);
  white-space: nowrap;
}

.listing__contact {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  min-height: 44px;
  border: 1px solid var(--se-navy-500);
  border-radius: var(--se-r-md);
  background: transparent;
  color: var(--se-navy-600);
  font-family: var(--se-font-body);
  font-size: var(--se-fs-sm);
  font-weight: 600;
  cursor: pointer;
  transition:
    background var(--se-t-fast) var(--se-ease-std),
    color var(--se-t-fast) var(--se-ease-std),
    border-color var(--se-t-fast) var(--se-ease-std),
    transform var(--se-t-fast) var(--se-ease-std);
}
.listing__contact:hover {
  background: var(--se-navy-50);
  color: var(--se-navy-700);
  transform: translateY(-1px);
}
.listing__contact:active {
  transform: scale(0.98);
}
.listing__contact.is-sent {
  border-color: var(--se-teal-600);
  background: var(--se-teal-50);
  color: var(--se-teal-800);
}
.listing__own {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  min-height: 44px;
  border: 1px dashed var(--se-border-strong);
  border-radius: var(--se-r-md);
  background: var(--se-sunken);
  color: var(--se-text-muted);
  font-size: var(--se-fs-xs);
  font-weight: 600;
}

/* Service tone — marigold ramp (no global badge variant exists) */
.badge-service {
  background: var(--se-marigold-100);
  color: var(--se-marigold-600);
}

/* ── Empty state ────────────────────────────────────────────── */
.market__empty {
  margin-top: var(--se-sp-4);
}
.market__empty-cta {
  margin-top: var(--se-sp-4);
}

/* ── Grid motion: entrance stagger + smooth reflow ──────────── */
.grid-enter-active {
  transition:
    opacity var(--se-t-slow) var(--se-ease-out),
    transform var(--se-t-slow) var(--se-ease-out);
  transition-delay: var(--stagger, 0ms);
}
.grid-enter-from {
  opacity: 0;
  transform: translateY(10px) scale(0.98);
}
.grid-leave-active {
  position: absolute;
  transition: opacity var(--se-t-fast) var(--se-ease-std);
}
.grid-leave-to {
  opacity: 0;
}
.grid-move {
  transition: transform var(--se-t-slow) var(--se-ease-out);
}

/* ── Small screens ──────────────────────────────────────────── */
@media (max-width: 575.98px) {
  .market__toggle {
    width: 100%;
  }
  .compose {
    padding: var(--se-sp-4);
  }
  .compose__grid {
    grid-template-columns: 1fr;
  }
  .compose__submit {
    width: 100%;
  }
}
</style>
