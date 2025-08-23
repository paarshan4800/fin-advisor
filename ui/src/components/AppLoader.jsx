import React from "react";
import { Box, CircularProgress, Typography } from "@mui/material";

export default function AppLoader({ text = "Loading...", size = 48 }) {
    return (
        <Box
            sx={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                height: "100%",
                p: 2,
            }}
        >
            <CircularProgress size={size} />
            {text && (
                <Typography variant="body2" sx={{ mt: 1, color: "text.secondary" }}>
                    {text}
                </Typography>
            )}
        </Box>
    );
}
