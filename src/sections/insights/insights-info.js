import Head from "next/head";
import { useEffect, useState } from "react";
import axios from "axios";
import { TableRow, TableCell, TableContainer, TableHead, Table, TableBody } from "@mui/material";

const InsightPage = () => {
  const [predictions, setPredictions] = useState([]);

  useEffect(() => {
    fetchPredictions();
  }, []);

  const fetchPredictions = async () => {
    try {
      const response = await axios.get("/get-last-50-predictions");
      setPredictions(response.data);
    } catch (error) {
      console.error("Error fetching predictions:", error);
    }
  };

  return (
    <div>
      <Head>
        <title>Insight Page</title>
      </Head>
      <h1>Last 50 Predictions</h1>
      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Date</TableCell>
              <TableCell>Time</TableCell>
              <TableCell>pH</TableCell>
              <TableCell>Temperature</TableCell>
              <TableCell>Taste</TableCell>
              <TableCell>Odor</TableCell>
              <TableCell>Fat</TableCell>
              <TableCell>Turbidity</TableCell>
              <TableCell>Colour</TableCell>
              <TableCell>Grade</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {predictions.map((prediction, index) => (
              <TableRow key={index}>
                <TableCell>{prediction.date}</TableCell>
                <TableCell>{prediction.time}</TableCell>
                <TableCell>{prediction.pH}</TableCell>
                <TableCell>{prediction.Temperature}</TableCell>
                <TableCell>{prediction.Taste}</TableCell>
                <TableCell>{prediction.Odor}</TableCell>
                <TableCell>{prediction.Fat}</TableCell>
                <TableCell>{prediction.Turbidity}</TableCell>
                <TableCell>{prediction.Colour}</TableCell>
                <TableCell>{prediction.Grade}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </div>
  );
};

export default InsightPage;
