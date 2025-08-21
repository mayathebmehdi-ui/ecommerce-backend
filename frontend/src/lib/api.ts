import axios from 'axios'

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface AnalysisResult {
  id: number
  domain: string
  shipping_policy: string
  shipping_url: string
  return_policy: string
  return_url: string
  self_help_returns: string
  self_help_url: string
  insurance: string
  insurance_url: string
  analyzed_at: string
}

export interface AnalysisJob {
  job_id: string
  url: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  created_at: string
  completed_at?: string
  error_message?: string
}

export interface PlatformStats {
  total_sites: number
  success_rate: number
  self_service_rate: number
  insurance_rate: number
  sites_with_self_service: number
  sites_with_insurance: number
}

export const apiService = {
  // Start analysis
  analyzeWebsite: async (url: string) => {
    const response = await api.post('/analyze', { url })
    return response.data
  },

  // Get job status
  getJobStatus: async (jobId: string): Promise<AnalysisJob> => {
    const response = await api.get(`/job/${jobId}`)
    return response.data
  },

  // Get all results
  getAllResults: async (): Promise<AnalysisResult[]> => {
    const response = await api.get('/results')
    return response.data
  },

  // Get specific result
  getResult: async (id: number): Promise<AnalysisResult> => {
    const response = await api.get(`/results/${id}`)
    return response.data
  },

  // Get platform stats
  getStats: async (): Promise<PlatformStats> => {
    const response = await api.get('/stats')
    return response.data
  },

  // Export CSV
  exportCsv: async () => {
    const response = await api.get('/export/csv', {
      responseType: 'blob',
    })
    return response.data
  },

  // Delete specific result
  deleteResult: async (id: number) => {
    const response = await api.delete(`/results/${id}`)
    return response.data
  },

  // Delete all results
  deleteAllResults: async () => {
    const response = await api.delete('/results')
    return response.data
  },
}

export default api
