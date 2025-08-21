import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ExternalLink, Copy, ChevronDown, ChevronRight, Trash2 } from 'lucide-react'
import { Button } from './ui/button'
import { type AnalysisResult } from '../lib/api'
import { formatDate } from '../lib/utils'

interface DataTableProps {
  results: AnalysisResult[]
  onRowClick: (result: AnalysisResult) => void
  onDeleteResult: (id: number) => void
}

export const DataTable: React.FC<DataTableProps> = ({ results, onRowClick, onDeleteResult }) => {
  const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set())
  const [copiedText, setCopiedText] = useState<string | null>(null)

  const toggleRow = (id: number) => {
    const newExpanded = new Set(expandedRows)
    if (newExpanded.has(id)) {
      newExpanded.delete(id)
    } else {
      newExpanded.add(id)
    }
    setExpandedRows(newExpanded)
  }

  const copyToClipboard = async (text: string, label: string) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedText(label)
      setTimeout(() => setCopiedText(null), 2000)
    } catch (error) {
      console.error('Failed to copy:', error)
    }
  }

  const formatCsvLine = (result: AnalysisResult) => {
    return `${result.domain},${result.shipping_policy}${result.shipping_url},${result.return_policy}${result.return_url},${result.self_help_returns}${result.self_help_url},${result.insurance}${result.insurance_url},,,,,,`
  }



  if (results.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="w-24 h-24 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
          <ExternalLink className="h-12 w-12 text-gray-400" />
        </div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          No results found
        </h3>
        <p className="text-gray-600">
          Start by analyzing your first e-commerce URL
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <AnimatePresence>
        {results.map((result, index) => (
          <motion.div
            key={result.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ delay: index * 0.05 }}
            className="bg-white rounded-lg border shadow-sm hover:shadow-md transition-all duration-200"
          >
            {/* Main Row */}
            <div className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4 flex-1">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => toggleRow(result.id)}
                    className="p-1 h-8 w-8"
                  >
                    {expandedRows.has(result.id) ? (
                      <ChevronDown className="h-4 w-4" />
                    ) : (
                      <ChevronRight className="h-4 w-4" />
                    )}
                  </Button>
                  
                  <div className="flex-1">
                    <div className="flex items-center space-x-3">
                      <h3 className="font-semibold text-lg text-gray-900">
                        {result.domain}
                      </h3>
                    </div>
                    <p className="text-sm text-gray-600 mt-1">
                      Analyzed on {formatDate(result.analyzed_at)}
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => copyToClipboard(formatCsvLine(result), `CSV-${result.domain}`)}
                    className="flex items-center space-x-2"
                  >
                    <Copy className="h-4 w-4" />
                    <span>{copiedText === `CSV-${result.domain}` ? 'Copied!' : 'CSV'}</span>
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => onRowClick(result)}
                    className="flex items-center space-x-2"
                  >
                    <ExternalLink className="h-4 w-4" />
                    <span>Details</span>
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      if (window.confirm(`Delete analysis for ${result.domain}?`)) {
                        onDeleteResult(result.id)
                      }
                    }}
                    className="flex items-center space-x-2 text-red-600 hover:text-red-800 hover:border-red-300"
                  >
                    <Trash2 className="h-4 w-4" />
                    <span>Delete</span>
                  </Button>
                </div>
              </div>
            </div>

            {/* Expanded Content */}
            <AnimatePresence>
              {expandedRows.has(result.id) && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.3 }}
                  className="border-t bg-gray-50"
                >
                  <div className="p-4 space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {/* Shipping Policy */}
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <h4 className="font-medium text-gray-900">Shipping Policy</h4>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => window.open(result.shipping_url, '_blank')}
                            className="text-blue-600 hover:text-blue-800"
                          >
                            <ExternalLink className="h-3 w-3 mr-1" />
                            View
                          </Button>
                        </div>
                        <p className="text-sm text-gray-600 bg-white p-3 rounded border">
                          {result.shipping_policy}
                        </p>
                      </div>

                      {/* Return Policy */}
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <h4 className="font-medium text-gray-900">Return Policy</h4>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => window.open(result.return_url, '_blank')}
                            className="text-blue-600 hover:text-blue-800"
                          >
                            <ExternalLink className="h-3 w-3 mr-1" />
                            View
                          </Button>
                        </div>
                        <p className="text-sm text-gray-600 bg-white p-3 rounded border">
                          {result.return_policy}
                        </p>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {/* Self Help Returns */}
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <h4 className="font-medium text-gray-900">Self-Service Returns</h4>
                          {result.self_help_url && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => window.open(result.self_help_url, '_blank')}
                              className="text-blue-600 hover:text-blue-800"
                            >
                              <ExternalLink className="h-3 w-3 mr-1" />
                              View
                            </Button>
                          )}
                        </div>
                        <p className="text-sm text-gray-600 bg-white p-3 rounded border">
                          {result.self_help_returns}
                        </p>
                      </div>

                      {/* Insurance */}
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <h4 className="font-medium text-gray-900">Shipping Insurance</h4>
                          {result.insurance_url && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => window.open(result.insurance_url, '_blank')}
                              className="text-blue-600 hover:text-blue-800"
                            >
                              <ExternalLink className="h-3 w-3 mr-1" />
                              View
                            </Button>
                          )}
                        </div>
                        <p className="text-sm text-gray-600 bg-white p-3 rounded border">
                          {result.insurance}
                        </p>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  )
}
