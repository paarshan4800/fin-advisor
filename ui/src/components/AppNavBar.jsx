import React from "react";
import { AppBar, Toolbar, Typography, Button, Box } from "@mui/material";
import { SavingsOutlined } from "@mui/icons-material";
import { Link } from "react-router-dom";
import CurrentUserPicker from "./CurrentUserPicker";
import { useUser } from "../context/UserContext";

const AppNavBar = ({ usersData }) => {
  const { user, setUser } = useUser();

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
        <Box mx={2}>
          <CurrentUserPicker
            users={usersData}
            currentUser={user}
            onChange={(user) => setUser(user)}
          />
        </Box>
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
