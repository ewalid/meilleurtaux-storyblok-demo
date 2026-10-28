/**
 * Shared Style + Visibility tabs for every Meilleurtaux section.
 * Returns the classes for the section shell and whether it should render.
 */
export function useMtSection(blok, defaults = {}, forceTheme = ref(null)) {
  const route = useRoute();
  const inEditor = computed(() => route.query._storyblok !== undefined);

  const background = computed(() => blok.value?.background || defaults.background || 'white');
  const theme = computed(() => forceTheme.value || (background.value === 'image' ? 'image' : background.value));

  const classes = computed(() => {
    const b = blok.value || {};
    return [
      'mt-section',
      `mt-theme-${theme.value}`,
      `mt-pt-${b.space_top || defaults.space_top || 'm'}`,
      `mt-pb-${b.space_bottom || defaults.space_bottom || 'm'}`,
      `mt-align-${b.align || defaults.align || 'left'}`,
      theme.value === 'image' ? `mt-overlay-${b.overlay || 'dark'}` : '',
      b.hide_mobile ? 'mt-hide-mobile' : '',
      b.hide_desktop ? 'mt-hide-desktop' : '',
    ];
  });

  const wrapClass = computed(() => `mt-wrap mt-w-${blok.value?.width || defaults.width || 'standard'}`);

  // Schedule: hidden on the live site outside its window, always shown in the
  // editor with a badge. ?preview_date=YYYY-MM-DD simulates another day.
  const now = computed(() => (route.query.preview_date ? new Date(route.query.preview_date) : new Date()));
  const from = computed(() => (blok.value?.show_from ? new Date(blok.value.show_from.replace(' ', 'T')) : null));
  const until = computed(() => (blok.value?.show_until ? new Date(blok.value.show_until.replace(' ', 'T')) : null));
  const inWindow = computed(() => (!from.value || now.value >= from.value) && (!until.value || now.value <= until.value));
  const visible = computed(() => inEditor.value || inWindow.value);

  const fmt = d => d.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' });
  const badge = computed(() => {
    if (!inEditor.value || (!from.value && !until.value)) {
      return null;
    }
    const parts = [];
    if (from.value) {
      parts.push(`à partir du ${fmt(from.value)}`);
    }
    if (until.value) {
      parts.push(`jusqu'au ${fmt(until.value)}`);
    }
    return { text: `${inWindow.value ? 'En ligne' : 'Masqué sur le site'} · ${parts.join(' ')}`, off: !inWindow.value };
  });

  return { classes, wrapClass, visible, badge, theme, inEditor };
}
