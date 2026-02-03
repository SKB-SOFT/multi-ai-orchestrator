// src/views/dashboard/components/MetricsChart.tsx
import React, { useState, useEffect } from 'react'
import {
  Box,
  Flex,
  Heading,
  ButtonGroup,
  Button,
  Skeleton,
  useColorModeValue,
} from '@chakra-ui/react'
import { dashboardService } from '@/services/dashboard'

type TimeRange = '1h' | '6h' | '24h' | '7d'

const MetricsChart: React.FC = () => {
  const [timeRange, setTimeRange] = useState<TimeRange>('24h')
  const [loading, setLoading] = useState(false)

  const bg = useColorModeValue('white', 'gray.800')
  const textColor = useColorModeValue('gray.800', 'white')

  useEffect(() => {
    fetchMetrics()
  }, [timeRange])

  const fetchMetrics = async () => {
    setLoading(true)
    try {
      // Simulate fetching metrics
      await new Promise(resolve => setTimeout(resolve, 500))
    } catch (error) {
      console.error('Failed to fetch metrics:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box bg={bg} p={6} borderRadius="lg" boxShadow="sm">
      <Flex justify="space-between" align="center" mb={6}>
        <Heading size="lg" color="#0a192f" fontWeight="800" fontFamily="Inter, Space Grotesk, ui-sans-serif">Performance Metrics</Heading>
        <ButtonGroup size="sm" isAttached variant="outline">
          <Button
            colorScheme={timeRange === '1h' ? 'blue' : 'gray'}
            onClick={() => setTimeRange('1h')}
          >
            1h
          </Button>
          <Button
            colorScheme={timeRange === '6h' ? 'blue' : 'gray'}
            onClick={() => setTimeRange('6h')}
          >
            6h
          </Button>
          <Button
            colorScheme={timeRange === '24h' ? 'blue' : 'gray'}
            onClick={() => setTimeRange('24h')}
          >
            24h
          </Button>
          <Button
            colorScheme={timeRange === '7d' ? 'blue' : 'gray'}
            onClick={() => setTimeRange('7d')}
          >
            7d
          </Button>
        </ButtonGroup>
      </Flex>

      {loading ? (
        <Skeleton height="400px" />
      ) : (
        <Box
          w="100%"
          h="400px"
          display="flex"
          alignItems="center"
          justifyContent="center"
          bg={useColorModeValue('gray.50', 'gray.700')}
          borderRadius="md"
          color="gray.500"
        >
          <div>Chart visualization goes here</div>
        </Box>
      )}
    </Box>
  )
}

export default MetricsChart
