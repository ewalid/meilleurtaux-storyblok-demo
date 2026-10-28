<script setup>
defineProps({ blok: { type: Object, required: true } });
</script>

<template>
  <MtSection :blok="blok" :defaults="{ align: 'center' }" class="mt-trust">
    <MtHeading :text="blok.headline" :highlight="blok.highlight" :size="blok.title_size || 'm'" class="mt-trust__title" />
    <div v-if="blok.features?.length" class="mt-trust__grid">
      <div v-for="f in blok.features" :key="f._uid" v-editable="f" class="mt-trust__item">
        <MtIcon :name="f.icon || 'screen'" :size="38" />
        <p class="mt-trust__name">{{ f.title }}</p>
        <p class="mt-trust__text">{{ f.text }}</p>
      </div>
    </div>
    <MtTrustpilot v-if="blok.trust !== false" variant="stacked" class="mt-trust__tp" />
  </MtSection>
</template>
