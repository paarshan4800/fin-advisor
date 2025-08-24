import React, { useState } from "react";
import {
  Container,
  Box,
  Typography,
  TextField,
  Button,
  Paper,

} from "@mui/material";

const PromptInput = ({onSubmit}) => {
  const [prompt, setPrompt] = useState("");
  const [response, setResponse] = useState(null);
  const [chartData, setChartData] = useState([]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    // --- Simulated response + data (replace with your real backend call) ---
    // Example: weekly totals for the last 8 weeks
    const demoData = [
      { label: "W-8", amount: 12450 },
      { label: "W-7", amount: 9800 },
      { label: "W-6", amount: 11230 },
      { label: "W-5", amount: 9050 },
      { label: "W-4", amount: 13320 },
      { label: "W-3", amount: 10110 },
      { label: "W-2", amount: 12040 },
      { label: "Last Wk", amount: 11570 },
    ];

    setResponse({
      echo: `You asked: "${prompt}"`,
      summary:
        "Showing a sample bar chart of weekly spend for the last ~8 weeks.",
      highlights: ["Peak in W-4", "Recent trend slightly down"],
    });
    setChartData(demoData);

    setPrompt("");
    onSubmit()
  };

  return (
    <Container maxWidth="md" sx={{ py: 2, overflowX: 'clip' }}>
      {/* Header */}
      <Box sx={{ mb: 3, textAlign: "center" }}>
        <Typography variant="h4" sx={{ fontWeight: 700 }}>
          Finance Assistant
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Ask questions about your spending and view insights
        </Typography>
      </Box>

      {/* Prompt input */}
      <Paper sx={{ p: 3, mb: 4, overflowX: 'clip' }} elevation={3}>
        <Box
          component="form"
          onSubmit={handleSubmit}
          sx={{ width: 1, maxWidth: '100%', minWidth: 0 }}
        >
          <TextField
            fullWidth
            label="Enter your prompt"
            placeholder='e.g. "How much did I spend last 2 months?"'
            variant="outlined"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
                handleSubmit(e);
              }
            }}
            helperText="Tip: Press ⌘+Enter / Ctrl+Enter to submit"
            sx={{ mb: 2, minWidth: 0 }}
          />
          <Button type="submit" variant="contained" fullWidth>
            Submit
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default PromptInput;
