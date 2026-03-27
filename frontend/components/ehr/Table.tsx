import React from 'react';

interface Column<T> {
  header: string;
  accessor: keyof T | ((row: T) => React.ReactNode);
  width?: string;
}

interface TableProps<T> {
  columns: Column<T>[];
  data: T[];
  onRowClick?: (row: T) => void;
  emptyMessage?: string;
}

export function Table<T extends { id: string | number }>({ 
  columns, 
  data, 
  onRowClick,
  emptyMessage = 'No data available'
}: TableProps<T>) {
  return (
    <div className="w-full overflow-x-auto border-2 border-[#CCCCCC] rounded">
      <table className="w-full border-collapse">
        <thead>
          <tr className="bg-[#F5F5F5] border-b-2 border-[#CCCCCC]">
            {columns.map((column, idx) => (
              <th
                key={idx}
                className="px-4 py-3 text-left font-medium"
                style={{ width: column.width }}
              >
                {column.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.length === 0 ? (
            <tr>
              <td
                colSpan={columns.length}
                className="px-4 py-8 text-center text-[#333333]"
              >
                {emptyMessage}
              </td>
            </tr>
          ) : (
            data.map((row) => (
              <tr
                key={row.id}
                className={`border-b border-[#CCCCCC] ${
                  onRowClick ? 'cursor-pointer hover:bg-[#F5F5F5]' : ''
                }`}
                onClick={() => onRowClick?.(row)}
                role={onRowClick ? 'button' : undefined}
                tabIndex={onRowClick ? 0 : undefined}
                onKeyDown={
                  onRowClick
                    ? (e) => {
                        if (e.key === 'Enter' || e.key === ' ') {
                          e.preventDefault();
                          onRowClick(row);
                        }
                      }
                    : undefined
                }
              >
                {columns.map((column, idx) => (
                  <td key={idx} className="px-4 py-3">
                    {typeof column.accessor === 'function'
                      ? column.accessor(row)
                      : String(row[column.accessor])}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
