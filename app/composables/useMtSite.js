/**
 * Site settings (mt-site-config) shared with every block, e.g. the Trustpilot
 * score shown in the header, heroes and review sections. Set by the layout.
 */
export function useMtSite() {
  return useState('mtSite', () => ({}));
}

// "4,8" / "4.8" -> 4.8
export function mtNumber(v, fallback = 0) {
  const n = Number.parseFloat(String(v ?? '').replace(/\s/g, '').replace(',', '.'));
  return Number.isFinite(n) ? n : fallback;
}

// Locale for numbers and dates, set from the URL language (fr-FR, nl-BE, en-GB).
let LOCALE = 'fr-FR';
export function mtSetLocale(locale) {
  LOCALE = locale || 'fr-FR';
}

const fmtCache = {};
export function mtFormat(n, digits = 0, style = 'decimal') {
  const key = `${LOCALE}${digits}${style}`;
  fmtCache[key] ||= new Intl.NumberFormat(LOCALE, {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
    ...(style === 'currency' ? { style: 'currency', currency: 'EUR' } : {}),
  });
  return fmtCache[key].format(n);
}

export function mtEuros(n, digits = 0) {
  return mtFormat(Math.round(n * 10 ** digits) / 10 ** digits, digits, 'currency');
}

export const MT_CATEGORIES = {
  'credit-immobilier': 'Crédit immobilier',
  'assurance-de-pret': 'Assurance de prêt',
  'rachat-de-credit': 'Rachat de crédit',
  'assurances': 'Assurances',
  'placement': 'Placement et épargne',
  'credit-consommation': 'Crédit consommation',
};

export function mtDate(d, long = false) {
  if (!d) {
    return '';
  }
  const date = new Date(String(d).replace(' ', 'T'));
  return Number.isNaN(date.getTime())
    ? ''
    : date.toLocaleDateString(LOCALE, long ? { day: 'numeric', month: 'long', year: 'numeric' } : { day: '2-digit', month: 'long', year: 'numeric' });
}
