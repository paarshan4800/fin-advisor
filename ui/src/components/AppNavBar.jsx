import React from "react";
import { AppBar, Toolbar, Typography, Button, Box } from "@mui/material";
import { SavingsOutlined } from "@mui/icons-material";
import { Link } from "react-router-dom";

const AppNavBar = () => {
  return (
    <AppBar position="static" color="transparent" elevation={0}>
      <Toolbar>
        <Box
          component={Link}
          to="/"
          sx={{
            display: "flex",
            alignItems: "center",
            textDecoration: "none",
            color: "inherit",
          }}
        >
          <SavingsOutlined sx={{ mr: 1 }} />
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            SpendSmart
          </Typography>
        </Box>

        <Box sx={{ flexGrow: 1 }} />

        <Button
          component={Link}
          to="/insights-hub"
          color="inherit"
          size="medium"
          sx={{ textTransform: "none" }}
        >
          Insights Hub
        </Button>
        <Button
          component={Link}
          to="/transactions"
          color="inherit"
          size="medium"
          sx={{ textTransform: "none" }}
        >
          Transactions
        </Button>
      </Toolbar>
    </AppBar>
  );
};

export default AppNavBar;
