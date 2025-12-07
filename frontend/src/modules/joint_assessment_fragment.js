export function jointAssessmentFragment(visitId, initialData) {
    return {
        visitId: visitId,
        joints: initialData || {},
        stage: null,
        layer: null,
        Konva: null, // Lazy-loaded
        width: 400,
        height: 600,
        isSaving: false,

        // Mark fragment dirty - coordinatedSave in medical_note_form.html handles the actual save
        markDirty() {
            if (window._markDirty) {
                window._markDirty();
            }
        },

        jointDefs: [
            { id: 'l_shoulder', x: 120, y: 60, label: 'L Shoulder' },
            { id: 'r_shoulder', x: 280, y: 60, label: 'R Shoulder' },
            { id: 'l_elbow', x: 100, y: 140, label: 'L Elbow' },
            { id: 'r_elbow', x: 300, y: 140, label: 'R Elbow' },
            { id: 'l_wrist', x: 85, y: 210, label: 'L Wrist' },
            { id: 'r_wrist', x: 315, y: 210, label: 'R Wrist' },
            { id: 'l_ip', x: 45, y: 275, label: 'L IP' },
            { id: 'r_ip', x: 355, y: 275, label: 'R IP' },
            { id: 'l_mcp1', x: 70, y: 270, label: 'L MCP1' },
            { id: 'l_mcp2', x: 65, y: 290, label: 'L MCP2' },
            { id: 'l_mcp3', x: 68, y: 310, label: 'L MCP3' },
            { id: 'l_mcp4', x: 75, y: 330, label: 'L MCP4' },
            { id: 'l_mcp5', x: 85, y: 348, label: 'L MCP5' },
            { id: 'r_mcp1', x: 330, y: 270, label: 'R MCP1' },
            { id: 'r_mcp2', x: 335, y: 290, label: 'R MCP2' },
            { id: 'r_mcp3', x: 332, y: 310, label: 'R MCP3' },
            { id: 'r_mcp4', x: 325, y: 330, label: 'R MCP4' },
            { id: 'r_mcp5', x: 315, y: 348, label: 'R MCP5' },
            { id: 'l_pip2', x: 50, y: 310, label: 'L PIP2' },
            { id: 'l_pip3', x: 48, y: 330, label: 'L PIP3' },
            { id: 'l_pip4', x: 52, y: 350, label: 'L PIP4' },
            { id: 'l_pip5', x: 60, y: 368, label: 'L PIP5' },
            { id: 'r_pip2', x: 350, y: 310, label: 'R PIP2' },
            { id: 'r_pip3', x: 352, y: 330, label: 'R PIP3' },
            { id: 'r_pip4', x: 348, y: 350, label: 'R PIP4' },
            { id: 'r_pip5', x: 340, y: 368, label: 'R PIP5' },
            { id: 'l_knee', x: 160, y: 550, label: 'L Knee' },
            { id: 'r_knee', x: 240, y: 550, label: 'R Knee' }
        ],

        async init() {
            // Lazy-load Konva only when joint assessment fragment is initialized
            if (!this.Konva) {
                const module = await import(/* webpackChunkName: "joint-diagram" */ 'konva');
                this.Konva = module.default;
            }
            this.$nextTick(() => {
                this.setupKonva();
            });
        },

        setupKonva() {
            if (this.stage) return;
            const Konva = this.Konva;
            this.stage = new Konva.Stage({
                container: this.$refs.konvaContainer,
                width: this.width,
                height: this.height
            });
            this.layer = new this.Konva.Layer();
            this.stage.add(this.layer);
            this.drawWireframe();
            this.drawJoints();
            this.layer.draw();
        },

        drawWireframe() {
            const Konva = this.Konva;
            const lines = [
                [200, 60, 200, 400],
                [120, 60, 280, 60],
                [120, 60, 100, 140, 85, 210],
                [280, 60, 300, 140, 315, 210],
                [200, 400, 160, 550],
                [200, 400, 240, 550],
                [85, 210, 70, 270], [85, 210, 65, 290], [85, 210, 68, 310], [85, 210, 75, 330], [85, 210, 85, 348],
                [70, 270, 45, 275], [65, 290, 50, 310], [68, 310, 48, 330], [75, 330, 52, 350], [85, 348, 60, 368],
                [315, 210, 330, 270], [315, 210, 335, 290], [315, 210, 332, 310], [315, 210, 325, 330], [315, 210, 315, 348],
                [330, 270, 355, 275], [335, 290, 350, 310], [332, 310, 352, 330], [325, 330, 348, 350], [315, 348, 340, 368]
            ];
            lines.forEach(points => {
                this.layer.add(new Konva.Line({
                    points: points,
                    stroke: '#e2e8f0',
                    strokeWidth: 4,
                    lineCap: 'round',
                    lineJoin: 'round',
                    tension: 0
                }));
            });
        },

        drawJoints() {
            const Konva = this.Konva;
            const tooltipMap = {};
            this.jointDefs.forEach(joint => {
                const circle = new Konva.Circle({
                    x: joint.x,
                    y: joint.y,
                    radius: 12,
                    fill: this.getColor(this.joints[joint.id] || 'normal'),
                    stroke: '#475569',
                    strokeWidth: 2,
                    id: joint.id
                });

                circle.on('click', () => {
                    this.cycleState(joint.id, circle);
                });

                circle.on('mouseenter', () => {
                    this.stage.container().style.cursor = 'pointer';
                    if(tooltipMap[joint.id]) {
                        tooltipMap[joint.id].opacity(1);
                        this.layer.batchDraw();
                    }
                });

                circle.on('mouseleave', () => {
                    this.stage.container().style.cursor = 'default';
                    if(tooltipMap[joint.id]) {
                        tooltipMap[joint.id].opacity(0);
                        this.layer.batchDraw();
                    }
                });

                this.layer.add(circle);

                const tooltip = new Konva.Label({
                    x: joint.x,
                    y: joint.y - 20,
                    opacity: 0,
                    listening: false
                });

                tooltip.add(new Konva.Tag({
                    fill: '#1e293b',
                    pointerDirection: 'down',
                    pointerWidth: 10,
                    pointerHeight: 10,
                    lineJoin: 'round',
                    shadowColor: 'black',
                    shadowBlur: 10,
                    shadowOffset: {x: 5, y: 5},
                    shadowOpacity: 0.2,
                    cornerRadius: 5
                }));

                tooltip.add(new Konva.Text({
                    text: joint.label,
                    fontFamily: 'sans-serif',
                    fontSize: 14,
                    padding: 8,
                    fill: 'white',
                    align: 'center'
                }));

                this.layer.add(tooltip);
                tooltipMap[joint.id] = tooltip;
            });
        },

        cycleState(id, node) {
            const states = ['normal', 'tender', 'swollen', 'both'];
            const currentState = this.joints[id] || 'normal';
            const nextState = states[(states.indexOf(currentState) + 1) % states.length];

            if (nextState === 'normal') delete this.joints[id];
            else this.joints[id] = nextState;

            node.fill(this.getColor(nextState));
            this.layer.batchDraw();

            // Mark dirty - coordinatedSave handles the actual network request
            this.markDirty();
        },

        getColor(state) {
            const colors = {
                'normal': '#ffffff',
                'tender': '#eab308',
                'swollen': '#ef4444',
                'both': '#f97316'
            };
            return colors[state] || '#ffffff';
        }
    };
}
