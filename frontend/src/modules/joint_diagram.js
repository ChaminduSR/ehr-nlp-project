// Joint Assessment Diagram (Konva.js)
// Implements 28-joint DAS28 visualization with interactive states

export const JointDiagram = {
    stage: null,
    layer: null,
    joints: {}, // id -> { group, circle, text, state }
    onHoverCallback: null,
    onClickCallback: null,
    Konva: null, // Store Konva reference

    // Joint Coordinates
    // 28 Joints: Shoulders(2), Elbows(2), Wrists(2), Knees(2), MCP(10), PIP(10)
    // Note: For PIP of thumb, we use IP.
    jointData: [
        // Upper Limbs
        { id: 'l_shoulder', x: 120, y: 60, label: 'L Shoulder' },
        { id: 'r_shoulder', x: 280, y: 60, label: 'R Shoulder' },
        { id: 'l_elbow', x: 100, y: 140, label: 'L Elbow' },
        { id: 'r_elbow', x: 300, y: 140, label: 'R Elbow' },
        { id: 'l_wrist', x: 85, y: 210, label: 'L Wrist' },
        { id: 'r_wrist', x: 315, y: 210, label: 'R Wrist' },

        // Lower Limbs
        { id: 'l_knee', x: 160, y: 550, label: 'L Knee' },
        { id: 'r_knee', x: 240, y: 550, label: 'R Knee' },

        // Left Hand (MCP 1-5) - Jazz Hands (Splayed)
        { id: 'l_mcp1', x: 35, y: 240, label: 'L MCP1' }, // Thumb (Lateral)
        { id: 'l_mcp2', x: 55, y: 260, label: 'L MCP2' },
        { id: 'l_mcp3', x: 85, y: 270, label: 'L MCP3' },
        { id: 'l_mcp4', x: 115, y: 260, label: 'L MCP4' },
        { id: 'l_mcp5', x: 135, y: 240, label: 'L MCP5' }, // Pinky (Medial)

        // Right Hand (MCP 1-5) - Jazz Hands (Splayed)
        { id: 'r_mcp1', x: 365, y: 240, label: 'R MCP1' }, // Thumb (Lateral)
        { id: 'r_mcp2', x: 345, y: 260, label: 'R MCP2' },
        { id: 'r_mcp3', x: 315, y: 270, label: 'R MCP3' },
        { id: 'r_mcp4', x: 285, y: 260, label: 'R MCP4' },
        { id: 'r_mcp5', x: 265, y: 240, label: 'R MCP5' }, // Pinky (Medial)

        // Left Hand (PIP 1-5) - Extending from MCPs
        { id: 'l_pip1', x: 20, y: 260, label: 'L IP1' }, // Thumb IP
        { id: 'l_pip2', x: 45, y: 290, label: 'L PIP2' },
        { id: 'l_pip3', x: 85, y: 310, label: 'L PIP3' },
        { id: 'l_pip4', x: 125, y: 290, label: 'L PIP4' },
        { id: 'l_pip5', x: 150, y: 260, label: 'L PIP5' },

        // Right Hand (PIP 1-5) - Extending from MCPs
        { id: 'r_pip1', x: 380, y: 260, label: 'R IP1' }, // Thumb IP
        { id: 'r_pip2', x: 355, y: 290, label: 'R PIP2' },
        { id: 'r_pip3', x: 315, y: 310, label: 'R PIP3' },
        { id: 'r_pip4', x: 275, y: 290, label: 'R PIP4' },
        { id: 'r_pip5', x: 250, y: 260, label: 'R PIP5' }
    ],

    async init(containerId, onClickCallback, onHoverCallback, onRightClickCallback) {
        // Dynamic Import
        if (!this.Konva) {
            const module = await import('konva');
            this.Konva = module.default;
        }
        const Konva = this.Konva;

        this.onClickCallback = onClickCallback;
        this.onHoverCallback = onHoverCallback;
        this.onRightClickCallback = onRightClickCallback;

        this.stage = new Konva.Stage({
            container: containerId,
            width: 400,
            height: 600
        });

        this.layer = new Konva.Layer();
        this.stage.add(this.layer);

        // Draw Skeleton (Lines connecting joints)
        this.drawSkeleton();

        this.jointData.forEach(joint => {
            this.createJoint(joint);
        });

        this.layer.draw();
    },

    drawSkeleton() {
        const Konva = this.Konva;
        // Helper to find joint position
        const getPos = (id) => this.jointData.find(j => j.id === id);

        // 1. Arms
        const armConnections = [
            ['l_shoulder', 'l_elbow'], ['l_elbow', 'l_wrist'],
            ['r_shoulder', 'r_elbow'], ['r_elbow', 'r_wrist']
        ];

        armConnections.forEach(([start, end]) => {
            const s = getPos(start);
            const e = getPos(end);
            if (s && e) this.createLine(s.x, s.y, e.x, e.y);
        });

        // 2. Spine & Legs (Stick Figure Style - No Body Box)
        const lShoulder = getPos('l_shoulder');
        const rShoulder = getPos('r_shoulder');
        const lKnee = getPos('l_knee');
        const rKnee = getPos('r_knee');

        if (lShoulder && rShoulder && lKnee && rKnee) {
            const neck = { x: (lShoulder.x + rShoulder.x) / 2, y: lShoulder.y };
            const hipY = 380;
            const pelvis = { x: neck.x, y: hipY };
            const lHip = { x: 140, y: hipY };
            const rHip = { x: 260, y: hipY };

            // Shoulders connection
            this.createLine(lShoulder.x, lShoulder.y, rShoulder.x, rShoulder.y);

            // Spine (Neck to Pelvis)
            this.createLine(neck.x, neck.y, pelvis.x, pelvis.y);

            // Pelvis to Hips (V shape)
            this.createLine(pelvis.x, pelvis.y, lHip.x, lHip.y);
            this.createLine(pelvis.x, pelvis.y, rHip.x, rHip.y);

            // Hips to Knees
            this.createLine(lHip.x, lHip.y, lKnee.x, lKnee.y);
            this.createLine(rHip.x, rHip.y, rKnee.x, rKnee.y);
        }

        // 3. Hands (Wrist -> MCP -> PIP)
        const hands = ['l', 'r'];
        hands.forEach(side => {
            const wrist = getPos(`${side}_wrist`);
            if (!wrist) return;

            for (let i = 1; i <= 5; i++) {
                const mcp = getPos(`${side}_mcp${i}`);
                const pip = getPos(`${side}_pip${i}`);

                if (mcp) {
                    this.createLine(wrist.x, wrist.y, mcp.x, mcp.y);
                    if (pip) {
                        this.createLine(mcp.x, mcp.y, pip.x, pip.y);
                    }
                }
            }
        });
    },

    createLine(x1, y1, x2, y2) {
        const Konva = this.Konva;
        const line = new Konva.Line({
            points: [x1, y1, x2, y2],
            stroke: '#ccc',
            strokeWidth: 4,
            lineCap: 'round',
            lineJoin: 'round'
        });
        this.layer.add(line);
    },

    createJoint(data) {
        const Konva = this.Konva;
        const group = new Konva.Group({
            x: data.x,
            y: data.y
        });

        const circle = new Konva.Circle({
            radius: 12,
            fill: 'white',
            stroke: '#333',
            strokeWidth: 2,
            shadowColor: 'black',
            shadowBlur: 2,
            shadowOpacity: 0.2,
            shadowOffset: {x: 1, y: 1}
        });

        // Invisible hit area for easier clicking
        const hitArea = new Konva.Circle({
            radius: 20,
            fill: 'transparent'
        });

        group.add(hitArea);
        group.add(circle);

        // Event Handling
        group.on('mouseenter', () => {
            this.stage.container().style.cursor = 'pointer';
            circle.strokeWidth(4);
            this.layer.batchDraw();
            if (this.onHoverCallback) {
                // Pass absolute position for tooltip
                const pos = group.getAbsolutePosition();
                this.onHoverCallback(data, pos.x, pos.y);
            }
        });

        group.on('mouseleave', () => {
            this.stage.container().style.cursor = 'default';
            circle.strokeWidth(2);
            this.layer.batchDraw();
            if (this.onHoverCallback) {
                this.onHoverCallback(null);
            }
        });

        group.on('click tap', (e) => {
            if (e.evt.button === 2) {
                // Right click handled by contextmenu event usually, but let's be safe
                return;
            }
            if (this.onClickCallback) {
                const pos = group.getAbsolutePosition();
                this.onClickCallback(data.id, pos.x, pos.y);
            }
        });

        group.on('contextmenu', (e) => {
            e.evt.preventDefault(); // Prevent default browser context menu
            if (this.onRightClickCallback) {
                const pos = group.getAbsolutePosition();
                this.onRightClickCallback(data.id, pos.x, pos.y);
            }
        });

        this.layer.add(group);
        this.joints[data.id] = { group, circle };
    },

    // Update visual state based on clinical data
    updateJointState(jointId, data) {
        const joint = this.joints[jointId];
        if (!joint) return;

        const { circle } = joint;
        const { tenderness, swelling, pain } = data;

        // Color Logic:
        // - Tenderness + Swelling -> Orange
        // - Swelling only -> Red
        // - Tenderness only -> Yellow
        // - Normal -> White

        let fill = 'white';
        if (tenderness && swelling > 0) {
            fill = '#FF8C00'; // Dark Orange
        } else if (swelling > 0) {
            fill = '#FF4444'; // Red
        } else if (tenderness) {
            fill = '#FFEB3B'; // Yellow
        }

        // Pain indicator (Blue border)
        let stroke = '#333';
        if (pain) {
            stroke = '#2196F3'; // Blue
        }

        circle.fill(fill);
        circle.stroke(stroke);
        this.layer.batchDraw();
    }
};
