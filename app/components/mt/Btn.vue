<script setup>
// One Meilleurtaux button (from a mt-button block).
const props = defineProps({ button: { type: Object, required: true } });
const lang = useMtLang();
const href = computed(() => mtHref(props.button.link, lang.value));
const external = computed(() => mtIsExternal(props.button.link) || props.button.new_tab);
const style = computed(() => props.button.style || 'primary');
const NuxtLink = resolveComponent('NuxtLink');
</script>

<template>
  <component
    :is="href && !external ? NuxtLink : 'a'"
    v-if="button.label"
    v-editable="button"
    :to="href && !external ? href : undefined"
    :href="external ? href : (href ? undefined : null)"
    :target="external ? '_blank' : undefined"
    :rel="external ? 'noopener' : undefined"
    class="mt-btn"
    :class="`mt-btn--${style}`"
  >
    {{ button.label }}
    <span v-if="style === 'link' || button.arrow" class="mt-btn__arrow" aria-hidden="true">→</span>
  </component>
</template>
