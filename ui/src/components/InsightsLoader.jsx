import React from "react";
import { Box, CircularProgress, Typography, Paper } from "@mui/material";

const InsightsLoader = ({ query }) => {
  return (
    <Box
      sx={{
        position: "fixed",
        top: 0,
        left: 0,
        width: "100vw",
        height: "100vh",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        bgcolor: "background.default",
        zIndex: 1300,
        p: 2,
        textAlign: "center"
      }}
    >
      <CircularProgress size={48} />
      <Typography variant="h6" sx={{ mt: 2, fontWeight: 500 }}>
        Processing your query...
      </Typography>
      <Typography
        variant="body1"
        color="text.secondary"
        sx={{ mt: 1, fontStyle: "italic", maxWidth: "80%" }}
      >
        “{query}”
      </Typography>
    </Box>
  );
};

export default InsightsLoader;
