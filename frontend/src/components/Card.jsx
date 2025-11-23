import React from 'react'

export default function Card({ title, children }) {
  return (
    <section className="card">
      {title && <div className="card-header"><h3>{title}</h3></div>}
      <div className="card-body">{children}</div>
    </section>
  )
}
