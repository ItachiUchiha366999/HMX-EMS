import { describe, it, expect, vi, beforeEach } from 'vitest'

const { mockAddRow, mockWorksheet, mockWriteBuffer, mockWorkbook } = vi.hoisted(() => {
  const mockAddRow = vi.fn().mockReturnValue({
    eachCell: vi.fn((cb) => {
      cb({ font: {}, fill: {}, alignment: {} })
    }),
  })
  const mockWorksheet = {
    addRow: mockAddRow,
    columns: [],
  }
  const mockWriteBuffer = vi.fn().mockResolvedValue(new ArrayBuffer(8))
  const mockWorkbook = {
    addWorksheet: vi.fn().mockReturnValue(mockWorksheet),
    xlsx: { writeBuffer: mockWriteBuffer },
  }
  return { mockAddRow, mockWorksheet, mockWriteBuffer, mockWorkbook }
})

vi.mock('exceljs', () => ({
  Workbook: vi.fn().mockImplementation(() => mockWorkbook),
}))

vi.mock('../useToast.js', () => ({
  useToast: () => ({
    show: vi.fn(),
  }),
}))

// Mock URL and document APIs
global.URL.createObjectURL = vi.fn(() => 'blob:test')
global.URL.revokeObjectURL = vi.fn()

import { useExportExcel } from '../useExportExcel.js'

describe('useExportExcel', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockWorksheet.columns = []
  })

  it('generates Excel workbook with header row and data rows', async () => {
    const { exportToExcel } = useExportExcel()

    await exportToExcel({
      title: 'Test',
      columns: [{ header: 'Name', accessorKey: 'name' }],
      rows: [{ name: 'Alice' }],
    })

    expect(mockWorkbook.addWorksheet).toHaveBeenCalledWith('Test')
    expect(mockAddRow).toHaveBeenCalledWith(['Name'])
    expect(mockAddRow).toHaveBeenCalledWith(['Alice'])
    expect(mockWriteBuffer).toHaveBeenCalled()
  })

  it('applies auto-width to columns', async () => {
    mockWorksheet.columns = [{}]

    const { exportToExcel } = useExportExcel()

    await exportToExcel({
      title: 'Test',
      columns: [{ header: 'Name', accessorKey: 'name' }],
      rows: [{ name: 'Alice' }],
    })

    expect(mockWorksheet.columns[0].width).toBeGreaterThan(0)
  })
})
