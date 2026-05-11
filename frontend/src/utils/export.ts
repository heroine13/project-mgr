// 导出工具函数

export const exportToExcel = (data: any[], filename: string, sheetName: string = 'Sheet1') => {
  // 简单实现：转换为CSV下载
  if (!data || data.length === 0) return
  
  const headers = Object.keys(data[0])
  const csvContent = [
    headers.join(','),
    ...data.map(row => headers.map(h => JSON.stringify(row[h] ?? '')).join(','))
  ].join('\n')
  
  downloadFile(csvContent, `${filename}.csv`, 'text/csv')
}

export const exportToJSON = (data: any[], filename: string) => {
  const jsonContent = JSON.stringify(data, null, 2)
  downloadFile(jsonContent, `${filename}.json`, 'application/json')
}

export const exportToPDF = (data: any[], filename: string) => {
  // 简单实现：打印窗口
  const printContent = `
    <html>
    <head><title>${filename}</title></head>
    <body>
      <pre>${JSON.stringify(data, null, 2)}</pre>
    </body>
    </html>
  `
  const printWindow = window.open('', '_blank')
  if (printWindow) {
    printWindow.document.write(printContent)
    printWindow.document.close()
    printWindow.print()
  }
}

const downloadFile = (content: string, filename: string, mimeType: string) => {
  const blob = new Blob([content], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}
