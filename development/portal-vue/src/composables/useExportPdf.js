import jsPDF from 'jspdf'
import autoTable from 'jspdf-autotable'
import { useToast } from './useToast.js'

export function useExportPdf() {
  const { show } = useToast()

  function exportToPdf({ title, columns, rows }) {
    try {
      const doc = new jsPDF()
      doc.setFontSize(16)
      doc.text(title, 14, 20)
      doc.setFontSize(8)
      doc.text(`Generated: ${new Date().toLocaleString()}`, 14, 28)

      autoTable(doc, {
        startY: 35,
        head: [columns.map(c => c.header)],
        body: rows.map(row => columns.map(c => row[c.accessorKey] ?? '')),
        headStyles: { fillColor: [79, 70, 229] },
        alternateRowStyles: { fillColor: [248, 250, 252] },
        styles: { fontSize: 9, cellPadding: 4 },
      })

      doc.save(`${title}.pdf`)
      show('Exported to PDF', 'success')
    } catch (e) {
      show('Export failed. Please try again or reduce the data range.', 'error')
      throw e
    }
  }

  return { exportToPdf }
}
