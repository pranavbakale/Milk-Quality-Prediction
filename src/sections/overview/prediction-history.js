import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import GetAppRoundedIcon from "@mui/icons-material/GetAppRounded";
import {
  Box,
  IconButton,
  Card,
  CardHeader,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
} from "@mui/material";
import axios from "axios";

export const OverviewLatestOrders = (props) => {
  const { sx, fetchTrigger } = props;
  const [files, setFiles] = useState([]);
  const token = localStorage.getItem('token');
  console.log(token);
  useEffect(() => {
    const fetchFiles = async () => {
      try {
          const response = await axios.post(
            `http://localhost:5000/last-six-months-data?token=${token}`
          );
        setFiles(response.data);
      } catch (error) {
        console.error("Error fetching files:", error);
      }
    };

    fetchFiles();
  }, [fetchTrigger]); // Fetch files each time fetchTrigger changes

  return (
    <Card sx={sx}>
      <CardHeader title="Prediction History" />
      <Box sx={{ minWidth: "100%" }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>No.</TableCell>
              <TableCell>File Name</TableCell>
              <TableCell>Download</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {files.map((file, index) => (
              <TableRow hover key={index}>
                <TableCell>{index + 1}</TableCell>
                <TableCell>{file.file_name}</TableCell>
                <TableCell>
                  <IconButton href={file.file_path} download>
                    <GetAppRoundedIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Box>
    </Card>
  );
};

OverviewLatestOrders.propTypes = {
  sx: PropTypes.object,
  fetchTrigger: PropTypes.bool, // Add fetchTrigger prop
};
