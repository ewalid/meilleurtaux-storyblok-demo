<script setup>
defineProps({ buttons: { type: Array, default: () => [] }, stack: { type: Boolean, default: true } });
</script>

<template>
  <div v-if="buttons?.length" class="mt-actions" :class="{ 'mt-actions--stack': stack }">
    <MtBtn v-for="b in buttons" :key="b._uid" :button="b" />
  </div>
</template>
