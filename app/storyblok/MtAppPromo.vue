<script setup>
defineProps({ blok: { type: Object, required: true } });
const lang = useMtLang();
const href = l => mtHref(l, lang.value);
</script>

<template>
  <MtSection :blok="blok" class="mt-apps">
    <div class="mt-apps__grid">
      <div>
        <MtHeading :text="blok.title" :size="blok.title_size || 'm'" class="mt-sec-title" />
        <div v-for="a in blok.apps" :key="a._uid" v-editable="a" class="mt-app">
          <p class="mt-app__name">{{ a.name }}</p>
          <p class="mt-app__text">{{ a.text }}</p>
          <div class="mt-app__row">
            <a v-if="href(a.app_store)" :href="href(a.app_store)" target="_blank" rel="noopener" class="mt-store">
              <MtIcon name="screen" :size="18" /><span><small>Télécharger dans</small> l'App Store</span>
            </a>
            <a v-if="href(a.google_play)" :href="href(a.google_play)" target="_blank" rel="noopener" class="mt-store">
              <MtIcon name="play" :size="18" /><span><small>Disponible sur</small> Google Play</span>
            </a>
            <NuxtLink v-if="a.more_label" :to="href(a.more_link) || '/'" class="mt-btn mt-btn--link">{{ a.more_label }} <span class="mt-btn__arrow" aria-hidden="true">→</span></NuxtLink>
          </div>
        </div>
      </div>
      <div class="mt-apps__media"><MtMedia v-if="blok.media?.filename" :asset="blok.media" :width="800" /></div>
    </div>
  </MtSection>
</template>
