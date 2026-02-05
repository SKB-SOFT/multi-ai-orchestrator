'use client'

import * as React from 'react'
import { PieChart } from '@mui/x-charts/PieChart'
import { useDrawingArea } from '@mui/x-charts/hooks'
import { styled } from '@mui/material/styles'
import Card from '@mui/material/Card'
import CardContent from '@mui/material/CardContent'
import Typography from '@mui/material/Typography'
import Box from '@mui/material/Box'
import Stack from '@mui/material/Stack'
import LinearProgress, { linearProgressClasses } from '@mui/material/LinearProgress'
import Avatar from '@mui/material/Avatar'

interface CountryPieProps {
  data: { country: string; users: number; percentage: number }[]
}

interface StyledTextProps {
  variant: 'primary' | 'secondary'
}

const StyledText = styled('text', {
  shouldForwardProp: (prop) => prop !== 'variant',
})<StyledTextProps>(({ theme }) => ({
  textAnchor: 'middle',
  dominantBaseline: 'central',
  fill: (theme.vars || theme).palette.text.secondary,
  variants: [
    {
      props: { variant: 'primary' },
      style: { fontSize: theme.typography.h5.fontSize, fontWeight: theme.typography.h5.fontWeight },
    },
    {
      props: { variant: 'secondary' },
      style: { fontSize: theme.typography.body2.fontSize, fontWeight: theme.typography.body2.fontWeight },
    },
  ],
}))

function PieCenterLabel({ primaryText, secondaryText }: { primaryText: string; secondaryText: string }) {
  const { width, height, left, top } = useDrawingArea()
  const primaryY = top + height / 2 - 10
  const secondaryY = primaryY + 22

  return (
    <React.Fragment>
      <StyledText variant="primary" x={left + width / 2} y={primaryY}>
        {primaryText}
      </StyledText>
      <StyledText variant="secondary" x={left + width / 2} y={secondaryY}>
        {secondaryText}
      </StyledText>
    </React.Fragment>
  )
}

const palette = ['#94A3B8', '#64748B', '#475569', '#334155']

export default function CountryPie({ data }: CountryPieProps) {
  const total = data.reduce((sum, item) => sum + item.users, 0)

  const chartData = data.map((item, index) => ({
    id: item.country,
    value: item.users,
    label: item.country,
    color: palette[index % palette.length],
  }))

  return (
    <Card variant="outlined" sx={{ display: 'flex', flexDirection: 'column', gap: 1, flexGrow: 1, height: '100%' }}>
      <CardContent>
        <Typography component="h2" variant="subtitle2" sx={{ mb: 1 }}>
          Users by country
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 1 }}>
          <PieChart
            colors={palette}
            margin={{ left: 80, right: 80, top: 70, bottom: 70 }}
            series={[
              {
                data: chartData,
                innerRadius: 84,
                outerRadius: 112,
                paddingAngle: 0,
                highlightScope: { fade: 'global', highlight: 'item' },
              },
            ]}
            height={280}
            width={280}
            hideLegend
          >
            <PieCenterLabel primaryText={`${(total / 1000).toFixed(1)}K`} secondaryText="Total" />
          </PieChart>
        </Box>

        {data.map((country, index) => (
          <Stack key={country.country} direction="row" sx={{ alignItems: 'center', gap: 2, pb: 2.5 }}>
            <Avatar
              sx={{
                width: 28,
                height: 28,
                bgcolor: 'rgba(124,92,252,0.12)',
                color: 'text.primary',
                fontSize: 12,
              }}
            >
              {country.country.slice(0, 1)}
            </Avatar>
            <Stack sx={{ gap: 1, flexGrow: 1 }}>
              <Stack direction="row" sx={{ justifyContent: 'space-between', alignItems: 'center', gap: 2 }}>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>
                  {country.country}
                </Typography>
                <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                  {country.percentage}%
                </Typography>
              </Stack>
              <LinearProgress
                variant="determinate"
                aria-label="Users by country"
                value={country.percentage}
                sx={{
                  height: 8,
                  borderRadius: 4,
                  [`& .${linearProgressClasses.bar}`]: {
                    backgroundColor: palette[index % palette.length],
                  },
                }}
              />
            </Stack>
          </Stack>
        ))}
      </CardContent>
    </Card>
  )
}
