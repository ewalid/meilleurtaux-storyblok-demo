<script setup>
// Shell for every Meilleurtaux section: background, spacing, width, schedule.
const props = defineProps({
  blok: { type: Object, required: true },
  defaults: { type: Object, default: () => ({}) },
  tag: { type: String, default: 'section' },
  forceTheme: { type: String, default: null },
});
const blokRef = toRef(props, 'blok');
const { classes, wrapClass, visible, badge } = useMtSection(blokRef, props.defaults, toRef(props, 'forceTheme'));
const bgAsset = computed(() => (props.blok.background === 'image' ? props.blok.background_image : null));
// A block just added in the editor has only component + _uid: say so instead of showing empty space.
const route = useRoute();
const isBlank = computed(() => route.query._storyblok !== undefined
  && Object.keys(props.blok).every(k => ['component', '_uid', '_editable'].includes(k)));
</script>

<template>
  <component
    :is="tag"
    v-if="visible"
    :id="blok.anchor || undefined"
    v-editable="blok"
    :class="classes"
  >
    <div v-if="bgAsset?.filename" class="mt-section__bg">
      <MtMedia :asset="bgAsset" cover :width="2000" />
      <div class="mt-section__overlay"></div>
    </div>
    <span v-if="badge" class="mt-sched-badge" :class="{ 'is-off': badge.off }">{{ badge.text }}</span>
    <slot name="full"></slot>
    <div v-if="$slots.default" :class="wrapClass">
      <p v-if="isBlank" class="mt-blank-hint">Bloc vide : remplissez les champs à droite, ou supprimez-le et ajoutez-le depuis un modèle (preset).</p>
      <slot></slot>
    </div>
  </component>
</template>
