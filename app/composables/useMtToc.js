/**
 * Sections that should appear in the page's "Sommaire": any section with an
 * anchor name. Collected from the story body by the page component.
 */
export function useMtToc() {
  return useState('mtToc', () => []);
}

export function mtTocFrom(bloks = []) {
  return bloks
    .filter(b => b?.anchor)
    .map(b => ({ id: b.anchor, label: b.toc_label || b.title || b.headline || b.anchor }));
}
