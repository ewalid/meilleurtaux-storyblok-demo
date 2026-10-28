<script setup>
defineProps({ blok: { type: Object, required: true } });
</script>

<template>
  <div v-editable="blok"></div>
</template>
