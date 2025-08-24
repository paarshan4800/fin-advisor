export const PIE_CHART_DATA = {
  data: {
    analysis: {
      recommendations: [
        "Consolidate transfers to the same person to avoid multiple transactions.",
        "Review utility bills for accuracy to prevent overpayments.",
        "Consider setting a budget for hotel stays to avoid excessive spending.",
      ],
      unnecessary_patterns: [
        "Multiple transfers to the same recipient (Sarah Morgan) within a short time frame.",
        "Refunds for utility payments may indicate overpayment or billing errors.",
      ],
    },
    query: "Categorize last 2 months spending in a chart",
    visualization: {
      chartType: "pie",
      data: [
        {
          label: "Transfers",
          value: 10791.17,
        },
        {
          label: "Hotels",
          value: 4823.6,
        },
        {
          label: "Utilities",
          value: 7030.95,
        },
        {
          label: "Refunds",
          value: 10000.22,
        },
      ],
      text_summary:
        "Categorized spending over the last 2 months shows the largest portion in Transfers, followed by Refunds and Utilities.",
      type: "chart",
    },
  },
  error: null,
  success: true,
};
