<script setup>
defineProps({ blok: { type: Object, required: true } });
</script>

<template>
  <MtSection :blok="blok" :defaults="{ background: 'cream', space_top: 's', space_bottom: 's' }" class="mt-alert" :class="`mt-alert--${blok.tone || 'warning'}`">
    <div class="mt-alert__box" :role="blok.tone === 'warning' ? 'note' : undefined">
      <p v-if="blok.title" class="mt-alert__title">
        <MtIcon v-if="blok.tone !== 'legal'" :name="blok.tone === 'info' ? 'info' : 'warning'" :size="22" />
        {{ blok.title }}
      </p>
      <MtRich :doc="blok.text" class="mt-alert__text" />
    </div>
  </MtSection>
</template>
