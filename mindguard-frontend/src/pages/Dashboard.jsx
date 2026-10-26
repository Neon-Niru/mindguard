import { useEffect, useState } from 'react'
import { Heart, Moon, Gauge, TrendingUp, MessageCircle, ListChecks, ArrowUpRight, ArrowDownRight, Sparkles, AlertCircle } from 'lucide-react'
import { Link } from 'react-router-dom'
import PageHeader from '../components/ui/PageHeader.jsx'
import GlassCard from '../components/ui/GlassCard.jsx'
import StatTile from '../components/ui/StatTile.jsx'
import ProgressBar from '../components/ui/ProgressBar.jsx'
import Badge from '../components/ui/Badge.jsx'
import { dashboard as dashboardApi } from '../services/api'
import { useAuth } from '../context/AuthContext.jsx'

const RISK_TONES = { low: 'low', moderate: 'moderate', high: 'high' }

export default function Dashboard() {
  const { user } = useAuth()
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false

    dashboardApi.get()
      .then((response) => {
        if (!cancelled) setData(response)
      })
      .catch((err) => {
        if (!cancelled) setError(err.message)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-text-lo">Loading dashboard...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div>
        <PageHeader
          eyebrow="Dashboard"
          title={`Welcome, ${user?.full_name?.split(' ')[0] || 'Student'}`}
          description="We couldn't load your wellness snapshot."
        />
        <GlassCard className="p-7 text-center">
          <p className="flex items-center justify-center gap-2 text-sm text-rose-300">
            <AlertCircle size={16} />
            {error}
          </p>
        </GlassCard>
      </div>
    )
  }

  if (!data || !data.has_assessment) {
    return (
      <div>
        <PageHeader
          eyebrow="Dashboard"
          title={`Welcome, ${user?.full_name?.split(' ')[0] || 'Student'}`}
          description="Start a check-in conversation to see your wellness snapshot."
        />
        <GlassCard glow className="p-7 text-center">
          <p className="text-text-lo mb-4">No assessment data yet.</p>
          <Link to="/app/chat" className="inline-flex items-center gap-2 glass rounded-xl px-5 py-3 text-sm hover:bg-glass-fillhover transition-colors">
            <MessageCircle size={17} className="text-accent-purple" />
            Start your first check-in
          </Link>
        </GlassCard>
      </div>
    )
  }

  const firstName = user?.full_name?.split(' ')[0] || 'Student'
  const hasPrevious = Boolean(data.previous_comparison)

  const scoreDelta = hasPrevious
    ? Math.round(data.wellness_score - data.previous_comparison.wellness_score)
    : 0
  const riskDelta = hasPrevious
    ? Math.round(data.burnout_score - data.previous_comparison.burnout_score)
    : 0

  const plannerTotal = data.planner_total ?? 0
  const plannerCompleted = data.planner_completed ?? 0
  const plannerPercent = data.planner_progress
    ?? (plannerTotal > 0 ? Math.round((plannerCompleted / plannerTotal) * 100) : 0)

  const riskTone = RISK_TONES[(data.risk_level || '').toLowerCase()] || 'low'

  return (
    <div>
      <PageHeader
        eyebrow="Dashboard"
        title={`Welcome back, ${firstName}`}
        description="Here's your latest wellness snapshot."
      />

      <div className="grid lg:grid-cols-3 gap-5 mb-6">
        <GlassCard glow className="lg:col-span-2 p-7">
          <div className="flex items-start justify-between mb-6">
            <div>
              <p className="text-xs text-text-lo mb-1">Wellness Score</p>
              <div className="flex items-end gap-3">
                <p className="text-5xl font-display font-semibold">{Math.round(data.wellness_score)}</p>
                {hasPrevious && scoreDelta !== 0 && (
                  <span className={`flex items-center gap-1 text-sm mb-1.5 ${scoreDelta > 0 ? 'text-accent-teal' : 'text-rose-300'}`}>
                    {scoreDelta > 0 ? <ArrowUpRight size={15} /> : <ArrowDownRight size={15} />}
                    {Math.abs(scoreDelta)} vs last check-in
                  </span>
                )}
              </div>
            </div>
            {hasPrevious ? (
              <Badge tone={scoreDelta > 0 ? 'low' : scoreDelta < 0 ? 'high' : 'neutral'}>
                {scoreDelta > 0 ? 'Improving' : scoreDelta < 0 ? 'Declining' : 'Steady'}
              </Badge>
            ) : (
              <Badge tone="neutral">First check-in</Badge>
            )}
          </div>
          <ProgressBar value={data.wellness_score} height="h-3" />
        </GlassCard>

        <GlassCard className="p-7">
          <div className="flex items-start justify-between mb-4">
            <span className="w-10 h-10 rounded-xl bg-accent-amber/10 flex items-center justify-center">
              <Gauge size={18} className="text-accent-amber" />
            </span>
            <Badge tone={riskTone}>{data.risk_level || 'N/A'}</Badge>
          </div>
          <p className="text-xs text-text-lo mb-1">Burnout Risk</p>
          <div className="flex items-end gap-2">
            <p className="text-4xl font-display font-semibold text-accent-amber">{Math.round(data.burnout_score)}%</p>
            {hasPrevious && riskDelta !== 0 && (
              <span className={`flex items-center gap-1 text-xs mb-1 ${riskDelta < 0 ? 'text-accent-teal' : 'text-rose-300'}`}>
                {riskDelta < 0 ? <ArrowDownRight size={13} /> : <ArrowUpRight size={13} />}
                {Math.abs(riskDelta)}%
              </span>
            )}
          </div>
          {hasPrevious && riskDelta !== 0 && (
            <p className="text-xs text-text-faint mt-2">
              {riskDelta < 0 ? 'Lower than your last check-in' : 'Higher than your last check-in'}
            </p>
          )}
        </GlassCard>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-6">
        <StatTile icon={Heart} label="Mood" value={data.mood_score != null ? `${Math.round(data.mood_score)}%` : '--'} iconTone="text-accent-purple bg-accent-purple/10" />
        <StatTile icon={Moon} label="Sleep" value={data.sleep_score != null ? `${Math.round(data.sleep_score)}%` : '--'} iconTone="text-accent-blue bg-accent-blue/10" />
        <StatTile icon={Gauge} label="Stress Resilience" value={data.stress_score != null ? `${Math.round(data.stress_score)}%` : '--'} iconTone="text-accent-teal bg-accent-teal/10" />
        <StatTile icon={TrendingUp} label="Productivity" value={data.productivity_score != null ? `${Math.round(data.productivity_score)}%` : '--'} iconTone="text-accent-amber bg-accent-amber/10" />
      </div>

      <div className="grid lg:grid-cols-3 gap-5">
        <GlassCard className="lg:col-span-2 p-7">
          <div className="flex items-center justify-between mb-5">
            <h3 className="font-medium">Today's Planner Progress</h3>
            <Link to="/app/planner" className="text-xs text-accent-purple hover:text-accent-teal transition-colors">
              Open planner →
            </Link>
          </div>

          <ProgressBar
            value={plannerPercent}
            label={
              plannerTotal > 0
                ? `${plannerCompleted} of ${plannerTotal} tasks done · ${plannerPercent}%`
                : 'No tasks scheduled for today'
            }
            height="h-3"
          />

          {data.recovery_goals && data.recovery_goals.length > 0 && (
            <div className="mt-6 pt-6 border-t border-white/10">
              <h4 className="text-sm font-medium mb-4">Recovery Goals</h4>
              <div className="space-y-3">
                {data.recovery_goals.map((g) => (
                  <div key={g.goal_id} className="flex items-center gap-3">
                    <span className={`rounded-md border flex items-center justify-center shrink-0 ${g.completed ? 'bg-brand-gradient border-transparent' : 'border-white/20'}`} style={{ width: 18, height: 18 }} />
                    <p className={`text-sm ${g.completed ? 'text-text-faint line-through' : 'text-text-lo'}`}>{g.goal}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </GlassCard>

        <GlassCard className="p-7">
          <h3 className="font-medium mb-5 flex items-center gap-2">
            <Sparkles size={16} className="text-accent-purple" />
            Quick Actions
          </h3>
          <div className="space-y-3">
            <Link to="/app/chat">
              <button className="w-full flex items-center gap-3 glass rounded-xl px-4 py-3.5 text-sm hover:bg-glass-fillhover transition-colors">
                <MessageCircle size={17} className="text-accent-purple" />
                Start a check-in conversation
              </button>
            </Link>
            <Link to="/app/planner">
              <button className="w-full flex items-center gap-3 glass rounded-xl px-4 py-3.5 text-sm hover:bg-glass-fillhover transition-colors">
                <ListChecks size={17} className="text-accent-teal" />
                Review your tasks
              </button>
            </Link>
            <Link to="/app/progress">
              <button className="w-full flex items-center gap-3 glass rounded-xl px-4 py-3.5 text-sm hover:bg-glass-fillhover transition-colors">
                <TrendingUp size={17} className="text-accent-blue" />
                View long-term progress
              </button>
            </Link>
          </div>
        </GlassCard>
      </div>
    </div>
  )
}
