<script setup>
const props = defineProps({ blok: { type: Object, required: true } });
const openIdx = ref(0);
const playing = ref(false);
const ytId = computed(() => mtYoutubeId(props.blok.youtube));
const poster = computed(() => props.blok.poster?.filename || (ytId.value ? `https://img.youtube.com/vi/${ytId.value}/maxresdefault.jpg` : ''));
</script>

<template>
  <MtSection :blok="blok" :defaults="{ background: 'cream', width: 'full', space_top: 'none', space_bottom: 'none' }" class="mt-steps">
    <div class="mt-steps__grid" :class="{ 'is-flipped': blok.media_side === 'left' }">
      <div class="mt-steps__copy">
        <MtHeading :text="blok.title" :size="blok.title_size || 'm'" class="mt-sec-title" />
        <ol class="mt-steps__list">
          <li v-for="(s, i) in blok.steps" :key="s._uid" v-editable="s" :class="{ 'is-open': openIdx === i }">
            <button type="button" class="mt-steps__q" :aria-expanded="openIdx === i" @click="openIdx = openIdx === i ? -1 : i">
              <span class="mt-steps__n">{{ i + 1 }}.</span>
              <span class="mt-steps__t">{{ s.title }}</span>
              <span class="mt-round mt-round--s"><MtIcon name="chevron" :size="16" /></span>
            </button>
            <div v-show="openIdx === i" class="mt-steps__a"><MtRich :doc="s.text" /></div>
          </li>
        </ol>
        <MtButtons :buttons="blok.buttons" :stack="false" />
      </div>
      <div class="mt-steps__media" :class="`mt-bg-${blok.media_color || 'peach'}`">
        <div class="mt-steps__frame">
          <template v-if="(blok.media_source || 'youtube') === 'youtube' && ytId">
            <MtYoutube v-if="playing" :source="`${ytId}`" :title="blok.title || 'Vidéo'" class="is-autoplay" />
            <button v-else type="button" class="mt-video-poster" :aria-label="`Lire la vidéo : ${blok.title || ''}`" @click="playing = true">
              <img :src="poster" alt="" loading="lazy" />
              <span class="mt-video-poster__play"><MtIcon name="play" :size="30" /></span>
            </button>
          </template>
          <MtMedia v-else-if="blok.media?.filename" :asset="blok.media" cover :width="1000" />
          <div v-else-if="$route.query._storyblok" class="mt-empty">Ajoutez une vidéo YouTube ou une image</div>
        </div>
      </div>
    </div>
  </MtSection>
</template>
