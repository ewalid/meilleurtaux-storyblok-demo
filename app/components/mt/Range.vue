<script setup>
// Slider + editable number field, for the simulators.
const props = defineProps({
  label: { type: String, required: true },
  min: { type: Number, default: 0 },
  max: { type: Number, default: 100 },
  step: { type: Number, default: 1 },
  unit: { type: String, default: '€' },
  id: { type: String, required: true },
});
const model = defineModel({ type: Number, default: 0 });
const pct = computed(() => `${((model.value - props.min) / (props.max - props.min || 1)) * 100}%`);
function onText(e) {
  const n = mtNumber(e.target.value, model.value);
  model.value = Math.min(props.max, Math.max(props.min, n));
}
</script>

<template>
  <div class="mt-range">
    <div class="mt-range__head">
      <label :for="id" class="mt-range__label">{{ label }}</label>
      <span class="mt-range__value">
        <input :value="mtFormat(model)" inputmode="numeric" :aria-label="`${label} (${unit})`" @change="onText" />
        <span>{{ unit }}</span>
      </span>
    </div>
    <input :id="id" v-model.number="model" type="range" :min="min" :max="max" :step="step" class="mt-range__input" :style="{ '--pct': pct }" />
    <div class="mt-range__scale"><span>{{ mtFormat(min) }} {{ unit }}</span><span>{{ mtFormat(max) }} {{ unit }}</span></div>
  </div>
</template>
