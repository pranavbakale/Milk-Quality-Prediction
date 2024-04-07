import PropTypes from 'prop-types';
import React, { useState } from 'react';
import axios from 'axios';

import {
  Box,
  Button,
  Card,
  CardContent,
  CardHeader,
  Stack,
  Typography,
  useTheme,
  TextField
} from '@mui/material';


export const InputForm = ({ onSubmit }) => {
  const [formData, setFormData] = useState({
    pH: '',
    Temperature: '',
    Taste: '',
    Odor: '',
    Fat: '',
    Turbidity: '',
    Colour: ''
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit}>
      <Stack spacing={2}>
        <TextField
          fullWidth
          label="pH"
          name="pH"
          value={formData.pH}
          onChange={handleChange}
        />
        <TextField
          fullWidth
          label="Temperature"
          name="Temperature"
          value={formData.Temperature}
          onChange={handleChange}
        />
        <TextField
          fullWidth
          label="Taste"
          name="Taste"
          value={formData.Taste}
          onChange={handleChange}
        />
        <TextField
          fullWidth
          label="Odor"
          name="Odor"
          value={formData.Odor}
          onChange={handleChange}
        />
        <TextField
          fullWidth
          label="Fat"
          name="Fat"
          value={formData.Fat}
          onChange={handleChange}
        />
        <TextField
          fullWidth
          label="Turbidity"
          name="Turbidity"
          value={formData.Turbidity}
          onChange={handleChange}
        />
        <TextField
          fullWidth
          label="Colour"
          name="Colour"
          value={formData.Colour}
          onChange={handleChange}
        />
        <Button type="submit" variant="contained" color="primary">
          Submit
        </Button>
      </Stack>
    </form>
  );
};

InputForm.propTypes = {
  onSubmit: PropTypes.func.isRequired
};

export const useChartOptions = (labels) => {
  const theme = useTheme();

  return {
    chart: {
      background: 'transparent'
    },
    colors: [
      theme.palette.primary.main,
      theme.palette.success.main,
      theme.palette.warning.main
    ],
    dataLabels: {
      enabled: false
    },
    labels,
    legend: {
      show: false
    },
    plotOptions: {
      pie: {
        expandOnClick: false
      }
    },
    states: {
      active: {
        filter: {
          type: 'none'
        }
      },
      hover: {
        filter: {
          type: 'none'
        }
      }
    },
    stroke: {
      width: 0
    },
    theme: {
      mode: theme.palette.mode
    },
    tooltip: {
      fillSeriesColor: false
    }
  };
};
