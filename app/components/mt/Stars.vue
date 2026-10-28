<script setup>
defineProps({ rating: { type: [Number, String], default: 5 } });
</script>

<template>
  <span class="mt-stars" :aria-label="`${rating} étoiles sur 5`" role="img">
    <span v-for="i in 5" :key="i" class="mt-stars__s" :class="{ 'is-off': i > Number(rating) }">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m12 3.5 2.6 5.5 6 .8-4.4 4.2 1.1 6L12 17.1 6.7 20l1.1-6-4.4-4.2 6-.8L12 3.5Z" fill="#fff" /></svg>
    </span>
  </span>
</template>
