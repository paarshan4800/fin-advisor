import * as React from "react";
import {
  Box,
  TableCell,
  TableRow,
  Chip,
  Typography,
  IconButton,
  Collapse,
  Divider,
  Stack,
} from "@mui/material";
import KeyboardArrowDownIcon from "@mui/icons-material/KeyboardArrowDown";
import KeyboardArrowUpIcon from "@mui/icons-material/KeyboardArrowUp";
import ExpandedSection from "./ExpandedSection";

const currency = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
});

function statusColor(s) {
  if (s === "success") return "success";
  if (s === "pending") return "warning";
  if (s === "failed") return "error";
  return "default";
}

function TransactionRow({ r }) {
  const [open, setOpen] = React.useState(false);

  return (
    <>
      <TableRow hover key={r.id}>
        <TableCell padding="checkbox" sx={{ width: 56 }}>
          <IconButton
            aria-label={open ? "Collapse details" : "Expand details"}
            size="small"
            onClick={() => setOpen((o) => !o)}
          >
            {open ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
          </IconButton>
        </TableCell>

        <TableCell>
          {new Date(r.initiated_at).toLocaleDateString("en-IN", {
            year: "numeric",
            month: "short",
            day: "numeric",
          })}
        </TableCell>

        <TableCell>
          <Box sx={{ display: "flex", flexDirection: "column" }}>
            {r.to_account && (
              <Typography variant="body2" sx={{ fontWeight: 600 }}>
                {r.to_account.user_name}
              </Typography>
            )}
            {r.merchant && (
              <Typography variant="body2" sx={{ fontWeight: 600 }}>
                {r.merchant.name}
              </Typography>
            )}
          </Box>
        </TableCell>

        <TableCell>{r.transaction_mode}</TableCell>

        <TableCell sx={{ textTransform: "capitalize" }}>
          {r.transaction_type}
        </TableCell>

        <TableCell align="right" sx={{ fontVariantNumeric: "tabular-nums" }}>
          {currency.format(r.amount)}
        </TableCell>

        <TableCell>
          <Chip
            size="small"
            label={r.status}
            color={statusColor(r.status)}
            variant="outlined"
          />
        </TableCell>
      </TableRow>
      <ExpandedSection r={r} open={open} />
    </>
  );
}

export default TransactionRow;
