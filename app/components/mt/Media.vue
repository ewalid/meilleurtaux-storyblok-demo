<script setup>
// Image or video from a Storyblok asset field. Honours the editor's focus point.
const props = defineProps({
  asset: { type: Object, default: null },
  cover: { type: Boolean, default: false },
  width: { type: Number, default: 1400 },
  eager: { type: Boolean, default: false },
});

const src = computed(() => props.asset?.filename || '');
const isVideo = computed(() => /\.(?:mp4|webm|mov)(?:\?|$)/i.test(src.value));
const isSvg = computed(() => /\.svg(?:\?|$)/i.test(src.value));

const dims = computed(() => {
  const m = src.value.match(/\/(\d+)x(\d+)\//);
  return m ? { w: +m[1], h: +m[2] } : null;
});

const imgSrc = computed(() => {
  if (!src.value || isSvg.value || !src.value.includes('a.storyblok.com')) {
    return src.value;
  }
  const focus = props.asset?.focus ? `:focal(${props.asset.focus})` : '';
  return `${src.value}/m/${props.width}x0/filters:quality(80)${focus}`;
});

const objectPosition = computed(() => {
  const f = props.asset?.focus;
  if (!f || !dims.value) {
    return undefined;
  }
  const m = f.match(/(\d+)x(\d+):(\d+)x(\d+)/);
  if (!m) {
    return undefined;
  }
  const x = ((+m[1] + +m[3]) / 2 / dims.value.w) * 100;
  const y = ((+m[2] + +m[4]) / 2 / dims.value.h) * 100;
  return `${x.toFixed(1)}% ${y.toFixed(1)}%`;
});

const video = ref(null);
function play() {
  if (!video.value) {
    return;
  }
  video.value.muted = true;
  video.value.play?.().catch(() => {});
}
onMounted(play);
watch(src, () => nextTick(play));
</script>

<template>
  <video
    v-if="src && isVideo"
    ref="video"
    class="mt-media"
    :class="{ 'mt-media--cover': cover }"
    :src="src"
    autoplay
    loop
    muted
    playsinline
  ></video>
  <img
    v-else-if="src"
    class="mt-media"
    :class="{ 'mt-media--cover': cover }"
    :src="imgSrc"
    :alt="asset?.alt || ''"
    :width="dims?.w"
    :height="dims?.h"
    :loading="eager ? 'eager' : 'lazy'"
    :style="objectPosition ? { objectPosition } : undefined"
  />
</template>
