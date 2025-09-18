import React, { useEffect, useState } from "react";
import useTransactions from "./useTransactions";
import { Container, Box, Typography } from "@mui/material";
import TransactionsTable from "./TransactionsTable";
import TransactionFilters from "./TransactionFilters";
import { filtersDefaultState } from "../../utils/constants";
import { useUser } from "../../context/UserContext";

function Transactions() {
  const { fetchTransactions, transactionsData, transactionsLoading } =
    useTransactions();

  const { user } = useUser();

  const [filters, setFilters] = useState(filtersDefaultState);
  const [pagination, setPagination] = useState({
    page: 0,
    rowsPerPage: 10,
  });

  useEffect(() => {
    if (user) {
      fetchTransactions(pagination, filters);
    }
  }, [user]);

  return (
    <Container maxWidth="lg" sx={{ py: { xs: 5, md: 8 } }}>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 700 }}>
          Transactions
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Recent payments and transfers
        </Typography>
      </Box>

      <Box sx={{ mb: 3 }}>
        <TransactionFilters
          value={filters}
          onChange={setFilters}
          onApply={fetchTransactions}
          loading={transactionsLoading}
          pagination={pagination}
          setPagination={setPagination}
        />
      </Box>

      <TransactionsTable
        rows={transactionsData.items}
        totalRecords={transactionsData.total_records}
        fetchTransactions={fetchTransactions}
        pagination={pagination}
        setPagination={setPagination}
        filters={filters}
      />
    </Container>
  );
}

export default Transactions;
