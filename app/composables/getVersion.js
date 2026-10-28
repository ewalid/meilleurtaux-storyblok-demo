/**
 * Real visits read published content; only the Visual Editor (which adds
 * `_storyblok` to the URL) reads drafts. `?_storyblok_published` forces published.
 */
export default function () {
  const route = useRoute();
  if (route.query._storyblok_published !== undefined) {
    return 'published';
  }
  return route.query._storyblok !== undefined ? 'draft' : 'published';
}
