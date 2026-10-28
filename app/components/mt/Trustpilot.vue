<script setup>
// Trustpilot score from the site settings: stars + "(4,8 / 5 - 26 253 avis)".
const props = defineProps({
  variant: { type: String, default: 'inline' }, // inline | stacked | card | dark
  stars: { type: Number, default: 5 },
});
const site = useMtSite();
const score = computed(() => site.value.tp_score || '4,8');
const count = computed(() => site.value.tp_count || '26 253');
const label = computed(() => site.value.tp_label || 'Excellent');
const href = computed(() => mtHref(site.value.tp_link));
</script>

<template>
  <component
    :is="href ? 'a' : 'div'"
    class="mt-tp"
    :class="`mt-tp--${variant}`"
    :href="href || undefined"
    :target="href ? '_blank' : undefined"
    :rel="href ? 'noopener' : undefined"
  >
    <template v-if="variant === 'card'">
      <span class="mt-tp__big">{{ score }}<small>/5</small></span>
      <span class="mt-tp__sub">sur {{ count }} avis</span>
      <span class="mt-tp__label">{{ label }}</span>
      <MtStars :rating="props.stars" />
      <span class="mt-tp__brand"><MtTrustpilotMark /> Trustpilot</span>
      <span v-if="href" class="mt-tp__link">Voir les avis</span>
    </template>
    <template v-else>
      <span class="mt-tp__row"><span class="mt-tp__brand"><MtTrustpilotMark /> Trustpilot</span><MtStars :rating="props.stars" /></span>
      <span class="mt-tp__meta">({{ score }} / 5 - {{ count }} avis)</span>
    </template>
  </component>
</template>
