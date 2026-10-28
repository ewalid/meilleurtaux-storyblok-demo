<script setup>
// YouTube player from a link or a bare ID. `background` = muted, looping, no controls.
const props = defineProps({
  source: { type: String, default: '' },
  background: { type: Boolean, default: false },
  cover: { type: Boolean, default: false },
  title: { type: String, default: 'Video' },
});

const id = computed(() => mtYoutubeId(props.source));

const src = computed(() => {
  if (!id.value) {
    return '';
  }
  const q = new URLSearchParams({ rel: '0', modestbranding: '1', playsinline: '1' });
  if (props.background) {
    q.set('autoplay', '1');
    q.set('mute', '1');
    q.set('loop', '1');
    q.set('controls', '0');
    q.set('playlist', id.value);
  }
  return `https://www.youtube-nocookie.com/embed/${id.value}?${q}`;
});
</script>

<template>
  <div v-if="src" class="mt-yt" :class="{ 'mt-yt--cover': cover, 'mt-yt--bg': background }">
    <iframe
      :src="src"
      :title="title"
      loading="lazy"
      allow="autoplay; encrypted-media; picture-in-picture; fullscreen"
      allowfullscreen
      :tabindex="background ? -1 : undefined"
    ></iframe>
  </div>
</template>

<style>
.mt-yt {
  position: relative;
  aspect-ratio: 16 / 9;
  width: 100%;
  overflow: hidden;
  border-radius: 6px;
}
.mt-yt iframe {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  border: 0;
}
.mt-yt--bg iframe {
  pointer-events: none;
}
/* Fill any box like object-fit: cover, whatever its ratio. */
.mt-yt--cover {
  position: absolute;
  inset: 0;
  aspect-ratio: auto;
  height: 100%;
  border-radius: 0;
  container-type: size;
}
.mt-yt--cover iframe {
  inset: auto;
  top: 50%;
  left: 50%;
  width: max(100cqw, 177.78cqh);
  height: max(100cqh, 56.25cqw);
  transform: translate(-50%, -50%);
}
/* Background video: oversize so YouTube's title bar and logo fall outside the box. */
.mt-yt--bg.mt-yt--cover iframe {
  width: calc(max(100cqw, 177.78cqh) * 1.3);
  height: calc(max(100cqh, 56.25cqw) * 1.3);
}
</style>
