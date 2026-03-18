import { ref } from 'vue'
import { useFrappe } from './useFrappe.js'

export function useReportRunner() {
  const { call } = useFrappe()
  const columns = ref([])
  const rows = ref([])
  const filters = ref([])
  const reportLoading = ref(false)
  const reportError = ref(null)

  async function loadReportMeta(reportName) {
    reportError.value = null
    try {
      const result = await call('frappe.desk.query_report.get_script', {
        report_name: reportName
      })
      // get_script returns { script, filters, ... }
      if (result.filters && Array.isArray(result.filters)) {
        filters.value = result.filters
      } else if (result.script) {
        // Parse filters from the JS script string
        try {
          const filterMatch = result.script.match(/filters\s*:\s*(\[[\s\S]*?\])\s*[,}]/)
          if (filterMatch) {
            filters.value = new Function('return ' + filterMatch[1])()
          }
        } catch (parseErr) {
          console.warn('Could not parse report filters from script:', parseErr)
          filters.value = []
        }
      }
      return result
    } catch (e) {
      reportError.value = e.message
      throw e
    }
  }

  async function runReport(reportName, reportFilters = {}) {
    reportLoading.value = true
    reportError.value = null
    try {
      const result = await call('frappe.desk.query_report.run', {
        report_name: reportName,
        filters: JSON.stringify(reportFilters)
      })
      // Normalize columns: Frappe returns either strings or objects
      columns.value = (result.columns || []).map(col => {
        if (typeof col === 'string') {
          const parts = col.split(':')
          return { header: parts[0], accessorKey: parts[0].toLowerCase().replace(/\s+/g, '_'), fieldtype: parts[1] || 'Data' }
        }
        return {
          header: col.label || col.fieldname,
          accessorKey: col.fieldname || col.label?.toLowerCase().replace(/\s+/g, '_'),
          fieldtype: col.fieldtype || 'Data'
        }
      })
      // Normalize rows: Frappe returns array of arrays or array of objects
      if (result.result && result.result.length > 0) {
        if (Array.isArray(result.result[0])) {
          rows.value = result.result.map(row => {
            const obj = {}
            columns.value.forEach((col, i) => { obj[col.accessorKey] = row[i] })
            return obj
          })
        } else {
          rows.value = result.result
        }
      } else {
        rows.value = []
      }
      return { columns: columns.value, rows: rows.value }
    } catch (e) {
      reportError.value = e.message
      throw e
    } finally {
      reportLoading.value = false
    }
  }

  return { loadReportMeta, runReport, columns, rows, filters, loading: reportLoading, error: reportError }
}
