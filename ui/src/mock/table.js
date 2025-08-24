export const TABLE_DATA = {
  data: {
    analysis: {
      recommendations: [
        "Consolidate transfers to Sarah Morgan to reduce frequency.",
        "Review internet provider subscriptions to ensure they are necessary and not duplicated.",
        "Consider negotiating or switching internet providers for better rates.",
      ],
      unnecessary_patterns: [
        "Multiple transfers to the same recipient (Sarah Morgan) on different dates.",
        "High spending on internet providers without clear justification.",
      ],
    },
    query: "List my top 10 biggest spends this year in a table",
    visualization: {
      headers: ["Description", "Amount"],
      rows: [
        ["Transfer to Sarah Morgan", 7507.73],
        ["Transfer to Victoria Walsh", 4591.3],
        ["Transfer to Michelle Ray", 2503.55],
        ["Payment to Gates PLC Hotel", 4823.6],
        ["Payment to Ortiz-Jimenez Internet Provider", 7030.95],
        ["Payment to Shaffer LLC Internet Provider", 8073.11],
        ["Payment to Woodard, Bennett and Shelton Internet Provider", 655.22],
        ["Payment to Golden Inc Water Supply", 721.07],
        ["Transfer to Jeremy Taylor", 4432.99],
        ["Other", 0],
      ],
      text_summary:
        "Top 10 biggest spends this year, with smaller items grouped into 'Other'.",
      type: "table",
    },
  },
  error: null,
  success: true,
};
