import React from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, ExternalLink, Copy, Calendar, Globe } from 'lucide-react'
import { Button } from './ui/button'
import { Badge } from './ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { type AnalysisResult } from '../lib/api'
import { formatDate } from '../lib/utils'

interface AnalysisModalProps {
  result: AnalysisResult | null
  isOpen: boolean
  onClose: () => void
}

export const AnalysisModal: React.FC<AnalysisModalProps> = ({ result, isOpen, onClose }) => {
  if (!result) return null

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text)
    } catch (error) {
      console.error('Failed to copy:', error)
    }
  }

  const formatCsvLine = (result: AnalysisResult) => {
    return `${result.domain},${result.shipping_policy}${result.shipping_url},${result.return_policy}${result.return_url},${result.self_help_returns}${result.self_help_url},${result.insurance}${result.insurance_url},,,,,,`
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50"
            onClick={onClose}
          />

          {/* Modal */}
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden"
            >
              {/* Header */}
              <div className="flex items-center justify-between p-6 border-b bg-gradient-to-r from-blue-50 to-indigo-50">
                <div className="flex items-center space-x-3">
                  <div className="h-10 w-10 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
                    <Globe className="h-5 w-5 text-white" />
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-gray-900">{result.domain}</h2>
                    <div className="flex items-center space-x-2 text-sm text-gray-600">
                      <Calendar className="h-4 w-4" />
                      <span>Analysé le {formatDate(result.analyzed_at)}</span>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => copyToClipboard(formatCsvLine(result))}
                    className="flex items-center space-x-2"
                  >
                    <Copy className="h-4 w-4" />
                    <span>Copier CSV</span>
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={onClose}
                    className="h-8 w-8 p-0"
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              </div>

              {/* Content */}
              <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Shipping Policy */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center justify-between text-lg">
                        <span>Politique de livraison</span>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => window.open(result.shipping_url, '_blank')}
                          className="text-blue-600 hover:text-blue-800"
                        >
                          <ExternalLink className="h-4 w-4 mr-1" />
                          Voir
                        </Button>
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-gray-700 leading-relaxed">
                        {result.shipping_policy}
                      </p>
                      <div className="mt-3 p-2 bg-gray-50 rounded text-xs text-gray-600 break-all">
                        <strong>Source:</strong> {result.shipping_url}
                      </div>
                    </CardContent>
                  </Card>

                  {/* Return Policy */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center justify-between text-lg">
                        <span>Politique de retour</span>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => window.open(result.return_url, '_blank')}
                          className="text-blue-600 hover:text-blue-800"
                        >
                          <ExternalLink className="h-4 w-4 mr-1" />
                          Voir
                        </Button>
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-gray-700 leading-relaxed">
                        {result.return_policy}
                      </p>
                      <div className="mt-3 p-2 bg-gray-50 rounded text-xs text-gray-600 break-all">
                        <strong>Source:</strong> {result.return_url}
                      </div>
                    </CardContent>
                  </Card>

                  {/* Self Help Returns */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center justify-between text-lg">
                        <span>Retours en self-service</span>
                        <div className="flex items-center space-x-2">
                          <Badge 
                            variant={result.self_help_returns.toLowerCase().startsWith('yes') || result.self_help_returns.toLowerCase().startsWith('oui') ? 'success' : 'secondary'}
                          >
                            {result.self_help_returns.toLowerCase().startsWith('yes') || result.self_help_returns.toLowerCase().startsWith('oui') ? 'Oui' : 'Non'}
                          </Badge>
                          {result.self_help_url && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => window.open(result.self_help_url, '_blank')}
                              className="text-blue-600 hover:text-blue-800"
                            >
                              <ExternalLink className="h-4 w-4 mr-1" />
                              Voir
                            </Button>
                          )}
                        </div>
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-gray-700 leading-relaxed">
                        {result.self_help_returns}
                      </p>
                      {result.self_help_url && (
                        <div className="mt-3 p-2 bg-gray-50 rounded text-xs text-gray-600 break-all">
                          <strong>Source:</strong> {result.self_help_url}
                        </div>
                      )}
                    </CardContent>
                  </Card>

                  {/* Insurance */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center justify-between text-lg">
                        <span>Assurance livraison</span>
                        <div className="flex items-center space-x-2">
                          <Badge 
                            variant={result.insurance.toLowerCase().startsWith('yes') || result.insurance.toLowerCase().startsWith('oui') ? 'success' : 'secondary'}
                          >
                            {result.insurance.toLowerCase().startsWith('yes') || result.insurance.toLowerCase().startsWith('oui') ? 'Oui' : 'Non'}
                          </Badge>
                          {result.insurance_url && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => window.open(result.insurance_url, '_blank')}
                              className="text-blue-600 hover:text-blue-800"
                            >
                              <ExternalLink className="h-4 w-4 mr-1" />
                              Voir
                            </Button>
                          )}
                        </div>
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-gray-700 leading-relaxed">
                        {result.insurance}
                      </p>
                      {result.insurance_url && (
                        <div className="mt-3 p-2 bg-gray-50 rounded text-xs text-gray-600 break-all">
                          <strong>Source:</strong> {result.insurance_url}
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </div>

                {/* CSV Preview */}
                <Card className="mt-6">
                  <CardHeader>
                    <CardTitle className="text-lg">Format CSV</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <pre className="text-xs text-gray-700 whitespace-pre-wrap break-all">
                        {formatCsvLine(result)}
                      </pre>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => copyToClipboard(formatCsvLine(result))}
                      className="mt-3 flex items-center space-x-2"
                    >
                      <Copy className="h-4 w-4" />
                      <span>Copier cette ligne</span>
                    </Button>
                  </CardContent>
                </Card>
              </div>
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  )
}
