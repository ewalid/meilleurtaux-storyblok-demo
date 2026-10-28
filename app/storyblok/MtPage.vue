<script setup>
defineProps({ blok: { type: Object, required: true } });
</script>

<template>
  <div v-editable="blok" class="mt-page">
    <ComponentCheck v-for="(b, i) in blok.body" :key="b._uid" :blok="b" :index="i" />
    <div v-if="!blok.body?.length && $route.query._storyblok" class="mt-wrap mt-w-standard mt-editor-empty">
      Cette page est vide. Cliquez sur « + » dans le champ Sections pour ajouter une section.
    </div>
  </div>
</template>
