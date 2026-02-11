'use client'

import { Grid, Card, CardContent, Typography, Chip, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Stack, Box } from '@mui/material'
import UserGrowthChart from '../charts/UserGrowthChart'
import CountryPie from '../charts/CountryPie'
import ActivityHeatmap from '../charts/ActivityHeatmap'
import { mockUsersData } from '../../data/mockData'

const StatCard = ({ label, value, chipLabel, chipColor }: { label: string; value: string | number; chipLabel?: string; chipColor?: 'success' | 'primary' | 'warning' }) => (
  <Card sx={{ 
    height: 160, 
    position: 'relative', 
    overflow: 'hidden',
    transition: 'all 0.2s ease-in-out'
  }}>
    <CardContent sx={{ height: '100%', p: 3, pt: 2.5 }}>
      <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 2 }}>
        <Typography variant="body2" color="text.secondary" fontWeight={500}>
          {label}
        </Typography>
        {chipLabel && <Chip label={chipLabel} color={chipColor || 'primary'} size="small" />}
      </Stack>
      <Typography variant="h3" fontWeight={700} sx={{ mb: 0.5 }}>
        {value}
      </Typography>
      <Box sx={{ 
        position: 'absolute', 
        right: -25, 
        top: -25, 
        width: 100, 
        height: 100, 
        borderRadius: '50%', 
        bgcolor: 'rgba(124,92,252,0.08)',
        opacity: 0.6
      }} />
    </CardContent>
  </Card>
)

export default function DashboardOverview() {
  return (
    <Box sx={{ px: 0, py: 2 }}>
      {/* Header */}
      <Stack
        direction={{ xs: 'column', sm: 'row' }}
        alignItems={{ xs: 'flex-start', sm: 'center' }}
        justifyContent="space-between"
        sx={{ mb: 5, gap: 2 }}
      >
        <Box>
          <Typography variant="h3" fontWeight={700} sx={{ mb: 0.5 }}>
            Dashboard Overview
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ fontSize: '1.1rem' }}>
            Real-time user growth, activity, and retention insights
          </Typography>
        </Box>
        <Chip label="Last 30 days" variant="outlined" size="medium" />
      </Stack>

      {/* KPI Cards */}
      <Grid container spacing={3} sx={{ mb: 5 }}>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard
            label="Total Users"
            value={mockUsersData.totalUsers.toLocaleString()}
            chipLabel="+12.4%"
            chipColor="success"
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard
            label="Active Users"
            value={mockUsersData.activeUsers.toLocaleString()}
            chipLabel="78%"
            chipColor="primary"
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard
            label="New Today"
            value={mockUsersData.newUsersToday}
            chipLabel="+8"
            chipColor="success"
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard
            label="Retention"
            value={`${mockUsersData.retentionRate}%`}
            chipLabel="7d"
            chipColor="warning"
          />
        </Grid>
      </Grid>

      {/* Charts Row */}
      <Grid container spacing={{ xs: 2, md: 3 }} sx={{ mb: 4 }}>
        <Grid size={{ xs: 12, md: 8 }}>
          <Paper sx={{ 
            p: { xs: 3, sm: 4 }, 
            minHeight: 420, 
            display: 'flex', 
            flexDirection: 'column',
            boxShadow: 4
          }}>
            <Typography variant="h5" fontWeight={600} sx={{ mb: 1.5, color: 'text.primary' }}>
              Sessions
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3, fontSize: '1rem' }}>
              Sessions per day for the last 30 days
            </Typography>
            <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 4 }}>
              <Typography variant="h3" component="span" fontWeight={700} color="primary.main">
                13,277
              </Typography>
              <Chip size="medium" color="success" label="+35%" />
            </Stack>
            <Box sx={{ flexGrow: 1 }}>
              <UserGrowthChart />
            </Box>
          </Paper>
        </Grid>
        
        <Grid size={{ xs: 12, md: 4 }}>
          <Paper sx={{ 
            p: 4, 
            height: 480,
            display: 'flex',
            flexDirection: 'column',
            boxShadow: 4
          }}>
            <Typography variant="h6" fontWeight={600} sx={{ mb: 2, color: 'text.primary' }}>
              Users by Country
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Distribution across regions
            </Typography>
            <CountryPie data={mockUsersData.usersByCountry} />
          </Paper>
        </Grid>
      </Grid>

      {/* Bottom Row */}
      <Grid container spacing={{ xs: 2, md: 3 }}>
        <Grid size={{ xs: 12, md: 8 }}>
          <Paper sx={{ 
            p: { xs: 3, sm: 4 }, 
            boxShadow: 4,
            borderRadius: 3
          }}>
            <Typography variant="h6" fontWeight={600} sx={{ mb: 3, color: 'text.primary' }}>
              Recent Users
            </Typography>
            <TableContainer sx={{ maxHeight: 400 }}>
              <Table stickyHeader>
                <TableHead sx={{ bgcolor: 'grey.50' }}>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 600, color: 'text.primary' }}>ID</TableCell>
                    <TableCell sx={{ fontWeight: 600, color: 'text.primary' }}>Name</TableCell>
                    <TableCell sx={{ fontWeight: 600, color: 'text.primary' }}>Email</TableCell>
                    <TableCell sx={{ fontWeight: 600, color: 'text.primary' }}>Country</TableCell>
                    <TableCell sx={{ fontWeight: 600, color: 'text.primary' }}>Joined</TableCell>
                    <TableCell sx={{ fontWeight: 600, color: 'text.primary' }} align="right">Status</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {mockUsersData.recentUsers.map((user) => (
                    <TableRow key={user.id} hover sx={{ '&:hover': { bgcolor: 'action.hover' } }}>
                      <TableCell sx={{ fontWeight: 500 }}>{user.id}</TableCell>
                      <TableCell sx={{ fontWeight: 500 }}>{user.name}</TableCell>
                      <TableCell>{user.email}</TableCell>
                      <TableCell>
                        <Chip label={user.country} size="small" color="primary" variant="outlined" />
                      </TableCell>
                      <TableCell>{user.joined}</TableCell>
                      <TableCell align="right">
                        <Chip
                          label={user.status.toUpperCase()}
                          color={user.status === 'active' ? 'success' : 'default'}
                          size="small"
                          variant="filled"
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>
        
        <Grid size={{ xs: 12, md: 4 }}>
          <Paper sx={{ 
            p: 4, 
            height: '100%',
            boxShadow: 4,
            borderRadius: 3
          }}>
            <Typography variant="h6" fontWeight={600} sx={{ mb: 3, color: 'text.primary' }}>
              User Activity Heatmap
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Peak hours and activity patterns
            </Typography>
            <ActivityHeatmap />
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}
