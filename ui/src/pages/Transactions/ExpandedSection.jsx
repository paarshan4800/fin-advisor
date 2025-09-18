import * as React from "react";
import {
  Box,
  TableCell,
  TableRow,
  Typography,
  Collapse,
  Divider,
  Stack,
} from "@mui/material";

function ExpandedSection({ r, open }) {
  const data = [
    {
      label: "Transaction ID",
      value: r.transaction_id,
    },
    {
      label: "Recipient Account Number",
      value: r?.to_account?.account_number,
    },
    {
      label: "Merchant Type",
      value: `${r?.merchant?.category} - ${r?.merchant?.type}`,
    },
    {
      label: "Date/Time",
      value: new Date(r.initiated_at).toLocaleString("en-IN", {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      }),
    },
    {
      label: "Description",
      value: r.description || "—",
    },
    {
      label: "Notes",
      value: r.remarks || "—",
    },
  ];

  const isMerchantTransaction = r.to_account === null;

  return (
    <TableRow>
      <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={7}>
        <Collapse in={open} timeout="auto" unmountOnExit>
          <Box sx={{ px: 2, pb: 2 }}>
            <Divider sx={{ mb: 2 }} />
            <Stack
              direction={{ xs: "column", sm: "row" }}
              spacing={3}
              useFlexGap
              flexWrap="wrap"
            >
              {data.map((item, index) => {
                if (
                  isMerchantTransaction &&
                  item.label === "Recipient Account Number"
                )
                  return null;

                if (
                  !isMerchantTransaction &&
                  item.label === "Merchant Type"
                )
                  return null;
                return (
                  <Box key={index} sx={{ minWidth: 220 }}>
                    <Typography variant="overline" color="text.secondary">
                      {item.label}
                    </Typography>
                    <Typography variant="body2">{item.value}</Typography>
                  </Box>
                );
              })}
            </Stack>
          </Box>
        </Collapse>
      </TableCell>
    </TableRow>
  );
}

export default ExpandedSection;
