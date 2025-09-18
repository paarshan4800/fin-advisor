import React, { useState } from "react";
import {
  Container,
  Box,
  Typography,
  TextField,
  Button,
  Paper,
} from "@mui/material";

const PromptInput = ({ onSubmit }) => {
  const [prompt, setPrompt] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!prompt.trim()) return;
    onSubmit(prompt);
    setPrompt("");
    
  };

  return (
    <Container maxWidth="md" sx={{ py: 2, overflowX: "clip" }}>
      <Box sx={{ mb: 3, textAlign: "center" }}>
        <Typography variant="h4" sx={{ fontWeight: 700 }}>
          Finance Assistant
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Ask questions about your spending and view insights
        </Typography>
      </Box>

      <Paper sx={{ p: 3, mb: 4, overflowX: "clip" }} elevation={3}>
        <Box
          component="form"
          onSubmit={handleSubmit}
          sx={{ width: 1, maxWidth: "100%", minWidth: 0 }}
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
