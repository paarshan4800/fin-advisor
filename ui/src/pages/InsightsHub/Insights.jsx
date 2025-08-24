import React from "react";
import { Box, Stack, Button } from "@mui/material";
import AppPieChart from "../../components/Visualizations/AppPieChart";
import InsightsCard from "../../components/InsightsCard";
import RefreshIcon from "@mui/icons-material/Refresh";
import AppBarChart from "../../components/Visualizations/AppBarChart";
import AppLineChart from "../../components/Visualizations/AppLineChart";
import AppTable from "../../components/Visualizations/AppTable";

function Insights(props) {
  const { data, onTryAnother } = props;

  const { query = "", analysis = {}, visualization = {} } = data;

  const visualizationType = visualization?.type;

  const chartType =
    visualizationType === "chart" ? visualization.chartType : "";

  return (
    <Stack sx={{ width: 1, minWidth: 0 }}>
      <Box
        sx={{
          display: "flex",
          justifyContent: "flex-end",
          mb: 2,
        }}
      >
        <Button
          variant="contained"
          color="primary"
          startIcon={<RefreshIcon />}
          onClick={onTryAnother}
          sx={{
            textTransform: "none",
            borderRadius: 2,
            fontWeight: 500,
            px: 2.5,
          }}
        >
          Try another prompt
        </Button>
      </Box>
      <Stack
        direction={{ xs: "column", md: "row" }}
        spacing={2}
        alignItems="stretch"
        sx={{ width: 1, minWidth: 0 }}
      >
        <Box sx={{ flex: 1, minWidth: 0, display: "flex" }}>
          <InsightsCard query={query} analysis={analysis} />
        </Box>
        <Box
          sx={{ flex: 1, minWidth: 0, display: "flex", overflowX: "hidden" }}
        >
          {visualizationType === "table" && (
            <AppTable visualization={visualization} />
          )}
          {visualizationType === "chart" && chartType === "pie" && (
            <AppPieChart visualization={visualization} />
          )}
          {visualizationType === "chart" && chartType === "bar" && (
            <AppBarChart visualization={visualization} />
          )}
          {visualizationType === "chart" && chartType === "line" && (
            <AppLineChart visualization={visualization} />
          )}
        </Box>
      </Stack>
    </Stack>
  );
}

export default Insights;
