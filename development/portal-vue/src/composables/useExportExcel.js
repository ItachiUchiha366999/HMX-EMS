import { useToast } from './useToast.js'

export function useExportExcel() {
  const { show } = useToast()

  async function exportToExcel({ title, columns, rows }) {
    try {
      const ExcelJS = await import('exceljs')
      const workbook = new ExcelJS.Workbook()
      const worksheet = workbook.addWorksheet(title.substring(0, 31))

      // Header row
      const headerRow = worksheet.addRow(columns.map(c => c.header))
      headerRow.eachCell(cell => {
        cell.font = { bold: true, color: { argb: 'FFFFFFFF' } }
        cell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF4F46E5' } }
        cell.alignment = { horizontal: 'left' }
      })

      // Data rows
      rows.forEach(row => {
        worksheet.addRow(columns.map(c => row[c.accessorKey] ?? ''))
      })

      // Auto-width columns
      worksheet.columns.forEach((column, i) => {
        let maxLength = columns[i]?.header?.length || 10
        rows.forEach(row => {
          const val = String(row[columns[i]?.accessorKey] ?? '')
          if (val.length > maxLength) maxLength = val.length
        })
        column.width = Math.min(maxLength + 4, 50)
      })

      // Download
      const buffer = await workbook.xlsx.writeBuffer()
      const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${title}.xlsx`
      a.click()
      URL.revokeObjectURL(url)

      show('Exported to Excel', 'success')
    } catch (e) {
      show('Export failed. Please try again or reduce the data range.', 'error')
      throw e
    }
  }

  return { exportToExcel }
}
