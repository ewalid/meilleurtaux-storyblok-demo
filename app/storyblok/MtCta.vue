<script setup>
const props = defineProps({ blok: { type: Object, required: true } });
const layout = computed(() => props.blok.layout || 'band');
</script>

<template>
  <MtSection :blok="blok" :defaults="{ background: 'terracotta', align: 'center' }" class="mt-cta" :class="`mt-cta--${layout}`">
    <div class="mt-cta__grid">
      <div v-if="layout === 'pill'" class="mt-cta__pill">
        <MtHeading :text="blok.title" :highlight="blok.highlight" size="s" tag="p" />
        <MtButtons :buttons="blok.buttons" :stack="false" />
      </div>
      <div v-else class="mt-cta__copy">
        <p v-if="blok.eyebrow" class="mt-eyebrow">{{ blok.eyebrow }}</p>
        <MtHeading :text="blok.title" :highlight="blok.highlight" :size="blok.title_size || 'm'" />
        <MtRich :doc="blok.text" class="mt-lead" />
        <MtButtons :buttons="blok.buttons" :stack="false" />
      </div>
      <div v-if="layout === 'split'" class="mt-cta__media"><MtMedia v-if="blok.media?.filename" :asset="blok.media" cover :width="900" /></div>
    </div>
  </MtSection>
</template>
