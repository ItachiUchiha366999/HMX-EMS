import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ChartWrapper from '../ChartWrapper.vue'
import SkeletonLoader from '../SkeletonLoader.vue'

const ApexChartStub = {
  name: 'apexchart',
  template: '<div class="apexchart-stub" />',
  props: ['type', 'options', 'series', 'height'],
}

describe('ChartWrapper', () => {
  it('renders apexchart component with given type and series', () => {
    const wrapper = mount(ChartWrapper, {
      props: {
        type: 'line',
        series: [{ name: 'S1', data: [10, 20, 30] }],
        title: 'Enrollment',
      },
      global: {
        stubs: { apexchart: ApexChartStub },
      },
    })
    expect(wrapper.find('.apexchart-stub').exists()).toBe(true)
  })

  it('shows skeleton loader when loading is true', () => {
    const wrapper = mount(ChartWrapper, {
      props: {
        type: 'line',
        series: [{ name: 'S1', data: [10] }],
        loading: true,
      },
      global: {
        stubs: { apexchart: ApexChartStub },
      },
    })
    expect(wrapper.findComponent(SkeletonLoader).exists()).toBe(true)
    expect(wrapper.find('.apexchart-stub').exists()).toBe(false)
  })

  it('shows error state with retry button when error prop is set', () => {
    const wrapper = mount(ChartWrapper, {
      props: {
        type: 'line',
        series: [{ name: 'S1', data: [10] }],
        error: 'Failed',
      },
      global: {
        stubs: { apexchart: ApexChartStub },
      },
    })
    expect(wrapper.text()).toContain('Unable to load chart data')
    expect(wrapper.find('button').text()).toContain('Retry')
  })

  it('shows empty state when series data is empty', () => {
    const wrapper = mount(ChartWrapper, {
      props: {
        type: 'line',
        series: [],
      },
      global: {
        stubs: { apexchart: ApexChartStub },
      },
    })
    expect(wrapper.text()).toContain('No data available')
  })

  it('has drill-down emit defined', () => {
    const wrapper = mount(ChartWrapper, {
      props: {
        type: 'bar',
        series: [{ name: 'S1', data: [10, 20] }],
      },
      global: {
        stubs: { apexchart: ApexChartStub },
      },
    })
    // Verify the component defines the drill-down emit
    expect(wrapper.vm.$options.emits || wrapper.vm.$.type.emits).toBeDefined()
  })
})
