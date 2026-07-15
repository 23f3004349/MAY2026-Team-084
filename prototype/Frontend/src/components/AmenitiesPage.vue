<template>
  <div class="amenities-page">
    <!-- Header + reactive summary line -->
    <div class="se-page-actions">
      <div>
        <h1 class="se-section-title">Book an Amenity</h1>
        <p class="se-subtitle">
          <i class="fas fa-calendar-check"></i>
          You have <strong class="se-num">{{ todayCount }}</strong>
          booking{{ todayCount === 1 ? '' : 's' }} today
        </p>
      </div>

      <div class="slot-legend" aria-hidden="true">
        <span class="legend-item"><span class="legend-dot legend-dot--available"></span>Available</span>
        <span class="legend-item"><span class="legend-dot legend-dot--mine"></span>Yours</span>
        <span class="legend-item"><span class="legend-dot legend-dot--booked"></span>Full</span>
      </div>
    </div>

    <!-- Amenity grid -->
    <div v-if="amenities.length" class="row g-3">
      <div v-for="(a, i) in amenities" :key="a.id" class="col-md-6 col-lg-4">
        <div class="card amenity-card">
          <div class="amenity-head">
            <div class="stat-icon" :class="accentClass(i)">
              <i class="fas" :class="a.icon"></i>
            </div>
            <div class="amenity-meta">
              <div class="amenity-name">{{ a.name }}</div>
              <div class="amenity-desc">{{ a.desc }}</div>
            </div>
          </div>

          <div class="slot-row">
            <button
              v-for="slot in a.slots"
              :key="slot.time"
              type="button"
              class="slot-pill"
              :class="'slot-pill--' + slot.status"
              :disabled="slot.status === 'booked'"
              :title="pillTitle(slot)"
              @click="onSlot(a, slot)"
            >
              <template v-if="slot.status === 'booked'">Full</template>
              <template v-else>
                <span class="se-num">{{ slot.time }}</span>
                <i v-if="slot.status === 'mine'" class="fas fa-check"></i>
              </template>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else class="empty-state card">
      <i class="fas fa-calendar-xmark"></i>
      <p>No amenities are available to book right now.</p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { demo } from '../store/demo'
import { useCelebrate } from '../composables/useCelebrate'

const { reward, toast } = useCelebrate()

const amenities = computed(() => demo.amenities)

// Total slots the current user holds across every amenity — reactive.
const todayCount = computed(() =>
  demo.amenities.reduce((n, a) => n + a.slots.filter(s => s.status === 'mine').length, 0)
)

const ACCENTS = ['teal', 'navy', 'marigold']
const accentClass = (i) => 'amenity-icon--' + ACCENTS[i % ACCENTS.length]

const pillTitle = (slot) => {
  if (slot.status === 'booked') return 'Fully booked'
  if (slot.status === 'mine') return 'Tap to cancel your booking'
  return 'Tap to book this slot'
}

function onSlot(amenity, slot) {
  if (slot.status === 'booked') return // 'Full' slots are never actionable
  const booked = demo.bookSlot(amenity.id, slot.time)
  if (booked) {
    reward(8, 'Booked ' + amenity.name + ' · ' + slot.time)
  } else {
    toast('Booking cancelled', 'info')
  }
}
</script>

<style scoped>
.se-subtitle {
  margin: 4px 0 0;
  color: var(--se-text-muted);
  font-size: var(--se-fs-sm);
  display: inline-flex;
  align-items: center;
  gap: 7px;
}
.se-subtitle i { color: var(--se-teal-600); }
.se-subtitle strong { color: var(--se-teal-700); font-weight: 700; }

/* ── Legend ─────────────────────────────────────────── */
.slot-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  font-size: var(--se-fs-xs);
  font-weight: 600;
  color: var(--se-text-muted);
}
.legend-item { display: inline-flex; align-items: center; gap: 6px; }
.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: var(--se-r-pill);
  flex-shrink: 0;
}
.legend-dot--available { background: var(--se-surface); border: 1.5px solid var(--se-border-strong); }
.legend-dot--mine { background: var(--se-teal-600); }
.legend-dot--booked { background: var(--se-sunken); border: 1.5px dashed var(--se-border-strong); }

/* ── Amenity card ───────────────────────────────────── */
.amenity-card {
  padding: var(--se-sp-5);
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: var(--se-sp-4);
  transition: box-shadow var(--se-t-med) var(--se-ease-std),
              transform var(--se-t-med) var(--se-ease-out);
}
.amenity-card:hover {
  box-shadow: var(--se-shadow-2);
  transform: translateY(-2px);
}
.amenity-head { display: flex; align-items: flex-start; gap: 12px; }
.amenity-meta { min-width: 0; }
.amenity-name {
  font-family: var(--se-font-display);
  font-weight: 700;
  font-size: var(--se-fs-lg);
  color: var(--se-ink);
  line-height: 1.2;
}
.amenity-desc {
  font-size: var(--se-fs-xs);
  color: var(--se-text-muted);
  margin-top: 2px;
}
.amenity-icon--teal { background: var(--se-teal-600); }
.amenity-icon--navy { background: var(--se-navy-600); }
.amenity-icon--marigold { background: var(--se-marigold-400); color: var(--se-navy-800); }

/* ── Slot pills ─────────────────────────────────────── */
.slot-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: auto; /* keep pills bottom-aligned across uneven cards */
}
.slot-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 13px;
  border-radius: var(--se-r-pill);
  font-family: var(--se-font-body);
  font-size: var(--se-fs-xs);
  font-weight: 600;
  line-height: 1;
  cursor: pointer;
  transition: background var(--se-t-fast) var(--se-ease-std),
              border-color var(--se-t-fast),
              color var(--se-t-fast),
              transform var(--se-t-fast);
}
.slot-pill:focus-visible { outline: 2px solid var(--se-teal-600); outline-offset: 2px; }

/* available → outline, clickable */
.slot-pill--available {
  background: var(--se-surface);
  border: 1px solid var(--se-border-strong);
  color: var(--se-text);
}
.slot-pill--available:hover {
  background: var(--se-teal-50);
  border-color: var(--se-teal-600);
  color: var(--se-teal-700);
  transform: translateY(-1px);
}

/* mine → teal filled with check, clickable to cancel */
.slot-pill--mine {
  background: var(--se-teal-600);
  border: 1px solid var(--se-teal-600);
  color: #fff;
}
.slot-pill--mine:hover {
  background: var(--se-teal-700);
  border-color: var(--se-teal-700);
  transform: translateY(-1px);
}
.slot-pill--mine .fa-check { font-size: 0.72em; }

/* booked → muted, truly non-clickable */
.slot-pill--booked {
  background: var(--se-sunken);
  border: 1px dashed var(--se-border-strong);
  color: var(--se-text-faint);
  cursor: not-allowed;
  font-style: italic;
}

@media (max-width: 575.98px) {
  .slot-legend { gap: 10px; }
}
</style>
