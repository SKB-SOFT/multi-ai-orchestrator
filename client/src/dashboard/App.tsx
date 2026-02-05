'use client'

import { useState } from 'react'
import {
  CssBaseline,
  Box,
  AppBar,
  Toolbar,
  Drawer,
  ThemeProvider,
  createTheme,
} from '@mui/material'
import Sidebar from './components/Sidebar'
import Topbar from './components/Topbar'
import DashboardOverview from './components/Dashboard/Overview'

const drawerWidth = 260

export default function App() {
  const [mobileOpen, setMobileOpen] = useState(false)
  const theme = createTheme({
    palette: {
      mode: 'dark',
      primary: { main: '#7C5CFC' },
      secondary: { main: '#22D3EE' },
      background: {
        default: '#0B1020',
        paper: '#0F172A',
      },
      text: {
        primary: '#F8FAFC',
        secondary: '#94A3B8',
      },
    },
    shape: { borderRadius: 16 },
    typography: {
      fontFamily: 'Inter, ui-sans-serif, system-ui',
      h4: { fontWeight: 700, letterSpacing: '-0.02em' },
      h6: { fontWeight: 600, letterSpacing: '-0.01em' },
    },
    components: {
      MuiPaper: {
        styleOverrides: {
          root: {
            backgroundImage: 'none',
            border: '1px solid rgba(148,163,184,0.08)',
            boxShadow: '0 18px 40px rgba(2,6,23,0.45)',
          },
        },
      },
      MuiCard: {
        styleOverrides: {
          root: {
            border: '1px solid rgba(148,163,184,0.08)',
            boxShadow: '0 18px 40px rgba(2,6,23,0.45)',
          },
        },
      },
      MuiTableCell: {
        styleOverrides: {
          head: { color: '#CBD5E1', fontWeight: 700 },
          body: { color: '#E2E8F0' },
        },
      },
    },
  })

  const handleDrawerToggle = () => setMobileOpen(!mobileOpen)

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex' }}>
        {/* AppBar - Perfect top spacing */}
        <AppBar
          position="fixed"
          sx={{
            zIndex: 1400,
            width: { sm: `calc(100% - ${drawerWidth}px)` },
            ml: { sm: `${drawerWidth}px` },
            bgcolor: 'rgba(11,16,32,0.95)',
            backdropFilter: 'blur(20px)',
            borderBottom: '1px solid rgba(148,163,184,0.12)',
            boxShadow: '0 4px 20px rgba(0,0,0,0.3)',
            height: { xs: 56, sm: 64 },
          }}
        >
          <Toolbar sx={{ px: { xs: 2, sm: 3, md: 4 }, height: '100%' }}>
            <Topbar onMenuClick={handleDrawerToggle} />
          </Toolbar>
        </AppBar>

        {/* Permanent Desktop Sidebar */}
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
              bgcolor: 'background.default',
              borderRight: '1px solid rgba(148,163,184,0.12)',
              boxShadow: '8px 0 24px rgba(0,0,0,0.15)',
            },
          }}
          open
        >
          <Sidebar />
        </Drawer>

        {/* Mobile Temporary Sidebar */}
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{ keepMounted: true }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { 
              boxSizing: 'border-box', 
              width: drawerWidth,
              bgcolor: 'background.paper',
              borderRight: '1px solid rgba(148,163,184,0.2)',
            },
          }}
        >
          <Sidebar />
        </Drawer>

        {/* Main Content Area - PERFECT SPACING */}
        <Box
          component="main"
          sx={{
            flexGrow: 1,
            width: { sm: `calc(100% - ${drawerWidth}px)` },
            mt: { xs: '56px', sm: '64px' }, // Exact AppBar height
            pb: 8, // Bottom padding for perfect scroll
            bgcolor: 'background.default',
            minHeight: '100vh',
            overflow: 'hidden',
            // Perfect responsive padding system
            px: { xs: 0, sm: 0 },
            pl: { xs: 1, sm: 2, md: 3 },
            pr: { xs: 1, sm: 2, md: 3 },
            pt: { xs: 1, sm: 1 }, // Minimal top padding
          }}
        >
          {/* Content Container - Perfect max-width */}
          <Box sx={{ 
            width: '100%',
            maxWidth: 1700,
            ml: 'auto',
            mr: { xs: 1, sm: 2, md: 3 },
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
            py: 0,
          }}>
            <DashboardOverview />
          </Box>
        </Box>
      </Box>
    </ThemeProvider>
  )
}
