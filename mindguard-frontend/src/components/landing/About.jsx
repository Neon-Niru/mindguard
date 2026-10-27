import GlassCard from '../ui/GlassCard.jsx'

export default function About() {
  return (
    <section id="about" className="px-6 py-24">
      <div className="max-w-5xl mx-auto">
        <GlassCard className="p-10 md:p-14 text-center" glow>
          <p className="text-xs uppercase tracking-widest text-accent-purple mb-4">About the Project</p>
          <h2 className="text-2xl md:text-3xl font-semibold mb-5">Built for students, by students</h2>
          <p className="text-text-lo leading-relaxed max-w-2xl mx-auto">
            MindGuard AI was built with one goal: help students
            notice burnout before it becomes overwhelming. Instead of another productivity
            app that adds pressure, it listens first, then offers a calm, personalized
            path back to balance — one conversation and one small task at a time.
          </p>
        </GlassCard>
      </div>
    </section>
  )
}
