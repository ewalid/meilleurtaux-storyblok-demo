<script setup>
const props = defineProps({ blok: { type: Object, required: true } });
const layout = computed(() => props.blok.layout || 'faq');
const openUid = ref(null);
const toggle = uid => (openUid.value = openUid.value === uid ? null : uid);
const half = computed(() => Math.ceil((props.blok.items?.length || 0) / 2));
const groups = computed(() => (layout.value === 'images'
  ? [props.blok.items?.slice(0, half.value) || [], props.blok.items?.slice(half.value) || []]
  : [props.blok.items || []]));

function plainText(doc) {
  if (!doc || typeof doc === 'string') {
    return doc || '';
  }
  const out = [];
  const walk = n => (n.text ? out.push(n.text) : (n.content || []).forEach(walk));
  walk(doc);
  return out.join(' ');
}
if (props.blok.schema_faq !== false && props.blok.items?.length) {
  useHead({ script: [{ type: 'application/ld+json', children: JSON.stringify({
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    'mainEntity': props.blok.items.map(q => ({ '@type': 'Question', 'name': q.question, 'acceptedAnswer': { '@type': 'Answer', 'text': plainText(q.answer) } })),
  }) }] });
}
</script>

<template>
  <MtSection :blok="blok" class="mt-acc" :class="`mt-acc--${layout}`">
    <div class="mt-acc__grid">
      <div class="mt-acc__head">
        <p v-if="blok.eyebrow" class="mt-eyebrow">{{ blok.eyebrow }}</p>
        <MtHeading :text="blok.title" :size="blok.title_size || (layout === 'faq' ? 'l' : 'm')" class="mt-sec-title" />
        <MtRich :doc="blok.intro" class="mt-lead" />
        <MtButtons v-if="layout === 'faq'" :buttons="blok.buttons" />
      </div>
      <div class="mt-acc__body">
        <div v-for="(g, gi) in groups" :key="gi" class="mt-acc__row" :class="{ 'is-flipped': gi === 1 }">
          <div class="mt-acc__list">
            <div v-for="q in g" :key="q._uid" v-editable="q" class="mt-acc__item" :class="{ 'is-open': openUid === q._uid }">
              <button :id="`q-${q._uid}`" type="button" class="mt-acc__q" :aria-expanded="openUid === q._uid" :aria-controls="`a-${q._uid}`" @click="toggle(q._uid)">
                <span>{{ q.question }}</span>
                <span class="mt-round mt-round--s"><MtIcon name="chevron" :size="16" /></span>
              </button>
              <div v-show="openUid === q._uid" :id="`a-${q._uid}`" role="region" :aria-labelledby="`q-${q._uid}`" class="mt-acc__a"><MtRich :doc="q.answer" /></div>
            </div>
          </div>
          <div v-if="layout === 'images'" class="mt-acc__img">
            <MtMedia v-if="(gi === 0 ? blok.image_1 : blok.image_2)?.filename" :asset="gi === 0 ? blok.image_1 : blok.image_2" cover :width="900" />
          </div>
        </div>
        <MtButtons v-if="layout !== 'faq'" :buttons="blok.buttons" :stack="false" class="mt-sec-foot" />
      </div>
    </div>
  </MtSection>
</template>
