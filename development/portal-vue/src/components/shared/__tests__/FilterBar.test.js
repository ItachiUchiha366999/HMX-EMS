import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import FilterBar from '../FilterBar.vue'

describe('FilterBar', () => {
  it('renders date range, academic year, department, and program selectors', () => {
    const wrapper = mount(FilterBar, {
      props: {
        academicYears: ['2024-25', '2025-26'],
        departments: ['CS', 'EE'],
        programs: ['BTech', 'MTech'],
      },
    })
    // date inputs
    const dateInputs = wrapper.findAll('input[type="date"]')
    expect(dateInputs.length).toBe(2)
    // select elements
    const selects = wrapper.findAll('select')
    expect(selects.length).toBeGreaterThanOrEqual(3)
  })

  it('emits filter-change event when Apply Filters button is clicked', async () => {
    const wrapper = mount(FilterBar, {
      props: {
        academicYears: ['2024-25'],
        departments: ['CS'],
        programs: ['BTech'],
      },
    })
    const applyBtn = wrapper.findAll('button').find(b => b.text().includes('Apply Filters'))
    expect(applyBtn).toBeDefined()
    await applyBtn.trigger('click')
    expect(wrapper.emitted('filter-change')).toBeTruthy()
    expect(wrapper.emitted('filter-change')[0][0]).toHaveProperty('dateFrom')
    expect(wrapper.emitted('filter-change')[0][0]).toHaveProperty('academicYear')
  })

  it('resets all filters when Clear Filters button is clicked', async () => {
    const wrapper = mount(FilterBar, {
      props: {
        academicYears: ['2024-25'],
        departments: ['CS'],
        programs: ['BTech'],
      },
    })
    // Set a value first
    const selects = wrapper.findAll('select')
    if (selects.length > 0) {
      await selects[0].setValue('2024-25')
    }
    const clearBtn = wrapper.findAll('button').find(b => b.text().includes('Clear Filters'))
    expect(clearBtn).toBeDefined()
    await clearBtn.trigger('click')
    expect(wrapper.emitted('filter-change')).toBeTruthy()
    const lastEmit = wrapper.emitted('filter-change').at(-1)[0]
    expect(lastEmit.academicYear).toBe('')
    expect(lastEmit.department).toBe('')
    expect(lastEmit.program).toBe('')
  })

  it('populates academic year options from academicYears prop', () => {
    const wrapper = mount(FilterBar, {
      props: {
        academicYears: ['2024-25', '2025-26'],
        departments: [],
        programs: [],
      },
    })
    const options = wrapper.findAll('option')
    const optionTexts = options.map(o => o.text())
    expect(optionTexts).toContain('2024-25')
    expect(optionTexts).toContain('2025-26')
  })
})
