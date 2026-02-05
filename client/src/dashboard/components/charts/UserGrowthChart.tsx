'use client'

import { useTheme } from '@mui/material/styles'
import { LineChart } from '@mui/x-charts/LineChart'

function AreaGradient({ color, id }: { color: string; id: string }) {
  return (
    <defs>
      <linearGradient id={id} x1="50%" y1="0%" x2="50%" y2="100%">
        <stop offset="0%" stopColor={color} stopOpacity={0.5} />
        <stop offset="100%" stopColor={color} stopOpacity={0} />
      </linearGradient>
    </defs>
  )
}

const days = [
  'Jan 1', 'Jan 3', 'Jan 5', 'Jan 7', 'Jan 9', 'Jan 11', 'Jan 13', 'Jan 15',
  'Jan 17', 'Jan 19', 'Jan 21', 'Jan 23', 'Jan 25', 'Jan 27', 'Jan 29',
]

export default function UserGrowthChart() {
  const theme = useTheme()

  const colorPalette = [
    theme.palette.primary.light,
    theme.palette.primary.main,
    theme.palette.primary.dark,
  ]

  return (
    <LineChart
      colors={colorPalette}
      xAxis={[
        {
          scaleType: 'point',
          data: days,
          tickInterval: (index, i) => (i + 1) % 3 === 0,
          height: 24,
        },
      ]}
      yAxis={[{ width: 50 }]}
      series={[
        {
          id: 'direct',
          label: 'Direct',
          showMark: false,
          curve: 'linear',
          stack: 'total',
          area: true,
          stackOrder: 'ascending',
          data: [300, 600, 900, 1200, 900, 1400, 1800, 2100, 1700, 2300, 2500, 2800, 2600, 3000, 3200],
        },
        {
          id: 'referral',
          label: 'Referral',
          showMark: false,
          curve: 'linear',
          stack: 'total',
          area: true,
          stackOrder: 'ascending',
          data: [500, 900, 700, 1400, 1100, 1700, 2300, 2000, 2600, 2900, 2300, 3200, 3500, 3800, 4100],
        },
        {
          id: 'organic',
          label: 'Organic',
          showMark: false,
          curve: 'linear',
          stack: 'total',
          area: true,
          stackOrder: 'ascending',
          data: [1000, 1400, 1200, 1700, 1300, 2000, 2400, 2200, 2600, 2800, 2500, 3000, 3400, 3700, 3900],
        },
      ]}
      height={260}
      margin={{ left: 0, right: 20, top: 20, bottom: 0 }}
      grid={{ horizontal: true }}
      sx={{
        '& .MuiAreaElement-series-organic': { fill: "url('#organic')" },
        '& .MuiAreaElement-series-referral': { fill: "url('#referral')" },
        '& .MuiAreaElement-series-direct': { fill: "url('#direct')" },
      }}
      hideLegend
    >
      <AreaGradient color={theme.palette.primary.dark} id="organic" />
      <AreaGradient color={theme.palette.primary.main} id="referral" />
      <AreaGradient color={theme.palette.primary.light} id="direct" />
    </LineChart>
  )
}
