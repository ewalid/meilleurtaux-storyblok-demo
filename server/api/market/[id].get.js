// Market indicators from the European Central Bank's public data API (no key).
// This route is the integration layer: the page never calls the ECB directly
// (the ECB API sends no CORS headers), the response is cached for an hour, and
// the block receives one clean shape whatever the source.
//   GET /api/market/<id>?n=12  →  { id, source, points: [{ period, value }], latest, previous }
const SERIES = {
  'credit-immo-fr': 'MIR/M.FR.B.A2C.A.R.A.2250.EUR.N', // new housing loans to households, France
  'credit-immo-be': 'MIR/M.BE.B.A2C.A.R.A.2250.EUR.N', // same, Belgium
  'oat-10-fr': 'IRS/M.FR.L.L40.CI.0000.EUR.N.Z', // 10-year government bond yield, France
  'euribor-3m': 'FM/M.U2.EUR.RT.MM.EURIBOR3MD_.HSTA', // 3-month Euribor, monthly average
};

export default defineCachedEventHandler(async (event) => {
  const id = getRouterParam(event, 'id');
  const key = SERIES[id];
  if (!key) {
    throw createError({ statusCode: 404, statusMessage: `Unknown indicator: ${id}` });
  }
  const n = Math.min(60, Math.max(2, Number(getQuery(event).n) || 12));
  const data = await $fetch(`https://data-api.ecb.europa.eu/service/data/${key}`, {
    query: { lastNObservations: n, format: 'jsondata' },
    timeout: 8000,
  });
  const series = Object.values(data.dataSets?.[0]?.series || {})[0];
  const periods = data.structure?.dimensions?.observation?.[0]?.values || [];
  const points = Object.entries(series?.observations || {})
    .map(([i, v]) => ({ period: periods[Number(i)]?.id, value: v?.[0] }))
    .filter(p => p.period && typeof p.value === 'number')
    .sort((a, b) => a.period.localeCompare(b.period));
  if (!points.length) {
    throw createError({ statusCode: 502, statusMessage: 'No data from the ECB' });
  }
  return {
    id,
    source: 'BCE (Banque centrale européenne)',
    series: key,
    points,
    latest: points.at(-1),
    previous: points.at(-2) || null,
    fetched_at: new Date().toISOString(),
  };
}, {
  maxAge: 60 * 60,
  swr: true,
  getKey: event => `${getRouterParam(event, 'id')}:${getQuery(event).n || 12}`,
});
