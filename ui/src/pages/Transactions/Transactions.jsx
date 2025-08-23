import React, { useEffect } from 'react'
import useTransactions from './useTransactions'
import { Container, Box, Typography } from "@mui/material";
import TransactionsTable from "./TransactionsTable";

function Transactions() {

  const { fetchTransactions, transactionsData } = useTransactions();  

  useEffect(() => {
    fetchTransactions();
  }, [])

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

      <TransactionsTable rows={transactionsData.items} totalRecords={transactionsData.total_records} fetchTransactions={fetchTransactions} />
    </Container>
  )
}

export default Transactions