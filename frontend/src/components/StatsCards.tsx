import React from 'react'
import { motion } from 'framer-motion'
import { TrendingUp, Package, Shield, RotateCcw } from 'lucide-react'
import { Card, CardContent } from './ui/card'
import { type PlatformStats } from '../lib/api'

interface StatsCardsProps {
  stats: PlatformStats
}

export const StatsCards: React.FC<StatsCardsProps> = ({ stats }) => {
  const statsData = [
    {
      title: 'Sites Analyzed',
      value: stats.total_sites.toLocaleString(),
      icon: Package,
      color: 'from-blue-500 to-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      title: 'Success Rate',
      value: `${stats.success_rate}%`,
      icon: TrendingUp,
      color: 'from-green-500 to-green-600',
      bgColor: 'bg-green-50',
    },
    {
      title: 'Self-Service Portal',
      value: `${stats.self_service_rate}%`,
      icon: RotateCcw,
      color: 'from-purple-500 to-purple-600',
      bgColor: 'bg-purple-50',
      subtitle: `${stats.sites_with_self_service} sites`
    },
    {
      title: 'Shipping Insurance',
      value: `${stats.insurance_rate}%`,
      icon: Shield,
      color: 'from-orange-500 to-orange-600',
      bgColor: 'bg-orange-50',
      subtitle: `${stats.sites_with_insurance} sites`
    },
  ]

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
      className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
    >
      {statsData.map((stat, index) => (
        <motion.div
          key={stat.title}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 * index }}
          whileHover={{ scale: 1.02 }}
          className="group"
        >
          <Card className="relative overflow-hidden border-0 shadow-lg hover:shadow-xl transition-all duration-300">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div className="space-y-2">
                  <p className="text-sm font-medium text-muted-foreground">
                    {stat.title}
                  </p>
                  <div className="space-y-1">
                    <p className="text-3xl font-bold text-gray-900">
                      {stat.value}
                    </p>
                    {stat.subtitle && (
                      <p className="text-xs text-muted-foreground">
                        {stat.subtitle}
                      </p>
                    )}
                  </div>
                </div>
                <div className={`p-3 rounded-full ${stat.bgColor} group-hover:scale-110 transition-transform duration-300`}>
                  <stat.icon className={`h-6 w-6 bg-gradient-to-r ${stat.color} bg-clip-text text-transparent`} />
                </div>
              </div>
              
              {/* Gradient overlay */}
              <div className={`absolute inset-0 bg-gradient-to-r ${stat.color} opacity-0 group-hover:opacity-5 transition-opacity duration-300`} />
            </CardContent>
          </Card>
        </motion.div>
      ))}
    </motion.div>
  )
}
