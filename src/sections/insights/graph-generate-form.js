import React, { useState } from "react";
import {
  Button,
  Card,
  CardContent,
  CardHeader,
  MenuItem,
  FormControl,
  TextField,
  Typography,
  Tooltip,
  IconButton,
  SvgIcon,
} from "@mui/material";
import axios from "axios";
import GetAppRoundedIcon from "@mui/icons-material/GetAppRounded";
import { Hmac } from "crypto";

export const GenerateGraphForm = () => {
  const [selectedAttribute, setSelectedAttribute] = useState("");
  const [graphData, setGraphData] = useState([]);
  const [isExportEnabled, setIsExportEnabled] = useState(false);
  const [files, setFiles] = useState([]);


  const attributes = [
    "pH",
    "Temperature",
    "Taste",
    "Odor",
    "Fat",
    "Turbidity",
    "Colour",
    "Grade",
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post("http://localhost:5000/generate-graphs", {
        attribute: selectedAttribute,
      });
      const graphUrls = response.data;
      setGraphData([
        { name: `${selectedAttribute} Line Plot`, url: graphUrls.linePlotUrl },
        {
          name: `Distribution Plot of ${selectedAttribute}`,
          url: graphUrls.histogramUrl,
        },
        { name: `${selectedAttribute} Count Plot`, url: graphUrls.boxPlotUrl },
        {
          name: `Count Plot of ${selectedAttribute}`,
          url: graphUrls.countPlotUrl,
        },
        { name: "Heatmap", url: graphUrls.heatmapUrl },
      ]);
      setIsExportEnabled(true); // Enable export button after generating graphs
    } catch (error) {
      console.error("Error generating graphs:", error);
    }
  };

//   const handleExport = async () => {
//     try {
//         // Make a GET request to the backend endpoint to get the PDF folder path
//         const response = await axios.get(`http://localhost:5000/generate-graphs-pdf?attribute=${selectedAttribute}`);
//         const pdfFolderPath = response.data.pdf_folder_path

        
//     } catch (error) {
//         console.error("Error exporting PDF:", error);
//     }
// };

  

  return (
    <Card>
      <CardHeader title="Generate Graphs" />
      <CardContent>
        <form onSubmit={handleSubmit}>
          <FormControl fullWidth sx={{ my: 1 }}>
            <TextField
              select
              name="Attribute"
              id="attribute-label"
              label="Attribute"
              labelId="attribute-label"
              value={selectedAttribute}
              onChange={(e) => setSelectedAttribute(e.target.value)}
            >
              {attributes.map((attribute) => (
                <MenuItem key={attribute} value={attribute}>
                  {attribute}
                </MenuItem>
              ))}
            </TextField>
          </FormControl>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <Button type="submit" variant="contained" sx={{ mt: 2 }}>
              Generate Graphs
            </Button>
            {isExportEnabled && (
              <Tooltip title="Export">
                <IconButton onClick={handleExport}>
                  <SvgIcon fontSize="big">
                    <GetAppRoundedIcon />
                  </SvgIcon>
                </IconButton>
              </Tooltip>
            )}
          </div>
        </form>
        {graphData.length > 0 && (
          <div>
            <Typography variant="h6" sx={{ mt: 4 }}>
              Generated Graphs:
            </Typography>
            {graphData.map((graph, index) => (
              <div key={index} style={{ marginBottom: "20px" }}>
                <Typography variant="subtitle1" sx={{ mt: 2 }}>
                  {graph.name}
                </Typography>
                <img 
                  src={"http://localhost:5000/graphs/" + graph.url + `?${Math.random()}`}
                  alt={graph.name}
                  style={{ maxWidth: "100%", marginTop: "10px" }}
                />
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};
