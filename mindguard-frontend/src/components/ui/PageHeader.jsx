export default function PageHeader({ eyebrow, title, description, action }) {
  return (
    <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4 mb-8">
      <div>
        {eyebrow && <p className="text-xs uppercase tracking-widest text-accent-purple mb-2">{eyebrow}</p>}
        <h1 className="text-2xl md:text-3xl font-semibold text-text-hi">{title}</h1>
        {description && <p className="text-text-lo text-sm mt-2 max-w-xl">{description}</p>}
      </div>
      {action}
    </div>
  )
}
