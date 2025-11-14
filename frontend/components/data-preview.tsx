'use client'

interface DataPreviewProps {
  data: any[]
}

export function DataPreview({ data }: DataPreviewProps) {
  if (!data || data.length === 0) {
    return <p className="text-muted-foreground">No data to preview</p>
  }

  const columns = Object.keys(data[0] || {})
  const rows = data.slice(0, 10)

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border">
            {columns.map(col => (
              <th
                key={col}
                className="text-left px-4 py-3 font-semibold text-foreground bg-muted/50"
              >
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, idx) => (
            <tr key={idx} className="border-b border-border hover:bg-muted/30">
              {columns.map(col => (
                <td
                  key={`${idx}-${col}`}
                  className="px-4 py-3 text-foreground"
                >
                  {String(row[col] || '-')}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      {data.length > 10 && (
        <p className="text-sm text-muted-foreground mt-4">
          Showing 10 of {data.length} rows
        </p>
      )}
    </div>
  )
}
