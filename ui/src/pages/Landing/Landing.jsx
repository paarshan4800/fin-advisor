import * as React from "react";
import { Typography, Box, Button, Grid, Paper } from "@mui/material";

export default function Landing() {
  return (
    <Grid
      container
      justifyContent="center"
      alignItems="center"
      sx={{
        py: { xs: 6, md: 10 },
        textAlign: "center",
      }}
    >
      <Grid item xs={12} md={10}>
        <Typography variant="h3" sx={{ mb: 2 }}>
          See your money. Spend with intent.
        </Typography>

        <Typography variant="body1" sx={{ color: "text.secondary", mb: 3 }}>
          A simple expense & finance advisor that helps you track spending,
          spot patterns, and nudge better decisions—without getting in the way.
        </Typography>

        <Paper
          variant="outlined"
          sx={{
            p: 2,
            mb: 3,
            bgcolor: "background.paper",
            display: "inline-block",
          }}
        >
          <Typography variant="body2" sx={{ fontStyle: "italic" }}>
            “Save first, then spend on what matters.”
          </Typography>
        </Paper>

        <Box sx={{ display: "flex", gap: 2, justifyContent: "center" }}>
          <Button variant="contained">Get Started</Button>
          <Button variant="text">Learn More</Button>
        </Box>
      </Grid>
    </Grid>
  );
}
