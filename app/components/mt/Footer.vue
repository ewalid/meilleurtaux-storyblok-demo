<script setup>
const props = defineProps({ config: { type: Object, default: () => ({}) } });
const lang = useMtLang();
const href = l => mtHref(l, lang.value);
const year = new Date().getFullYear();
const copyright = computed(() => (props.config.copyright || '').replace('{year}', year));
const socials = computed(() => [
  ['facebook', props.config.social_facebook],
  ['linkedin', props.config.social_linkedin],
  ['youtube', props.config.social_youtube],
  ['x', props.config.social_x],
].filter(([, l]) => href(l)));
const email = ref('');
const sent = ref(false);
</script>

<template>
  <footer class="mt-footer">
    <div class="mt-wrap mt-w-standard mt-footer__top">
      <div class="mt-footer__brand">
        <img v-if="config.footer_logo?.filename" :src="config.footer_logo.filename" :alt="config.footer_logo.alt || 'Meilleurtaux'" width="260" height="34" />
        <div class="mt-footer__cols">
          <div v-for="col in config.footer_columns" :key="col._uid" v-editable="col" class="mt-footer__col">
            <p class="mt-footer__title">{{ col.title }}</p>
            <NuxtLink v-for="l in col.links" :key="l._uid" :to="href(l.link) || '/'">{{ l.label }}</NuxtLink>
          </div>
        </div>
      </div>
      <div class="mt-footer__side">
        <form class="mt-news-box" @submit.prevent="sent = true">
          <p class="mt-footer__title">{{ config.newsletter_title || 'Inscrivez-vous à notre newsletter' }}</p>
          <div v-if="!sent" class="mt-news-box__row">
            <label class="sr-only" for="mt-nl">Votre adresse email</label>
            <input id="mt-nl" v-model="email" type="email" required placeholder="Votre adresse email" />
            <button type="submit" class="mt-news-box__go" aria-label="S'inscrire"><MtIcon name="arrow" :size="18" /></button>
          </div>
          <p v-else class="mt-news-box__ok">Merci ! Votre inscription est bien prise en compte (démo).</p>
          <MtRich :doc="config.newsletter_text" class="mt-news-box__text" />
        </form>
        <div class="mt-footer__social">
          <a v-for="[name, l] in socials" :key="name" :href="href(l)" target="_blank" rel="noopener" :aria-label="name"><MtIcon :name="name" :size="20" /></a>
          <MtTrustpilot />
        </div>
      </div>
    </div>
    <div v-if="config.product_columns?.length" class="mt-footer__products">
      <div class="mt-wrap mt-w-standard mt-footer__pgrid">
        <div v-for="col in config.product_columns" :key="col._uid" v-editable="col" class="mt-footer__col">
          <p class="mt-footer__title">{{ col.title }}</p>
          <NuxtLink v-for="l in col.links" :key="l._uid" :to="href(l.link) || '/'">{{ l.label }}</NuxtLink>
        </div>
      </div>
    </div>
    <div class="mt-footer__legal mt-wrap mt-w-standard">
      <MtRich :doc="config.legal_text" />
      <p v-if="copyright" class="mt-footer__copy">{{ copyright }}</p>
    </div>
  </footer>
</template>
