<script setup>
// "Taux du marché": an official indicator read live from the ECB public API through
// our server route /api/market/<id> (cached 1 h). Storyblok holds the editorial part:
// which indicator, wording, period, display, expert comment.
const props = defineProps({ blok: { type: Object, required: true } });
const lang = useMtLang();
const t = useMtT();
const indicator = computed(() => props.blok.indicator || 'credit-immo-fr');
const months = computed(() => Number(props.blok.months || 12));
const display = computed(() => props.blok.display || 'chart');

const data = ref(null);
const failed = ref(false);
async function load() {
  failed.value = false;
  try {
    data.value = await $fetch(`/api/market/${indicator.value}`, { query: { n: months.value } });
  }
  catch {
    data.value = null;
    failed.value = true;
  }
}
onMounted(load);
watch([indicator, months], load);

const monthLabel = (period, long = true) => {
  const d = new Date(`${period}-01T12:00:00`);
  return Number.isNaN(d.getTime()) ? period : d.toLocaleDateString(mtLocale(lang.value), long ? { month: 'long', year: 'numeric' } : { month: 'short', year: '2-digit' });
};
const change = computed(() => (data.value?.previous ? data.value.latest.value - data.value.previous.value : null));
const trend = computed(() => (change.value === null || Math.abs(change.value) < 0.005 ? 'stable' : change.value > 0 ? 'up' : 'down'));

// Sparkline geometry (viewBox 600 × 180).
const W = 600;
const H = 180;
const PAD = 16;
const chart = computed(() => {
  const pts = data.value?.points || [];
  if (pts.length < 2) {
    return null;
  }
  const vals = pts.map(p => p.value);
  const min = Math.min(...vals);
  const max = Math.max(...vals);
  const span = max - min || 1;
  const xy = pts.map((p, i) => [PAD + (i * (W - 2 * PAD)) / (pts.length - 1), PAD + (1 - (p.value - min) / span) * (H - 2 * PAD)]);
  const line = xy.map(([x, y], i) => `${i ? 'L' : 'M'}${x.toFixed(1)},${y.toFixed(1)}`).join(' ');
  const area = `${line} L${xy.at(-1)[0].toFixed(1)},${H} L${xy[0][0].toFixed(1)},${H} Z`;
  return { line, area, last: xy.at(-1), min, max, first: pts[0].period, end: pts.at(-1).period };
});
</script>

<template>
  <MtSection :blok="blok" class="mt-market" :class="`mt-market--${display}`">
    <div class="mt-sec-head">
      <p v-if="blok.eyebrow" class="mt-eyebrow">{{ blok.eyebrow }}</p>
      <MtHeading :text="blok.title" :highlight="blok.highlight" :size="blok.title_size || 'm'" class="mt-sec-title" />
      <MtRich :doc="blok.intro" class="mt-lead" />
    </div>
    <div class="mt-market__grid">
      <div class="mt-market__card" aria-live="polite">
        <p class="mt-market__name">{{ t(`mkt_${indicator}`) }}</p>
        <template v-if="data">
          <p class="mt-market__value">{{ mtFormat(data.latest.value, 2) }} <small>%</small></p>
          <p class="mt-market__change" :class="`is-${trend}`">
            <MtIcon v-if="trend !== 'stable'" :name="trend" :size="18" />
            {{ change === null ? '' : t('mktVsPrev', { d: `${change > 0 ? '+' : ''}${mtFormat(change, 2)}` }) }}
          </p>
          <p class="mt-market__period">{{ t('mktLatest', { p: monthLabel(data.latest.period) }) }}</p>
        </template>
        <p v-else-if="failed" class="mt-market__state">{{ t('mktUnavailable') }}</p>
        <p v-else class="mt-market__state mt-market__state--loading">{{ t('mktLoading') }}</p>
        <MtButtons :buttons="blok.buttons" :stack="false" />
      </div>
      <div v-if="display === 'chart'" class="mt-market__chart">
        <svg v-if="chart" :viewBox="`0 0 ${W} ${H}`" preserveAspectRatio="none" role="img" :aria-label="`${t(`mkt_${indicator}`)} : ${monthLabel(chart.first)} → ${monthLabel(chart.end)}`">
          <defs>
            <linearGradient :id="`mkt-${blok._uid}`" x1="0" x2="0" y1="0" y2="1">
              <stop offset="0" stop-color="#c0543a" stop-opacity="0.22" />
              <stop offset="1" stop-color="#c0543a" stop-opacity="0" />
            </linearGradient>
          </defs>
          <path :d="chart.area" :fill="`url(#mkt-${blok._uid})`" />
          <path :d="chart.line" fill="none" stroke="#c0543a" stroke-width="3" stroke-linejoin="round" stroke-linecap="round" vector-effect="non-scaling-stroke" />
          <circle :cx="chart.last[0]" :cy="chart.last[1]" r="6" fill="#fff" stroke="#c0543a" stroke-width="3" />
        </svg>
        <div v-if="chart" class="mt-market__axis">
          <span>{{ monthLabel(chart.first, false) }}</span>
          <span>{{ mtFormat(chart.min, 2) }} % – {{ mtFormat(chart.max, 2) }} %</span>
          <span>{{ monthLabel(chart.end, false) }}</span>
        </div>
        <div v-else class="mt-market__skeleton" aria-hidden="true"></div>
      </div>
      <MtRich v-if="blok.comment" :doc="blok.comment" class="mt-market__comment" />
    </div>
    <p class="mt-market__source">{{ t('mktSource', { s: data?.source || 'BCE (Banque centrale européenne)' }) }}</p>
  </MtSection>
</template>
