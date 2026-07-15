<template>
  <div class="wall">
    <!-- ── Composer ─────────────────────────────────────────── -->
    <section class="card composer" aria-label="Write a post">
      <div class="composer__row">
        <div class="se-avatar" :class="avatarTone(user.initials + user.flat)">{{ user.initials }}</div>
        <textarea
          ref="composerEl"
          v-model="draft"
          rows="2"
          class="form-control-custom composer__input"
          placeholder="Share something with your society…"
          aria-label="Share something with your society"
          @keydown.ctrl.enter.prevent="publish"
          @keydown.meta.enter.prevent="publish"
        ></textarea>
      </div>

      <div class="composer__foot">
        <div class="chip-row" aria-label="Choose a category">
          <button
            v-for="c in CATEGORIES"
            :key="c.name"
            type="button"
            class="pick-chip"
            :class="{ 'is-on': draftCategory === c.name }"
            :aria-pressed="draftCategory === c.name"
            @click="draftCategory = c.name"
          >
            <i class="fas" :class="c.icon" aria-hidden="true"></i>{{ c.name }}
          </button>
        </div>
        <button class="btn-primary-custom composer__post" :disabled="!draft.trim()" @click="publish">
          <i class="fas fa-paper-plane me-2" aria-hidden="true"></i>Post
        </button>
      </div>
      <p class="composer__hint">Ctrl + Enter to post · earns <span class="se-num">+15</span> NP</p>
    </section>

    <!-- ── Filters ──────────────────────────────────────────── -->
    <div class="chip-row filters" aria-label="Filter posts by category">
      <button
        type="button"
        class="pick-chip"
        :class="{ 'is-on': filter === 'All' }"
        :aria-pressed="filter === 'All'"
        @click="filter = 'All'"
      >
        All <span class="pick-chip__count se-num">{{ demo.wallPosts.length }}</span>
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
        {{ c.name }} <span class="pick-chip__count se-num">{{ countFor(c.name) }}</span>
      </button>
    </div>

    <!-- ── Feed ─────────────────────────────────────────────── -->
    <TransitionGroup name="feed" tag="div" class="feed">
      <article v-for="post in filteredPosts" :key="post.id" class="card post">
        <header class="post__head">
          <div class="se-avatar" :class="avatarTone(post.initials + post.flat)">{{ post.initials }}</div>
          <div class="post__meta">
            <div class="post__who">
              <span class="post__author">{{ post.author }}</span>
              <span class="post__flat se-num">· {{ post.flat }}</span>
              <span class="post__time"><i class="fas fa-clock" aria-hidden="true"></i> {{ post.time }}</span>
            </div>
            <span class="se-chip post__chip" :class="chipFor(post.category)">
              <i class="fas" :class="iconFor(post.category)" aria-hidden="true"></i>{{ post.category }}
            </span>
          </div>
        </header>

        <p class="post__text">{{ post.text }}</p>

        <!-- Reactions -->
        <div class="post__reactions">
          <button
            v-for="r in REACTIONS"
            :key="r.kind"
            type="button"
            class="reaction-pill"
            :class="{ 'is-active': post.myReaction === r.kind }"
            :aria-pressed="post.myReaction === r.kind"
            :title="r.label"
            @click="onReact(post, r.kind)"
          >
            <span class="reaction-pill__emoji">{{ r.emoji }}</span>
            <span class="reaction-pill__count se-num">{{ post.reactions[r.kind] }}</span>
          </button>
          <span v-if="post.comments.length" class="post__ccount" :title="post.comments.length + ' comments'">
            <i class="fas fa-comment" aria-hidden="true"></i>
            <span class="se-num">{{ post.comments.length }}</span>
          </span>
        </div>

        <!-- Comment thread -->
        <div v-if="post.comments.length" class="post__comments">
          <div v-for="(cm, i) in post.comments" :key="post.id + '-' + i" class="comment">
            <div class="se-avatar se-avatar--sm" :class="avatarTone(cm.author + cm.flat)">{{ initialsOf(cm.author) }}</div>
            <div class="comment__bubble">
              <div class="comment__meta">
                <span class="comment__author">{{ cm.author }}</span>
                <span class="comment__flat se-num">· {{ cm.flat }}</span>
                <span class="comment__time">{{ cm.time }}</span>
              </div>
              <p class="comment__text">{{ cm.text }}</p>
            </div>
          </div>
        </div>

        <!-- Comment composer -->
        <div class="comment-compose">
          <div class="se-avatar se-avatar--sm" :class="avatarTone(user.initials + user.flat)">{{ user.initials }}</div>
          <input
            v-model="commentDrafts[post.id]"
            type="text"
            class="form-control-custom comment-compose__input"
            placeholder="Write a comment…"
            :aria-label="'Comment on ' + post.author + '\u2019s post'"
            @keydown.enter.prevent="sendComment(post)"
          />
          <button
            type="button"
            class="comment-compose__send"
            :disabled="!(commentDrafts[post.id] || '').trim()"
            aria-label="Send comment"
            @click="sendComment(post)"
          >
            <i class="fas fa-paper-plane" aria-hidden="true"></i>
          </button>
        </div>
      </article>
    </TransitionGroup>

    <!-- ── Empty state ──────────────────────────────────────── -->
    <div v-if="filteredPosts.length === 0" class="card empty-state wall__empty">
      <i class="fas fa-comment-slash" aria-hidden="true"></i>
      <p>{{ emptyMessage }}</p>
      <button type="button" class="btn-accent wall__empty-cta" @click="startPost">
        <i class="fas fa-pen-nib me-2" aria-hidden="true"></i>Write the first post
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { engagement } from '../store/engagement'
import { demo, me } from '../store/demo'
import { useCelebrate } from '../composables/useCelebrate'

const { reward, celebrate, toast } = useCelebrate()

const user = me()

const CATEGORIES = [
  { name: 'Announcement', icon: 'fa-bullhorn',                  chip: 'se-chip--navy' },
  { name: 'Help',         icon: 'fa-hand-holding-heart',        chip: 'se-chip--flame' },
  { name: 'Recommend',    icon: 'fa-thumbs-up',                 chip: 'se-chip--teal' },
  { name: 'Lost & Found', icon: 'fa-magnifying-glass-location', chip: 'se-chip--warn' },
  { name: 'Celebration',  icon: 'fa-champagne-glasses',         chip: 'se-chip--marigold' },
]

const REACTIONS = [
  { kind: 'like',      emoji: '👍', label: 'Like' },
  { kind: 'love',      emoji: '❤️', label: 'Love' },
  { kind: 'celebrate', emoji: '🎉', label: 'Celebrate' },
  { kind: 'pray',      emoji: '🙏', label: 'Grateful' },
]

const draft = ref('')
const draftCategory = ref('Announcement')
const filter = ref('All')
const commentDrafts = reactive({})
const composerEl = ref(null)

const filteredPosts = computed(() =>
  filter.value === 'All' ? demo.wallPosts : demo.wallPosts.filter(p => p.category === filter.value)
)

const emptyMessage = computed(() =>
  filter.value === 'All'
    ? 'The wall is quiet… be the first to say hello!'
    : `No ${filter.value} posts yet — start the conversation!`
)

const countFor = (name) => demo.wallPosts.filter(p => p.category === name).length
const catMeta = (name) => CATEGORIES.find(c => c.name === name)
const chipFor = (name) => catMeta(name)?.chip || 'se-chip--navy'
const iconFor = (name) => catMeta(name)?.icon || 'fa-bullhorn'

const initialsOf = (name) => name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase()

// Deterministic avatar tint so each neighbour keeps a stable colour.
const TONES = ['', 'se-avatar--teal', 'se-avatar--marigold']
function avatarTone(seed) {
  let h = 0
  for (const ch of seed) h = (h * 31 + ch.charCodeAt(0)) % 997
  return TONES[h % TONES.length]
}

function publish() {
  const text = draft.value.trim()
  if (!text) {
    toast('Write something first — your neighbours are all ears!', 'info')
    return
  }
  demo.addPost(text, draftCategory.value)
  reward(15, 'Shared a post on the wall')
  const badge = engagement.unlock('first_post')
  if (badge && badge.name) {
    celebrate({ title: 'Badge unlocked!', subtitle: `${badge.name} — ${badge.desc}`, icon: badge.icon })
  }
  draft.value = ''
  // Make sure the author sees their fresh post.
  if (filter.value !== 'All' && filter.value !== draftCategory.value) filter.value = 'All'
}

function onReact(post, kind) {
  demo.toggleReaction(post.id, kind)
  if (post.myReaction === kind) {
    // Reaction was added (or switched to this kind) — never fires on un-react.
    engagement.react()
    reward(3, 'Reacted to a post')
  }
}

function sendComment(post) {
  const text = (commentDrafts[post.id] || '').trim()
  if (!text) return
  demo.addComment(post.id, text)
  reward(5, 'Left a comment')
  commentDrafts[post.id] = ''
}

function startPost() {
  if (filter.value !== 'All') draftCategory.value = filter.value
  composerEl.value?.scrollIntoView({ behavior: 'smooth', block: 'center' })
  composerEl.value?.focus({ preventScroll: true })
}
</script>

<style scoped>
/* ── Layout ─────────────────────────────────────────────────── */
.wall {
  max-width: 680px;
  margin-inline: auto;
}

/* ── Composer ───────────────────────────────────────────────── */
.composer {
  padding: var(--se-sp-4) var(--se-sp-5) var(--se-sp-3);
  margin-bottom: var(--se-sp-5);
}
.composer__row {
  display: flex;
  align-items: flex-start;
  gap: var(--se-sp-3);
}
.composer__input {
  resize: none;
  min-height: 64px;
  font-size: var(--se-fs-sm);
  line-height: 1.5;
}
.composer__foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--se-sp-3);
  flex-wrap: wrap;
  margin-top: var(--se-sp-3);
}
.composer__post {
  white-space: nowrap;
  margin-left: auto;
}
.composer__hint {
  margin: var(--se-sp-2) 0 0;
  text-align: right;
  font-size: var(--se-fs-2xs);
  color: var(--se-text-faint);
}

/* ── Chips (category picker + filters) ──────────────────────── */
.chip-row {
  display: flex;
  flex-wrap: wrap;
  gap: var(--se-sp-2);
}
.filters {
  margin-bottom: var(--se-sp-4);
}
.pick-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 12px;
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

/* Lost & Found tone — mirrors the global .se-chip--* recipe with the warn ramp */
.se-chip--warn {
  background: var(--se-warn-50);
  color: var(--se-warn-ink);
}

/* ── Post cards ─────────────────────────────────────────────── */
.feed {
  display: flex;
  flex-direction: column;
  gap: var(--se-sp-4);
}
.post {
  padding: var(--se-sp-5);
}
.post__head {
  display: flex;
  align-items: flex-start;
  gap: var(--se-sp-3);
}
.post__meta {
  flex: 1;
  min-width: 0;
}
.post__who {
  display: flex;
  align-items: baseline;
  gap: var(--se-sp-2);
  flex-wrap: wrap;
}
.post__author {
  font-family: var(--se-font-display);
  font-weight: 700;
  color: var(--se-ink);
}
.post__flat {
  font-size: var(--se-fs-xs);
  color: var(--se-text-muted);
}
.post__time {
  margin-left: auto;
  font-size: var(--se-fs-2xs);
  color: var(--se-text-faint);
  white-space: nowrap;
}
.post__chip {
  margin-top: var(--se-sp-1);
}
.post__text {
  margin: var(--se-sp-3) 0 0;
  color: var(--se-text);
  font-size: var(--se-fs-md);
  line-height: 1.6;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}

/* ── Reaction bar ───────────────────────────────────────────── */
.post__reactions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--se-sp-2);
  margin-top: var(--se-sp-4);
  padding-top: var(--se-sp-3);
  border-top: 1px solid var(--se-border);
}
.reaction-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border: 1px solid transparent;
  border-radius: var(--se-r-pill);
  background: var(--se-sunken);
  color: var(--se-text-muted);
  font-size: var(--se-fs-xs);
  font-weight: 600;
  cursor: pointer;
  transition:
    transform var(--se-t-fast) var(--se-ease-std),
    border-color var(--se-t-fast) var(--se-ease-std),
    background var(--se-t-fast) var(--se-ease-std),
    color var(--se-t-fast) var(--se-ease-std);
}
.reaction-pill:hover {
  transform: translateY(-1px);
  border-color: var(--se-border-strong);
}
.reaction-pill.is-active {
  background: var(--se-navy-50);
  border-color: var(--se-navy-500);
  color: var(--se-ink);
}
.reaction-pill__emoji {
  font-size: var(--se-fs-sm);
  line-height: 1;
}
.reaction-pill.is-active .reaction-pill__emoji {
  animation: se-pop var(--se-t-slow) var(--se-ease-out);
}
@keyframes se-pop {
  0%   { transform: scale(1); }
  45%  { transform: scale(1.4); }
  100% { transform: scale(1); }
}
.post__ccount {
  margin-left: auto;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: var(--se-fs-xs);
  color: var(--se-text-faint);
}

/* ── Comment thread ─────────────────────────────────────────── */
.post__comments {
  margin: var(--se-sp-3) 0 0 var(--se-sp-5);
  padding-left: var(--se-sp-4);
  border-left: 2px solid var(--se-border);
  display: flex;
  flex-direction: column;
  gap: var(--se-sp-3);
}
.comment {
  display: flex;
  align-items: flex-start;
  gap: var(--se-sp-2);
}
.comment__bubble {
  background: var(--se-sunken);
  border-radius: var(--se-r-md);
  padding: var(--se-sp-2) var(--se-sp-3);
  min-width: 0;
}
.comment__meta {
  display: flex;
  align-items: baseline;
  gap: var(--se-sp-2);
  flex-wrap: wrap;
}
.comment__author {
  font-weight: 600;
  font-size: var(--se-fs-xs);
  color: var(--se-ink);
}
.comment__flat {
  font-size: var(--se-fs-2xs);
  color: var(--se-text-muted);
}
.comment__time {
  font-size: var(--se-fs-2xs);
  color: var(--se-text-faint);
}
.comment__text {
  margin: 2px 0 0;
  font-size: var(--se-fs-sm);
  color: var(--se-text);
  line-height: 1.5;
  overflow-wrap: anywhere;
}

/* ── Comment composer ───────────────────────────────────────── */
.comment-compose {
  display: flex;
  align-items: center;
  gap: var(--se-sp-2);
  margin-top: var(--se-sp-3);
}
.comment-compose__input {
  min-height: 38px;
  padding: 7px 14px;
  font-size: var(--se-fs-sm);
  border-radius: var(--se-r-pill);
}
.comment-compose__send {
  width: 38px;
  height: 38px;
  flex-shrink: 0;
  display: grid;
  place-items: center;
  border: none;
  border-radius: 50%;
  background: var(--se-ink);
  color: var(--se-surface);
  font-size: var(--se-fs-sm);
  cursor: pointer;
  transition:
    transform var(--se-t-fast) var(--se-ease-std),
    opacity var(--se-t-fast) var(--se-ease-std);
}
.comment-compose__send:hover:not(:disabled) {
  transform: translateY(-1px) scale(1.05);
}
.comment-compose__send:active:not(:disabled) {
  transform: scale(0.95);
}
.comment-compose__send:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

/* ── Empty state + feed motion ──────────────────────────────── */
.wall__empty {
  margin-top: var(--se-sp-4);
}
.wall__empty-cta {
  margin-top: var(--se-sp-4);
}
.feed-enter-active {
  transition:
    opacity var(--se-t-slow) var(--se-ease-out),
    transform var(--se-t-slow) var(--se-ease-out);
}
.feed-enter-from {
  opacity: 0;
  transform: translateY(-10px) scale(0.985);
}
.feed-move {
  transition: transform var(--se-t-slow) var(--se-ease-out);
}

/* ── Small screens ──────────────────────────────────────────── */
@media (max-width: 575.98px) {
  .post {
    padding: var(--se-sp-4);
  }
  .composer {
    padding: var(--se-sp-4) var(--se-sp-4) var(--se-sp-3);
  }
  .composer__post {
    width: 100%;
    justify-content: center;
  }
  .post__comments {
    margin-left: var(--se-sp-3);
    padding-left: var(--se-sp-3);
  }
}
</style>
