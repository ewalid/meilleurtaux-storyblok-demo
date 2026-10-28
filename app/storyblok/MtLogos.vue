<script setup>
const props = defineProps({ blok: { type: Object, required: true } });
const logos = computed(() => (props.blok.logos || []).filter(l => l?.filename));
const marquee = computed(() => (props.blok.layout || 'marquee') === 'marquee' && logos.value.length > 3);
</script>

<template>
  <MtSection :blok="blok" :defaults="{ align: 'center' }" class="mt-logos">
    <div class="mt-sec-head">
      <MtHeading :text="blok.title" :size="blok.title_size || 's'" class="mt-sec-title" />
      <MtRich :doc="blok.intro" class="mt-lead" />
    </div>
    <div v-if="marquee" class="mt-marquee mt-bleed" :class="{ 'is-gray': blok.grayscale }">
      <div class="mt-marquee__track">
        <img v-for="(l, i) in [...logos, ...logos]" :key="`${l.id}-${i}`" :src="l.filename" :alt="i < logos.length ? (l.alt || '') : ''" :aria-hidden="i >= logos.length" loading="lazy" />
      </div>
    </div>
    <div v-if="!marquee" class="mt-logo-grid" :class="{ 'is-gray': blok.grayscale }">
      <img v-for="l in logos" :key="l.id" :src="l.filename" :alt="l.alt || ''" loading="lazy" />
    </div>
    <div v-if="$route.query._storyblok && !logos.length" class="mt-empty">Ajoutez des logos dans le champ « Logos »</div>
    <MtButtons :buttons="blok.buttons" :stack="false" class="mt-sec-foot" />
  </MtSection>
</template>
