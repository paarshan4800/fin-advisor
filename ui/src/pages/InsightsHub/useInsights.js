import React, { useState } from "react";
import { useUser } from "../../context/UserContext";
import api from "../../api";

function useInsights() {
  const [insightsData, setinsightsData] = useState(null);
  const [insightsLoading, setinsightsLoading] = useState(false);
  const [insightsError, setinsightsError] = useState(null);

  const INSIGHTS_URI = "/query";

  const { user } = useUser();

  const fetchInsights = async (query) => {
    setinsightsLoading(true);

    try {
      const payload = {
        session_id: user._id,
        query: query,
      };
      const resp = await api.post(INSIGHTS_URI, payload);

      setinsightsData(resp.data);
    } catch (e) {
      setinsightsError(e.message);
    } finally {
      setinsightsLoading(false);
    }
  };

  return {
    insightsData,
    insightsLoading,
    insightsError,
    fetchInsights,
  };
}

export default useInsights;
