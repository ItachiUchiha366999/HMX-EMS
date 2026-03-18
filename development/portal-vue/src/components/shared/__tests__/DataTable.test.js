import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'

// Mock export composables
vi.mock('../../../composables/useExportPdf.js', () => ({
  useExportPdf: () => ({
    exportToPdf: vi.fn(),
  }),
}))

vi.mock('../../../composables/useExportExcel.js', () => ({
  useExportExcel: () => ({
    exportToExcel: vi.fn(),
  }),
}))

import DataTable from '../DataTable.vue'

const columns = [
  { accessorKey: 'name', header: 'Name' },
  { accessorKey: 'dept', header: 'Dept' },
]

const data = [
  { name: 'Alice', dept: 'CS' },
  { name: 'Bob', dept: 'EE' },
]

describe('DataTable', () => {
  it('renders column headers and row data', () => {
    const wrapper = mount(DataTable, {
      props: { columns, data, totalRows: 2 },
    })

    const headers = wrapper.findAll('th')
    expect(headers.length).toBeGreaterThanOrEqual(2)
    const headerTexts = headers.map(h => h.text())
    expect(headerTexts).toContain('Name')
    expect(headerTexts).toContain('Dept')

    const cells = wrapper.findAll('td')
    const cellTexts = cells.map(c => c.text())
    expect(cellTexts).toContain('Alice')
    expect(cellTexts).toContain('Bob')
  })

  it('emits sort-change when sortable column header clicked', async () => {
    const sortableColumns = [
      { accessorKey: 'name', header: 'Name', sortable: true },
      { accessorKey: 'dept', header: 'Dept' },
    ]
    const wrapper = mount(DataTable, {
      props: { columns: sortableColumns, data, totalRows: 2 },
    })

    const sortableHeader = wrapper.findAll('th').find(th => th.text().includes('Name'))
    await sortableHeader.trigger('click')

    expect(wrapper.emitted('sort-change')).toBeTruthy()
    expect(wrapper.emitted('sort-change')[0][0]).toHaveProperty('id', 'name')
  })

  it('emits page-change when pagination button clicked', async () => {
    const wrapper = mount(DataTable, {
      props: { columns, data, totalRows: 2, pageSize: 1 },
    })

    expect(wrapper.text()).toContain('Showing')
    expect(wrapper.text()).toContain('of 2')

    // Find page 2 button or next button
    const pageButtons = wrapper.findAll('.data-table__pagination button')
    const page2Btn = pageButtons.find(b => b.text() === '2')
    const nextBtn = page2Btn || pageButtons.find(b => b.text().includes('navigate_next') || b.attributes('aria-label') === 'Next page')
    if (nextBtn) {
      await nextBtn.trigger('click')
      expect(wrapper.emitted('page-change')).toBeTruthy()
    }
  })

  it('emits selection-change when row checkbox toggled', async () => {
    const wrapper = mount(DataTable, {
      props: { columns, data, totalRows: 2, selectable: true },
    })

    const checkboxes = wrapper.findAll('input[type="checkbox"]')
    expect(checkboxes.length).toBeGreaterThanOrEqual(2)

    // Toggle first row checkbox (index 1, index 0 is header)
    await checkboxes[1].setValue(true)

    expect(wrapper.emitted('selection-change')).toBeTruthy()
  })

  it('shows search input and emits search-change on input', async () => {
    const wrapper = mount(DataTable, {
      props: { columns, data, totalRows: 2 },
    })

    const searchInput = wrapper.find('.data-table__search')
    expect(searchInput.exists()).toBe(true)

    await searchInput.setValue('Alice')
    // Wait for debounce (300ms)
    await new Promise(resolve => setTimeout(resolve, 350))

    expect(wrapper.emitted('search-change')).toBeTruthy()
    expect(wrapper.emitted('search-change')[0][0]).toBe('Alice')
  })

  it('shows skeleton rows when loading is true', () => {
    const wrapper = mount(DataTable, {
      props: { columns, data: [], totalRows: 0, loading: true },
    })

    expect(wrapper.findAll('.skeleton').length).toBeGreaterThan(0)
  })

  it('shows empty state when data array is empty', () => {
    const wrapper = mount(DataTable, {
      props: { columns, data: [], totalRows: 0 },
    })

    expect(wrapper.text()).toContain('No records found')
  })

  it('has export PDF button with correct aria-label', () => {
    const wrapper = mount(DataTable, {
      props: { columns, data, totalRows: 2 },
    })

    const pdfBtn = wrapper.find('[aria-label="Export to PDF"]')
    expect(pdfBtn.exists()).toBe(true)
  })

  it('has export Excel button with correct aria-label', () => {
    const wrapper = mount(DataTable, {
      props: { columns, data, totalRows: 2 },
    })

    const excelBtn = wrapper.find('[aria-label="Export to Excel"]')
    expect(excelBtn.exists()).toBe(true)
  })
})
