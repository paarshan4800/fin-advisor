import React, { useMemo, useState } from "react";
import {
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TableSortLabel,
  Paper,
} from "@mui/material";

// Simple number formatter (customize currency/locale if needed)
const formatNumber = (n) =>
  typeof n === "number"
    ? new Intl.NumberFormat(undefined, { maximumFractionDigits: 2 }).format(n)
    : n;

function AppTable({ visualization }) {
  const { headers = [], rows = [], text_summary } = visualization;

  // Infer which columns are numeric by checking the first non-null value in each column
  const numericCols = useMemo(() => {
    return headers.map((_, colIdx) => {
      const sample = rows.find(
        (r) => r[colIdx] !== null && r[colIdx] !== undefined
      )?.[colIdx];
      return typeof sample === "number";
    });
  }, [headers, rows]);

  // Sorting state
  const [orderBy, setOrderBy] = useState(0); // default: first column
  const [order, setOrder] = useState("asc"); // 'asc' | 'desc'

  const sortedRows = useMemo(() => {
    const sorted = [...rows].sort((a, b) => {
      const va = a[orderBy];
      const vb = b[orderBy];

      // Handle undefined/null consistently
      if (va == null && vb == null) return 0;
      if (va == null) return order === "asc" ? 1 : -1;
      if (vb == null) return order === "asc" ? -1 : 1;

      if (numericCols[orderBy]) {
        return order === "asc" ? va - vb : vb - va;
      }
      // string compare
      const sa = String(va).toLowerCase();
      const sb = String(vb).toLowerCase();
      if (sa < sb) return order === "asc" ? -1 : 1;
      if (sa > sb) return order === "asc" ? 1 : -1;
      return 0;
    });
    return sorted;
  }, [rows, orderBy, order, numericCols]);

  const handleSort = (colIdx) => () => {
    if (orderBy === colIdx) {
      setOrder((prev) => (prev === "asc" ? "desc" : "asc"));
    } else {
      setOrderBy(colIdx);
      setOrder("asc");
    }
  };

  const empty = headers.length === 0 || rows.length === 0;

  return (
    <Card
      sx={{
        width: 1,
        minWidth: 0,
        height: "100%",
        p: 2,
        boxShadow: 3,
        borderRadius: 3,
      }}
    >
      <CardContent sx={{ p: 0 }}>
        <Typography variant="h6" sx={{ px: 2, pt: 2, pb: 1 }}>
          Table
        </Typography>

        <TableContainer
          component={Paper}
          elevation={0}
          sx={{ maxHeight: 420, overflow: "auto" }}
        >
          <Table stickyHeader size="small" aria-label="visualization table">
            <TableHead>
              <TableRow>
                {headers.map((h, idx) => (
                  <TableCell
                    key={h + idx}
                    align={numericCols[idx] ? "right" : "left"}
                    sortDirection={orderBy === idx ? order : false}
                    sx={{
                      fontWeight: 600,
                      whiteSpace: "normal",
                      wordBreak: "break-word",
                    }}
                  >
                    <TableSortLabel
                      active={orderBy === idx}
                      direction={orderBy === idx ? order : "asc"}
                      onClick={handleSort(idx)}
                    >
                      {h}
                    </TableSortLabel>
                  </TableCell>
                ))}
              </TableRow>
            </TableHead>

            <TableBody>
              {empty ? (
                <TableRow>
                  <TableCell
                    colSpan={headers.length}
                    align="center"
                    sx={{ py: 6, color: "text.secondary" }}
                  >
                    No data available
                  </TableCell>
                </TableRow>
              ) : (
                sortedRows.map((row, rIdx) => (
                  <TableRow key={`row-${rIdx}`} hover>
                    {row.map((cell, cIdx) => (
                      <TableCell
                        key={`cell-${rIdx}-${cIdx}`}
                        align={numericCols[cIdx] ? "right" : "left"}
                        sx={{
                          whiteSpace: "normal",
                          wordBreak: "break-word",
                        }}
                      >
                        {numericCols[cIdx] ? formatNumber(cell) : String(cell)}
                      </TableCell>
                    ))}
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>

        {text_summary && (
          <Typography
            variant="body2"
            color="text.secondary"
            sx={{ mt: 2, px: 2, pb: 1 }}
          >
            {text_summary}
          </Typography>
        )}
      </CardContent>
    </Card>
  );
}

export default AppTable;
