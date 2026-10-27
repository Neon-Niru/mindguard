import PublicNavbar from '../components/layout/PublicNavbar.jsx'
import Footer from '../components/layout/Footer.jsx'
import Hero from '../components/landing/Hero.jsx'
import Features from '../components/landing/Features.jsx'
import HowItWorks from '../components/landing/HowItWorks.jsx'
import About from '../components/landing/About.jsx'

export default function Landing() {
  return (
    <div>
      <PublicNavbar />
      <Hero />
      <Features />
      <HowItWorks />
      <About />
      <Footer />
    </div>
  )
}
