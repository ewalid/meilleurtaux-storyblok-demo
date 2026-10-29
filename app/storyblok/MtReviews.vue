<script setup>
defineProps({ blok: { type: Object, required: true } });
const lang = useMtLang();
const t = useMtT();
</script>

<template>
  <MtSection :blok="blok" :defaults="{ width: 'full' }" class="mt-reviews">
    <div class="mt-reviews__grid">
      <div class="mt-reviews__panel">
        <MtHeading :text="blok.title" :size="blok.title_size || 'm'" />
        <MtRich :doc="blok.text" />
        <MtTrustpilot variant="dark" />
        <NuxtLink v-if="blok.link_label" :to="mtHref(blok.link, lang) || '/'" class="mt-reviews__link"><MtIcon name="info" :size="16" /> {{ blok.link_label }}</NuxtLink>
      </div>
      <MtScroller label="Avis clients" class="mt-reviews__track">
        <figure v-for="r in blok.reviews" :key="r._uid" v-editable="r" class="mt-review">
          <blockquote>{{ r.text }}</blockquote>
          <figcaption>
            <MtStars :rating="r.rating || 5" />
            <span class="mt-review__name">{{ r.name }}</span>
            <span class="mt-review__date">{{ r.date }}<template v-if="r.experience"> · {{ t('experience', { d: r.experience }) }}</template></span>
          </figcaption>
        </figure>
      </MtScroller>
    </div>
  </MtSection>
</template>
