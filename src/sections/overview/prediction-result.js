import React from 'react';
import { Card, CardContent, Typography, Grid } from '@mui/material';

const PredictionResult = ({ rfPrediction, svmPrediction, rfAccuracy, svmAccuracy }) => {
  return (
    <Grid container spacing={3}>
      <Grid item xs={12} sm={6}>
        <Card>
          <CardContent>
            <Typography variant="h5" component="h2" gutterBottom>
              Random Forest Prediction
            </Typography>
            <Typography variant="body1" gutterBottom>
              Prediction: {rfPrediction}
            </Typography>
            <Typography variant="body1" gutterBottom>
              Accuracy: {rfAccuracy}%
            </Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} sm={6}>
        <Card>
          <CardContent>
            <Typography variant="h5" component="h2" gutterBottom>
              SVM Prediction
            </Typography>
            <Typography variant="body1" gutterBottom>
              Prediction: {svmPrediction}
            </Typography>
            <Typography variant="body1" gutterBottom>
              Accuracy: {svmAccuracy}%
            </Typography>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

export default PredictionResult;
