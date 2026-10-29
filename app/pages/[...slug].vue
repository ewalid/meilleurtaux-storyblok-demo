<script setup>
// Single-site router: `/` = home, `/<slug>` = story, a folder resolves to its
// start page (`actualites/`). `/en/...` = the English field-level translation.
const processedSlug = await getProcessedSlug();
const language = await getLanguage(await getSlug());
useMtLang().value = language;
mtSetLocale(mtLocale(language));
const releaseId = await getReleaseId();
const story = ref(null);
const storyblokApi = useStoryblokApi();

const apiParams = {
  version: getVersion(),
  language,
  fallback_lang: 'default',
  resolve_links: 'url',
  from_release: releaseId,
};

const { customParent } = useRuntimeConfig().public;

async function load(path) {
  const { data } = await storyblokApi.get(`cdn/stories/${path}`, apiParams);
  return data.story;
}

try {
  try {
    story.value = await load(processedSlug);
  }
  catch (error) {
    if (error.status !== 404) {
      throw error;
    }
    try {
      story.value = await load(`${processedSlug.replace(/\/$/, '')}/`);
    }
    catch {
      story.value = await load('error-404');
    }
  }

  onMounted(() => {
    useStoryblokBridge(
      story.value?.id,
      (evStory) => {
        story.value = evStory;
      },
      { preventClicks: true, customParent },
    );
  });
}
catch (error) {
  console.log(error);
}

const mtStoryName = useMtStoryName();
const mtPageComponent = useState('mtPageComponent', () => null);
const toc = useMtToc();
watchEffect(() => {
  const c = story.value?.content;
  mtStoryName.value = story.value?.name || '';
  mtPageComponent.value = c?.component || null;
  // Only block lists: an article's `body` is a rich-text document, not an array.
  toc.value = mtTocFrom(['body', 'hero', 'sections', 'cta', 'after'].flatMap(k => (Array.isArray(c?.[k]) ? c[k] : [])));
});

const viewingSiteConfig = ref(['site-config', 'mt-site-config'].includes(story.value?.content?.component));
useState('viewingSiteConfig', () => viewingSiteConfig.value).value = viewingSiteConfig.value;

const c = story.value?.content || {};
const name = c.title || story.value?.name;

// hreflang: the same page in every space language (French is the default, unprefixed).
const alternates = [];
if (story.value && !c.noindex) {
  const { data: space } = await storyblokApi.get('cdn/spaces/me');
  const origin = useRequestURL().origin;
  const path = processedSlug === 'home' ? '' : `/${processedSlug.replace(/\/$/, '')}`;
  const href = code => `${origin}${code ? `/${code}` : ''}${path}` || `${origin}/`;
  alternates.push({ rel: 'alternate', hreflang: 'fr', href: href('') });
  for (const code of space.space.language_codes || []) {
    alternates.push({ rel: 'alternate', hreflang: code, href: href(code) });
  }
  alternates.push({ rel: 'alternate', hreflang: 'x-default', href: href('') });
}

useHead({
  link: alternates,
  title: c.meta_title || (name && processedSlug !== 'home' ? `${name} | Meilleurtaux` : 'Meilleurtaux : Courtier en crédit immobilier, assurances & placement'),
  meta: [
    { name: 'description', content: c.meta_description || c.excerpt || '' },
    ...(c.noindex ? [{ name: 'robots', content: 'noindex' }] : []),
    ...(c.og_image?.filename ? [{ property: 'og:image', content: c.og_image.filename }] : []),
  ],
});
</script>

<template>
  <StoryblokComponent
    v-if="story && !viewingSiteConfig"
    :blok="story.content"
    :uuid="story.uuid"
  />
</template>
