import { useState, useEffect } from 'react'
import { Plus, Clock, Tag, Sparkles, User as UserIcon, Trash2 } from 'lucide-react'
import PageHeader from '../components/ui/PageHeader.jsx'
import GlassCard from '../components/ui/GlassCard.jsx'
import ProgressBar from '../components/ui/ProgressBar.jsx'
import Badge from '../components/ui/Badge.jsx'
import Button from '../components/ui/Button.jsx'
import TextField from '../components/ui/TextField.jsx'
import { planner as plannerApi } from '../services/api'

const priorityTone = { High: 'high', Medium: 'moderate', Low: 'low' }

export default function Planner() {
  const [tasks, setTasks] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ title: '', description: '', category: 'General', priority: 'Medium', due_date: '', due_time: '' })

  useEffect(() => {
    plannerApi.list()
      .then(setTasks)
      .catch(() => setTasks([]))
      .finally(() => setLoading(false))
  }, [])

  async function toggleTask(task) {
    await plannerApi.update(task.task_id, { completed: !task.completed })
    setTasks((prev) => prev.map((t) =>
      t.task_id === task.task_id ? { ...t, completed: !t.completed } : t
    ))
  }

  async function deleteTask(taskId) {
    await plannerApi.remove(taskId)
    setTasks((prev) => prev.filter((t) => t.task_id !== taskId))
  }

  async function addTask(e) {
    e.preventDefault()
    if (!form.title.trim()) return
    const res = await plannerApi.add({ ...form, task_source: 'USER' })
    setTasks((prev) => [{ ...form, task_id: res.task_id, completed: false, task_source: 'USER' }, ...prev])
    setForm({ title: '', description: '', category: 'General', priority: 'Medium', due_date: '', due_time: '' })
    setShowForm(false)
  }

  const completed = tasks.filter((t) => t.completed).length
  const percent = tasks.length > 0 ? Math.round((completed / tasks.length) * 100) : 0

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-text-lo">Loading tasks...</p>
      </div>
    )
  }

  return (
    <div>
      <PageHeader
        eyebrow="Recovery Planner"
        title="Today's Plan"
        description="Your tasks and recovery goals, together in one place."
      />

      <GlassCard glow className="p-7 mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <p className="text-xs text-text-lo mb-1">Daily Progress</p>
            <p className="text-3xl font-display font-semibold">{percent}%</p>
          </div>
          <p className="text-sm text-text-lo">{completed} of {tasks.length} tasks completed</p>
        </div>
        <ProgressBar value={percent} height="h-3" />
      </GlassCard>

      <div className="flex justify-end mb-4">
        <Button variant="secondary" icon={Plus} onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancel' : 'New Task'}
        </Button>
      </div>

      {showForm && (
        <GlassCard className="p-6 mb-6">
          <form onSubmit={addTask} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="sm:col-span-2">
                <TextField
                  label="Title *"
                  placeholder="What do you need to do?"
                  value={form.title}
                  onChange={(e) => setForm({ ...form, title: e.target.value })}
                  required
                />
              </div>
              <div className="sm:col-span-2">
                <TextField
                  label="Description"
                  placeholder="Optional details..."
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                />
              </div>
              <label className="block">
                <span className="block text-xs text-text-lo mb-2">Category</span>
                <select
                  value={form.category}
                  onChange={(e) => setForm({ ...form, category: e.target.value })}
                  className="w-full bg-white/5 border border-white/10 rounded-xl py-3 px-4 text-sm text-text-hi outline-none focus:border-accent-purple/50 appearance-none cursor-pointer"
                >
                  <option value="General">General</option>
                  <option value="Study">Study</option>
                  <option value="Assignment">Assignment</option>
                  <option value="Exam">Exam</option>
                  <option value="Recovery">Recovery</option>
                  <option value="Exercise">Exercise</option>
                  <option value="Personal">Personal</option>
                  <option value="Other">Other</option>
                </select>
              </label>
              <label className="block">
                <span className="block text-xs text-text-lo mb-2">Priority</span>
                <select
                  value={form.priority}
                  onChange={(e) => setForm({ ...form, priority: e.target.value })}
                  className="w-full bg-white/5 border border-white/10 rounded-xl py-3 px-4 text-sm text-text-hi outline-none focus:border-accent-purple/50 appearance-none cursor-pointer"
                >
                  <option value="Low">Low</option>
                  <option value="Medium">Medium</option>
                  <option value="High">High</option>
                </select>
              </label>
              <TextField
                label="Due Date"
                type="date"
                value={form.due_date}
                onChange={(e) => setForm({ ...form, due_date: e.target.value })}
              />
              <TextField
                label="Due Time"
                type="time"
                value={form.due_time}
                onChange={(e) => setForm({ ...form, due_time: e.target.value })}
              />
            </div>
            <div className="flex justify-end gap-3">
              <Button variant="ghost" type="button" onClick={() => setShowForm(false)}>Cancel</Button>
              <Button variant="primary" type="submit">Add Task</Button>
            </div>
          </form>
        </GlassCard>
      )}

      {tasks.length === 0 && (
        <GlassCard className="p-7 text-center">
          <p className="text-text-lo">No tasks yet. Start a check-in to get recovery suggestions.</p>
        </GlassCard>
      )}

      <div className="space-y-3">
        {tasks.map((task) => (
          <GlassCard key={task.task_id} hover className="p-5 flex items-center gap-4">
            <button
              onClick={() => toggleTask(task)}
              className={`w-6 h-6 rounded-lg border flex items-center justify-center shrink-0 transition-colors ${
                task.completed ? 'bg-brand-gradient border-transparent' : 'border-white/20 hover:border-accent-purple/50'
              }`}
              aria-label="Toggle task completion"
            >
              {task.completed && <span className="w-2 h-2 rounded-full bg-white" />}
            </button>

            <div className="flex-1 min-w-0">
              <p className={`text-sm font-medium mb-1.5 ${task.completed ? 'text-text-faint line-through' : 'text-text-hi'}`}>
                {task.title}
              </p>
              <div className="flex flex-wrap items-center gap-3 text-xs text-text-lo">
                <span className="flex items-center gap-1.5">
                  <Tag size={12} /> {task.category || 'General'}
                </span>
                {task.due_date && (
                  <span className="flex items-center gap-1.5">
                    <Clock size={12} /> {task.due_date}{task.due_time ? `, ${task.due_time}` : ''}
                  </span>
                )}
                <span className="flex items-center gap-1.5">
                  {task.task_source === 'ENGINE' ? <Sparkles size={12} className="text-accent-purple" /> : <UserIcon size={12} />}
                  {task.task_source === 'ENGINE' ? 'AI Suggested' : 'Your Task'}
                </span>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Badge tone={priorityTone[task.priority] || 'moderate'}>{task.priority || 'Medium'}</Badge>
              <button
                onClick={() => deleteTask(task.task_id)}
                className="text-text-faint hover:text-rose-300 transition-colors"
                aria-label="Delete task"
              >
                <Trash2 size={15} />
              </button>
            </div>
          </GlassCard>
        ))}
      </div>
    </div>
  )
}
