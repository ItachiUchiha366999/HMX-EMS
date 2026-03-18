import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'

// Mock useFrappe
const mockCall = vi.fn()
vi.mock('../../../composables/useFrappe.js', () => ({
  useFrappe: () => ({
    call: mockCall,
    loading: { value: false },
    error: { value: null },
  }),
}))

// Mock export composables (used by DataTable internally)
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

import ReportViewer from '../ReportViewer.vue'

describe('ReportViewer', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // Default: get_script returns filters, run returns data
    mockCall.mockImplementation((method) => {
      if (method === 'frappe.desk.query_report.get_script') {
        return Promise.resolve({
          filters: [
            { fieldname: 'department', label: 'Department', fieldtype: 'Link', options: 'Department' },
          ],
        })
      }
      if (method === 'frappe.desk.query_report.run') {
        return Promise.resolve({
          columns: [{ label: 'Name', fieldname: 'name', fieldtype: 'Data' }],
          result: [{ name: 'Test' }],
        })
      }
      return Promise.resolve({})
    })
  })

  it('renders the report name as heading', async () => {
    const wrapper = mount(ReportViewer, {
      props: { reportName: 'Faculty Workload Summary' },
    })
    await flushPromises()

    expect(wrapper.text()).toContain('Faculty Workload Summary')
  })

  it('renders filter inputs from report filter definitions', async () => {
    const wrapper = mount(ReportViewer, {
      props: { reportName: 'Faculty Workload Summary' },
    })
    await flushPromises()

    // Should have loaded report meta via get_script
    expect(mockCall).toHaveBeenCalledWith('frappe.desk.query_report.get_script', {
      report_name: 'Faculty Workload Summary',
    })

    // Filter input should be rendered with label
    expect(wrapper.text()).toContain('Department')
    const inputs = wrapper.findAll('.form-input')
    expect(inputs.length).toBeGreaterThan(0)
  })

  it('calls run report when Run Report button clicked', async () => {
    const wrapper = mount(ReportViewer, {
      props: { reportName: 'Faculty Workload Summary' },
    })
    await flushPromises()

    const runBtn = wrapper.find('button')
    const runReportBtn = wrapper.findAll('button').find(b => b.text().includes('Run Report'))
    expect(runReportBtn).toBeTruthy()

    await runReportBtn.trigger('click')
    await flushPromises()

    // Should call run with JSON stringified filters
    expect(mockCall).toHaveBeenCalledWith('frappe.desk.query_report.run', expect.objectContaining({
      report_name: 'Faculty Workload Summary',
    }))
  })

  it('renders results in DataTable component', async () => {
    const wrapper = mount(ReportViewer, {
      props: { reportName: 'Faculty Workload Summary' },
    })
    await flushPromises()

    // Click Run Report
    const runReportBtn = wrapper.findAll('button').find(b => b.text().includes('Run Report'))
    await runReportBtn.trigger('click')
    await flushPromises()

    // DataTable should be rendered with data
    const dataTable = wrapper.findComponent({ name: 'DataTable' })
    expect(dataTable.exists()).toBe(true)
  })

  it('shows error alert when report fails to load', async () => {
    mockCall.mockImplementation((method) => {
      if (method === 'frappe.desk.query_report.get_script') {
        return Promise.resolve({ filters: [] })
      }
      if (method === 'frappe.desk.query_report.run') {
        return Promise.reject(new Error('Server error'))
      }
      return Promise.resolve({})
    })

    const wrapper = mount(ReportViewer, {
      props: { reportName: 'Faculty Workload Summary' },
    })
    await flushPromises()

    // Click Run Report
    const runReportBtn = wrapper.findAll('button').find(b => b.text().includes('Run Report'))
    await runReportBtn.trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('Report failed to load')
  })
})
