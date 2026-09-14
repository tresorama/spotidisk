import type { ColumnDef } from "@tanstack/react-table";
import {
  flexRender,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { cn } from "#/lib/utils";

type DataTableProps<TData, TValue> = {
  columns: ColumnDef<TData, TValue>[];
  data: TData[];
  classNameWrapper?: React.ComponentProps<'div'>['className'];
  classNameTable?: React.ComponentProps<'table'>['className'];
  classNameTHead?: React.ComponentProps<'thead'>['className'];
  classNameTHeadTr?: React.ComponentProps<'tr'>['className'];
  classNameTHeadTh?: React.ComponentProps<'th'>['className'];
  classNameTBody?: React.ComponentProps<'tbody'>['className'];
  classNameTBodyTr?: React.ComponentProps<'tr'>['className'];
  classNameTBodyTd?: React.ComponentProps<'td'>['className'];
} & Omit<React.ComponentProps<'div'>, 'children' | 'className'>;

export function DataTable<TData, TValue>({
  columns,
  data,
  classNameWrapper,
  classNameTable,
  classNameTHead,
  classNameTHeadTr,
  classNameTHeadTh,
  classNameTBody,
  classNameTBodyTr,
  classNameTBodyTd,
  ...htmlProps
}: DataTableProps<TData, TValue>) {
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  return (
    <div
      data-comp="DataTable"
      className={cn("rounded-md border overflow-hidden", classNameWrapper)}
      {...htmlProps}
    >
      <Table
        aria-label="Table"
        className={classNameTable}
      >
        <TableHeader
          aria-label="Table Header"
          className={cn("", classNameTHead)}
        >
          {table.getHeaderGroups().map((headerGroup) => (
            <TableRow
              key={headerGroup.id}
              aria-label={"Header Group " + headerGroup.id}
              className={classNameTHeadTr}
            >
              {headerGroup.headers.map((header) => {
                return (
                  <TableHead
                    key={header.id}
                    aria-label={"Header " + header.column.columnDef.id}
                    style={{
                      width: header.column.getSize(),
                      minWidth: header.column.columnDef.minSize,
                      maxWidth: header.column.columnDef.maxSize,
                    }}
                    className={classNameTHeadTh}
                  >
                    {header.isPlaceholder
                      ? null
                      : flexRender(
                        header.column.columnDef.header,
                        header.getContext()
                      )}
                  </TableHead>
                );
              })}
            </TableRow>
          ))}
        </TableHeader>
        <TableBody
          aria-label="Table Body"
          className={classNameTBody}
        >
          {table.getRowModel().rows?.length ? (
            table.getRowModel().rows.map((row) => (
              <TableRow
                key={row.id}
                aria-label={"Item " + row.id}
                data-state={row.getIsSelected() && "selected"}
                className={classNameTBodyTr}
              >
                {row.getVisibleCells().map((cell) => (
                  <TableCell
                    key={cell.id}
                    aria-label={cell.column.columnDef.id}
                    className={classNameTBodyTd}
                  >
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </TableCell>
                ))}
              </TableRow>
            ))
          ) : (
            <TableRow>
              <TableCell
                colSpan={columns.length}
                className="h-24 text-center"
              >
                No results.
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </div>
  );
}
