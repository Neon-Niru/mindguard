import { GraduationCap, MessageSquareText, Gauge, ClipboardList, CalendarCheck2, Sparkle } from 'lucide-react'

const steps = [
  { icon: GraduationCap, title: 'Student', description: 'You open MindGuard AI and check in.' },
  { icon: MessageSquareText, title: 'AI Conversation', description: 'A short, natural conversation about your week.' },
  { icon: Gauge, title: 'Burnout Assessment', description: 'Your responses are scored into a clear wellness report.' },
  { icon: ClipboardList, title: 'Recovery Plan', description: 'Personalized recovery goals are added to your planner.' },
  { icon: CalendarCheck2, title: 'Daily Progress', description: 'Small daily tasks keep you moving in the right direction.' },
  { icon: Sparkle, title: 'Long-Term Wellness', description: 'Trends improve, and burnout risk quietly drops over time.' },
]

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="px-6 py-24">
      <div className="max-w-7xl mx-auto">
        <div className="text-center max-w-xl mx-auto mb-16">
          <p className="text-xs uppercase tracking-widest text-accent-purple mb-3">How It Works</p>
          <h2 className="text-3xl md:text-4xl font-semibold mb-4">A simple, steady path to feeling better</h2>
          <p className="text-text-lo">From one conversation to lasting change — here's the flow.</p>
        </div>

        <div className="relative grid md:grid-cols-3 lg:grid-cols-6 gap-6">
          <div className="hidden lg:block absolute top-9 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />
          {steps.map(({ icon: Icon, title, description }, i) => (
            <div key={title} className="relative flex flex-col items-center text-center">
              <div className="w-[72px] h-[72px] rounded-2xl glass flex items-center justify-center mb-4 shrink-0 relative z-10">
                <Icon size={26} className="text-accent-purple" />
              </div>
              <p className="font-medium text-sm mb-1.5">{title}</p>
              <p className="text-xs text-text-lo leading-relaxed max-w-[10rem]">{description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
