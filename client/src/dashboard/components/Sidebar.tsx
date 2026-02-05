'use client'

import { Box, List, ListItem, ListItemButton, ListItemIcon, ListItemText, Avatar, Divider, Typography, ListSubheader } from '@mui/material'
import { Dashboard, People, BarChart, Analytics, Settings } from '@mui/icons-material'

export default function Sidebar() {
  const menuItems = [
    { icon: <Dashboard />, label: 'Dashboard', active: true },
    { icon: <People />, label: 'Users', active: false },
    { icon: <BarChart />, label: 'Metrics', active: false },
    { icon: <Analytics />, label: 'Analytics', active: false },
    { icon: <Settings />, label: 'Settings', active: false },
  ]

  return (
    <>
      <Box sx={{ p: 3, pt: 3, pb: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
        <Avatar sx={{ width: 40, height: 40, bgcolor: 'primary.main', boxShadow: '0 6px 16px rgba(124,92,252,0.35)' }}>AI</Avatar>
        <Box>
          <Typography variant="subtitle1" fontWeight={700} color="text.primary">
            Multi-AI Brain
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Enterprise Dashboard
          </Typography>
        </Box>
      </Box>
      <Divider />
      <List
        sx={{ px: 1, pt: 1 }}
        subheader={
          <ListSubheader component="div" sx={{ bgcolor: 'transparent', color: 'text.secondary' }}>
            MAIN
          </ListSubheader>
        }
      >
        {menuItems.map((item) => (
          <ListItem key={item.label} disablePadding>
            <ListItemButton
              sx={{
                borderRadius: 2,
                mx: 1,
                mb: 0.5,
                color: 'text.secondary',
                '&:hover': { bgcolor: 'rgba(124,92,252,0.12)', color: 'text.primary' },
                ...(item.active && {
                  bgcolor: 'primary.main',
                  color: 'white',
                  '&:hover': { bgcolor: '#6D4CFF' },
                }),
              }}
            >
              <ListItemIcon sx={{ minWidth: 44, color: item.active ? 'white' : 'inherit' }}>
                {item.icon}
              </ListItemIcon>
              <ListItemText primary={item.label} primaryTypographyProps={{ fontWeight: item.active ? 700 : 500 }} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </>
  )
}
