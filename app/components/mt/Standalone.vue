<script setup>
// An item (card, button, review...) placed directly in a page, outside its usual section.
const props = defineProps({ blok: { type: Object, required: true } });
const c = computed(() => props.blok.component);
</script>

<template>
  <div v-editable="blok" class="mt-standalone mt-wrap mt-w-standard">
    <MtBtn v-if="c === 'mt-button'" :button="blok" />
    <div v-else-if="c === 'mt-review'" class="mt-review"><blockquote>{{ blok.text }}</blockquote><MtStars :rating="blok.rating || 5" /> <strong>{{ blok.name }}</strong></div>
    <div v-else-if="c === 'mt-faq-item'" class="mt-acc__item is-open"><p class="mt-acc__q">{{ blok.question }}</p><div class="mt-acc__a"><MtRich :doc="blok.answer" /></div></div>
    <div v-else class="mt-gcard mt-gcard--photo">
      <div v-if="blok.image?.filename || blok.icon?.filename" class="mt-gcard__photo"><MtMedia :asset="blok.image || blok.icon" :width="800" /></div>
      <div class="mt-gcard__body">
        <h3 class="mt-gcard__title">{{ blok.title || blok.label || blok.name || blok.question }}</h3>
        <MtRich :doc="blok.text" />
      </div>
    </div>
  </div>
</template>
