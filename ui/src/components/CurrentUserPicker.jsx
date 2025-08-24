import React from "react";
import {
  Avatar,
  Box,
  Button,
  Divider,
  IconButton,
  InputAdornment,
  List,
  ListItemButton,
  ListItemText,
  Popover,
  TextField,
  Typography,
} from "@mui/material";
import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown";
import SearchIcon from "@mui/icons-material/Search";
import CloseIcon from "@mui/icons-material/Close";

function initials(name = "") {
  return name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((s) => s[0]?.toUpperCase())
    .join("");
}

export default function CurrentUserPicker({
  users = [],
  currentUser,
  onChange,
  sx,
}) {
  const [anchorEl, setAnchorEl] = React.useState(null);
  const [q, setQ] = React.useState("");

  const open = Boolean(anchorEl);
  const id = open ? "current-user-popover" : undefined;

  const filtered = React.useMemo(() => {
    const query = q.trim().toLowerCase();
    if (!query) return users;
    return users.filter(
      (u) =>
        u.name.toLowerCase().includes(query) ||
        (u.email || "").toLowerCase().includes(query)
    );
  }, [q, users]);

  const handleOpen = (e) => setAnchorEl(e.currentTarget);
  const handleClose = () => setAnchorEl(null);

  const handleSelect = (user) => {
    if (onChange) onChange(user);
    handleClose();
  };

  return (
    <Box sx={{ display: "inline-flex", alignItems: "center", ...sx }}>
      <Button
        onClick={handleOpen}
        variant="outlined"
        size="small"
        startIcon={
          <Avatar sx={{ width: 24, height: 24, fontSize: 12 }}>
            {initials(currentUser?.name || "U")}
          </Avatar>
        }
        endIcon={<ArrowDropDownIcon />}
        sx={{
          textTransform: "none",
          borderRadius: 2,
          px: 1.25,
          py: 0.5,
          minWidth: 0,
          gap: 1,
        }}
      >
        <Typography variant="body2" noWrap maxWidth={160}>
          {currentUser ? currentUser.name : "Select user"}
        </Typography>
      </Button>

      <Popover
        id={id}
        open={open}
        anchorEl={anchorEl}
        onClose={handleClose}
        anchorOrigin={{ vertical: "bottom", horizontal: "left" }}
        transformOrigin={{ vertical: "top", horizontal: "left" }}
        PaperProps={{ sx: { width: 320, borderRadius: 2 } }}
      >
        <Box sx={{ p: 1.5, pb: 1 }}>
          <Box
            sx={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              mb: 1,
            }}
          >
            <Typography variant="subtitle2">Switch user</Typography>
            <IconButton size="small" onClick={handleClose}>
              <CloseIcon fontSize="small" />
            </IconButton>
          </Box>

          <TextField
            fullWidth
            size="small"
            placeholder="Search by name or email"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon fontSize="small" />
                </InputAdornment>
              ),
            }}
          />
        </Box>

        <Divider />

        <List dense disablePadding sx={{ maxHeight: 320, overflowY: "auto" }}>
          {filtered.length === 0 ? (
            <Box sx={{ p: 2 }}>
              <Typography variant="body2" color="text.secondary">
                No users found
              </Typography>
            </Box>
          ) : (
            filtered.map((u) => {
              const selected = u._id === currentUser._id;
              return (
                <ListItemButton
                  key={u._id}
                  selected={!!selected}
                  onClick={() => handleSelect(u)}
                  sx={{ py: 1 }}
                >
                  <Avatar sx={{ width: 28, height: 28, mr: 1.5, fontSize: 12 }}>
                    {initials(u.name)}
                  </Avatar>
                  <ListItemText
                    primary={
                      <Typography variant="body2" noWrap>
                        {u.name}
                      </Typography>
                    }
                    secondary={
                      <Typography
                        variant="caption"
                        color="text.secondary"
                        noWrap
                      >
                        {u.email}
                      </Typography>
                    }
                  />
                </ListItemButton>
              );
            })
          )}
        </List>
      </Popover>
    </Box>
  );
}
