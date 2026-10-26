import { Brain, Github } from 'lucide-react'

const REPO_URL = 'https://github.com/Neon-Niru/mindguard'

export default function Footer() {
  return (
    <footer id="contact" className="border-t border-white/5 mt-24">
      <div className="max-w-7xl mx-auto px-6 py-14 grid md:grid-cols-3 gap-10">
        <div>
          <div className="flex items-center gap-2.5 mb-4">
            <span className="w-9 h-9 rounded-xl bg-brand-gradient flex items-center justify-center">
              <Brain size={18} className="text-white" />
            </span>
            <span className="font-display font-semibold text-lg">MindGuard AI</span>
          </div>
          <p className="text-sm text-text-lo max-w-xs">
            A calmer way for students to notice burnout early and recover with a personalized plan.
          </p>
        </div>

        <div>
          <p className="text-sm font-medium text-text-hi mb-4">Contact</p>
          <ul className="space-y-2 text-sm text-text-lo">
            <li>Team MindGuard</li>
            <li className="text-text-faint">
              Questions or feedback? Open an issue on GitHub.
            </li>
            <li>
              <a
                href={REPO_URL}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1.5 hover:text-text-hi transition-colors"
              >
                <Github size={14} />
                Neon-Niru/mindguard
              </a>
            </li>
          </ul>
        </div>

        <div>
          <p className="text-sm font-medium text-text-hi mb-4">Product</p>
          <ul className="space-y-2 text-sm text-text-lo">
            <li><a href="#features" className="hover:text-text-hi transition-colors">Features</a></li>
            <li><a href="#how-it-works" className="hover:text-text-hi transition-colors">How It Works</a></li>
            <li><a href="#about" className="hover:text-text-hi transition-colors">About</a></li>
          </ul>
        </div>
      </div>
      <div className="text-center text-xs text-text-faint pb-8 px-6">
        © {new Date().getFullYear()} MindGuard AI. Made with care for student wellness.
        MindGuard supports self-reflection and is not a substitute for professional care.
      </div>
    </footer>
  )
}
