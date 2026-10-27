import { ArrowRight, Sparkles, Heart, Moon, Activity, Shield } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import Button from '../ui/Button.jsx'
import ProgressBar from '../ui/ProgressBar.jsx'

export default function Hero() {
  const navigate = useNavigate()
  return (
    <section id="home" className="relative pt-40 pb-24 px-6 overflow-hidden">
      <div className="max-w-7xl mx-auto grid lg:grid-cols-2 gap-16 items-center">
        <div className="animate-fadeUp">
          <div className="inline-flex items-center gap-2 glass rounded-full px-4 py-2 text-xs text-text-lo mb-7">
            <Sparkles size={14} className="text-accent-purple" />
            AI-Powered Student Wellness Platform
          </div>

          <h1 className="text-4xl md:text-5xl lg:text-[3.4rem] leading-[1.1] font-semibold mb-6">
            Your Personal AI Wellness
            <br />
            <span className="text-gradient">Companion for Student Success</span>
          </h1>

          <p className="text-text-lo text-base md:text-lg max-w-lg mb-9 leading-relaxed">
            MindGuard AI helps students detect, predict, and prevent academic burnout
            through adaptive AI conversations, personalized recovery plans, wellness
            analytics, and intelligent study guidance.
          </p>

          <div className="flex flex-wrap gap-4">
            <Button variant="primary" icon={ArrowRight} onClick={() => navigate('/register')}>
              Get Started
            </Button>
            <a href="#how-it-works">
              <Button variant="secondary">Learn More</Button>
            </a>
          </div>
        </div>

        <div className="relative animate-fadeUp" style={{ animationDelay: '0.15s' }}>
          <div className="relative mx-auto max-w-md lg:max-w-none rotate-2 hover:rotate-0 transition-transform duration-500">
            <div className="glass rounded-3xl p-6 shadow-glow">
              <div className="flex items-center gap-3 mb-6">
                <span className="w-10 h-10 rounded-xl bg-brand-gradient flex items-center justify-center">
                  <Activity size={18} className="text-white" />
                </span>
                <div>
                  <p className="font-medium text-sm">Wellness Dashboard</p>
                  <p className="text-xs text-text-faint">Today's Overview</p>
                </div>
              </div>

              <div className="glass rounded-2xl p-4 mb-4">
                <div className="flex items-end justify-between mb-3">
                  <p className="text-xs text-text-lo">Wellness Score</p>
                  <span className="text-xs text-accent-teal">+5%</span>
                </div>
                <p className="text-3xl font-display font-semibold mb-3">72</p>
                <ProgressBar value={72} />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="glass rounded-2xl p-4">
                  <Heart size={16} className="text-accent-purple mb-3" />
                  <p className="text-xs text-text-faint mb-1">Stress</p>
                  <p className="text-sm font-medium">Low</p>
                </div>
                <div className="glass rounded-2xl p-4">
                  <Moon size={16} className="text-accent-blue mb-3" />
                  <p className="text-xs text-text-faint mb-1">Sleep</p>
                  <p className="text-sm font-medium">7.5h</p>
                </div>
                <div className="glass rounded-2xl p-4 col-span-2 bg-accent-amber/5 border-accent-amber/15">
                  <p className="text-xs text-text-faint mb-1">Burnout Risk</p>
                  <p className="text-2xl font-display font-semibold text-accent-amber">38%</p>
                  <p className="text-xs text-accent-amber/80">Low Risk</p>
                </div>
              </div>
            </div>

            <div className="absolute -top-6 -right-6 w-14 h-14 rounded-2xl bg-brand-gradient flex items-center justify-center shadow-glow animate-float">
              <Shield size={22} className="text-white" />
            </div>
            <div className="absolute -bottom-5 -left-6 w-12 h-12 rounded-2xl glass flex items-center justify-center animate-floatSlow" style={{ animationDelay: '1s' }}>
              <Heart size={18} className="text-accent-teal" />
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
