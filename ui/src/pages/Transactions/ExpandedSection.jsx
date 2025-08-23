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

function ExpandedSection({r, open}) {
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
                            <Box sx={{ minWidth: 220 }}>
                                <Typography variant="overline" color="text.secondary">
                                    Overview
                                </Typography>
                                <Typography variant="body2">Transaction ID: {r.transaction_id}</Typography>
                            </Box>

                            <Box sx={{ minWidth: 220 }}>
                                <Typography variant="overline" color="text.secondary">
                                    Overview
                                </Typography>
                                <Typography variant="body2">
                                    Date/Time:{" "}
                                    {new Date(r.initiated_at).toLocaleString("en-IN", {
                                        year: "numeric",
                                        month: "short",
                                        day: "numeric",
                                        hour: "2-digit",
                                        minute: "2-digit",
                                    })}
                                </Typography>
                            </Box>

                            <Box sx={{ minWidth: 220 }}>
                                <Typography variant="overline" color="text.secondary">
                                    Description
                                </Typography>
                                <Typography variant="body2">{r.description || "—"}</Typography>
                            </Box>

                            <Box sx={{ flex: 1, minWidth: 260 }}>
                                <Typography variant="overline" color="text.secondary">
                                    Notes
                                </Typography>
                                <Typography variant="body2">
                                    {r.remarks || "—"}
                                </Typography>
                            </Box>
                        </Stack>
                    </Box>
                </Collapse>
            </TableCell>
        </TableRow>
    )
}

export default ExpandedSection