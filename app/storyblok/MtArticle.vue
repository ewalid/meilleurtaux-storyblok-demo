<script setup>
const props = defineProps({ blok: { type: Object, required: true } });
const lang = useMtLang();
const t = useMtT();
const base = computed(() => (lang.value ? `/${lang.value}` : ''));
useHead({ script: [{ type: 'application/ld+json', children: JSON.stringify({
  '@context': 'https://schema.org',
  '@type': 'NewsArticle',
  'headline': props.blok.title,
  'datePublished': props.blok.date,
  'image': props.blok.image?.filename,
  'author': props.blok.author ? { '@type': 'Person', 'name': props.blok.author } : undefined,
  'publisher': { '@type': 'Organization', 'name': 'Meilleurtaux' },
}) }] });
</script>

<template>
  <article v-editable="blok" class="mt-article">
    <header class="mt-article__head mt-theme-cream">
      <div class="mt-wrap mt-w-narrow">
        <nav class="mt-crumbs" :aria-label="t('breadcrumb')">
          <NuxtLink :to="base || '/'">{{ t('home') }}</NuxtLink><span aria-hidden="true">›</span>
          <NuxtLink :to="`${base}/actualites`">{{ t('news') }}</NuxtLink><span aria-hidden="true">›</span>
          <span>{{ blok.category ? t.category(blok.category) : t('news') }}</span>
        </nav>
        <span class="mt-chip mt-chip--s">{{ blok.category ? t.category(blok.category) : t('news') }}</span>
        <h1 class="mt-h mt-h--l">{{ blok.title }}</h1>
        <p v-if="blok.excerpt" class="mt-article__lead">{{ blok.excerpt }}</p>
        <p class="mt-article__meta">
          <span v-if="blok.date">{{ t('publishedOn', { d: mtDate(blok.date, true) }) }}</span>
          <span v-if="blok.author"> · {{ t('by') }} <strong>{{ blok.author }}</strong><template v-if="blok.author_role">, {{ blok.author_role }}</template></span>
          <span v-if="blok.reading_time"> · {{ t('readingTime', { t: blok.reading_time }) }}</span>
        </p>
      </div>
    </header>
    <div class="mt-wrap mt-w-narrow mt-article__img"><MtMedia v-if="blok.image?.filename" :asset="blok.image" cover eager :width="1400" /></div>
    <div class="mt-wrap mt-w-narrow mt-article__body">
      <MtRich :doc="blok.body" class="mt-prose" />
    </div>
    <ComponentCheck v-for="(b, i) in blok.after" :key="b._uid" :blok="b" :index="i" />
  </article>
</template>
