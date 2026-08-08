"use client";

import React from "react";
import { DataTableWidgetPayload } from "../types";
import { Table as TableIcon } from "lucide-react";

export function DataTable(props: DataTableWidgetPayload) {
  const { title, columns = [], rows = [] } = props;

  return (
    <div className="w-full glass-panel rounded-2xl p-4 border border-gray-800 my-3 overflow-hidden shadow-lg">
      {title && (
        <div className="flex items-center gap-2 mb-3 pb-2 border-b border-gray-800 text-sm font-semibold text-gray-200">
          <TableIcon className="h-4 w-4 text-indigo-400" />
          <span>{title}</span>
        </div>
      )}

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-gray-300">
          <thead className="bg-gray-900/80 text-gray-400 uppercase font-semibold tracking-wider text-[10px]">
            <tr>
              {columns.map((col, idx) => (
                <th key={idx} className="px-3 py-2.5 rounded-lg">
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800/60">
            {rows.map((row, rIdx) => (
              <tr key={rIdx} className="hover:bg-gray-800/40 transition-colors">
                {columns.map((col, cIdx) => (
                  <td key={cIdx} className="px-3 py-2.5 font-medium whitespace-nowrap">
                    {row[col] ?? row[col.toLowerCase()] ?? "-"}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
