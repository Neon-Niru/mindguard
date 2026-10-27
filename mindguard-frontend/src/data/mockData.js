// Static mock data for frontend/UI demo purposes only.
// The real backend, AI engine, and database are separate layers (see plan.md).

export const currentUser = {
  name: 'Aditi Sharma',
  grade: '12th Grade',
  initials: 'A',
}

export const latestAssessment = {
  wellnessScore: 72,
  wellnessChange: 5,
  burnoutRisk: 38,
  riskLevel: 'low',
  mood: 'Steady',
  sleepHours: 7.5,
  stressLevel: 'Low',
  productivity: 81,
  plannerProgress: 64,
  previousComparison: {
    wellnessScore: 67,
    burnoutRisk: 44,
  },
  recoveryGoals: [
    { id: 'g1', goal: 'Wind down screens 30 minutes before bed', completed: false },
    { id: 'g2', goal: 'Take a 10-minute walk between study blocks', completed: true },
    { id: 'g3', goal: 'Keep a fixed wake-up time this week', completed: false },
  ],
}

export const plannerTasks = [
  { id: 't1', title: 'Physics problem set — Ch. 7', category: 'Academics', priority: 'High', date: 'Today', time: '4:00 PM', completed: false, source: 'USER' },
  { id: 't2', title: 'Wind down screens before bed', category: 'Recovery', priority: 'Medium', date: 'Today', time: '9:30 PM', completed: false, source: 'ENGINE' },
  { id: 't3', title: '10-minute walk after school', category: 'Recovery', priority: 'Medium', date: 'Today', time: '3:15 PM', completed: true, source: 'ENGINE' },
  { id: 't4', title: 'Revise chemistry flashcards', category: 'Academics', priority: 'Low', date: 'Today', time: '6:00 PM', completed: false, source: 'USER' },
  { id: 't5', title: 'Call a friend / socialize', category: 'Wellbeing', priority: 'Low', date: 'Today', time: '7:30 PM', completed: true, source: 'USER' },
]

export const chatMessages = [
  { id: 'm1', role: 'ai', text: "Hi Aditi, good to see you. How has this week felt compared to last week?" },
  { id: 'm2', role: 'user', text: "Honestly kind of tiring. Two tests back to back and I haven't slept great." },
  { id: 'm3', role: 'ai', text: "That sounds like a lot to carry at once. When you say you haven't slept great, roughly how many hours have you been getting?" },
  { id: 'm4', role: 'user', text: "Maybe 5-6 hours most nights this week." },
  { id: 'm5', role: 'ai', text: "Thanks for sharing that. One more thing — on a scale of low, medium, high, how would you describe your stress today?" },
  { id: 'm6', role: 'user', text: "Probably medium-high, but I think it'll ease up after Friday." },
]

export const wellnessReport = {
  burnoutScore: 38,
  moodSummary: 'Generally steady, with some tiredness showing through.',
  stressSummary: 'Medium-high, tied to upcoming tests this week.',
  sleepSummary: 'Below target — averaging 5–6 hours versus a recommended 7–9.',
  recoverySuggestions: [
    'Aim for one earlier night this week, even by 30–45 minutes.',
    'Short breaks between study blocks to reset focus.',
    'Revisit workload after Friday\'s tests to rebalance the week.',
  ],
}

export const weeklyTrend = [
  { week: 'W1', wellness: 58, burnout: 55, mood: 60, sleep: 62, stress: 64 },
  { week: 'W2', wellness: 61, burnout: 52, mood: 63, sleep: 65, stress: 60 },
  { week: 'W3', wellness: 59, burnout: 54, mood: 58, sleep: 60, stress: 63 },
  { week: 'W4', wellness: 65, burnout: 47, mood: 66, sleep: 68, stress: 55 },
  { week: 'W5', wellness: 67, burnout: 44, mood: 69, sleep: 70, stress: 50 },
  { week: 'W6', wellness: 72, burnout: 38, mood: 74, sleep: 75, stress: 44 },
]

export const plannerCompletionTrend = [
  { week: 'W1', completion: 48 },
  { week: 'W2', completion: 55 },
  { week: 'W3', completion: 51 },
  { week: 'W4', completion: 62 },
  { week: 'W5', completion: 58 },
  { week: 'W6', completion: 64 },
]

export const recoveryGoalCompletion = { completed: 9, total: 14 }
