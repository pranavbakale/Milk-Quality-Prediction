import React, { useState, useEffect } from "react";
import axios from "axios";
import Head from "next/head";
import { Box, Container, Grid } from "@mui/material";
import { Layout as DashboardLayout } from "src/layouts/dashboard/layout";
import { OverviewLatestOrders } from "src/sections/overview/prediction-history";
import { ImportData } from "src/sections/overview/import-data";
import { PredictionAnalysis } from "src/sections/overview/prediction-analysis";
import { PredictionResult } from "src/sections/overview/prediction-result";
import { InputForm } from "src/sections/overview/input-data";

const now = new Date();

const Page = () => {
  const [predictionResults, setPredictionResults] = useState({
    prediction: null,
    accuracy: null,
  });
  const [fetchTrigger, setFetchTrigger] = useState(false);
  const [token, setToken] = useState(""); // State to store the token

  useEffect(() => {
    const storedToken = localStorage.getItem("token");
    if (storedToken) {
      setToken(storedToken);
      console.log("Token:", storedToken); // Log the token after it's retrieved
    } else {
      // Handle case where token is not available in session storage
      console.error("Token not found in session storage.");
    }
  }, []); // Run this effect only once on component mount

  const handleInputFormSubmit = (formData) => {
    axios
      .post(`http://localhost:5000/predict?token=${token}`, formData)
      .then((response) => {
        setPredictionResults({
          prediction: response.data.prediction,
          accuracy: response.data.accuracy,
        });
        setFetchTrigger((prev) => !prev); // Toggle fetch trigger
      })
      .catch((error) => {
        console.error("Error predicting with Ensemble model:", error);
      });
  };

  return (
    <>
      <Head>
        <title>Overview</title>
      </Head>
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          py: 8,
        }}
      >
        <Container maxWidth="xl">
          <Grid container spacing={3}>
            <Grid item xs={12} md={6} lg={4}>
              <PredictionAnalysis
                chartSeries={[22, 15, 63]}
                labels={["Low", "Medium", "High"]}
                sx={{ height: "100%" }}
              />
            </Grid>
            <Grid item xs={12} md={6} lg={8}>
              <InputForm onSubmit={handleInputFormSubmit} />
              <PredictionResult
                prediction={predictionResults.prediction}
                accuracy={predictionResults.accuracy}
              />
            </Grid>
            <Grid item xs={12} md={12} lg={8}>
              <OverviewLatestOrders
                fetchTrigger={fetchTrigger} // Pass fetch trigger as prop
                sx={{ height: "100%" }}
              />
            </Grid>
            <Grid item xs={6} md={12} lg={4}>
              <ImportData
                difference={16}
                positive={false}
                sx={{ height: "100%" }}
                value="1.6k"
              />
            </Grid>
          </Grid>
        </Container>
      </Box>
    </>
  );
};

Page.getLayout = (page) => <DashboardLayout>{page}</DashboardLayout>;

export default Page;
