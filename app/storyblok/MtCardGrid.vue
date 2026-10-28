<script setup>
const props = defineProps({ blok: { type: Object, required: true } });
const layout = computed(() => props.blok.layout || 'icon');
const lang = useMtLang();
const href = l => mtHref(l, lang.value);
const STEP_ICONS = ['pen', 'doc', 'euro', 'thumb', 'key', 'home'];
const NuxtLink = resolveComponent('NuxtLink');
</script>

<template>
  <MtSection :blok="blok" class="mt-cgrid" :class="`mt-cgrid--${layout}`">
    <div class="mt-sec-head">
      <p v-if="blok.eyebrow" class="mt-eyebrow">{{ blok.eyebrow }}</p>
      <MtHeading :text="blok.title" :highlight="blok.highlight" :size="blok.title_size || 'm'" class="mt-sec-title" />
      <MtRich :doc="blok.intro" class="mt-lead" />
    </div>
    <div class="mt-grid" :class="`mt-grid--${blok.columns || 3}`">
      <component
        :is="layout === 'tiles' ? NuxtLink : 'article'"
        v-for="(c, i) in blok.cards"
        :key="c._uid"
        v-editable="c"
        :to="layout === 'tiles' ? (href(c.link) || '/') : undefined"
        class="mt-gcard"
        :class="`mt-gcard--${layout}`"
      >
        <div v-if="layout === 'photo'" class="mt-gcard__photo"><MtMedia v-if="c.image?.filename" :asset="c.image" cover :width="800" /></div>
        <div v-else-if="layout === 'case'" class="mt-gcard__avatar"><MtMedia v-if="c.image?.filename" :asset="c.image" cover :width="200" /></div>
        <div v-else-if="layout === 'steps'" class="mt-gcard__stepicon">
          <img v-if="c.image?.filename" :src="c.image.filename" alt="" />
          <MtIcon v-else :name="STEP_ICONS[i % STEP_ICONS.length]" :size="28" />
        </div>
        <div v-else-if="layout === 'tiles'" class="mt-gcard__tileicon">
          <img v-if="c.image?.filename" :src="c.image.filename" alt="" />
          <MtIcon v-else :name="['calc', 'chart', 'euro', 'sliders', 'home', 'doc', 'key', 'person', 'chat'][i % 9]" :size="26" />
        </div>
        <div v-else-if="layout === 'icon'" class="mt-gcard__icon">
          <img v-if="c.image?.filename" :src="c.image.filename" alt="" />
          <MtIcon v-else :name="['sliders', 'calc', 'chart'][i % 3]" :size="44" />
        </div>
        <div class="mt-gcard__body">
          <p v-if="c.tag" class="mt-gcard__tag">{{ c.tag }}</p>
          <h3 v-if="c.title" class="mt-gcard__title">{{ layout === 'steps' ? `${i + 1} – ` : '' }}{{ c.title }}</h3>
          <p v-if="c.quote" class="mt-gcard__quote">{{ c.quote }}</p>
          <MtRich :doc="c.text" class="mt-gcard__text mt-rich--accent" />
          <MtIcon v-if="layout === 'tiles'" name="arrow" :size="18" class="mt-gcard__go" />
          <NuxtLink v-else-if="c.link_label" :to="href(c.link) || '/'" class="mt-btn" :class="layout === 'icon' ? 'mt-btn--primary mt-btn--block' : 'mt-btn--link'">
            {{ c.link_label }}<span v-if="layout !== 'icon'" class="mt-btn__arrow" aria-hidden="true">→</span>
          </NuxtLink>
        </div>
      </component>
    </div>
    <MtButtons :buttons="blok.buttons" :stack="false" class="mt-sec-foot mt-sec-foot--center" />
  </MtSection>
</template>
