import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Container, Grid, Paper, Typography, Box, Alert, Tooltip, IconButton } from '@mui/material';
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend
} from 'recharts';
import InfoIcon from '@mui/icons-material/Info';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import Filters from './Filters.js';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

function Dashboard() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    startDate: null,
    endDate: null,
    selectedProducts: [],
    searchTerm: ''
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await axios.get('http://localhost:5001/api/data/overview', {
          params: {
            start_date: filters.startDate,
            end_date: filters.endDate,
            products: filters.selectedProducts.length > 0 ? filters.selectedProducts.join(',') : null,
            search: filters.searchTerm
          }
        });
        setData(response.data);
      } catch (error) {
        console.error('Error fetching data:', error);
        setError(
          error.response?.data?.error || 
          'Failed to fetch data. Please try again later.'
        );
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [filters]);

  const renderKPICard = (title, value, previousValue, info) => {
    const percentageChange = ((value - previousValue) / previousValue) * 100;
    const isPositive = percentageChange > 0;

    return (
      <Paper sx={{ p: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <Typography variant="h6" color="textSecondary">
            {title}
          </Typography>
          <Tooltip title={info}>
            <IconButton size="small">
              <InfoIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
        <Typography variant="h4" sx={{ my: 2 }}>
          {typeof value === 'number' ? value.toLocaleString('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
          }) : value.toLocaleString()}
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
          {isPositive ? (
            <TrendingUpIcon color="success" />
          ) : (
            <TrendingDownIcon color="error" />
          )}
          <Typography
            variant="body2"
            color={isPositive ? 'success.main' : 'error.main'}
            sx={{ ml: 1 }}
          >
            {Math.abs(percentageChange).toFixed(1)}% vs previous period
          </Typography>
        </Box>
      </Paper>
    );
  };

  if (loading) {
    return (
      <Container maxWidth="lg">
        <Typography variant="h6" align="center" sx={{ mt: 4 }}>
          Loading...
        </Typography>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg">
        <Alert severity="error" sx={{ mt: 4 }}>
          {error}
        </Alert>
      </Container>
    );
  }

  if (!data) {
    return (
      <Container maxWidth="lg">
        <Alert severity="info" sx={{ mt: 4 }}>
          No data available for the selected filters.
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Pharmaceutical Sales Dashboard
        </Typography>
        <Typography variant="subtitle1" color="textSecondary" gutterBottom>
          Track and analyze your pharmaceutical sales performance
        </Typography>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={3}>
          <Filters
            filters={filters}
            setFilters={setFilters}
            dateRange={{
              min: data.date_range.min,
              max: data.date_range.max
            }}
            products={data.products}
          />
        </Grid>

        <Grid item xs={12} md={9}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              {renderKPICard(
                'Total Sales',
                data.total_sales,
                data.previous_total_sales,
                'Total revenue from all sales in the selected period'
              )}
            </Grid>
            
            <Grid item xs={12} md={4}>
              {renderKPICard(
                'Total Units',
                data.total_units,
                data.previous_total_units,
                'Total number of units sold in the selected period'
              )}
            </Grid>
            
            <Grid item xs={12} md={4}>
              {renderKPICard(
                'Average Order Value',
                data.avg_order_value,
                data.previous_avg_order_value,
                'Average value per order in the selected period'
              )}
            </Grid>

            <Grid item xs={12}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Sales Trend Analysis
                </Typography>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  Monthly revenue and unit sales comparison
                </Typography>
                <div style={{ width: '100%', height: 400 }}>
                  <ResponsiveContainer>
                    <AreaChart data={data.monthly_trend}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="Month" />
                      <YAxis yAxisId="left" />
                      <YAxis yAxisId="right" orientation="right" />
                      <RechartsTooltip formatter={(value) => `$${value.toLocaleString()}`} />
                      <Legend />
                      {filters.selectedProducts.length > 0 ? (
                        filters.selectedProducts.map((product, index) => (
                          <Area
                            key={product}
                            type="monotone"
                            dataKey={product}
                            yAxisId="left"
                            stroke={COLORS[index % COLORS.length]}
                            fill={COLORS[index % COLORS.length]}
                            fillOpacity={0.3}
                            strokeWidth={2}
                          />
                        ))
                      ) : (
                        <Area
                          type="monotone"
                          dataKey="Total"
                          yAxisId="left"
                          stroke="#8884d8"
                          fill="#8884d8"
                          fillOpacity={0.3}
                          strokeWidth={2}
                        />
                      )}
                      <Area
                        type="monotone"
                        dataKey="Units"
                        yAxisId="right"
                        stroke="#82ca9d"
                        fill="#82ca9d"
                        fillOpacity={0.3}
                        strokeWidth={2}
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </Paper>
            </Grid>

            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Product Performance
                </Typography>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  Sales distribution by product
                </Typography>
                <div style={{ width: '100%', height: 400 }}>
                  <ResponsiveContainer>
                    <BarChart data={data.product_summary} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis type="number" />
                      <YAxis dataKey="Product" type="category" width={150} />
                      <RechartsTooltip formatter={(value) => `$${value.toLocaleString()}`} />
                      <Bar 
                        dataKey="Total" 
                        fill="#82ca9d"
                        label={{ position: 'right', formatter: (value) => `$${value.toLocaleString()}` }}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </Paper>
            </Grid>

            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Market Share Analysis
                </Typography>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  Revenue distribution across product categories
                </Typography>
                <div style={{ width: '100%', height: 400 }}>
                  <ResponsiveContainer>
                    <PieChart>
                      <Pie
                        data={data.product_summary}
                        dataKey="Total"
                        nameKey="Product"
                        cx="50%"
                        cy="50%"
                        outerRadius={150}
                        label={(entry) => `${entry.Product} (${((entry.Total / data.total_sales) * 100).toFixed(1)}%)`}
                      >
                        {data.product_summary.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <RechartsTooltip formatter={(value) => `$${value.toLocaleString()}`} />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </Paper>
            </Grid>
          </Grid>
        </Grid>
      </Grid>
    </Container>
  );
}

export default Dashboard; 