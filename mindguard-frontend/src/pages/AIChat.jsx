import { useState, useRef, useEffect } from 'react'
import { Send, Plus, Brain, User, FileText, Moon, Gauge, Heart, ListChecks } from 'lucide-react'
import PageHeader from '../components/ui/PageHeader.jsx'
import GlassCard from '../components/ui/GlassCard.jsx'
import Button from '../components/ui/Button.jsx'
import { interview } from '../services/api'

function Bubble({ role, text }) {
  const isAI = role === 'ai'
  return (
    <div className={`flex gap-3 ${isAI ? '' : 'flex-row-reverse'}`}>
      <span className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${isAI ? 'bg-brand-gradient' : 'bg-white/10'}`}>
        {isAI ? <Brain size={15} className="text-white" /> : <User size={15} className="text-text-hi" />}
      </span>
      <div className={`max-w-[75%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${isAI ? 'glass rounded-tl-sm' : 'bg-brand-gradient text-white rounded-tr-sm'}`}>
        {text}
      </div>
    </div>
  )
}

function ReportCard({ report }) {
  if (!report) return null
  return (
    <div className="glass rounded-2xl p-5 md:p-6 border-accent-purple/20 animate-fadeUp">
      <div className="flex items-center gap-2.5 mb-5">
        <span className="w-8 h-8 rounded-lg bg-brand-gradient-soft border border-white/10 flex items-center justify-center">
          <FileText size={15} className="text-accent-purple" />
        </span>
        <div>
          <p className="text-sm font-medium">Wellness Report</p>
          <p className="text-xs text-text-faint">Generated from this conversation</p>
        </div>
      </div>

      <div className="grid sm:grid-cols-3 gap-3 mb-5">
        <div className="rounded-xl bg-white/5 p-4">
          <Gauge size={15} className="text-accent-amber mb-2" />
          <p className="text-xs text-text-faint mb-1">Burnout Score</p>
          <p className="text-lg font-display font-semibold text-accent-amber">{Math.round(report.burnout_score)}%</p>
        </div>
        <div className="rounded-xl bg-white/5 p-4">
          <Heart size={15} className="text-accent-purple mb-2" />
          <p className="text-xs text-text-faint mb-1">Wellness Score</p>
          <p className="text-lg font-display font-semibold text-accent-purple">{Math.round(report.wellness_score)}%</p>
        </div>
        <div className="rounded-xl bg-white/5 p-4">
          <Moon size={15} className="text-accent-blue mb-2" />
          <p className="text-xs text-text-faint mb-1">Risk Level</p>
          <p className="text-lg font-display font-semibold text-accent-blue">{report.risk_level}</p>
        </div>
      </div>

      {report.primary_contributors && report.primary_contributors.length > 0 && (
        <div className="rounded-xl bg-white/5 p-4 mb-5">
          <p className="text-xs text-text-faint mb-1.5">Primary Contributors</p>
          <div className="flex flex-wrap gap-2">
            {report.primary_contributors.map((c, i) => (
              <span key={i} className="text-xs glass rounded-full px-3 py-1">{c}</span>
            ))}
          </div>
        </div>
      )}

      {report.recovery_focus_areas && report.recovery_focus_areas.length > 0 && (
        <div>
          <p className="text-xs text-text-faint mb-2.5 flex items-center gap-1.5">
            <ListChecks size={13} /> Recovery Suggestions
          </p>
          <ul className="space-y-2">
            {report.recovery_focus_areas.map((s, i) => (
              <li key={i} className="text-sm text-text-lo flex gap-2.5">
                <span className="text-accent-teal mt-1">•</span>
                {s}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

export default function AIChat() {
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState([
    { id: 'welcome', role: 'ai', text: "Hi there! I'm your wellness companion. How has your week been feeling?" }
  ])
  const [sessionId, setSessionId] = useState(null)
  const [report, setReport] = useState(null)
  const [sending, setSending] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, report])

  async function handleSend(e) {
    e.preventDefault()
    if (!input.trim() || sending) return

    const userText = input.trim()
    setInput('')
    setMessages((prev) => [...prev, { id: Date.now().toString(), role: 'user', text: userText }])
    setSending(true)

    try {
      const data = await interview.send(userText, sessionId)
      setSessionId(data.session_id)

      if (data.complete) {
        setReport(data.report)
        setMessages((prev) => [
          ...prev,
          { id: (Date.now() + 1).toString(), role: 'ai', text: "I've gathered enough information. Here's your wellness report:" }
        ])
      } else {
        setMessages((prev) => [
          ...prev,
          { id: (Date.now() + 1).toString(), role: 'ai', text: data.reply || "Tell me more about how you've been feeling." }
        ])
      }
    } catch {
      setMessages((prev) => [
        ...prev,
        { id: (Date.now() + 1).toString(), role: 'ai', text: "Sorry, I'm having trouble connecting right now. Please try again." }
      ])
    } finally {
      setSending(false)
    }
  }

  function resetChat() {
    setMessages([
      { id: 'welcome', role: 'ai', text: "Hi there! I'm your wellness companion. How has your week been feeling?" }
    ])
    setSessionId(null)
    setReport(null)
  }

  return (
    <div className="flex flex-col h-[calc(100vh-3rem)] md:h-[calc(100vh-4rem)]">
      <PageHeader
        eyebrow="AI Wellness Chat"
        title="Check in with your AI companion"
        description="A short, counselor-like conversation to understand how your week has really been."
        action={
          <Button variant="secondary" icon={Plus} onClick={resetChat}>
            New Conversation
          </Button>
        }
      />

      <GlassCard className="flex-1 flex flex-col min-h-0 p-5 md:p-6">
        <div className="flex-1 overflow-y-auto space-y-5 pr-1">
          {messages.map((m) => (
            <Bubble key={m.id} role={m.role} text={m.text} />
          ))}
          {report && <ReportCard report={report} />}
          <div ref={bottomRef} />
        </div>

        <form onSubmit={handleSend} className="flex items-center gap-3 mt-5 pt-5 border-t border-white/10">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={sending ? 'Waiting for response...' : 'Type your message...'}
            disabled={sending || !!report}
            className="flex-1 bg-white/5 border border-white/10 rounded-full px-5 py-3 text-sm outline-none focus:border-accent-purple/50 focus:bg-white/[0.07] transition-colors disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={sending || !input.trim() || !!report}
            className="w-11 h-11 rounded-full bg-brand-gradient flex items-center justify-center shrink-0 shadow-glow-sm hover:brightness-110 transition-all active:scale-95 disabled:opacity-50"
            aria-label="Send message"
          >
            <Send size={16} className="text-white" />
          </button>
        </form>
      </GlassCard>
    </div>
  )
}
