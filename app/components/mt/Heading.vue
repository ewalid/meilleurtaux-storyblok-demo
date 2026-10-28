<script setup>
// Headline with optional orange words. Line breaks typed in the field are kept.
const props = defineProps({
  text: { type: String, default: '' },
  highlight: { type: String, default: '' },
  tag: { type: String, default: 'h2' },
  size: { type: String, default: 'm' },
  condensed: { type: Boolean, default: false },
});

const esc = s => s.replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', '\'': '&#39;' })[c]);

const html = computed(() => {
  let out = esc(props.text || '');
  const words = (props.highlight || '').split('|').map(w => w.trim()).filter(Boolean);
  for (const w of words) {
    const re = new RegExp(esc(w).replace(/[.*+?^${}()[\]\\]/g, '\\$&'), 'i');
    out = out.replace(re, m => `<span class="mt-h__hl">${m}</span>`);
  }
  return out.replace(/\n/g, '<br>');
});
</script>

<template>
  <!-- eslint-disable vue/no-v-text-v-html-on-component -->
  <component
    :is="tag"
    v-if="text"
    class="mt-h"
    :class="[`mt-h--${size}`, { 'mt-h--condensed': condensed }]"
    v-html="html"
  />
</template>
