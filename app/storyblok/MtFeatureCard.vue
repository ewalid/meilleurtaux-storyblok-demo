<script setup>
const props = defineProps({ blok: { type: Object, required: true } });
const layout = computed(() => props.blok.layout || 'image_left');
const hasMedia = computed(() => !['text', 'rating', 'quote'].includes(layout.value));
</script>

<template>
  <MtSection :blok="blok" class="mt-fcard-section">
    <div class="mt-fcard-row" :class="`is-${layout}`">
      <figure v-if="layout === 'quote'" class="mt-quote" :class="`mt-card-${blok.card_color || 'cream'}`">
        <span class="mt-quote__mark" aria-hidden="true">“</span>
        <div class="mt-quote__body">
          <MtHeading :text="blok.title" :highlight="blok.highlight" :size="blok.title_size || 's'" tag="h2" class="mt-h--accent" />
          <blockquote><MtRich :doc="blok.text" /></blockquote>
          <figcaption>
            <span class="mt-quote__avatar"><MtMedia v-if="blok.media?.filename" :asset="blok.media" cover :width="200" /></span>
            <span><strong>{{ blok.quote_name }}</strong><template v-if="blok.quote_role"> • {{ blok.quote_role }}</template></span>
          </figcaption>
          <MtButtons :buttons="blok.buttons" :stack="false" />
        </div>
        <span class="mt-quote__mark mt-quote__mark--end" aria-hidden="true">”</span>
      </figure>
      <div v-else class="mt-fcard" :class="[`mt-fcard--${layout}`, `mt-card-${blok.card_color || 'cream'}`]">
        <div v-if="hasMedia" class="mt-fcard__media">
          <MtMedia v-if="blok.media?.filename" :asset="blok.media" cover :width="1000" />
          <div v-else-if="$route.query._storyblok" class="mt-empty">Ajoutez une image</div>
        </div>
        <div class="mt-fcard__body">
          <p v-if="blok.eyebrow" class="mt-eyebrow">{{ blok.eyebrow }}</p>
          <div class="mt-fcard__titlerow">
            <img v-if="blok.icon?.filename" :src="blok.icon.filename" alt="" class="mt-fcard__icon" />
            <MtHeading :text="blok.title" :highlight="blok.highlight" :size="blok.title_size || 'm'" tag="h2" :class="{ 'mt-h--accent': layout === 'rating' }" />
          </div>
          <MtRich :doc="blok.text" class="mt-fcard__text" />
          <MtButtons :buttons="blok.buttons" :stack="false" />
        </div>
      </div>
      <div v-if="layout === 'rating'" class="mt-fcard-aside">
        <MtTrustpilot variant="card" />
      </div>
    </div>
  </MtSection>
</template>
