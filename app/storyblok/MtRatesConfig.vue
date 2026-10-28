<script setup>
// Editing the rate sheet: show where the rates are used, live from the draft.
const props = defineProps({ blok: { type: Object, required: true } });
const sheet = useState('mtRates');
watchEffect(() => {
  sheet.value = props.blok;
});
const preview = { _uid: 'rates-preview', component: 'mt-rates', layout: 'table', title: 'Aperçu : tableau des taux', show_trend: true, show_date: true, background: 'white' };
const sim = { _uid: 'sim-preview', component: 'mt-simulator', type: 'project', layout: 'with_rates', title: 'Aperçu : simulateur', rates_title: 'Les taux nationaux pour un prêt immo', background: 'cream' };
</script>

<template>
  <div v-editable="blok">
    <div class="mt-theme-cream" style="padding: 3rem 0 1rem">
      <div class="mt-wrap mt-w-standard">
        <p class="mt-eyebrow">Barème des taux</p>
        <h1 class="mt-h mt-h--m">Ces taux alimentent tout le site</h1>
        <p class="mt-lead">Tuiles de l'accueil, simulateurs et tableaux lisent ce barème. Modifiez un taux : l'aperçu ci-dessous se met à jour, et toutes les pages changent à la publication.</p>
      </div>
    </div>
    <MtRates :blok="preview" />
    <MtSimulator :blok="sim" />
  </div>
</template>
