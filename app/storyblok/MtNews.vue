<script setup>
// Latest news (automatic, optionally one theme) or hand-picked articles.
const props = defineProps({ blok: { type: Object, required: true } });
const lang = useMtLang();
const tr = useMtT();
const items = ref([]);
const loaded = ref(false);
const active = ref('all');
const source = computed(() => props.blok.source || 'latest');

async function load() {
  const api = useStoryblokApi();
  const params = { version: getVersion(), language: lang.value || undefined, resolve_links: 'url' };
  try {
    if (source.value === 'picked') {
      const ids = props.blok.articles || [];
      if (!ids.length) {
        items.value = [];
        return;
      }
      const { data } = await api.get('cdn/stories', { ...params, by_uuids_ordered: ids.join(','), per_page: 25 });
      items.value = data.stories;
    }
    else {
      const cat = props.blok.category && props.blok.category !== 'all' ? props.blok.category : null;
      const { data } = await api.get('cdn/stories', {
        ...params,
        starts_with: 'actualites/',
        content_type: 'mt-article',
        sort_by: 'content.date:desc',
        per_page: Number(props.blok.count || 3),
        ...(cat ? { filter_query: { category: { in: cat } } } : {}),
      });
      items.value = data.stories;
    }
  }
  catch {
    items.value = [];
  }
  finally {
    loaded.value = true;
  }
}
onMounted(load);
watch(() => [props.blok.source, props.blok.category, props.blok.count, (props.blok.articles || []).join()], load);

const themes = computed(() => ['all', ...new Set(items.value.map(s => s.content.category).filter(Boolean))]);
const shown = computed(() => (active.value === 'all' ? items.value : items.value.filter(s => s.content.category === active.value)));
const href = s => `/${lang.value ? `${lang.value}/` : ''}${s.full_slug.replace(/^en\//, '')}`;
</script>

<template>
  <MtSection :blok="blok" class="mt-news">
    <div class="mt-sec-head">
      <MtHeading :text="blok.title" :size="blok.title_size || 'm'" class="mt-sec-title" />
    </div>
    <div v-if="blok.filters && themes.length > 2" class="mt-filters" role="toolbar" :aria-label="tr('filterTheme')">
      <button v-for="t in themes" :key="t" type="button" class="mt-filter" :class="{ 'is-on': active === t }" :aria-pressed="active === t" @click="active = t">
        {{ t === 'all' ? tr('allNews') : tr.category(t) }}
      </button>
    </div>
    <div class="mt-grid mt-grid--3">
      <NuxtLink v-for="s in shown" :key="s.uuid" :to="href(s)" class="mt-ncard">
        <div class="mt-ncard__img"><MtMedia v-if="s.content.image?.filename" :asset="s.content.image" cover :width="700" /></div>
        <div class="mt-ncard__body">
          <div class="mt-ncard__meta">
            <span class="mt-chip mt-chip--s">{{ s.content.category ? tr.category(s.content.category) : tr('news') }}</span>
            <span class="mt-ncard__date">{{ mtDate(s.content.date || s.first_published_at) }}</span>
          </div>
          <h3 class="mt-ncard__title">{{ s.content.title || s.name }}</h3>
          <p v-if="s.content.excerpt" class="mt-ncard__text">{{ s.content.excerpt }}</p>
        </div>
      </NuxtLink>
    </div>
    <p v-if="loaded && !shown.length && $route.query._storyblok" class="mt-empty">Aucun article ne correspond. Publiez un article dans le dossier Actualités.</p>
    <MtButtons :buttons="blok.buttons" :stack="false" class="mt-sec-foot mt-sec-foot--center" />
  </MtSection>
</template>
