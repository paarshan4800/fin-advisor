import React from "react";
import {
    Card,
    CardContent,
    CardHeader,
    Divider,
    Typography,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    Box,
    Chip,
} from "@mui/material";
import HelpOutlineIcon from "@mui/icons-material/HelpOutline";
import CheckCircleOutlineIcon from "@mui/icons-material/CheckCircleOutline";
import WarningAmberOutlinedIcon from "@mui/icons-material/WarningAmberOutlined";


const InsightsCard = ({ query, analysis }) => {
    const recommendations = analysis?.recommendations ?? [];
    const unnecessary = analysis?.unnecessary_patterns ?? [];

    return (
        <Card sx={{ width: "100%", height: "100%", p: 1, borderRadius: 3, boxShadow: 3 }}>
            <CardHeader
                title="Insights"
                sx={{ pb: 0 }}
            />
            <CardContent>
                {/* Query */}
                <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" color="text.secondary" sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                        <HelpOutlineIcon fontSize="small" />
                        User Query
                    </Typography>
                    <Typography variant="h6" sx={{ mt: 0.5 }}>
                        {query || "—"}
                    </Typography>
                </Box>

                <Divider sx={{ my: 2 }} />

                {/* Recommendations */}
                <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" color="text.secondary" sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                        <CheckCircleOutlineIcon fontSize="small" />
                        Recommendations
                        <Chip label={recommendations.length} size="small" sx={{ ml: 1 }} />
                    </Typography>
                    {recommendations.length > 0 ? (
                        <List dense>
                            {recommendations.map((item, idx) => (
                                <ListItem key={`rec-${idx}`} disableGutters>
                                    <ListItemIcon sx={{ minWidth: 32 }}>
                                        <CheckCircleOutlineIcon fontSize="small" />
                                    </ListItemIcon>
                                    <ListItemText primary={item} />
                                </ListItem>
                            ))}
                        </List>
                    ) : (
                        <Typography variant="body2" color="text.secondary">No recommendations.</Typography>
                    )}
                </Box>

                {/* Unnecessary Patterns */}
                <Box>
                    <Typography variant="subtitle2" color="text.secondary" sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                        <WarningAmberOutlinedIcon fontSize="small" />
                        Unnecessary Patterns
                        <Chip label={unnecessary.length} size="small" sx={{ ml: 1 }} />
                    </Typography>
                    {unnecessary.length > 0 ? (
                        <List dense>
                            {unnecessary.map((item, idx) => (
                                <ListItem key={`unnec-${idx}`} disableGutters>
                                    <ListItemIcon sx={{ minWidth: 32 }}>
                                        <WarningAmberOutlinedIcon fontSize="small" />
                                    </ListItemIcon>
                                    <ListItemText primary={item} />
                                </ListItem>
                            ))}
                        </List>
                    ) : (
                        <Typography variant="body2" color="text.secondary">No unnecessary patterns detected.</Typography>
                    )}
                </Box>
            </CardContent>
        </Card>
    );
};

export default InsightsCard;
