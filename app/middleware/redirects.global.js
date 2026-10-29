// Redirects managed in Storyblok (folder `redirects/`, type mt-redirect).
// Loaded once per visit. This demo is a client-rendered app, so the redirect
// happens in the browser; in production it would run at the edge (301/302).
let table = null;

async function loadRedirects() {
  if (table) {
    return table;
  }
  table = {};
  try {
    const { data } = await useStoryblokApi().get('cdn/stories', {
      starts_with: 'redirects/',
      content_type: 'mt-redirect',
      per_page: 100,
      version: 'published',
      resolve_links: 'url',
    });
    for (const s of data.stories) {
      const from = (s.content.from_path || '').trim().replace(/\/+$/, '');
      const to = mtHref(s.content.to, null);
      if (from.startsWith('/') && to) {
        table[from.toLowerCase()] = { to, code: Number(s.content.type) || 301 };
      }
    }
  }
  catch {
    // No redirects: navigation continues normally.
  }
  return table;
}

export default defineNuxtRouteMiddleware(async (to) => {
  if (to.query._storyblok !== undefined) {
    return;
  }
  const hit = (await loadRedirects())[to.path.replace(/\/+$/, '').toLowerCase()];
  if (hit && hit.to !== to.path) {
    return navigateTo(hit.to, { redirectCode: hit.code, replace: true });
  }
});
