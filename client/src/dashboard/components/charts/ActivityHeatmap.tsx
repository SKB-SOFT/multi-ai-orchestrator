'use client'

import { Box } from '@mui/material'

const heatmapData = [
  [1, 2, 1, 3, 2, 4, 2, 3, 1, 0, 2, 3],
  [0, 1, 2, 2, 3, 4, 3, 2, 1, 1, 2, 4],
  [1, 1, 0, 2, 3, 3, 4, 4, 2, 1, 3, 2],
  [2, 3, 2, 1, 2, 4, 4, 3, 2, 2, 3, 4],
  [1, 2, 3, 3, 4, 4, 3, 2, 1, 0, 1, 2],
  [0, 1, 2, 2, 3, 3, 2, 1, 1, 2, 3, 3],
  [1, 2, 2, 3, 4, 4, 3, 2, 2, 3, 4, 4],
]

const colorScale = ['#0f172a', '#1e293b', '#334155', '#475569', '#60a5fa']

export default function ActivityHeatmap() {
  return (
    <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(12, 1fr)', gap: 1 }}>
      {heatmapData.flat().map((value, index) => (
        <Box
          key={index}
          sx={{
            width: '100%',
            pt: '100%',
            borderRadius: 1,
            bgcolor: colorScale[value],
            border: '1px solid rgba(255,255,255,0.08)',
            transition: 'transform 0.15s ease, box-shadow 0.15s ease',
            '&:hover': {
              transform: 'scale(1.05)',
              boxShadow: '0 4px 12px rgba(96,165,250,0.25)',
            },
          }}
        />
      ))}
    </Box>
  )
}
