<script setup>
// Rich-text body copy. A plain string also renders.
const props = defineProps({ doc: { type: [Object, String], default: null } });
const isDoc = computed(() => props.doc && typeof props.doc === 'object' && props.doc.type === 'doc');
const hasText = computed(() => (isDoc.value ? JSON.stringify(props.doc.content || []).includes('"text"') : !!props.doc));
</script>

<template>
  <div v-if="hasText" class="mt-rich">
    <StoryblokRichText v-if="isDoc" :document="doc" />
    <p v-else>{{ doc }}</p>
  </div>
</template>
