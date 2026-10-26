import { useEffect, useState } from 'react'
import { ResponsiveContainer, AreaChart, Area, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts'
import { TrendingUp, TrendingDown, Target, ListChecks, AlertCircle } from 'lucide-react'
import PageHeader from '../components/ui/PageHeader.jsx'
import GlassCard from '../components/ui/GlassCard.jsx'
import ProgressBar from '../components/ui/ProgressBar.jsx'
import { progress as progressApi } from '../services/api'

// Every category score produced by the engine is a *health* score
// (higher is better). Only burnout is inverted.
const INVERTED_KEYS = new Set(['burnout_score'])

function ChartTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div className="glass rounded-xl px-3.5 py-2.5 text-xs">
      <p className="text-text-faint mb-1">{label}</p>
      {payload.map((p) => (
        <p key={p.dataKey} style={{ color: p.color }}>
          {p.name}: {Math.round(p.value)}{p.unit || ''}
        </p>
      ))}
    </div>
  )
}

function TrendCard({ title, dataKey, color, unit = '', data }) {
  if (!data || data.length < 2) {
    return (
      <GlassCard className="p-6">
        <p className="text-sm font-medium mb-4">{title}</p>
        <p className="text-xs text-text-lo">Not enough check-ins yet.</p>
      </GlassCard>
    )
  }

  const first = data[0][dataKey] ?? 0
  const last = data[data.length - 1][dataKey] ?? 0
  const delta = Math.round(last - first)
  const improving = INVERTED_KEYS.has(dataKey) ? delta <= 0 : delta >= 0
  const Arrow = improving ? TrendingUp : TrendingDown

  return (
    <GlassCard className="p-6">
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm font-medium">{title}</p>
        <span className={`flex items-center gap-1 text-xs ${improving ? 'text-accent-teal' : 'text-rose-300'}`}>
          <Arrow size={13} />
          {Math.abs(delta)}{unit}
        </span>
      </div>
      <ResponsiveContainer width="100%" height={120}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id={`grad-${dataKey}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={color} stopOpacity={0.35} />
              <stop offset="100%" stopColor={color} stopOpacity={0} />
            </linearGradient>
          </defs>
          <XAxis dataKey="label" hide />
          <YAxis hide domain={[0, 100]} />
          <Tooltip content={<ChartTooltip />} />
          <Area type="monotone" dataKey={dataKey} name={title} unit={unit} stroke={color} strokeWidth={2} fill={`url(#grad-${dataKey})`} />
        </AreaChart>
      </ResponsiveContainer>
    </GlassCard>
  )
}

export default function Progress() {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false

    progressApi.get()
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
        <p className="text-text-lo">Loading progress...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div>
        <PageHeader
          eyebrow="Progress"
          title="Your Long-Term Wellness"
          description="Trends from your past check-ins, so you can see how far you've come."
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

  const assessments = data?.assessments || []
  const assessmentData = assessments.map((a) => ({
    label: a.date ? a.date.slice(0, 10) : `#${a.assessment_id}`,
    wellness: a.wellness_score,
    burnout_score: a.burnout_score,
    mood: a.mood_score,
    sleep: a.sleep_score,
    stress: a.stress_score,
  }))

  // Planner history is a separate, weekly series measured in completion %.
  const plannerHistory = (data?.planner?.history || []).map((week) => ({
    label: week.label?.slice(5) || '',
    percent: week.percent,
    total: week.total,
    completed: week.completed,
  }))

  const planner = data?.planner || { total: 0, completed: 0, percent: 0 }
  const goalData = data?.recovery_goals || { total: 0, completed: 0, percent: 0 }

  const hasHistory = assessments.length > 0
  const hasPlannerHistory = plannerHistory.length > 0

  return (
    <div>
      <PageHeader
        eyebrow="Progress"
        title="Your Long-Term Wellness"
        description="Trends from your past check-ins, so you can see how far you've come."
      />

      {!hasHistory ? (
        <GlassCard className="p-7 text-center mb-6">
          <p className="text-text-lo">No assessment history yet. Complete a check-in to see your progress.</p>
        </GlassCard>
      ) : (
        <>
          <GlassCard glow className="p-7 mb-6">
            <p className="text-sm font-medium mb-5">Wellness Score Trend</p>
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={assessmentData}>
                <CartesianGrid stroke="rgba(255,255,255,0.06)" vertical={false} />
                <XAxis dataKey="label" stroke="#6b7390" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#6b7390" fontSize={12} tickLine={false} axisLine={false} domain={[0, 100]} />
                <Tooltip content={<ChartTooltip />} />
                <Line type="monotone" dataKey="wellness" name="Wellness Score" unit="%" stroke="#a56bff" strokeWidth={3} dot={{ r: 3, fill: '#a56bff' }} />
              </LineChart>
            </ResponsiveContainer>
          </GlassCard>

          <div className="grid md:grid-cols-2 gap-5 mb-6">
            <TrendCard title="Burnout Trend" dataKey="burnout_score" color="#f5a623" unit="%" data={assessmentData} />
            <TrendCard title="Mood Trend" dataKey="mood" color="#a56bff" unit="%" data={assessmentData} />
            <TrendCard title="Sleep Trend" dataKey="sleep" color="#4d7fff" unit="%" data={assessmentData} />
            <TrendCard title="Stress Resilience Trend" dataKey="stress" color="#2dd9c0" unit="%" data={assessmentData} />
          </div>
        </>
      )}

      <div className="grid md:grid-cols-2 gap-5">
        <GlassCard className="p-7">
          <div className="flex items-center gap-2.5 mb-5">
            <span className="w-9 h-9 rounded-xl bg-accent-blue/10 flex items-center justify-center">
              <ListChecks size={17} className="text-accent-blue" />
            </span>
            <div>
              <p className="text-sm font-medium">Planner Completion</p>
              <p className="text-xs text-text-faint">
                {planner.completed} of {planner.total} tasks completed ({planner.percent}%)
              </p>
            </div>
          </div>

          {hasPlannerHistory ? (
            <ResponsiveContainer width="100%" height={140}>
              <AreaChart data={plannerHistory}>
                <defs>
                  <linearGradient id="grad-planner" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#4d7fff" stopOpacity={0.35} />
                    <stop offset="100%" stopColor="#4d7fff" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="label" stroke="#6b7390" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis hide domain={[0, 100]} />
                <Tooltip content={<ChartTooltip />} />
                <Area
                  type="monotone"
                  dataKey="percent"
                  name="Completed"
                  unit="%"
                  stroke="#4d7fff"
                  strokeWidth={2}
                  fill="url(#grad-planner)"
                />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-xs text-text-lo">Add planner tasks to see your weekly completion.</p>
          )}
        </GlassCard>

        <GlassCard className="p-7">
          <div className="flex items-center gap-2.5 mb-5">
            <span className="w-9 h-9 rounded-xl bg-accent-purple/10 flex items-center justify-center">
              <Target size={17} className="text-accent-purple" />
            </span>
            <p className="text-sm font-medium">Recovery Goal Completion</p>
          </div>
          <p className="text-3xl font-display font-semibold mb-1">{goalData.percent ?? 0}%</p>
          <p className="text-xs text-text-lo mb-5">{goalData.completed} of {goalData.total} goals completed</p>
          <ProgressBar value={goalData.percent ?? 0} height="h-3" />
        </GlassCard>
      </div>
    </div>
  )
}
