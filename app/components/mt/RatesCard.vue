<script setup>
// "Les taux nationaux" card: tabs per duration, one row per profile.
defineProps({ title: { type: String, default: '' }, buttonLabel: { type: String, default: '' }, buttonLink: { type: Object, default: null }, showTrend: { type: Boolean, default: true } });
const { row, updatedLabel } = useMtRates();
const lang = useMtLang();
const tab = ref('15');
const t = useMtT();
const ICON = { up: 'up', down: 'down', stable: '' };
const trendOf = (d, p) => row(d, p)?.trend || 'stable';
</script>

<template>
  <div class="mt-ratescard">
    <h3 v-if="title" class="mt-ratescard__title">{{ title }}</h3>
    <div class="mt-tabs" role="tablist" :aria-label="t('loanTerm')">
      <button v-for="d in MT_DURATIONS" :key="d" type="button" role="tab" class="mt-tabs__tab" :class="{ 'is-on': tab === d }" :aria-selected="tab === d" @click="tab = d">{{ t('overYears', { n: d }) }}</button>
    </div>
    <table class="mt-ratescard__table">
      <caption class="sr-only">{{ t('rate') }} · {{ t('years', { n: tab }) }}</caption>
      <tbody>
        <tr v-for="(p, i) in MT_PROFILES" :key="p.key" :class="{ 'is-top': i === 0 }">
          <th scope="row">{{ i === 0 ? `${t('rate')} ` : '' }}{{ t(p.key) }}</th>
          <td class="mt-ratescard__rate">{{ row(tab, p.key)?.rate || '–' }} %</td>
          <td v-if="showTrend" class="mt-ratescard__trend" :class="`is-${row(tab, p.key)?.trend || 'stable'}`">
            <MtIcon v-if="ICON[trendOf(tab, p.key)]" :name="ICON[trendOf(tab, p.key)]" :size="20" />
            <span v-else aria-hidden="true">–</span>
            <small>{{ t(trendOf(tab, p.key)) }}</small>
          </td>
        </tr>
      </tbody>
    </table>
    <p v-if="updatedLabel" class="mt-ratescard__date">{{ t('ratesAt', { d: updatedLabel }) }}</p>
    <div v-if="buttonLabel" class="mt-ratescard__cta">
      <NuxtLink :to="mtHref(buttonLink, lang) || '/'" class="mt-btn mt-btn--dark">{{ buttonLabel }} <span class="mt-btn__arrow" aria-hidden="true">→</span></NuxtLink>
    </div>
  </div>
</template>
