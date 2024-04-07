import React from 'react';
import {
  Avatar,
  Box,
  Button,
  Card,
  CardActions,
  CardContent,
  Divider,
  Typography
} from '@mui/material';

export const AccountProfile = ({ user }) => {
  return (
    <Card>
      <CardContent>
        {user ? (
          <Box
            sx={{
              alignItems: 'center',
              display: 'flex',
              flexDirection: 'column'
            }}
          >
            <Avatar
              alt='avatar'
              sx={{
                height: 80,
                mb: 2,
                width: 80
              }}
            />
            <Typography
              gutterBottom
              variant="h5"
            >
              {user.name ? user.name : "Name"}
            </Typography>
            <Typography
              color="text.secondary"
              variant="body2"
            >
              {user.state}, {user.country}
            </Typography>
            <Typography
              color="text.secondary"
              variant="body2"
            >
              {/* Timezone: {user.timezone} */}
              Timezone
            </Typography>
          </Box>
        ) : (
          <Typography variant="body1">Loading user data...</Typography>
        )}
      </CardContent>
      <Divider />
      <CardActions>
        <Button
          fullWidth
          variant="text"
        >
          Upload picture
        </Button>
      </CardActions>
    </Card>
  );
};
