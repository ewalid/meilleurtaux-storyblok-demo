<script setup>
// Reviews band as on meilleurtaux.com: a dark panel pinned on the left, and the
// review cards scrolling continuously from right to left, passing under the panel.
// Pauses on hover/focus; static (swipeable) when the visitor prefers reduced motion.
const props = defineProps({ blok: { type: Object, required: true } });
const lang = useMtLang();
const t = useMtT();
const reviews = computed(() => props.blok.reviews || []);
// The list is rendered twice so the loop is seamless; ~7 s per card keeps it readable.
const duration = computed(() => `${Math.max(20, reviews.value.length * 7)}s`);
</script>

<template>
  <MtSection :blok="blok" :defaults="{ width: 'full' }" class="mt-reviews">
    <div class="mt-reviews__band">
      <div class="mt-reviews__panel">
        <div class="mt-reviews__panel-inner">
          <MtHeading :text="blok.title" :size="blok.title_size || 'm'" />
          <MtRich :doc="blok.text" />
          <MtTrustpilot variant="dark" />
          <NuxtLink v-if="blok.link_label" :to="mtHref(blok.link, lang) || '/'" class="mt-reviews__link"><MtIcon name="info" :size="16" /> {{ blok.link_label }}</NuxtLink>
        </div>
      </div>
      <div class="mt-reviews__viewport" role="region" :aria-label="blok.title || t('reviews')" tabindex="0">
        <div v-if="reviews.length" class="mt-reviews__track" :style="{ '--mt-reviews-duration': duration }">
          <template v-for="pass in 2" :key="pass">
            <figure
              v-for="r in reviews"
              :key="`${pass}-${r._uid}`"
              v-editable="pass === 1 ? r : undefined"
              class="mt-review"
              :aria-hidden="pass === 2 ? 'true' : undefined"
            >
              <span class="mt-review__mark" aria-hidden="true">“</span>
              <blockquote>{{ r.text }}</blockquote>
              <figcaption>
                <span class="mt-review__who"><MtStars :rating="r.rating || 5" /> <span class="mt-review__name">{{ r.name }}</span></span>
                <span class="mt-review__date">{{ r.date }}<template v-if="r.experience"> - {{ t('experience', { d: r.experience }) }}</template></span>
              </figcaption>
            </figure>
          </template>
        </div>
      </div>
    </div>
  </MtSection>
</template>
