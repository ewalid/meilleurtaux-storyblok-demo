<script setup>
const props = defineProps({ blok: { type: Object, required: true } });
const layout = computed(() => props.blok.layout || 'stories');
const lang = useMtLang();
const href = l => mtHref(l, lang.value);
const NuxtLink = resolveComponent('NuxtLink');
</script>

<template>
  <MtSection :blok="blok" class="mt-carousel" :class="`mt-carousel--${layout}`">
    <div class="mt-sec-head">
      <MtHeading :text="blok.title" :size="blok.title_size || 'm'" class="mt-sec-title" />
      <MtRich :doc="blok.intro" class="mt-lead" />
    </div>
    <MtScroller :label="blok.title || 'Carrousel'">
      <component :is="href(c.link) ? NuxtLink : 'article'" v-for="c in blok.cards" :key="c._uid" v-editable="c" :to="href(c.link) || undefined" class="mt-ccard" :class="`mt-ccard--${layout}`">
        <div class="mt-ccard__img">
          <MtMedia v-if="c.image?.filename" :asset="c.image" cover :width="700" />
          <span v-if="layout === 'stories' && c.tag" class="mt-ccard__tag">{{ c.tag }}</span>
        </div>
        <div class="mt-ccard__body">
          <p v-if="layout !== 'stories' && c.tag" class="mt-ccard__eyebrow">{{ c.tag }}</p>
          <h3 v-if="c.title" class="mt-ccard__title">{{ c.title }}</h3>
          <p v-if="c.quote" class="mt-ccard__quote">“{{ c.quote.replace(/^[«“"\s]+|[»”"\s]+$/g, '') }}”</p>
          <MtRich :doc="c.text" class="mt-ccard__text" />
          <span v-if="c.link_label" class="mt-ccard__more">{{ c.link_label }} <MtIcon name="arrow" :size="16" /></span>
        </div>
      </component>
    </MtScroller>
    <MtButtons :buttons="blok.buttons" :stack="false" class="mt-sec-foot mt-sec-foot--center" />
  </MtSection>
</template>
