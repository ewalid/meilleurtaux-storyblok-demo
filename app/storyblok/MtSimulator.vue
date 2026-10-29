<script setup>
// Working calculators. Results are computed in the browser from the rate sheet
// (Barème des taux): indicative only, nothing is sent anywhere.
const props = defineProps({ blok: { type: Object, required: true } });
const b = computed(() => props.blok);
const type = computed(() => b.value.type || 'project');
const layout = computed(() => b.value.layout || 'with_rates');
const { rate, data } = useMtRates();
const lang = useMtLang();
const t = useMtT();
const uid = b.value._uid;

const duration = ref(String(b.value.default_duration || '20'));
const amount = ref(mtNumber(b.value.default_amount, 200000));
const monthly = ref(mtNumber(b.value.default_monthly, 1000));
const income = ref(mtNumber(b.value.default_income, 4000));
const charges = ref(0);
const current = ref(1450);
const mode = ref('monthly'); // project: which slider drives the other

watch(() => [b.value.default_amount, b.value.default_monthly, b.value.default_income, b.value.default_duration], () => {
  amount.value = mtNumber(b.value.default_amount, amount.value);
  monthly.value = mtNumber(b.value.default_monthly, monthly.value);
  income.value = mtNumber(b.value.default_income, income.value);
  duration.value = String(b.value.default_duration || duration.value);
});

const years = computed(() => Number(duration.value));
// Consumer loans start well below a mortgage: the scale follows the default amount.
const amountMin = computed(() => (mtNumber(b.value.default_amount, 20000) < 20000 ? 1000 : 20000));
const r = computed(() => rate(duration.value, b.value.rate_profile || 'tres-bon'));
const insBank = computed(() => mtNumber(data.value.insurance_bank_rate, 0.34));
const insDel = computed(() => mtNumber(data.value.insurance_delegated_rate, 0.1));
const consoRate = computed(() => mtNumber(data.value.consolidation_rate, 5.4));

const projectAmount = computed(() => Math.round(mtPrincipal(monthly.value, years.value, r.value) / 1000) * 1000);
const projectMonthly = computed(() => mtMonthly(amount.value, years.value, r.value));
const payment = computed(() => mtMonthly(amount.value, years.value, r.value));
const interest = computed(() => payment.value * years.value * 12 - amount.value);
const capMonthly = computed(() => Math.max(0, income.value * 0.35 - charges.value));
const capAmount = computed(() => Math.round(mtPrincipal(capMonthly.value, years.value, r.value) / 1000) * 1000);
const insBankCost = computed(() => (amount.value * insBank.value / 100) * years.value);
const insDelCost = computed(() => (amount.value * insDel.value / 100) * years.value);
const consoMonthly = computed(() => mtMonthly(amount.value, years.value, consoRate.value));

const result = computed(() => {
  const yrs = t('years', { n: years.value });
  const rate = `${mtFormat(r.value, 2)} %`;
  switch (type.value) {
    case 'monthly':
      return { label: t('resMonthly'), value: mtEuros(payment.value), unit: t('perMonth'), lines: [
        [t('rateUsed'), rate],
        [t('interestCost'), mtEuros(interest.value)],
        [t('term'), yrs],
      ] };
    case 'capacity':
      return { label: t('resCapacity'), value: mtEuros(capAmount.value), unit: '', lines: [
        [t('maxMonthly'), mtEuros(capMonthly.value)],
        [t('rateUsed'), rate],
        [t('term'), yrs],
      ] };
    case 'insurance':
      return { label: t('resInsurance'), value: mtEuros(insBankCost.value - insDelCost.value), unit: '', lines: [
        [t('bankInsurance'), mtEuros(insBankCost.value)],
        [t('withUs'), mtEuros(insDelCost.value)],
        [t('avgRate'), `${mtFormat(insBank.value, 2)} % → ${mtFormat(insDel.value, 2)} %`],
      ] };
    case 'consolidation':
      return { label: t('resConsolidation'), value: mtEuros(consoMonthly.value), unit: t('perMonth'), lines: [
        [t('currentPayments'), mtEuros(current.value)],
        [t('paymentDrop'), `${mtFormat(Math.max(0, (1 - consoMonthly.value / current.value) * 100), 0)} %`],
        [t('consoRate'), `${mtFormat(consoRate.value, 2)} %`],
      ] };
    default:
      return mode.value === 'monthly'
        ? { label: t('resProjectMonthly', { m: mtEuros(monthly.value) }), value: mtEuros(projectAmount.value), unit: '', lines: [[t('term'), yrs], [t('rateUsed'), rate]] }
        : { label: t('resProjectAmount', { a: mtEuros(amount.value) }), value: mtEuros(projectMonthly.value), unit: t('perMonth'), lines: [[t('term'), yrs], [t('rateUsed'), rate]] };
  }
});
const href = l => mtHref(l, lang.value);
</script>

<template>
  <MtSection :blok="blok" class="mt-sim-section" :class="`mt-sim-section--${layout}`">
    <div class="mt-sim-grid">
      <div class="mt-sim">
        <h2 v-if="blok.title" class="mt-sim__title">{{ blok.title }}</h2>
        <div class="mt-sim__fields">
          <template v-if="type === 'project'">
            <div :class="{ 'is-dim': mode !== 'monthly' }" @pointerdown="mode = 'monthly'" @focusin="mode = 'monthly'">
              <MtRange :id="`${uid}-m`" v-model="monthly" :label="t('monthlyWanted')" :min="300" :max="5000" :step="50" />
            </div>
            <p class="mt-sim__or">{{ t('or') }}</p>
            <div :class="{ 'is-dim': mode !== 'amount' }" @pointerdown="mode = 'amount'" @focusin="mode = 'amount'">
              <MtRange :id="`${uid}-a`" v-model="amount" :label="t('amountWanted')" :min="amountMin" :max="1000000" :step="5000" />
            </div>
          </template>
          <template v-else-if="type === 'capacity'">
            <MtRange :id="`${uid}-i`" v-model="income" :label="t('income')" :min="1000" :max="20000" :step="100" />
            <MtRange :id="`${uid}-c`" v-model="charges" :label="t('charges')" :min="0" :max="5000" :step="50" />
          </template>
          <template v-else-if="type === 'consolidation'">
            <MtRange :id="`${uid}-cur`" v-model="current" :label="t('currentMonthly')" :min="200" :max="6000" :step="50" />
            <MtRange :id="`${uid}-a`" v-model="amount" :label="t('remaining')" :min="10000" :max="400000" :step="1000" />
          </template>
          <template v-else>
            <MtRange :id="`${uid}-a`" v-model="amount" :label="t('amount')" :min="amountMin" :max="1000000" :step="5000" />
          </template>
          <div class="mt-sim__dur" role="radiogroup" :aria-label="type === 'consolidation' ? t('newTerm') : t('loanTerm')">
            <span class="mt-range__label">{{ type === 'consolidation' ? t('newTerm') : t('loanTerm') }}</span>
            <div class="mt-tabs">
              <button v-for="d in MT_DURATIONS" :key="d" type="button" role="radio" class="mt-tabs__tab" :class="{ 'is-on': duration === d }" :aria-checked="duration === d" @click="duration = d">{{ t('years', { n: d }) }}</button>
            </div>
          </div>
        </div>
        <div class="mt-sim__result" aria-live="polite">
          <p class="mt-sim__rlabel">{{ result.label }}</p>
          <p class="mt-sim__rvalue">{{ result.value }} <small>{{ result.unit }}</small></p>
          <dl v-if="layout === 'result' || layout === 'alone'" class="mt-sim__lines">
            <template v-for="[k, v] in result.lines" :key="k"><dt>{{ k }}</dt><dd>{{ v }}</dd></template>
          </dl>
        </div>
        <div class="mt-sim__foot">
          <NuxtLink v-if="blok.button_label" :to="href(blok.button_link) || '/'" class="mt-btn mt-btn--dark">{{ blok.button_label }} <span class="mt-btn__arrow" aria-hidden="true">→</span></NuxtLink>
          <MtRich :doc="blok.disclaimer" class="mt-sim__disclaimer" />
        </div>
      </div>
      <MtRatesCard v-if="layout === 'with_rates'" :title="blok.rates_title" :button-label="blok.rates_button_label" :button-link="blok.rates_button_link" />
      <div v-else-if="layout === 'result'" class="mt-sim-big" aria-hidden="true">
        <p class="mt-sim-big__label">{{ result.label }}</p>
        <p class="mt-sim-big__value">{{ result.value }}<small v-if="result.unit"> {{ result.unit }}</small></p>
        <ul>
          <li v-for="[k, v] in result.lines" :key="k"><span>{{ k }}</span><strong>{{ v }}</strong></li>
        </ul>
      </div>
    </div>
  </MtSection>
</template>
