<script setup>
// Horizontal scroll-snap track with round arrow buttons (carousels, reviews).
defineProps({ arrows: { type: Boolean, default: true }, label: { type: String, default: 'Carrousel' } });
const t = useMtT();
const track = ref(null);
const atStart = ref(true);
const atEnd = ref(false);
function update() {
  const el = track.value;
  if (!el) {
    return;
  }
  atStart.value = el.scrollLeft < 8;
  atEnd.value = el.scrollLeft + el.clientWidth > el.scrollWidth - 8;
}
function go(dir) {
  const el = track.value;
  if (!el) {
    return;
  }
  const card = el.firstElementChild;
  const step = card ? card.getBoundingClientRect().width + 24 : el.clientWidth * 0.8;
  el.scrollBy({ left: dir * step, behavior: 'smooth' });
}
onMounted(() => {
  update();
  window.addEventListener('resize', update);
});
onBeforeUnmount(() => window.removeEventListener('resize', update));
</script>

<template>
  <div class="mt-scroller">
    <div ref="track" class="mt-scroller__track" role="region" :aria-label="label" tabindex="0" @scroll.passive="update">
      <slot></slot>
    </div>
    <div v-if="arrows" class="mt-scroller__nav">
      <button type="button" class="mt-round" :disabled="atStart" :aria-label="t('previous')" @click="go(-1)"><MtIcon name="left" :size="18" /></button>
      <button type="button" class="mt-round" :disabled="atEnd" :aria-label="t('next')" @click="go(1)"><MtIcon name="right" :size="18" /></button>
    </div>
  </div>
</template>
