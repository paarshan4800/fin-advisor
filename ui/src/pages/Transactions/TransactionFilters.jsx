import * as React from "react";
import {
  Box,
  Stack,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Tooltip,
} from "@mui/material";
import PropTypes from "prop-types";
import { DatePicker, LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import dayjs from "dayjs";
import { filtersDefaultState } from "../../utils/constants";

export const STATUS_OPTIONS = ["initiated", "success", "failed", "refunded"];
export const MODE_OPTIONS = ["UPI", "Card", "BankTransfer", "Cash"];
export const TYPE_OPTIONS = ["credit", "debit", "refund"];

export default function TransactionFilters({
  value,
  onChange,
  onApply,
  onReset,
  compact = false,
  loading = false,
  pagination,
  setPagination
}) {

  const { page, rowsPerPage } = pagination

  const fromDate = React.useMemo(
    () => (value?.fromDate ? dayjs(value.fromDate) : null),
    [value?.fromDate]
  );
  const toDate = React.useMemo(
    () => (value?.toDate ? dayjs(value.toDate) : null),
    [value?.toDate]
  );

  const hasRangeError = Boolean(fromDate && toDate && fromDate.isAfter(toDate));

  const setField = (key, v) => onChange?.({ ...(value || {}), [key]: v });

  const handleApply = () => {
    if (hasRangeError) return;
    onApply(pagination, value);
    setPagination({...pagination, page: 0})
  };

  const handleReset = () => {
    if (onReset) return onReset();
    onChange(filtersDefaultState);
  };

  const toIsoStartOfDay = (d) => (d ? d.startOf("day").toISOString() : undefined);
  const toIsoEndOfDay = (d) => (d ? d.endOf("day").toISOString() : undefined);

  return (
    <LocalizationProvider dateAdapter={AdapterDayjs}>
      <Box
        sx={{
          p: 1.5,
          borderRadius: 2,
          border: (theme) => `1px solid ${theme.palette.divider}`,
          backgroundColor: (theme) => theme.palette.background.paper,
        }}
      >
        <Stack
          direction={compact ? "column" : { xs: "column", sm: "row" }}
          spacing={1.5}
          useFlexGap
          flexWrap={!compact ? "wrap" : undefined}
          alignItems={!compact ? "center" : undefined}
        >
          {/* From Date */}
          <DatePicker
            label="From date"
            value={fromDate}
            onChange={(newVal) => setField("fromDate", toIsoStartOfDay(newVal))}
            slotProps={{
              textField: {
                size: "small",
                error: hasRangeError,
                helperText: hasRangeError ? "From date must be before To date" : undefined,
              },
            }}
          />

          {/* To Date */}
          <DatePicker
            label="To date"
            value={toDate}
            onChange={(newVal) => setField("toDate", toIsoEndOfDay(newVal))}
            slotProps={{
              textField: {
                size: "small",
                error: hasRangeError,
                helperText: hasRangeError ? "To date must be after From date" : undefined,
              },
            }}
            minDate={fromDate || undefined}
          />

          {/* Status */}
          <FormControl size="small" sx={{ minWidth: 180 }}>
            <InputLabel shrink>Status</InputLabel>
            <Select
              label="Status"
              value={value?.status ?? ""}
              onChange={(e) => setField("status", e.target.value || "")}
              displayEmpty
            >
              <MenuItem value="">
                <em>Any</em>
              </MenuItem>
              {STATUS_OPTIONS.map((s) => (
                <MenuItem key={s} value={s}>
                  {capitalize(s)}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          {/* Transaction Mode */}
          <FormControl size="small" sx={{ minWidth: 180 }}>
            <InputLabel shrink>Mode</InputLabel>
            <Select
              label="Mode"
              value={value?.transactionMode ?? ""}
              onChange={(e) => setField("transactionMode", e.target.value || "")}
              displayEmpty
            >
              <MenuItem value="">
                <em>Any</em>
              </MenuItem>
              {MODE_OPTIONS.map((m) => (
                <MenuItem key={m} value={m}>
                  {m}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          {/* Transaction Type */}
          <FormControl size="small" sx={{ minWidth: 180 }}>
            <InputLabel shrink>Type</InputLabel>
            <Select
              label="Type"
              value={value?.transactionType ?? ""}
              onChange={(e) => setField("transactionType", e.target.value || "")}
              displayEmpty
            >
              <MenuItem value="">
                <em>Any</em>
              </MenuItem>
              {TYPE_OPTIONS.map((t) => (
                <MenuItem key={t} value={t}>
                  {capitalize(t)}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          {/* Action buttons */}
          <Stack direction="row" spacing={1} sx={{ ml: { xs: 0, sm: "auto" } }}>
            <Button variant="text" onClick={handleReset} disabled={loading}>
              Reset
            </Button>
            <Tooltip
              title={hasRangeError ? "Fix date range to apply" : "Apply filters"}
              disableHoverListener={!hasRangeError}
            >
              <span>
                <Button
                  variant="contained"
                  onClick={handleApply}
                  disabled={loading || hasRangeError}
                >
                  Apply
                </Button>
              </span>
            </Tooltip>
          </Stack>
        </Stack>
      </Box>
    </LocalizationProvider>
  );
}

TransactionFilters.propTypes = {
  value: PropTypes.shape({
    fromDate: PropTypes.string,
    toDate: PropTypes.string,
    status: PropTypes.string,
    transactionMode: PropTypes.string,
    transactionType: PropTypes.string,
  }),
  onChange: PropTypes.func.isRequired,
  onApply: PropTypes.func,
  onReset: PropTypes.func,
  compact: PropTypes.bool,
  loading: PropTypes.bool,
};

// -------------------- utils --------------------
function capitalize(s) {
  return s ? s.charAt(0).toUpperCase() + s.slice(1) : s;
}

