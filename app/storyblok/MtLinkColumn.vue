<script setup>
defineProps({ blok: { type: Object, required: true } });
</script>

<template>
  <MtStandalone :blok="blok" />
</template>
