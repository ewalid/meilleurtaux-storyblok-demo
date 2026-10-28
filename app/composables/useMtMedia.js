/**
 * Media helpers shared by blocks that offer "library image/video OR YouTube".
 */

// Accepts a bare ID or any common YouTube link form; returns the 11-char ID or ''.
export function mtYoutubeId(source) {
  const s = (source || '').trim();
  if (!s) {
    return '';
  }
  if (/^[\w-]{11}$/.test(s)) {
    return s;
  }
  const m = s.match(/(?:youtu\.be\/|[?&]v=|\/(?:embed|shorts|live|v)\/)([\w-]{11})/);
  return m ? m[1] : '';
}

// Name of the story being shown, for breadcrumbs. Set by the catch-all page.
export function useMtStoryName() {
  return useState('mtStoryName', () => '');
}
