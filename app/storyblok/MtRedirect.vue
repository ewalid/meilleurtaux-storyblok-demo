<script setup>
// Editor view of a redirect story. Visitors never land here: the redirects
// middleware sends the old address straight to the new page.
const props = defineProps({ blok: { type: Object, required: true } });
const lang = useMtLang();
const to = computed(() => mtHref(props.blok.to, lang.value));
</script>

<template>
  <section v-editable="blok" class="mt-section mt-theme-cream mt-pt-l mt-pb-l">
    <div class="mt-wrap mt-w-narrow mt-redirect">
      <p class="mt-eyebrow">Redirection {{ blok.type || '301' }}</p>
      <p class="mt-redirect__row">
        <code>{{ blok.from_path || '/ancienne-adresse' }}</code>
        <MtIcon name="arrow" :size="22" />
        <code>{{ to || 'Choisissez la nouvelle page' }}</code>
      </p>
      <p v-if="blok.note" class="mt-lead">{{ blok.note }}</p>
      <p class="mt-small">Les visiteurs de l'ancienne adresse arrivent directement sur la nouvelle page.</p>
    </div>
  </section>
</template>
