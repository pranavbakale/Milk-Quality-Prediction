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
  TextField,

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
  const [errors, setErrors] = useState({
    pH: '',
    Temperature: '',
    Taste: '',
    Odor: '',
    Fat: '',
    Turbidity: '',
    Colour: ''
  });
  const [touchedFields, setTouchedFields] = useState({});

  const validateField = (fieldName) => {
    let errorMessage = '';
    const value = formData[fieldName];

    switch (fieldName) {
      case 'pH':
        if (value === '' || parseFloat(value) < 3 || parseFloat(value) > 9.5) {
          errorMessage = 'pH should be between 3 to 9.5';
        }
        break;
      case 'Temperature':
        if (value === '' || parseFloat(value) < 34 || parseFloat(value) > 90) {
          errorMessage = 'Temperature should be between 34°C to 90°C';
        }
        break;
      case 'Taste':
      case 'Odor':
        if (value.toLowerCase() !== 'good' && value.toLowerCase() !== 'bad') {
          errorMessage = `${fieldName} should be either good or bad`;
        }
        break;
      case 'Fat':
      case 'Turbidity':
        if (value.toLowerCase() !== 'low' && value.toLowerCase() !== 'high') {
          errorMessage = `${fieldName} should be either low or high`;
        }
        break;
      case 'Colour':
        if (value === '' || parseInt(value) < 240 || parseInt(value) > 255) {
          errorMessage = 'Colour should be an integer between 240 to 255';
        }
        break;
      default:
        break;
    }

    setErrors((prevErrors) => ({
      ...prevErrors,
      [fieldName]: errorMessage
    }));

    return errorMessage;
  };

  const handleBlur = (fieldName) => {
    setTouchedFields((prevTouchedFields) => ({
      ...prevTouchedFields,
      [fieldName]: true
    }));
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });

    // If the field has been touched, validate it on change
    if (touchedFields[name]) {
      validateField(name);
    }
  };

  const handleSubmit = (e) => {
      e.preventDefault();
    
      let isValid = true;
      const newTouchedFields = {};
    
      // Validate all fields and set touched for empty fields
      Object.keys(formData).forEach((fieldName) => {
        if (formData[fieldName] === '') {
          isValid = false;
          newTouchedFields[fieldName] = true;
        } else {
          const fieldErrorMessage = validateField(fieldName);
          if (fieldErrorMessage !== '') {
            isValid = false;
          }
        }
      });
    
      setTouchedFields(newTouchedFields);
    
      if (isValid) {
        const convertedFormData = {
          ...formData,
          Taste: formData.Taste.toLowerCase() === 'good' ? 1 : 0,
          Odor: formData.Odor.toLowerCase() === 'good' ? 1 : 0,
          Fat: formData.Fat.toLowerCase() === 'high' ? 1 : 0,
          Turbidity: formData.Turbidity.toLowerCase() === 'high' ? 1 : 0
        };
        onSubmit(convertedFormData);
      }
    
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
          onBlur={() => handleBlur('pH')}
          error={errors.pH !== ''}
          helperText={touchedFields.pH && errors.pH}
        />
        <TextField
          fullWidth
          label="Temperature (°C)"
          name="Temperature"
          value={formData.Temperature}
          onChange={handleChange}
          onBlur={() => handleBlur('Temperature')}
          error={errors.Temperature !== ''}
          helperText={touchedFields.Temperature && errors.Temperature}
        />
        <TextField
          fullWidth
          label="Taste (Good/Bad)"
          name="Taste"
          value={formData.Taste}
          onChange={handleChange}
          onBlur={() => handleBlur('Taste')}
          error={errors.Taste !== ''}
          helperText={touchedFields.Taste && errors.Taste}
        />
        <TextField
          fullWidth
          label="Odor (Good/Bad)"
          name="Odor"
          value={formData.Odor}
          onChange={handleChange}
          onBlur={() => handleBlur('Odor')}
          error={errors.Odor !== ''}
          helperText={touchedFields.Odor && errors.Odor}
        />
        <TextField
          fullWidth
          label="Fat (Low/High)"
          name="Fat"
          value={formData.Fat}
          onChange={handleChange}
          onBlur={() => handleBlur('Fat')}
          error={errors.Fat !== ''}
          helperText={touchedFields.Fat && errors.Fat}
        />
        <TextField
          fullWidth
          label="Turbidity (Low/High)"
          name="Turbidity"
          value={formData.Turbidity}
          onChange={handleChange}
          onBlur={() => handleBlur('Turbidity')}
          error={errors.Turbidity !== ''}
          helperText={touchedFields.Turbidity && errors.Turbidity}
        />
        <TextField
          fullWidth
          label="Colour (240-255)"
          name="Colour"
          value={formData.Colour}
          onChange={handleChange}
          onBlur={() => handleBlur('Colour')}
          error={errors.Colour !== ''}
          helperText={touchedFields.Colour && errors.Colour}
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
