import * as React from "react";
import {
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Typography,
} from "@mui/material";
import TransactionRow from "./TransactionRow";


export default function TransactionsTable({ rows = [], totalRecords, fetchTransactions }) {

  const [page, setPage] = React.useState(0);
  const [rowsPerPage, setRowsPerPage] = React.useState(10);

  const handleChangePage = (_e, newPage) => { 
    setPage(newPage); 
    fetchTransactions(page + 1, rowsPerPage);
  }

  const handleChangeRowsPerPage = (e) => {
    const newRowsPerPage = parseInt(e.target.value, 10)
    setRowsPerPage(newRowsPerPage);
    setPage(0);
    fetchTransactions(1, newRowsPerPage);
  };

  const sliceStart = page * rowsPerPage;
  const paged = rows.slice(sliceStart, sliceStart + rowsPerPage);

  return (
    <Paper variant="outlined" sx={{ bgcolor: "background.paper" }}>
      <Box sx={{ p: 2, pb: 0 }}>
        <Typography variant="h6" sx={{ fontWeight: 600 }}>
          Payment Transactions
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {totalRecords} total
        </Typography>
      </Box>
      <TablePagination
        component="div"
        count={totalRecords}
        page={page}
        onPageChange={handleChangePage}
        rowsPerPage={rowsPerPage}
        onRowsPerPageChange={handleChangeRowsPerPage}
        rowsPerPageOptions={[5, 10, 25, 50]}
      />
      <TableContainer>
        <Table size="medium" aria-label="transactions table">
          <TableHead>
            <TableRow>
              <TableCell /> {/* expander column */}
              <TableCell>Date</TableCell>
              <TableCell>Merchant</TableCell>
              <TableCell>Mode</TableCell>
              <TableCell>Type</TableCell>
              <TableCell align="right">Amount</TableCell>
              <TableCell>Status</TableCell>
            </TableRow>
          </TableHead>

          <TableBody>
            {rows.map((r) => (
              <TransactionRow key={r.id} r={r} />
            ))}

            {rows.length === 0 && (
              <TableRow>
                <TableCell colSpan={7} align="center" sx={{ py: 6, color: "text.secondary" }}>
                  No transactions
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Paper>
  );
}
