import React from 'react';
import {
  Paper,
  Grid,
  TextField,
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Typography,
  Checkbox,
  ListItemText,
  FormHelperText,
  Button,
} from '@mui/material';
import { DateRangePicker } from '@mui/x-date-pickers-pro/DateRangePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { addDays, startOfMonth, endOfMonth, startOfYear, endOfYear, format } from 'date-fns';

const predefinedRanges = [
  {
    label: 'Last 7 Days',
    getValue: () => ({
      startDate: addDays(new Date(), -7),
      endDate: new Date(),
    }),
  },
  {
    label: 'Last 30 Days',
    getValue: () => ({
      startDate: addDays(new Date(), -30),
      endDate: new Date(),
    }),
  },
  {
    label: 'This Month',
    getValue: () => ({
      startDate: startOfMonth(new Date()),
      endDate: endOfMonth(new Date()),
    }),
  },
  {
    label: 'Last Month',
    getValue: () => {
      const start = startOfMonth(addDays(new Date(), -30));
      return {
        startDate: start,
        endDate: endOfMonth(start),
      };
    },
  },
  {
    label: 'Year to Date',
    getValue: () => ({
      startDate: startOfYear(new Date()),
      endDate: new Date(),
    }),
  },
  {
    label: 'Full Year',
    getValue: () => ({
      startDate: startOfYear(new Date()),
      endDate: endOfYear(new Date()),
    }),
  },
];

function Filters({ filters, setFilters, dateRange, products }) {
  const handleDateRangeChange = (newDateRange) => {
    setFilters(prev => ({
      ...prev,
      startDate: newDateRange[0] ? format(newDateRange[0], 'yyyy-MM-dd') : null,
      endDate: newDateRange[1] ? format(newDateRange[1], 'yyyy-MM-dd') : null
    }));
  };

  const handleProductChange = (event) => {
    const value = event.target.value;
    setFilters(prev => ({
      ...prev,
      selectedProducts: typeof value === 'string' ? value.split(',') : value
    }));
  };

  const handleSearchChange = (event) => {
    setFilters(prev => ({
      ...prev,
      searchTerm: event.target.value
    }));
  };

  const handlePredefinedRange = (range) => {
    const { startDate, endDate } = range.getValue();
    setFilters(prev => ({
      ...prev,
      startDate: format(startDate, 'yyyy-MM-dd'),
      endDate: format(endDate, 'yyyy-MM-dd')
    }));
  };

  const clearFilters = () => {
    setFilters({
      startDate: null,
      endDate: null,
      selectedProducts: [],
      searchTerm: ''
    });
  };

  return (
    <Paper sx={{ p: 2, height: '100%' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">
          Filters
        </Typography>
        <Button size="small" onClick={clearFilters}>
          Clear All
        </Button>
      </Box>

      <Box sx={{ mt: 2 }}>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <Typography variant="subtitle2" gutterBottom>
              Quick Select
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
              {predefinedRanges.map((range) => (
                <Button
                  key={range.label}
                  size="small"
                  variant="outlined"
                  onClick={() => handlePredefinedRange(range)}
                >
                  {range.label}
                </Button>
              ))}
            </Box>
          </Grid>

          <Grid item xs={12}>
            <LocalizationProvider dateAdapter={AdapterDateFns}>
              <DateRangePicker
                value={[
                  filters.startDate ? new Date(filters.startDate) : null,
                  filters.endDate ? new Date(filters.endDate) : null
                ]}
                onChange={handleDateRangeChange}
                calendars={2}
                minDate={new Date(dateRange.min)}
                maxDate={new Date(dateRange.max)}
                sx={{ width: '100%' }}
                slotProps={{
                  textField: {
                    helperText: 'Select date range',
                    size: 'small',
                  },
                  popper: {
                    sx: {
                      '& .MuiPickersCalendarHeader-root': {
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                      }
                    }
                  }
                }}
              />
            </LocalizationProvider>
          </Grid>

          <Grid item xs={12}>
            <FormControl fullWidth>
              <InputLabel>Products</InputLabel>
              <Select
                multiple
                value={filters.selectedProducts}
                onChange={handleProductChange}
                label="Products"
                renderValue={(selected) => selected.join(', ')}
                MenuProps={{
                  PaperProps: {
                    style: {
                      maxHeight: 224,
                      width: 250
                    }
                  }
                }}
              >
                {products.map((product) => (
                  <MenuItem key={product} value={product}>
                    <Checkbox checked={filters.selectedProducts.indexOf(product) > -1} />
                    <ListItemText primary={product} />
                  </MenuItem>
                ))}
              </Select>
              <FormHelperText>
                Select multiple products to compare
              </FormHelperText>
            </FormControl>
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Search"
              variant="outlined"
              value={filters.searchTerm}
              onChange={handleSearchChange}
              placeholder="Search by product or customer..."
              size="small"
            />
          </Grid>
        </Grid>
      </Box>
    </Paper>
  );
}

export default Filters; 