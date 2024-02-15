import PropTypes from 'prop-types';
import { useState } from 'react';
import FileUploadIcon from '@mui/icons-material/FileUpload';
import { styled } from '@mui/system';
import { Card, CardHeader, CardContent, Button, Stack, Typography } from '@mui/material';

const CustomButton = styled(Button)({
  backgroundColor: '#4caf50', // Green color
  color: 'white',
  '&:hover': {
    backgroundColor: '#45a049', // Darker green color on hover
  },
});

const StyledCard = styled(Card)({
  boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)', // Box shadow for a subtle lift
  maxWidth: 400,
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  padding: '20px',
  gap: '20px',
  margin: 'auto', // Center the card horizontally
  backgroundColor: 'rgb(231,230,230)', // Light blue background color
  borderRadius: '15px', // Rounded corners
});

export const ImportData = (props) => {
  const { difference, positive = false, sx, value } = props;
  const [selectedFiles, setSelectedFiles] = useState([]);

  const handleFileChange = (event) => {
    const files = event.target.files;
    const csvFiles = Array.from(files).filter(file => file.name.endsWith('.csv'));
    setSelectedFiles(csvFiles);
  };

  const handleUploadClick = () => {
    if (selectedFiles.length > 0) {
      // Perform the file upload action (e.g., send files to the server)
      console.log('Uploading CSV files:', selectedFiles);
      // You can use the 'fetch' API or any other method to upload the files to the server
    } else {
      console.error('No files selected');
    }
  };

  return (
    <StyledCard>
      <CardHeader title="Import Data" />
      <CardContent>
        <Stack
          alignItems="center"
          direction="column"
          justifyContent="center"
          spacing={2}
        >
          <Stack spacing={1}>
            <input
              type="file"
              id="fileInput"
              accept=".csv"
              capture="environment"
              style={{ display: 'none' }}
              onChange={handleFileChange}
              multiple // Allow multiple file selection
            />
            <label htmlFor="fileInput">
              <CustomButton
                variant="contained"
                color="primary"
                component="span"
                startIcon={<FileUploadIcon />}
              >
                Upload CSV Files
              </CustomButton>
            </label>
            <Button
              variant="contained"
              sx={{ backgroundColor: '#2196f3', color: 'white', fontSize: '16px' }} // Increased font size
              onClick={handleUploadClick}
            >
              Upload
            </Button>
          </Stack>
          {selectedFiles.length > 0 && (
            <Typography variant="body2"
                        color="text.secondary">
              Selected Files: {selectedFiles.map(file => file.name).join(', ')}
            </Typography>
          )}
        </Stack>
      </CardContent>
    </StyledCard>
  );
};

ImportData.propTypes = {
  difference: PropTypes.number,
  positive: PropTypes.bool,
  value: PropTypes.string.isRequired,
  sx: PropTypes.object,
};