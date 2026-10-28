<script setup>
defineProps({ blok: { type: Object, required: true } });
const lang = useMtLang();
const name = useMtStoryName();
</script>

<template>
  <div v-editable="blok" class="mt-page mt-product">
    <ComponentCheck v-for="(b, i) in blok.hero" :key="b._uid" :blok="b" :index="i" />
    <div v-if="!blok.hero?.length && $route.query._storyblok" class="mt-wrap mt-w-standard mt-editor-empty">Ajoutez le Hero de la page produit.</div>
    <ComponentCheck v-for="(b, i) in blok.sections" :key="b._uid" :blok="b" :index="i + 1" />
    <ComponentCheck v-for="(b, i) in blok.cta" :key="b._uid" :blok="b" :index="99 + i" />
    <nav class="mt-crumbbar" aria-label="Fil d'Ariane">
      <div class="mt-wrap mt-w-standard mt-crumbs">
        <NuxtLink :to="lang ? `/${lang}` : '/'"><MtIcon name="home" :size="15" /> Accueil</NuxtLink><span aria-hidden="true">›</span><span aria-current="page">{{ name }}</span>
      </div>
    </nav>
  </div>
</template>
