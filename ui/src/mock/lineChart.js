export const LINE_CHART_DATA = {
  data: {
    analysis: {
      recommendations: [],
      unnecessary_patterns: [],
    },
    query: "Show a line chart of my daily expenses in August",
    visualization: {
      chartType: "line",
      data: [
        {
          label: "2025-08-22",
          value: 12357.14,
        },
        {
          label: "2025-08-20",
          value: 10000.29,
        },
        {
          label: "2025-08-21",
          value: 9024.29,
        },
        {
          label: "2025-08-19",
          value: 7507.73,
        },
      ],
      text_summary: "Daily expenses aggregated for August 2025.",
      type: "chart",
    },
  },
  error: null,
  success: true,
};
