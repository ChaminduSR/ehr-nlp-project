# Konva.js Joint Assessment Implementation

## Overview
This document outlines the implementation of the interactive Joint Assessment diagram using Konva.js. This approach replaces static images or SVGs with a lightweight, code-drawn canvas, optimized for performance on older hardware in rural clinics.

## Technical Stack
- **Library**: `Konva.js` (Vanilla JS or integrated via Alpine.js)
- **Rendering**: HTML5 Canvas
- **Performance**: Zero external assets, instant color updates, low memory usage.

## Joint Map Coordinates
The diagram consists of 28 joints used in the DAS28 score calculation.

### Upper Body
| Joint | ID | X | Y | Label |
| :--- | :--- | :--- | :--- | :--- |
| **Shoulders** | `l_shoulder` | 120 | 60 | L Shoulder |
| | `r_shoulder` | 280 | 60 | R Shoulder |
| **Elbows** | `l_elbow` | 100 | 140 | L Elbow |
| | `r_elbow` | 300 | 140 | R Elbow |
| **Wrists** | `l_wrist` | 85 | 210 | L Wrist |
| | `r_wrist` | 315 | 210 | R Wrist |

### Hands (MCP & PIP)
| Joint | ID (Left) | X | Y | ID (Right) | X | Y |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **MCP 1** | `l_mcp1` | 70 | 270 | `r_mcp1` | 330 | 270 |
| **MCP 2** | `l_mcp2` | 65 | 290 | `r_mcp2` | 335 | 290 |
| **MCP 3** | `l_mcp3` | 68 | 310 | `r_mcp3` | 332 | 310 |
| **MCP 4** | `l_mcp4` | 75 | 330 | `r_mcp4` | 325 | 330 |
| **MCP 5** | `l_mcp5` | 85 | 348 | `r_mcp5` | 315 | 348 |
| **PIP 2** | `l_pip2` | 50 | 310 | `r_pip2` | 350 | 310 |
| **PIP 3** | `l_pip3` | 48 | 330 | `r_pip3` | 352 | 330 |
| **PIP 4** | `l_pip4` | 52 | 350 | `r_pip4` | 348 | 350 |
| **PIP 5** | `l_pip5` | 60 | 368 | `r_pip5` | 340 | 368 |

### Lower Body
| Joint | ID | X | Y | Label |
| :--- | :--- | :--- | :--- | :--- |
| **Knees** | `l_knee` | 160 | 550 | L Knee |
| | `r_knee` | 240 | 550 | R Knee |

## Interaction Logic

### States
Each joint tracks three properties:
1. **Tenderness** (Boolean)
2. **Pain** (Boolean) - *Note: DAS28 focuses on Tenderness, but Pain is often tracked.*
3. **Swelling** (Grade 0-3)

### Visual Feedback (Color Coding)
- **White**: Normal (No tenderness, No swelling)
- **Yellow**: Tenderness only
- **Red**: Swelling only (Grade > 0)
- **Orange**: Both Tenderness and Swelling

### Data Flow
1. User clicks a joint circle on the canvas.
2. `jointAssessmentFragment` (Alpine.js module) updates its internal state.
3. Visual feedback is updated immediately on the canvas.
4. `save()` method is triggered automatically (debounced or immediate) to persist state to backend.
5. Backend receives JSON payload with joint status.
