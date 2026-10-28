import { createAccessibilityChecker } from '@storyblok/accessibility-checker';

// Feeds axe-core results to the Visual Editor's A11y tab. Does nothing outside the editor.
export default defineNuxtPlugin(() => {
  createAccessibilityChecker().enable();
});
