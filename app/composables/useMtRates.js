/**
 * The rate sheet (story `parametres/bareme-des-taux`, type mt-rates-config).
 * One story drives every rate on the site: hero tiles, simulators, rate tables.
 * In the Visual Editor the draft version is read, so a rate change previews
 * everywhere before it is published.
 */
const FALLBACK = {
  updated_on: '',
  rows: [
    { duration: '15', profile: 'excellent', rate: '3,35', trend: 'up' },
    { duration: '15', profile: 'tres-bon', rate: '3,59', trend: 'stable' },
    { duration: '15', profile: 'bon', rate: '3,80', trend: 'stable' },
    { duration: '20', profile: 'excellent', rate: '3,45', trend: 'stable' },
    { duration: '20', profile: 'tres-bon', rate: '3,70', trend: 'stable' },
    { duration: '20', profile: 'bon', rate: '3,90', trend: 'stable' },
    { duration: '25', profile: 'excellent', rate: '3,55', trend: 'down' },
    { duration: '25', profile: 'tres-bon', rate: '3,80', trend: 'stable' },
    { duration: '25', profile: 'bon', rate: '4,00', trend: 'stable' },
  ],
  insurance_bank_rate: '0,34',
  insurance_delegated_rate: '0,10',
  consolidation_rate: '5,40',
};

export const MT_PROFILES = [
  { key: 'excellent', label: 'Excellent' },
  { key: 'tres-bon', label: 'Très bon' },
  { key: 'bon', label: 'Bon' },
];
export const MT_DURATIONS = ['15', '20', '25'];

export function useMtRates() {
  const sheet = useState('mtRates', () => null);
  const lang = useMtLang();
  const loading = useState('mtRatesLoading', () => false);

  if (!sheet.value && !loading.value && import.meta.client) {
    loading.value = true;
    useStoryblokApi()
      .get('cdn/stories/parametres/bareme-des-taux', { version: getVersion() })
      .then(({ data }) => {
        sheet.value = data.story.content;
      })
      .catch(() => {
        sheet.value = FALLBACK;
      })
      .finally(() => {
        loading.value = false;
      });
  }

  const data = computed(() => sheet.value || FALLBACK);

  function row(duration, profile = 'excellent') {
    return (data.value.rows || []).find(r => String(r.duration) === String(duration) && r.profile === profile) || null;
  }
  function rate(duration, profile = 'excellent') {
    return mtNumber(row(duration, profile)?.rate, 0);
  }
  const updatedLabel = computed(() => {
    const d = data.value.updated_on;
    if (!d) {
      return '';
    }
    const date = new Date(d.replace(' ', 'T'));
    return Number.isNaN(date.getTime()) ? '' : date.toLocaleDateString(mtLocale(lang.value), { day: '2-digit', month: '2-digit', year: '2-digit' });
  });

  return { data, row, rate, updatedLabel, sheet };
}

// Monthly payment of a fixed-rate loan, rate in % per year.
export function mtMonthly(amount, years, ratePct) {
  const n = years * 12;
  const r = ratePct / 100 / 12;
  if (!n) {
    return 0;
  }
  return r ? (amount * r) / (1 - (1 + r) ** -n) : amount / n;
}

// Amount that a monthly payment can borrow.
export function mtPrincipal(monthly, years, ratePct) {
  const n = years * 12;
  const r = ratePct / 100 / 12;
  return r ? (monthly * (1 - (1 + r) ** -n)) / r : monthly * n;
}
