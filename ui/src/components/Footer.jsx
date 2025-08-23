import React from 'react'
import {
  Typography,
  Box,
} from "@mui/material";

function Footer() {
    return (
        <Box sx={{ py: 4, textAlign: "center", color: "text.secondary" }}>
            <Typography variant="caption">
                © {new Date().getFullYear()} SpendSmart
            </Typography>
        </Box>
    )
}

export default Footer