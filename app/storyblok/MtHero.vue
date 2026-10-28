<script setup>
const props = defineProps({ blok: { type: Object, required: true } });
const layout = computed(() => props.blok.layout || 'split');
const lang = useMtLang();
const href = l => mtHref(l, lang.value);
const { rate, updatedLabel } = useMtRates();
const NuxtLink = resolveComponent('NuxtLink');
const tag = l => (href(l) ? NuxtLink : 'div');
const sizeClass = computed(() => `mt-h--${props.blok.title_size || 'l'}`);
</script>

<template>
  <MtSection
    :blok="blok"
    :defaults="{ background: 'cream' }"
    class="mt-hero"
    :class="`mt-hero--${layout}`"
    :force-theme="layout === 'background' && blok.media?.filename ? 'image' : null"
  >
    <template #full>
      <div v-if="layout === 'background' && blok.media?.filename" class="mt-section__bg">
        <MtMedia :asset="blok.media" cover eager :width="2000" />
        <div class="mt-section__overlay"></div>
      </div>
      <div v-if="layout === 'split'" class="mt-hero__glow" aria-hidden="true"></div>
    </template>

    <!-- Home: headline + product tiles + offer -->
    <template v-if="layout === 'products'">
      <MtHeading :text="blok.headline" :highlight="blok.highlight" tag="h1" size="hero-light" />
      <div class="mt-hero-p" :class="{ 'has-promo': blok.promo?.length }">
        <div class="mt-tiles">
          <component
            :is="tag(t.link)"
            v-for="t in blok.tiles"
            :key="t._uid"
            v-editable="t"
            :to="href(t.link) || undefined"
            class="mt-tile"
            :class="`mt-tile--${t.size || 'normal'}`"
          >
            <span v-if="t.badge" class="mt-tile__badge">{{ t.badge }}</span>
            <span class="mt-tile__head">
              <img v-if="t.icon?.filename" :src="t.icon.filename" alt="" class="mt-tile__icon" />
              <span class="mt-tile__label">{{ t.label }}</span>
            </span>
            <span v-if="t.show_rate" class="mt-tile__rate">
              <strong>{{ mtFormat(rate(t.rate_duration || '15'), 2) }} %</strong>
              <span>Taux moyen{{ updatedLabel ? ` au ${updatedLabel}` : '' }} sur {{ t.rate_duration || 15 }} ans</span>
            </span>
          </component>
        </div>
        <template v-for="p in blok.promo" :key="p._uid">
          <div v-editable="p" class="mt-promo">
            <MtMedia v-if="p.image?.filename" :asset="p.image" cover :width="900" class="mt-promo__bg" />
            <span v-if="p.tag" class="mt-promo__tag">{{ p.tag }}</span>
            <div class="mt-promo__box">
              <p v-if="p.eyebrow" class="mt-promo__eyebrow">{{ p.eyebrow }}</p>
              <p v-if="p.title" class="mt-promo__title">{{ p.title }}</p>
              <MtRich :doc="p.text" class="mt-promo__text" />
            </div>
            <div class="mt-promo__foot">
              <MtBtn v-for="b in p.button" :key="b._uid" :button="b" />
              <MtRich :doc="p.small_print" class="mt-promo__small" />
            </div>
          </div>
        </template>
      </div>
    </template>

    <!-- Product page / campaign hero -->
    <div v-else class="mt-hero__grid">
      <div class="mt-hero__copy">
        <span v-if="blok.label" class="mt-chip"><MtIcon name="home" :size="15" /> {{ blok.label }}</span>
        <MtHeading :text="blok.headline" :highlight="blok.highlight" tag="h1" :size="(blok.title_size || 'l')" :class="sizeClass" />
        <MtRich :doc="blok.intro" class="mt-hero__intro mt-rich--accent" />
        <p v-if="blok.choices?.length && blok.choices_label" class="mt-hero__ask">{{ blok.choices_label }}</p>
        <div v-if="blok.choices?.length" class="mt-choices">
          <component :is="href(c.link) ? NuxtLink : 'button'" v-for="c in blok.choices" :key="c._uid" v-editable="c" :to="href(c.link) || undefined" class="mt-choice">
            <MtIcon :name="c.icon || 'person'" :size="28" />
            <span>{{ c.label }}</span>
          </component>
        </div>
        <MtButtons :buttons="blok.buttons" :stack="false" />
        <MtTrustpilot v-if="blok.trust" class="mt-hero__tp" />
      </div>
      <div v-if="layout === 'split'" class="mt-hero__media">
        <MtMedia v-if="blok.media?.filename" :asset="blok.media" cover eager :width="1100" />
        <div v-else-if="$route.query._storyblok" class="mt-empty">Ajoutez une photo dans le champ « Photo ou vidéo »</div>
      </div>
    </div>
  </MtSection>
</template>
