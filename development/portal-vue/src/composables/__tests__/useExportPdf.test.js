import { describe, it, expect, vi, beforeEach } from 'vitest'

const { mockSave, mockText, mockSetFontSize, mockAutoTable } = vi.hoisted(() => ({
  mockSave: vi.fn(),
  mockText: vi.fn(),
  mockSetFontSize: vi.fn(),
  mockAutoTable: vi.fn(),
}))

vi.mock('jspdf', () => ({
  default: vi.fn().mockImplementation(() => ({
    save: mockSave,
    text: mockText,
    setFontSize: mockSetFontSize,
  })),
}))

vi.mock('jspdf-autotable', () => ({
  default: mockAutoTable,
}))

vi.mock('../useToast.js', () => ({
  useToast: () => ({
    show: vi.fn(),
  }),
}))

import { useExportPdf } from '../useExportPdf.js'

describe('useExportPdf', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('generates PDF with title, columns, and rows', () => {
    const { exportToPdf } = useExportPdf()

    exportToPdf({
      title: 'Test',
      columns: [{ header: 'Name', accessorKey: 'name' }],
      rows: [{ name: 'Alice' }],
    })

    expect(mockText).toHaveBeenCalledWith('Test', 14, 20)
    expect(mockAutoTable).toHaveBeenCalledWith(
      expect.anything(),
      expect.objectContaining({
        head: [['Name']],
        body: [['Alice']],
      })
    )
  })

  it('calls doc.save with the title as filename', () => {
    const { exportToPdf } = useExportPdf()

    exportToPdf({
      title: 'Test',
      columns: [{ header: 'Name', accessorKey: 'name' }],
      rows: [{ name: 'Alice' }],
    })

    expect(mockSave).toHaveBeenCalledWith('Test.pdf')
  })
})
