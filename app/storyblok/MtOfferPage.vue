<script setup>
// "Page offre": a guided form (the offer card) + 3 restricted zones (hero, simulator,
// content) + conditions. The offer switches state on its own from its dates:
// before the start "coming soon", during "N days left", after the end "offer ended".
// ?preview_date=YYYY-MM-DD simulates another day (editor and live).
const props = defineProps({ blok: { type: Object, required: true } });
const route = useRoute();
const lang = useMtLang();
const t = useMtT();
const inEditor = computed(() => route.query._storyblok !== undefined);

const parse = v => (v ? new Date(String(v).replace(' ', 'T')) : null);
const now = computed(() => (route.query.preview_date ? new Date(`${route.query.preview_date}T12:00:00`) : new Date()));
const start = computed(() => parse(props.blok.starts_on));
const end = computed(() => parse(props.blok.ends_on));
const state = computed(() => {
  if (start.value && now.value < start.value) {
    return 'soon';
  }
  if (end.value && now.value > end.value) {
    return 'ended';
  }
  return 'live';
});
const daysLeft = computed(() => (end.value ? Math.ceil((end.value - now.value) / 86400000) : null));
const badge = computed(() => {
  if (state.value === 'soon') {
    return t('offerFrom', { d: mtDate(props.blok.starts_on, true) });
  }
  if (state.value === 'ended') {
    return t('offerEnded');
  }
  if (daysLeft.value === null) {
    return '';
  }
  return daysLeft.value <= 1 ? t('offerLastDay') : t('offerEndsIn', { n: daysLeft.value });
});

// After the end date the button leads to the product page instead of the offer.
const PRODUCT_PAGES = { 'credit-immobilier': 'credit-immobilier', 'assurance-de-pret': 'assurance-de-pret', 'rachat-de-credit': 'rachat-de-credit' };
const prefix = computed(() => (lang.value ? `/${lang.value}` : ''));
const endedHref = computed(() => `${prefix.value}/${PRODUCT_PAGES[props.blok.product] || ''}`.replace(/\/$/, '') || '/');
const ctaHref = computed(() => mtHref(props.blok.cta_link, lang.value));

const copied = ref(false);
async function copy() {
  try {
    await navigator.clipboard.writeText(props.blok.promo_code);
    copied.value = true;
    setTimeout(() => (copied.value = false), 2000);
  }
  catch {
    copied.value = false;
  }
}
const NuxtLink = resolveComponent('NuxtLink');
const hasText = doc => !!doc && JSON.stringify(doc).includes('"text"');
</script>

<template>
  <div v-editable="blok" class="mt-page mt-offer" :class="`is-${state}`">
    <ComponentCheck v-for="(b, i) in blok.hero" :key="b._uid" :blok="b" :index="i" />
    <div v-if="!blok.hero?.length && inEditor" class="mt-wrap mt-w-standard mt-editor-empty">Zone « Bandeau » : ajoutez un Bandeau d'ouverture (onglet Zones de la page).</div>

    <section class="mt-offer__band">
      <div class="mt-wrap mt-w-standard">
        <div class="mt-offer__card">
          <div class="mt-offer__top">
            <img v-if="blok.partner_logo?.filename" :src="blok.partner_logo.filename" :alt="blok.partner_logo.alt || ''" class="mt-offer__logo" />
            <span v-if="badge" class="mt-offer__badge" :class="`is-${state}`"><MtIcon :name="state === 'ended' ? 'info' : 'clock'" :size="16" /> {{ badge }}</span>
          </div>
          <p v-if="blok.offer_label" class="mt-offer__label">{{ blok.offer_label }}</p>
          <p v-if="blok.amount" class="mt-offer__amount">{{ blok.amount }}</p>
          <p v-else-if="inEditor" class="mt-empty">Renseignez l'avantage (onglet principal), ex. « 200 € offerts ».</p>
          <template v-if="state !== 'ended'">
            <MtRich :doc="blok.summary" class="mt-offer__summary" />
            <div v-if="blok.promo_code" class="mt-offer__code">
              <span class="mt-offer__code-label">{{ t('code') }}</span>
              <strong>{{ blok.promo_code }}</strong>
              <button type="button" class="mt-btn mt-btn--outline mt-offer__copy" :disabled="state === 'soon'" @click="copy">
                <MtIcon name="doc" :size="16" /> {{ copied ? t('copied') : t('copy') }}
              </button>
            </div>
            <p v-if="end" class="mt-offer__dates">{{ t('offerUntil', { d: mtDate(blok.ends_on, true) }) }}</p>
            <component
              :is="ctaHref ? NuxtLink : 'span'"
              v-if="blok.cta_label && state === 'live'"
              :to="ctaHref || undefined"
              class="mt-btn mt-btn--primary mt-offer__cta"
            >
              {{ blok.cta_label }} <span class="mt-btn__arrow" aria-hidden="true">→</span>
            </component>
          </template>
          <template v-else>
            <p class="mt-offer__summary">{{ t('offerEndedText') }}</p>
            <NuxtLink :to="endedHref" class="mt-btn mt-btn--dark mt-offer__cta">{{ t('offerEndedCta') }} <span class="mt-btn__arrow" aria-hidden="true">→</span></NuxtLink>
          </template>
          <p v-if="inEditor && route.query.preview_date" class="mt-offer__preview">Aperçu au {{ mtDate(route.query.preview_date, true) }} (?preview_date)</p>
        </div>
      </div>
    </section>

    <template v-if="state !== 'ended'">
      <ComponentCheck v-for="(b, i) in blok.simulator" :key="b._uid" :blok="b" :index="i + 1" />
      <div v-if="!blok.simulator?.length && inEditor" class="mt-wrap mt-w-standard mt-editor-empty">Zone « Simulateur » (optionnelle) : ajoutez un Simulateur.</div>
    </template>

    <ComponentCheck v-for="(b, i) in blok.content" :key="b._uid" :blok="b" :index="i + 2" />
    <div v-if="!blok.content?.length && inEditor" class="mt-wrap mt-w-standard mt-editor-empty">Zone « Contenu » : jusqu'à 5 sections (avantages, étapes, questions, partenaires…).</div>

    <section v-if="hasText(blok.conditions) || hasText(blok.legal_mentions)" class="mt-offer__legal">
      <div class="mt-wrap mt-w-narrow">
        <details v-if="hasText(blok.conditions)" class="mt-offer__conditions">
          <summary>{{ t('conditions') }} <MtIcon name="chevron" :size="18" /></summary>
          <MtRich :doc="blok.conditions" class="mt-prose" />
        </details>
        <MtRich :doc="blok.legal_mentions" class="mt-offer__mentions" />
      </div>
    </section>
  </div>
</template>
