<script setup>
// Working calculators. Results are computed in the browser from the rate sheet
// (Barème des taux): indicative only, nothing is sent anywhere.
const props = defineProps({ blok: { type: Object, required: true } });
const b = computed(() => props.blok);
const type = computed(() => b.value.type || 'project');
const layout = computed(() => b.value.layout || 'with_rates');
const { rate, data } = useMtRates();
const lang = useMtLang();
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
  switch (type.value) {
    case 'monthly':
      return { label: 'Votre mensualité estimée', value: mtEuros(payment.value), unit: '/ mois', lines: [
        ['Taux utilisé', `${mtFormat(r.value, 2)} %`],
        ['Coût des intérêts', mtEuros(interest.value)],
        ['Durée', `${years.value} ans`],
      ] };
    case 'capacity':
      return { label: 'Vous pouvez emprunter environ', value: mtEuros(capAmount.value), unit: '', lines: [
        ['Mensualité max. (35 % des revenus)', mtEuros(capMonthly.value)],
        ['Taux utilisé', `${mtFormat(r.value, 2)} %`],
        ['Durée', `${years.value} ans`],
      ] };
    case 'insurance':
      return { label: 'Économie possible sur votre assurance', value: mtEuros(insBankCost.value - insDelCost.value), unit: '', lines: [
        ['Assurance de votre banque', mtEuros(insBankCost.value)],
        ['Avec Meilleurtaux', mtEuros(insDelCost.value)],
        ['Taux moyen constaté', `${mtFormat(insBank.value, 2)} % → ${mtFormat(insDel.value, 2)} %`],
      ] };
    case 'consolidation':
      return { label: 'Votre nouvelle mensualité unique', value: mtEuros(consoMonthly.value), unit: '/ mois', lines: [
        ['Mensualités actuelles', mtEuros(current.value)],
        ['Baisse de vos mensualités', `${mtFormat(Math.max(0, (1 - consoMonthly.value / current.value) * 100), 0)} %`],
        ['Taux moyen du rachat', `${mtFormat(consoRate.value, 2)} %`],
      ] };
    default:
      return mode.value === 'monthly'
        ? { label: `Avec ${mtEuros(monthly.value)} par mois, vous pouvez emprunter`, value: mtEuros(projectAmount.value), unit: '', lines: [['Sur', `${years.value} ans`], ['Taux utilisé', `${mtFormat(r.value, 2)} %`]] }
        : { label: `Pour emprunter ${mtEuros(amount.value)}, votre mensualité serait`, value: mtEuros(projectMonthly.value), unit: '/ mois', lines: [['Sur', `${years.value} ans`], ['Taux utilisé', `${mtFormat(r.value, 2)} %`]] };
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
              <MtRange :id="`${uid}-m`" v-model="monthly" label="Mensualité souhaitée" :min="300" :max="5000" :step="50" />
            </div>
            <p class="mt-sim__or">ou</p>
            <div :class="{ 'is-dim': mode !== 'amount' }" @pointerdown="mode = 'amount'" @focusin="mode = 'amount'">
              <MtRange :id="`${uid}-a`" v-model="amount" label="Montant du prêt souhaité" :min="20000" :max="1000000" :step="5000" />
            </div>
          </template>
          <template v-else-if="type === 'capacity'">
            <MtRange :id="`${uid}-i`" v-model="income" label="Revenus nets du foyer (par mois)" :min="1000" :max="20000" :step="100" />
            <MtRange :id="`${uid}-c`" v-model="charges" label="Crédits en cours (par mois)" :min="0" :max="5000" :step="50" />
          </template>
          <template v-else-if="type === 'consolidation'">
            <MtRange :id="`${uid}-cur`" v-model="current" label="Total de vos mensualités actuelles" :min="200" :max="6000" :step="50" />
            <MtRange :id="`${uid}-a`" v-model="amount" label="Capital restant dû (tous crédits)" :min="10000" :max="400000" :step="1000" />
          </template>
          <template v-else>
            <MtRange :id="`${uid}-a`" v-model="amount" label="Montant du prêt" :min="20000" :max="1000000" :step="5000" />
          </template>
          <div class="mt-sim__dur" role="radiogroup" :aria-label="type === 'consolidation' ? 'Nouvelle durée' : 'Durée du prêt'">
            <span class="mt-range__label">{{ type === 'consolidation' ? 'Nouvelle durée' : 'Durée du prêt' }}</span>
            <div class="mt-tabs">
              <button v-for="d in MT_DURATIONS" :key="d" type="button" role="radio" class="mt-tabs__tab" :class="{ 'is-on': duration === d }" :aria-checked="duration === d" @click="duration = d">{{ d }} ans</button>
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
