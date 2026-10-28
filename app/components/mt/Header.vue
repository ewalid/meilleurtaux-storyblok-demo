<script setup>
// Meilleurtaux header: logo, Trustpilot, two buttons, then the product menu
// with a mega-menu per item. Mobile: compact logo + drawer with accordions.
const props = defineProps({ config: { type: Object, default: () => ({}) } });
const lang = useMtLang();
const open = ref(null);
const drawer = ref(false);
const mobileOpen = ref(null);
const route = useRoute();
watch(() => route.fullPath, () => {
  open.value = null;
  drawer.value = false;
});
let timer;
function enter(uid) {
  clearTimeout(timer);
  timer = setTimeout(() => (open.value = uid), 90);
}
function leave() {
  clearTimeout(timer);
  timer = setTimeout(() => (open.value = null), 160);
}
const nav = computed(() => props.config.nav || []);
const href = l => mtHref(l, lang.value);
const NuxtLink = resolveComponent('NuxtLink');
const homeHref = computed(() => (lang.value ? `/${lang.value}` : '/'));
</script>

<template>
  <header class="mt-header" :class="{ 'is-open': open }">
    <div class="mt-header__top mt-wrap mt-w-wide">
      <NuxtLink :to="homeHref" class="mt-header__logo" aria-label="Meilleurtaux, accueil">
        <img v-if="config.logo?.filename" :src="config.logo.filename" :alt="config.logo.alt || 'Meilleurtaux'" class="mt-hide-mobile" width="300" height="40" />
        <img v-if="config.logo_mobile?.filename || config.logo?.filename" :src="(config.logo_mobile || config.logo).filename" alt="Meilleurtaux" class="mt-hide-desktop" width="68" height="30" />
      </NuxtLink>
      <MtTrustpilot class="mt-header__tp" />
      <div class="mt-header__actions">
        <MtBtn v-for="(b, i) in config.header_buttons" :key="b._uid" :button="b" :class="{ 'mt-hide-mobile': i === 0 }" />
        <button type="button" class="mt-header__burger mt-hide-desktop" :aria-expanded="drawer" aria-label="Menu" @click="drawer = !drawer">
          <MtIcon :name="drawer ? 'close' : 'menu'" :size="26" />
        </button>
      </div>
    </div>
    <nav class="mt-nav mt-hide-mobile" aria-label="Menu principal" @mouseleave="leave">
      <ul class="mt-nav__list">
        <li v-for="item in nav" :key="item._uid" v-editable="item" class="mt-nav__item" :class="{ 'is-active': open === item._uid }" @mouseenter="enter(item._uid)">
          <component :is="href(item.link) ? NuxtLink : 'button'" :to="href(item.link) || undefined" class="mt-nav__label" :aria-expanded="open === item._uid" @focus="enter(item._uid)">
            <span v-for="(line, i) in (item.label || '').split('\n')" :key="i">{{ line }}</span>
          </component>
        </li>
      </ul>
      <Transition name="mt-fade">
        <div v-if="open" class="mt-mega" @mouseenter="enter(open)">
          <template v-for="item in nav" :key="item._uid">
            <div v-if="open === item._uid" class="mt-mega__inner mt-wrap mt-w-wide">
              <div class="mt-mega__main">
                <div v-if="item.cta?.length" class="mt-mega__cta"><MtBtn v-for="b in item.cta" :key="b._uid" :button="b" /></div>
                <div class="mt-mega__cols" :style="{ '--cols': Math.max(1, item.columns?.length || 1) }">
                  <div v-for="col in item.columns" :key="col._uid" v-editable="col" class="mt-mega__col">
                    <p v-if="col.title" class="mt-mega__title">{{ col.title }}</p>
                    <ul>
                      <li v-for="l in col.links" :key="l._uid" v-editable="l">
                        <NuxtLink :to="href(l.link) || '/'" :class="{ 'is-highlight': l.highlight }">{{ l.label }}</NuxtLink>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
              <NuxtLink v-if="item.promo_image?.filename" :to="href(item.promo_link) || href(item.link) || '/'" class="mt-mega__promo">
                <MtMedia :asset="item.promo_image" cover :width="700" />
                <span v-if="item.promo_title" class="mt-mega__promo-title">{{ item.promo_title }} <MtIcon name="arrow" :size="18" /></span>
              </NuxtLink>
            </div>
          </template>
        </div>
      </Transition>
    </nav>
    <Transition name="mt-slide">
      <div v-if="drawer" class="mt-drawer mt-hide-desktop">
        <MtTrustpilot />
        <ul>
          <li v-for="item in nav" :key="item._uid" class="mt-drawer__item">
            <button type="button" class="mt-drawer__label" :aria-expanded="mobileOpen === item._uid" @click="mobileOpen = mobileOpen === item._uid ? null : item._uid">
              {{ (item.label || '').replace(/\n/g, ' ') }}
              <MtIcon name="chevron" :size="18" />
            </button>
            <div v-if="mobileOpen === item._uid" class="mt-drawer__panel">
              <NuxtLink v-if="href(item.link)" :to="href(item.link)" class="mt-drawer__all">Voir la rubrique</NuxtLink>
              <template v-for="col in item.columns" :key="col._uid">
                <p v-if="col.title" class="mt-mega__title">{{ col.title }}</p>
                <NuxtLink v-for="l in col.links" :key="l._uid" :to="href(l.link) || '/'">{{ l.label }}</NuxtLink>
              </template>
            </div>
          </li>
        </ul>
        <MtBtn v-for="b in config.header_buttons" :key="b._uid" :button="b" />
      </div>
    </Transition>
  </header>
</template>
