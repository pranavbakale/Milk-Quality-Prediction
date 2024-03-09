import Head from 'next/head';
import { Box, Container, Unstable_Grid2 as Grid } from '@mui/material';
import { Layout as DashboardLayout } from 'src/layouts/dashboard/layout';
import { OverviewLatestOrders } from 'src/sections/overview/prediction-history';
import { ImportData } from 'src/sections/overview/import-data';
import { PredictionAnalysis } from 'src/sections/overview/prediction-analysis';

const now = new Date();

const Page = () => (
  <>
    <Head>
      <title>
        Overview
      </title>
    </Head>
    <Box
      component="main"
      sx={{
        flexGrow: 1,
        py: 8
      }}
    >
      <Container maxWidth="xl">
        <Grid
          container
          spacing={3}
        >
          <Grid
            xs={12}
            sm={6}
            lg={12}
          >
            <ImportData
              difference={16}
              positive={false}
              sx={{ height: '100%' }}
              value="1.6k"
            />
          </Grid>          
          <Grid
            xs={12}
            md={6}
            lg={4}
          >
          <PredictionAnalysis
              chartSeries={[22, 15, 63]}
              labels={['Low', 'Medium', 'High']}
              sx={{ height: '100%' }}
          />
          </Grid>
          
          <Grid
            xs={12}
            md={12}
            lg={8}
          >
          <OverviewLatestOrders
            orders={[
              {
                id: 'f69f88012978187a6c12897f',
                no: '1',
                customer: {
                  name: 'Milk_Apr_2019'
                },
                createdAt: 1555016400000
              },
              {
                id: 'f69f88012978187a6c12897f',
                no: '2',
                customer: {
                  name: 'Milk_Apr_2019'
                },
                createdAt: 1555016400000
              },
              {
                id: 'f69f88012978187a6c12897f',
                no: '3',
                customer: {
                  name: 'Milk_Apr_2019'
                },
                createdAt: 1555016400000
              },
              {
                id: 'f69f88012978187a6c12897f',
                no: '4',
                customer: {
                  name: 'Milk_Apr_2019'
                },
                createdAt: 1555016400000
              },
              {
                id: 'f69f88012978187a6c12897f',
                no: '5',
                customer: {
                  name: 'Milk_Apr_2019'
                },
                createdAt: 1555016400000
              }
            ]}
            sx={{ height: '100%' }}
          />
          </Grid>
        </Grid>
      </Container>
    </Box>
  </>
);

Page.getLayout = (page) => (
  <DashboardLayout>
    {page}
  </DashboardLayout>
);

export default Page;