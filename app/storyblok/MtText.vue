<script setup>
defineProps({ blok: { type: Object, required: true } });
</script>

<template>
  <MtSection :blok="blok" :defaults="{ width: 'narrow' }" class="mt-textsec">
    <p v-if="blok.eyebrow" class="mt-eyebrow">{{ blok.eyebrow }}</p>
    <MtHeading :text="blok.title" :highlight="blok.highlight" :size="blok.title_size || 'm'" class="mt-sec-title" />
    <MtRich :doc="blok.body" class="mt-prose" />
    <MtButtons :buttons="blok.buttons" :stack="false" class="mt-sec-foot" />
  </MtSection>
</template>
