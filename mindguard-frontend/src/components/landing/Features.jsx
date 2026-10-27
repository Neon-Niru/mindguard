import { LayoutDashboard, MessageCircle, ListChecks, TrendingUp } from 'lucide-react'
import GlassCard from '../ui/GlassCard.jsx'

const features = [
  {
    icon: LayoutDashboard,
    title: 'Dashboard',
    description: 'See your latest wellness score, burnout risk, and daily progress in one calm, uncluttered view.',
  },
  {
    icon: MessageCircle,
    title: 'AI Wellness Companion',
    description: 'Talk through your week with a counselor-like AI that listens and builds a picture of how you\'re doing.',
  },
  {
    icon: ListChecks,
    title: 'Recovery Planner',
    description: 'Personalized recovery goals and daily tasks combined into one simple, trackable plan.',
  },
  {
    icon: TrendingUp,
    title: 'Progress Tracker',
    description: 'Watch your mood, sleep, stress, and wellness trends improve over weeks, not just days.',
  },
]

export default function Features() {
  return (
    <section id="features" className="px-6 py-24">
      <div className="max-w-7xl mx-auto">
        <div className="text-center max-w-xl mx-auto mb-14">
          <p className="text-xs uppercase tracking-widest text-accent-purple mb-3">Features</p>
          <h2 className="text-3xl md:text-4xl font-semibold mb-4">Everything you need to stay ahead of burnout</h2>
          <p className="text-text-lo">Four simple tools, working together quietly in the background of your school year.</p>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {features.map(({ icon: Icon, title, description }, i) => (
            <GlassCard key={title} hover className="p-6 animate-fadeUp" style={{ animationDelay: `${i * 0.08}s` }}>
              <div className="w-11 h-11 rounded-xl bg-brand-gradient-soft border border-white/10 flex items-center justify-center mb-5">
                <Icon size={20} className="text-accent-purple" />
              </div>
              <h3 className="font-medium text-lg mb-2">{title}</h3>
              <p className="text-sm text-text-lo leading-relaxed">{description}</p>
            </GlassCard>
          ))}
        </div>
      </div>
    </section>
  )
}
