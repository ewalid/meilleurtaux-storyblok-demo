/**
 * Turns a Storyblok link field into an href. Internal links keep the current
 * language prefix (/de/...), and `home` becomes the root.
 */
export function useMtLang() {
  return useState('mtLang', () => null);
}

export function mtHref(link, lang) {
  if (!link) {
    return '';
  }
  if (typeof link === 'string') {
    return link;
  }
  const anchor = link.anchor ? `#${link.anchor}` : '';
  switch (link.linktype) {
    case 'email':
      return link.email ? `mailto:${link.email}` : '';
    case 'url':
    case 'asset':
      return (link.url || link.cached_url || '') + anchor;
    case 'story':
    default: {
      let slug = link.story?.full_slug ?? link.cached_url ?? '';
      if (!slug && !anchor) {
        return '';
      }
      slug = slug.replace(/^\/+|\/+$/g, '');
      if (lang && slug.startsWith(`${lang}/`)) {
        slug = slug.slice(lang.length + 1);
      }
      if (slug === 'home') {
        slug = '';
      }
      // Market home pages (uk/home) live at the market root (/uk).
      slug = slug.replace(/\/home$/, '');
      const path = `/${lang ? `${lang}/` : ''}${slug}`.replace(/\/+$/, '') || '/';
      return path + anchor;
    }
  }
}

export function mtIsExternal(link) {
  return link?.linktype === 'url' && /^https?:\/\//.test(link.url || '');
}
