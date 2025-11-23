import React, { useState, useEffect } from 'react'

// Dynamically import react-konva at runtime so Konva is only fetched when this
// component mounts. This ensures Konva and react-konva land in a separate chunk
// and are not part of the initial bundle.
export default function JointCanvas({ initialPos = { x: 120, y: 80 } }) {
  const [circlePos, setCirclePos] = useState(initialPos)
  const [Konva, setKonva] = useState(null)

  useEffect(() => {
    let mounted = true
    import('react-konva')
      .then(mod => {
        if (mounted) setKonva(mod)
      })
      .catch(err => {
        // If import fails, leave Konva null and optionally log the error
        // (in production apps you might surface a friendly error UI)
        // console.error('Failed to load react-konva', err)
      })

    return () => { mounted = false }
  }, [])

  if (!Konva) {
    return <div style={{ height: 240 }}>Loading canvas...</div>
  }

  const { Stage, Layer, Circle } = Konva

  return (
    <div style={{ height: 240 }}>
      <Stage width={480} height={240}>
        <Layer>
          <Circle
            x={circlePos.x}
            y={circlePos.y}
            radius={24}
            fill="#60a5fa"
            draggable
            onDragEnd={e => setCirclePos({ x: e.target.x(), y: e.target.y() })}
          />
        </Layer>
      </Stage>
      <div style={{ marginTop: 8, color: '#6b7280' }}>Drag the circle to annotate a joint position (simple demo)</div>
    </div>
  )
}
