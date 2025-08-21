import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Search, Download, TrendingUp, Package, RotateCcw, Globe, CheckCircle, XCircle, Clock, Trash2 } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Button } from './ui/button'
import { Input } from './ui/input'
import { Badge } from './ui/badge'
import { apiService, type AnalysisResult, type PlatformStats } from '../lib/api'
import { StatsCards } from './StatsCards'
import { DataTable } from './DataTable'
import { AnalysisModal } from './AnalysisModal'

export const Dashboard: React.FC = () => {
  const [results, setResults] = useState<AnalysisResult[]>([])
  const [stats, setStats] = useState<PlatformStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [analyzing, setAnalyzing] = useState(false)
  const [url, setUrl] = useState('')
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedResult, setSelectedResult] = useState<AnalysisResult | null>(null)
  const [jobId, setJobId] = useState<string | null>(null)
  const [jobStatus, setJobStatus] = useState<string>('')

  useEffect(() => {
    loadData()
  }, [])

  useEffect(() => {
    let interval: NodeJS.Timeout
    if (jobId && jobStatus !== 'completed' && jobStatus !== 'failed') {
      interval = setInterval(async () => {
        try {
          const job = await apiService.getJobStatus(jobId)
          setJobStatus(job.status)
          if (job.status === 'completed') {
            await loadData()
            setJobId(null)
            setAnalyzing(false)
          } else if (job.status === 'failed') {
            setJobId(null)
            setAnalyzing(false)
          }
        } catch (error) {
          console.error('Error checking job status:', error)
        }
      }, 2000)
    }
    return () => clearInterval(interval)
  }, [jobId, jobStatus])

  const loadData = async () => {
    try {
      setLoading(true)
      const [resultsData, statsData] = await Promise.all([
        apiService.getAllResults(),
        apiService.getStats()
      ])
      setResults(resultsData)
      setStats(statsData)
    } catch (error) {
      console.error('Error loading data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleAnalyze = async () => {
    if (!url.trim()) return
    
    try {
      setAnalyzing(true)
      const response = await apiService.analyzeWebsite(url)
      setJobId(response.job_id)
      setJobStatus('pending')
      setUrl('')
    } catch (error) {
      console.error('Error starting analysis:', error)
      setAnalyzing(false)
    }
  }

  const handleExportCsv = async () => {
    try {
      const csvData = await apiService.exportCsv()
      const blob = new Blob([csvData], { type: 'text/csv' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'ecommerce_policies.csv'
      a.click()
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Error exporting CSV:', error)
    }
  }

  const handleDeleteResult = async (id: number) => {
    try {
      await apiService.deleteResult(id)
      await loadData() // Refresh data
    } catch (error) {
      console.error('Error deleting result:', error)
    }
  }

  const handleClearAll = async () => {
    if (window.confirm(`Delete all ${results.length} analysis results? This action cannot be undone.`)) {
      try {
        await apiService.deleteAllResults()
        await loadData() // Refresh data
      } catch (error) {
        console.error('Error clearing all results:', error)
      }
    }
  }

  const filteredResults = results.filter(result =>
    result.domain.toLowerCase().includes(searchTerm.toLowerCase()) ||
    result.shipping_policy.toLowerCase().includes(searchTerm.toLowerCase()) ||
    result.return_policy.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      {/* Header */}
      <div className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-40">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <motion.div 
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center space-x-3"
            >
              <div className="h-10 w-10 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
                <Globe className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                  E-commerce Policy Analyzer
                </h1>
                <p className="text-sm text-muted-foreground">
                  Automated analysis of shipping and return policies
                </p>
              </div>
            </motion.div>
            
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center space-x-3"
            >
              <Button
                onClick={handleExportCsv}
                variant="outline"
                size="sm"
                className="flex items-center space-x-2"
              >
                <Download className="h-4 w-4" />
                <span>Export CSV</span>
              </Button>
              {results.length > 0 && (
                <Button
                  onClick={handleClearAll}
                  variant="outline"
                  size="sm"
                  className="flex items-center space-x-2 text-red-600 hover:text-red-800 hover:border-red-300"
                >
                  <Trash2 className="h-4 w-4" />
                  <span>Clear All</span>
                </Button>
              )}
            </motion.div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8 space-y-8">
        {/* Hero Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center space-y-6"
        >
          <div className="max-w-3xl mx-auto">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Analyze e-commerce policies in 
              <span className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent"> real-time</span>
            </h2>
            <p className="text-xl text-gray-600 mb-8">
              Enter a URL and our AI automatically extracts all shipping, returns and insurance information
            </p>
          </div>

          {/* URL Input */}
          <motion.div 
            className="max-w-2xl mx-auto"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <div className="flex space-x-4">
              <Input
                type="url"
                placeholder="https://example.com"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                className="flex-1 h-12 text-lg"
                disabled={analyzing}
              />
              <Button
                onClick={handleAnalyze}
                disabled={analyzing || !url.trim()}
                size="lg"
                className="px-8 h-12 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
              >
                {analyzing ? (
                  <>
                    <RotateCcw className="h-5 w-5 mr-2 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <TrendingUp className="h-5 w-5 mr-2" />
                    Analyze
                  </>
                )}
              </Button>
            </div>

            {/* Job Status */}
            <AnimatePresence>
              {jobId && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="mt-4 p-4 bg-white rounded-lg border shadow-sm"
                >
                  <div className="flex items-center space-x-3">
                    {jobStatus === 'pending' && <Clock className="h-5 w-5 text-yellow-500" />}
                    {jobStatus === 'processing' && <RotateCcw className="h-5 w-5 text-blue-500 animate-spin" />}
                    {jobStatus === 'completed' && <CheckCircle className="h-5 w-5 text-green-500" />}
                    {jobStatus === 'failed' && <XCircle className="h-5 w-5 text-red-500" />}
                    <span className="text-sm font-medium">
                      {jobStatus === 'pending' && 'Pending...'}
                      {jobStatus === 'processing' && 'Analyzing...'}
                      {jobStatus === 'completed' && 'Analysis completed!'}
                      {jobStatus === 'failed' && 'Analysis failed'}
                    </span>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        </motion.div>

        {/* Stats Cards */}
        {stats && <StatsCards stats={stats} />}

        {/* Search and Filters */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Package className="h-5 w-5" />
                <span>Analysis Results</span>
                <Badge variant="secondary">{filteredResults.length}</Badge>
              </CardTitle>
              <CardDescription>
                Explore and filter extracted policies
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center space-x-4 mb-6">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search by domain, policy..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>

              {loading ? (
                <div className="text-center py-8">
                  <RotateCcw className="h-8 w-8 animate-spin mx-auto mb-4 text-muted-foreground" />
                  <p className="text-muted-foreground">Loading data...</p>
                </div>
              ) : (
                <DataTable 
                  results={filteredResults} 
                  onRowClick={setSelectedResult}
                  onDeleteResult={handleDeleteResult}
                />
              )}
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Analysis Modal */}
      <AnalysisModal
        result={selectedResult}
        isOpen={!!selectedResult}
        onClose={() => setSelectedResult(null)}
      />
    </div>
  )
}
