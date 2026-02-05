'use client'

import { Box, InputBase, Badge, Avatar, IconButton, Tooltip, Paper, Stack } from '@mui/material'
import { Search, Notifications, Menu, Mail } from '@mui/icons-material'

interface TopbarProps {
  onMenuClick?: () => void
}

export default function Topbar({ onMenuClick }: TopbarProps) {
  return (
    <Box sx={{ flexGrow: 1, display: 'flex', alignItems: 'center', gap: 2 }}>
      <IconButton
        color="inherit"
        edge="start"
        onClick={onMenuClick}
        sx={{ mr: 1, display: { sm: 'none' } }}
      >
        <Menu />
      </IconButton>
      <Paper
        elevation={0}
        sx={{
          display: 'flex',
          alignItems: 'center',
          bgcolor: 'background.paper',
          borderRadius: 3,
          px: 2,
          py: 0.5,
          flex: 1,
          maxWidth: 640,
          border: '1px solid rgba(148,163,184,0.18)',
          boxShadow: 'inset 0 0 0 1px rgba(255,255,255,0.02)',
        }}
      >
        <Search sx={{ mr: 1, color: 'text.secondary' }} />
        <InputBase placeholder="Search users, queries, insights…" sx={{ flex: 1 }} />
      </Paper>
      <Stack direction="row" spacing={1} alignItems="center">
        <Tooltip title="Inbox">
          <IconButton color="inherit">
            <Badge badgeContent={3} color="secondary">
              <Mail />
            </Badge>
          </IconButton>
        </Tooltip>
        <Tooltip title="Notifications">
          <IconButton color="inherit">
            <Badge badgeContent={5} color="error">
              <Notifications />
            </Badge>
          </IconButton>
        </Tooltip>
        <Avatar sx={{ bgcolor: 'primary.main' }}>SK</Avatar>
      </Stack>
    </Box>
  )
}
