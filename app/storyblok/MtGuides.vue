<script setup>
defineProps({ blok: { type: Object, required: true } });
const lang = useMtLang();
const href = l => mtHref(l, lang.value);
</script>

<template>
  <MtSection :blok="blok" :defaults="{ background: 'cream' }" class="mt-guides">
    <div class="mt-sec-head"><MtHeading :text="blok.title" :size="blok.title_size || 'm'" class="mt-sec-title" /></div>
    <div class="mt-guides__box" :class="{ 'is-card': blok.card !== false }">
      <div v-for="col in blok.columns" :key="col._uid" v-editable="col" class="mt-guides__col">
        <div class="mt-guides__head">
          <img v-if="col.icon?.filename" :src="col.icon.filename" alt="" />
          <NuxtLink v-if="href(col.link)" :to="href(col.link)" class="mt-guides__title">{{ col.title }}</NuxtLink>
          <p v-else class="mt-guides__title">{{ col.title }}</p>
        </div>
        <ul>
          <li v-for="l in col.links" :key="l._uid" v-editable="l"><NuxtLink :to="href(l.link) || '/'">{{ l.label }}</NuxtLink></li>
        </ul>
      </div>
    </div>
  </MtSection>
</template>
