import React, { useState, useEffect } from 'react'
import { getAnalytics } from '../api'

interface AnalyticsData {
  total_posts: number
  total_engagement: number
  engagement_rate: number
  followers_gained: number
  followers_lost: number
  top_posts: Array<{
    id: number
    title: string
    engagement: number
    platform: string
  }>
  platform_breakdown: Array<{
    platform: string
    posts: number
    engagement: number
  }>
}

interface AnalyticsProps {
  workspaceId: number
}

export function Analytics({ workspaceId }: AnalyticsProps) {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [period, setPeriod] = useState<'7d' | '30d' | '90d'>('30d')

  const fetchAnalytics = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await getAnalytics(workspaceId, period)
      setAnalytics(data)
    } catch (err: any) {
      setError(err.message || 'Failed to fetch analytics')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAnalytics()
  }, [workspaceId, period])

  if (loading) return <div style={{ padding: '20px', textAlign: 'center' }}>Loading analytics...</div>
  if (error) return <div style={{ padding: '20px', color: '#dc3545' }}>{error}</div>
  if (!analytics) return null

  return (
    <div style={{ padding: '20px', backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2>Analytics</h2>
        <select
          value={period}
          onChange={e => setPeriod(e.target.value as '7d' | '30d' | '90d')}
          style={{ padding: '8px', borderRadius: '4px', border: '1px solid #ced4da' }}
        >
          <option value="7d">Last 7 days</option>
          <option value="30d">Last 30 days</option>
          <option value="90d">Last 90 days</option>
        </select>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginBottom: '30px' }}>
        <div style={{ padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '8px', textAlign: 'center' }}>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#007bff' }}>{analytics.total_posts}</div>
          <div style={{ color: '#6c757d' }}>Total Posts</div>
        </div>
        <div style={{ padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '8px', textAlign: 'center' }}>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#28a745' }}>{analytics.total_engagement}</div>
          <div style={{ color: '#6c757d' }}>Total Engagement</div>
        </div>
        <div style={{ padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '8px', textAlign: 'center' }}>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#ffc107' }}>{analytics.engagement_rate}%</div>
          <div style={{ color: '#6c757d' }}>Engagement Rate</div>
        </div>
        <div style={{ padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '8px', textAlign: 'center' }}>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#17a2b8' }}>{analytics.followers_gained}</div>
          <div style={{ color: '#6c757d' }}>Followers Gained</div>
        </div>
      </div>

      <div style={{ marginBottom: '30px' }}>
        <h3>Platform Breakdown</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {analytics.platform_breakdown.map(platform => (
            <div key={platform.platform} style={{ display: 'flex', justifyContent: 'space-between', padding: '10px', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
              <span>{platform.platform}</span>
              <span>{platform.posts} posts, {platform.engagement} engagement</span>
            </div>
          ))}
        </div>
      </div>

      <div>
        <h3>Top Performing Posts</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {analytics.top_posts.map(post => (
            <div key={post.id} style={{ display: 'flex', justifyContent: 'space-between', padding: '10px', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
              <div>
                <strong>{post.title}</strong>
                <div style={{ fontSize: '12px', color: '#6c757d' }}>{post.platform}</div>
              </div>
              <div style={{ fontWeight: 'bold', color: '#28a745' }}>{post.engagement}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}