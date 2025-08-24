export const BAR_CHART_DATA = {
  data: {
    analysis: {
      recommendations: [
        "Consolidate transfers to the same person to avoid multiple transactions.",
        "Review utility bills for accuracy to prevent overpayments.",
        "Consider setting up alerts for recurring payments to avoid impulse buys.",
      ],
      unnecessary_patterns: [
        "Multiple transfers to the same recipient (Sarah Morgan) within a short time frame.",
        "Refunds for utility payments may indicate overpayment or billing errors.",
      ],
    },
    query: "Categorize last 2 months spending in a chart",
    visualization: {
      chartType: "bar",
      data: [
        {
          label: "Refunds",
          value: 8486.89,
        },
        {
          label: "Utilities",
          value: 7030.95,
        },
        {
          label: "Hotels",
          value: 4823.6,
        },
        {
          label: "Transfers",
          value: 2503.55,
        },
        {
          label: "Other",
          value: 721.07,
        },
      ],
      text_summary:
        "Spending by category over the last two months shows Transfers, Hotels, Utilities, and Refunds as the main categories, with a small portion categorized as Other.",
      type: "chart",
    },
  },
  error: null,
  success: true,
};
