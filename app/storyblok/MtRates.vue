<script setup>
const props = defineProps({ blok: { type: Object, required: true } });
const layout = computed(() => props.blok.layout || 'table');
const { row, updatedLabel } = useMtRates();
const amount = computed(() => mtNumber(props.blok.cost_amount, 200000));
const t = useMtT();
const costRows = computed(() => MT_DURATIONS.map((d) => {
  const rt = mtNumber(row(d, 'excellent')?.rate, 0);
  const m = mtMonthly(amount.value, Number(d), rt);
  return { d, rate: rt, monthly: m, cost: m * Number(d) * 12 - amount.value };
}));
</script>

<template>
  <MtSection :blok="blok" class="mt-rates">
    <div class="mt-sec-head">
      <p v-if="blok.eyebrow" class="mt-eyebrow">{{ blok.eyebrow }}</p>
      <MtHeading :text="blok.title" :size="blok.title_size || 'm'" class="mt-sec-title" />
      <MtRich :doc="blok.intro" class="mt-lead" />
    </div>
    <MtRatesCard v-if="layout === 'tabs'" :show-trend="blok.show_trend !== false" />
    <div v-else class="mt-table-wrap">
      <table v-if="layout === 'table'" class="mt-table">
        <thead>
          <tr><th scope="col">{{ t('loanTermShort') }}</th><th v-for="p in MT_PROFILES" :key="p.key" scope="col">{{ t('rate') }} {{ t(p.key).toLowerCase() }}</th></tr>
        </thead>
        <tbody>
          <tr v-for="d in MT_DURATIONS" :key="d">
            <th scope="row">{{ t('years', { n: d }) }}</th>
            <td v-for="p in MT_PROFILES" :key="p.key">
              <strong>{{ row(d, p.key)?.rate || '–' }} %</strong>
              <small v-if="blok.show_trend !== false" :class="`is-${row(d, p.key)?.trend || 'stable'}`">{{ t(row(d, p.key)?.trend || 'stable') }}</small>
            </td>
          </tr>
        </tbody>
      </table>
      <table v-else class="mt-table">
        <thead>
          <tr><th scope="col">{{ t('loanTermShort') }}</th><th scope="col">{{ t('rate') }} {{ t('excellent').toLowerCase() }}</th><th scope="col">{{ t('monthly') }}</th><th scope="col">{{ t('interestFor', { a: mtEuros(amount) }) }}</th></tr>
        </thead>
        <tbody>
          <tr v-for="c in costRows" :key="c.d">
            <th scope="row">{{ t('years', { n: c.d }) }}</th>
            <td>{{ mtFormat(c.rate, 2) }} %</td>
            <td>{{ mtEuros(c.monthly) }}</td>
            <td><strong>{{ mtEuros(c.cost) }}</strong></td>
          </tr>
        </tbody>
      </table>
    </div>
    <p v-if="blok.show_date !== false && updatedLabel" class="mt-rates__date">{{ t('ratesAtNoIns', { d: updatedLabel }) }}</p>
    <MtRich :doc="blok.note" class="mt-small" />
    <MtButtons :buttons="blok.buttons" :stack="false" class="mt-sec-foot" />
  </MtSection>
</template>
