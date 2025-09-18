import React, { useEffect, useState } from "react";
import PromptInput from "./PromptInput";
import { Box, Container, Stack, Button } from "@mui/material";
import useInsights from "./useInsights";
import Insights from "./Insights";
import InsightsLoader from "../../components/InsightsLoader";
import { MOCK_DATA } from "../../mock/dataSelector";

function InsightsHub() {
  const { fetchInsights, insightsData, insightsLoading } = useInsights();
  const [showResponse, setshowResponse] = useState(false);
  const [userQuery, setuserQuery] = useState("");

  return (
    <Container
      maxWidth="xl"
      disableGutters
      sx={{ px: { xs: 2, md: 3 }, py: 2, overflowX: "clip" }}
    >
      {!showResponse && (
        <Box
          sx={{
            width: 1,
            maxWidth: "100%",
            minWidth: 0,
            overflowX: "clip",
            display: "flex",
            flexWrap: "wrap",
            mb: 2,
          }}
        >
          <PromptInput
            onSubmit={(query) => {
              setuserQuery(query);
              fetchInsights(query);
              setshowResponse(true);
            }}
          />
        </Box>
      )}

      {insightsLoading && <InsightsLoader query={userQuery} />}

      {!insightsLoading && showResponse && (
        <Insights
          data={insightsData.data}
          onTryAnother={() => {
            setshowResponse(false);
          }}
        />
      )}
    </Container>
  );
}

export default InsightsHub;
