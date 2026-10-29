<script setup>
const props = defineProps({ blok: { type: Object, required: true } });
const toc = useMtToc();
const t = useMtT();
const open = ref(!props.blok.collapsed);
onMounted(() => {
  if (window.innerWidth >= 768) {
    open.value = true;
  }
});
</script>

<template>
  <MtSection :blok="blok" :defaults="{ background: 'cream', width: 'wide', space_top: 's', space_bottom: 's' }" tag="nav" class="mt-toc" :aria-label="t('toc')">
    <div class="mt-toc__row">
      <p class="mt-toc__title">{{ blok.title || t('toc') }}</p>
      <ul v-show="open" class="mt-toc__list">
        <li v-for="item in toc" :key="item.id"><a :href="`#${item.id}`">{{ item.label }} <MtIcon name="right" :size="14" /></a></li>
      </ul>
      <p v-if="!toc.length && $route.query._storyblok" class="mt-empty">Donnez un « Nom d'ancre » aux sections (onglet Visibilité) : elles apparaîtront ici.</p>
      <button type="button" class="mt-round" :aria-expanded="open" :aria-label="t('showToc')" @click="open = !open"><MtIcon name="chevron" :size="18" :class="{ 'is-flip': open }" /></button>
    </div>
  </MtSection>
</template>
