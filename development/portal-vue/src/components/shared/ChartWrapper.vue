<template>
  <div class="card chart-wrapper" role="figure" :aria-label="title ? title + ' chart' : 'Data visualization'">
    <div v-if="title || subtitle" class="card-header">
      <div>
        <h3 v-if="title" class="card-title chart-title">{{ title }}</h3>
        <p v-if="subtitle" class="card-subtitle">{{ subtitle }}</p>
      </div>
    </div>

    <div class="chart-body">
      <!-- Loading state -->
      <template v-if="loading">
        <SkeletonLoader :height="height + 'px'" />
      </template>

      <!-- Error state -->
      <template v-else-if="error">
        <div class="chart-state">
          <span class="material-symbols-outlined chart-state-icon">error_outline</span>
          <p class="chart-state-text">Unable to load chart data</p>
          <button class="btn-ghost btn-sm" @click="$emit('retry')">Retry</button>
        </div>
      </template>

      <!-- Empty state -->
      <template v-else-if="!series || series.length === 0">
        <div class="chart-state">
          <span class="material-symbols-outlined chart-state-icon">bar_chart</span>
          <p class="chart-state-text">No data available for this period</p>
        </div>
      </template>

      <!-- Chart -->
      <template v-else>
        <apexchart
          :type="type"
          :options="chartOptions"
          :series="series"
          :height="height"
        />
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import VueApexCharts from 'vue3-apexcharts'
import { useThemeColors } from '@/composables/useThemeColors.js'
import SkeletonLoader from './SkeletonLoader.vue'

const apexchart = VueApexCharts

const props = defineProps({
  type: { type: String, required: true, validator: v => ['line', 'bar', 'heatmap'].includes(v) },
  series: { type: Array, required: true },
  title: { type: String, default: '' },
  subtitle: { type: String, default: '' },
  categories: { type: Array, default: () => [] },
  height: { type: Number, default: 240 },
  loading: { type: Boolean, default: false },
  error: { type: String, default: null },
})

const emit = defineEmits(['drill-down', 'retry'])

const { colors } = useThemeColors()

const chartOptions = computed(() => {
  const opts = {
    chart: {
      type: props.type,
      height: props.height,
      fontFamily: 'Inter, sans-serif',
      toolbar: { show: false },
      events: {
        dataPointSelection: (event, chartContext, config) => {
          emit('drill-down', {
            seriesIndex: config.seriesIndex,
            dataPointIndex: config.dataPointIndex,
            value: props.series[config.seriesIndex]?.data?.[config.dataPointIndex],
            category: props.categories?.[config.dataPointIndex],
          })
        },
      },
    },
    colors: [
      colors.value.primary,
      colors.value.success,
      colors.value.warning,
      colors.value.info,
      colors.value.secondary,
      colors.value.error,
    ],
    xaxis: {
      categories: props.categories,
    },
    tooltip: {
      theme: 'light',
    },
    grid: {
      borderColor: 'rgba(100, 116, 139, 0.15)',
    },
  }

  if (props.type === 'heatmap') {
    opts.plotOptions = {
      heatmap: {
        colorScale: {
          ranges: [
            { from: 0, to: 33, color: '#D1FAE5', name: 'Low' },
            { from: 34, to: 66, color: '#10B981', name: 'Medium' },
            { from: 67, to: 100, color: '#065F46', name: 'High' },
          ],
        },
      },
    }
  }

  return opts
})
</script>

<style scoped>
.chart-wrapper {
  background: var(--bg-card);
  border-color: var(--border-default);
}

.chart-title {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
}

.chart-body {
  padding: var(--space-2) 0 0 0;
}

.chart-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  gap: var(--space-3);
}

.chart-state-icon {
  font-size: 48px;
  color: var(--gray-300);
}

.chart-state-text {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin: 0;
}
</style>
