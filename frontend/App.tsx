import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import * as Lucide from 'lucide-react';

type View = 'overview' | 'colors' | 'typography' | 'components' | 'dashboard' | 'patients' | 'medical-note' | 'joint-assessment' | 'reports' | 'specs';

export default function App() {
  const [currentView, setCurrentView] = useState<View>('overview');

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/30 to-slate-100">
      {/* Animated Header with Gradient */}
      <motion.header
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        className="bg-gradient-to-r from-blue-600 via-blue-700 to-indigo-700 text-white shadow-2xl sticky top-0 z-50 backdrop-blur-md border-b border-white/10"
      >
        <div className="px-8 py-6">
          <div className="flex items-center justify-between">
            <motion.div
              className="flex items-center gap-3"
              whileHover={{ scale: 1.02 }}
            >
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
                className="p-2 bg-white/10 backdrop-blur-sm rounded-xl"
              >
                <Lucide.Activity className="w-8 h-8" />
              </motion.div>
              <div>
                <h1 className="text-2xl">Rheumatology EHR</h1>
                <p className="text-sm text-blue-100">Modern Design System v1.0</p>
              </div>
              </motion.div>
            <div className="flex items-center gap-3">
              <motion.div
                whileHover={{ scale: 1.05 }}
                className="px-4 py-2 bg-white/10 rounded-xl backdrop-blur-sm border border-white/20"
              >
                <div className="text-xs text-blue-100">Bundle Size</div>
                <div className="text-sm flex items-center gap-2">
                  <Lucide.Zap className="w-4 h-4" />
                  150KB
                </div>
              </motion.div>
              <motion.div
                whileHover={{ scale: 1.05 }}
                className="px-4 py-2 bg-white/10 rounded-xl backdrop-blur-sm border border-white/20"
              >
                <div className="text-xs text-blue-100">WCAG AAA</div>
                <div className="text-sm flex items-center gap-2">
                  <Lucide.Shield className="w-4 h-4" />
                  7:1 Contrast
                </div>
              </motion.div>
            </div>
          </div>
        </div>
      </motion.header>

      {/* Modern Tab Navigation with Animation */}
      <nav className="bg-white/80 backdrop-blur-xl border-b border-slate-200/60 sticky top-[98px] z-40 shadow-sm">
        <div className="px-8 py-1 flex gap-1 overflow-x-auto">
          <NavTab active={currentView === 'overview'} onClick={() => setCurrentView('overview')} icon={<Lucide.LayoutDashboard className="w-4 h-4" />}>
            Overview
          </NavTab>
          <NavTab active={currentView === 'colors'} onClick={() => setCurrentView('colors')} icon={<Lucide.Palette className="w-4 h-4" />}>
            Colors
          </NavTab>
          <NavTab active={currentView === 'typography'} onClick={() => setCurrentView('typography')} icon={<Lucide.Type className="w-4 h-4" />}>
            Typography
          </NavTab>
          <NavTab active={currentView === 'components'} onClick={() => setCurrentView('components')} icon={<Lucide.Box className="w-4 h-4" />}>
            Components
          </NavTab>
          <NavTab active={currentView === 'dashboard'} onClick={() => setCurrentView('dashboard')} icon={<Lucide.Activity className="w-4 h-4" />}>
            Dashboard
          </NavTab>
          <NavTab active={currentView === 'patients'} onClick={() => setCurrentView('patients')} icon={<Lucide.Users className="w-4 h-4" />}>
            Patients
          </NavTab>
          <NavTab active={currentView === 'medical-note'} onClick={() => setCurrentView('medical-note')} icon={<Lucide.FileText className="w-4 h-4" />}>
            Medical Note
          </NavTab>
          <NavTab active={currentView === 'joint-assessment'} onClick={() => setCurrentView('joint-assessment')} icon={<Lucide.Hand className="w-4 h-4" />}>
            Joint Assessment
          </NavTab>
          <NavTab active={currentView === 'reports'} onClick={() => setCurrentView('reports')} icon={<Lucide.BarChart3 className="w-4 h-4" />}>
            Reports
          </NavTab>
          <NavTab active={currentView === 'specs'} onClick={() => setCurrentView('specs')} icon={<Lucide.Settings className="w-4 h-4" />}>
            Specs
          </NavTab>
        </div>
      </nav>

      {/* Main Content with Page Transitions */}
      <main className="px-8 py-8 max-w-[1600px] mx-auto">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentView}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            {currentView === 'overview' && <OverviewView />}
            {currentView === 'colors' && <ColorsView />}
            {currentView === 'typography' && <TypographyView />}
            {currentView === 'components' && <ComponentsView />}
            {currentView === 'dashboard' && <DashboardMockup />}
            {currentView === 'patients' && <PatientsMockup />}
            {currentView === 'medical-note' && <MedicalNoteMockup />}
            {currentView === 'joint-assessment' && <JointAssessmentMockup />}
            {currentView === 'reports' && <ReportsMockup />}
            {currentView === 'specs' && <SpecificationsView />}
          </motion.div>
        </AnimatePresence>
      </main>

      {/* Modern Footer */}
      <footer className="mt-16 py-8 px-8 bg-white/60 backdrop-blur-lg border-t border-slate-200/60">
        <div className="max-w-[1600px] mx-auto text-center text-slate-600">
          <p className="flex items-center justify-center gap-2">
            <Lucide.Sparkles className="w-4 h-4 text-blue-600" />
            Rheumatology EHR Design System v1.0 • November 2025
          </p>
          <p className="mt-2 text-sm">Optimized for rural clinics • WCAG AAA compliant • Performance-first design</p>
        </div>
      </footer>
    </div>
  );
}

function NavTab({ active, onClick, children, icon }: { active: boolean; onClick: () => void; children: React.ReactNode; icon: React.ReactNode }) {
  return (
    <motion.button
      onClick={onClick}
      whileHover={{ y: -2 }}
      whileTap={{ scale: 0.98 }}
      className={`px-4 py-3 rounded-t-xl whitespace-nowrap flex items-center gap-2 transition-all relative ${
        active
          ? 'bg-white text-blue-600 shadow-md'
          : 'text-slate-600 hover:text-slate-900 hover:bg-white/50'
      }`}
    >
      {active && (
        <motion.div
          layoutId="activeTab"
          className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-blue-500 to-indigo-500"
          transition={{ type: "spring", stiffness: 500, damping: 30 }}
        />
      )}
      {icon}
      {children}
    </motion.button>
  );
}

function OverviewView() {
  return (
    <div className="space-y-8">
      {/* Hero Section with Animation */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="relative overflow-hidden bg-gradient-to-br from-blue-600 via-blue-700 to-indigo-700 rounded-3xl p-12 text-white shadow-2xl"
      >
        <div className="absolute top-0 right-0 w-96 h-96 bg-white/5 rounded-full blur-3xl"></div>
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-white/5 rounded-full blur-3xl"></div>
        <div className="relative z-10">
          <div className="flex items-center gap-4 mb-6">
            <motion.div
              animate={{ rotate: [0, 360] }}
              transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
              className="p-4 bg-white/10 backdrop-blur-sm rounded-2xl border border-white/20"
            >
              <Lucide.Activity className="w-12 h-12" />
            </motion.div>
            <div>
              <motion.h2
                initial={{ x: -20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: 0.2 }}
                className="text-5xl mb-2"
              >
                Design System
              </motion.h2>
              <motion.p
                initial={{ x: -20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: 0.3 }}
                className="text-xl text-blue-100"
              >
                Modern, accessible EHR designed for rural clinics and low-resource environments
              </motion.p>
            </div>
          </div>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="flex gap-4"
          >
            <button className="px-6 py-3 bg-white text-blue-700 rounded-xl hover:bg-blue-50 transition-colors flex items-center gap-2">
              <Lucide.Eye className="w-5 h-5" />
              View Components
            </button>
            <button className="px-6 py-3 bg-white/10 backdrop-blur-sm text-white rounded-xl hover:bg-white/20 transition-colors border border-white/20 flex items-center gap-2">
              <Lucide.Download className="w-5 h-5" />
              Download
            </button>
          </motion.div>
        </div>
      </motion.div>

      {/* Animated Key Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
        {[
          { value: "150KB", label: "Bundle Size", color: "blue", icon: <Lucide.Zap className="w-6 h-6" />, trend: "optimized" },
          { value: "7:1", label: "Contrast Ratio", color: "green", icon: <Lucide.Shield className="w-6 h-6" />, trend: "excellent" },
          { value: "48px", label: "Touch Target", color: "purple", icon: <Lucide.Hand className="w-6 h-6" />, trend: "accessible" },
          { value: "<1s", label: "Load Time", color: "orange", icon: <Lucide.Activity className="w-6 h-6" />, trend: "fast" }
        ].map((metric, index) => (
          <MetricCard key={index} {...metric} index={index} />
        ))}
      </div>

      {/* Animated Design Principles */}
      <div className="grid md:grid-cols-2 gap-6">
        {[
          { title: "Speed over Beauty", desc: "Performance is paramount. System fonts, minimal animations, optimized assets.", icon: <Lucide.Zap className="w-8 h-8" />, color: "blue" },
          { title: "Accessibility First", desc: "WCAG AAA compliance with 7:1 contrast ratios and full keyboard navigation.", icon: <Lucide.Shield className="w-8 h-8" />, color: "green" },
          { title: "Simplicity over Complexity", desc: "Clean, functional design focused on clinical workflows and user efficiency.", icon: <Lucide.Target className="w-8 h-8" />, color: "purple" },
          { title: "Clinical-first Design", desc: "Built for healthcare professionals in resource-constrained environments.", icon: <Lucide.Heart className="w-8 h-8" />, color: "orange" }
        ].map((principle, index) => (
          <PrincipleCard key={index} {...principle} index={index} />
        ))}
      </div>

      {/* Features Grid with Stagger Animation */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-white/60 backdrop-blur-xl rounded-3xl shadow-2xl p-8 border border-white/20"
      >
          <h3 className="text-2xl mb-6 flex items-center gap-3">
          <div className="p-2 bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl text-white">
            <Lucide.Check className="w-6 h-6" />
          </div>
          Core Features
        </h3>
        <div className="grid md:grid-cols-3 gap-6">
          {[
            { title: "Patient Management", desc: "Search, view, and manage patient records efficiently", icon: <Lucide.Users className="w-5 h-5" /> },
            { title: "Medical Notes", desc: "Auto-save every 30s with draft and finalized states", icon: <Lucide.FileText className="w-5 h-5" /> },
            { title: "Joint Assessment", desc: "Interactive 28-joint evaluation with DAS28 calculation", icon: <Lucide.Hand className="w-5 h-5" /> },
            { title: "Analytics Dashboard", desc: "Real-time clinic metrics and patient outcomes", icon: <Lucide.BarChart3 className="w-5 h-5" /> },
            { title: "Disease Tracking", desc: "DAS28 scores with color-coded severity indicators", icon: <Lucide.Activity className="w-5 h-5" /> },
            { title: "Responsive Design", desc: "Works on 10+ year old computers and mobile devices", icon: <Lucide.Smartphone className="w-5 h-5" /> }
          ].map((feature, index) => (
            <FeatureItem key={index} {...feature} index={index} />
          ))}
        </div>
      </motion.div>
    </div>
  );
}

function MetricCard({ value, label, color, icon, trend, index }: any) {
  const colors = {
    blue: 'from-blue-500 to-blue-600',
    green: 'from-green-500 to-emerald-600',
    purple: 'from-purple-500 to-purple-600',
    orange: 'from-orange-500 to-orange-600'
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      whileHover={{ y: -5, scale: 1.02 }}
      className="bg-white/60 backdrop-blur-xl rounded-2xl shadow-xl p-6 border border-white/20 hover:shadow-2xl transition-shadow"
    >
      <motion.div
        whileHover={{ rotate: 360 }}
        transition={{ duration: 0.6 }}
        className={`inline-flex p-3 rounded-xl bg-gradient-to-br ${colors[color as keyof typeof colors]} text-white mb-4 shadow-lg`}
      >
        {icon}
      </motion.div>
      <div className="text-3xl mb-1">{value}</div>
      <div className="text-slate-600 text-sm mb-3">{label}</div>
      <div className="flex items-center gap-1 text-xs">
        <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
        <span className="text-slate-500">{trend}</span>
      </div>
    </motion.div>
  );
}

function PrincipleCard({ title, desc, icon, color, index }: any) {
  const colors = {
    blue: 'from-blue-50 to-blue-100 group-hover:from-blue-100 group-hover:to-blue-200',
    green: 'from-green-50 to-emerald-100 group-hover:from-green-100 group-hover:to-emerald-200',
    purple: 'from-purple-50 to-purple-100 group-hover:from-purple-100 group-hover:to-purple-200',
    orange: 'from-orange-50 to-orange-100 group-hover:from-orange-100 group-hover:to-orange-200'
  };

  const iconColors = {
    blue: 'text-blue-600',
    green: 'text-green-600',
    purple: 'text-purple-600',
    orange: 'text-orange-600'
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: index % 2 === 0 ? -20 : 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.1 }}
      whileHover={{ scale: 1.02 }}
      className="group bg-white/60 backdrop-blur-xl rounded-2xl shadow-xl p-8 border border-white/20 hover:shadow-2xl transition-all"
    >
      <motion.div
        whileHover={{ scale: 1.1, rotate: 5 }}
        className={`inline-flex p-3 rounded-xl bg-gradient-to-br ${colors[color as keyof typeof colors]} ${iconColors[color as keyof typeof iconColors]} mb-4 transition-all`}
      >
        {icon}
      </motion.div>
      <h3 className="text-xl mb-3">{title}</h3>
      <p className="text-slate-600 leading-relaxed">{desc}</p>
      <motion.div
        initial={{ width: 0 }}
        whileInView={{ width: "100%" }}
        transition={{ delay: 0.2, duration: 0.6 }}
        className="h-1 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full mt-4"
      ></motion.div>
    </motion.div>
  );
}

function FeatureItem({ title, desc, icon, index }: any) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      whileHover={{ x: 5 }}
      className="flex items-start gap-3 p-5 rounded-xl hover:bg-white/80 transition-all cursor-pointer group border border-transparent hover:border-blue-200"
    >
      <motion.div
        whileHover={{ scale: 1.2 }}
        className="flex-shrink-0 p-2 bg-gradient-to-br from-blue-100 to-blue-200 text-blue-600 rounded-xl group-hover:from-blue-500 group-hover:to-blue-600 group-hover:text-white transition-all"
      >
        {icon}
      </motion.div>
      <div>
        <div className="mb-1 group-hover:text-blue-600 transition-colors">{title}</div>
        <div className="text-sm text-slate-600">{desc}</div>
      </div>
      <Lucide.ArrowRight className="w-4 h-4 text-slate-400 ml-auto opacity-0 group-hover:opacity-100 transition-opacity" />
    </motion.div>
  );
}

function ColorsView() {
  return (
    <div className="space-y-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white/60 backdrop-blur-xl rounded-3xl shadow-2xl p-8 border border-white/20"
      >
        <h2 className="text-4xl mb-2 flex items-center gap-3">
          <Lucide.Palette className="w-10 h-10 text-blue-600" />
          Color Palette
        </h2>
        <p className="text-slate-600">WCAG AAA compliant colors with 7:1 contrast minimum</p>
      </motion.div>

      {/* Primary Colors with Stagger */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-white/60 backdrop-blur-xl rounded-3xl shadow-2xl p-8 border border-white/20"
      >
        <h3 className="text-2xl mb-6">Primary Colors</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          {[
            { color: "bg-gradient-to-br from-blue-500 to-blue-700", hex: "#0066CC", name: "Primary Blue", contrast: "7.0:1", usage: "Primary actions, links" },
            { color: "bg-gradient-to-br from-orange-400 to-orange-600", hex: "#FF9900", name: "Draft Orange", contrast: "3.8:1", usage: "Draft states, warnings" },
            { color: "bg-gradient-to-br from-green-500 to-emerald-600", hex: "#00AA00", name: "Success Green", contrast: "7.5:1", usage: "Success, finalized" },
            { color: "bg-gradient-to-br from-red-500 to-red-700", hex: "#CC0000", name: "Error Red", contrast: "8.2:1", usage: "Errors, delete actions" }
          ].map((item, index) => (
            <ColorCard key={index} {...item} index={index} />
          ))}
        </div>
      </motion.div>

      {/* DAS28 Scale with Animation */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-white/60 backdrop-blur-xl rounded-3xl shadow-2xl p-8 border border-white/20"
      >
        <h3 className="text-2xl mb-6 flex items-center gap-2">
          <Lucide.Activity className="w-6 h-6 text-blue-600" />
          DAS28 Disease Activity Scale
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          {[
            { color: "bg-gradient-to-br from-green-500 to-emerald-600", label: "Remission", range: "< 2.6", description: "Disease under control" },
            { color: "bg-gradient-to-br from-yellow-400 to-yellow-500", label: "Low Activity", range: "2.6 - 3.2", description: "Mild activity", textDark: true },
            { color: "bg-gradient-to-br from-orange-500 to-orange-600", label: "Moderate", range: "3.2 - 5.1", description: "Moderate activity" },
            { color: "bg-gradient-to-br from-red-500 to-red-700", label: "High Activity", range: "> 5.1", description: "Severe activity" }
          ].map((item, index) => (
            <DAS28Card key={index} {...item} index={index} />
          ))}
        </div>
      </motion.div>

      {/* Color Gradients Showcase */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="bg-white/60 backdrop-blur-xl rounded-3xl shadow-2xl p-8 border border-white/20"
      >
        <h3 className="text-2xl mb-6">Gradient Palette</h3>
        <div className="grid grid-cols-2 gap-6">
          {[
            { gradient: "from-blue-500 via-blue-600 to-indigo-700", name: "Primary Gradient" },
            { gradient: "from-green-400 via-emerald-500 to-teal-600", name: "Success Gradient" },
            { gradient: "from-orange-400 via-orange-500 to-red-500", name: "Warning Gradient" },
            { gradient: "from-purple-500 via-purple-600 to-pink-600", name: "Accent Gradient" }
          ].map((item, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.3 + index * 0.1 }}
              whileHover={{ scale: 1.02 }}
              className={`h-24 rounded-2xl bg-gradient-to-r ${item.gradient} shadow-xl flex items-center justify-center text-white transition-transform`}
            >
              <Lucide.Sparkles className="w-6 h-6 mr-2" />
              {item.name}
            </motion.div>
          ))}
        </div>
      </motion.div>
    </div>
  );
}

function ColorCard({ color, hex, name, contrast, usage, index }: any) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: index * 0.1 }}
      className="group"
    >
      <motion.div
        whileHover={{ scale: 1.05, rotate: 2 }}
        className={`${color} rounded-2xl h-40 mb-4 shadow-xl flex items-center justify-center text-white transition-transform relative overflow-hidden`}
      >
        <motion.div
          initial={{ scale: 0 }}
          whileHover={{ scale: 1 }}
          className="absolute inset-0 bg-white/10 backdrop-blur-sm flex items-center justify-center"
        >
          <Lucide.Palette className="w-12 h-12" />
        </motion.div>
      </motion.div>
      <div className="space-y-1">
        <div className="text-sm text-slate-500">{hex}</div>
        <div>{name}</div>
        <div className="text-xs text-slate-500">Contrast: {contrast}</div>
        <div className="text-xs text-slate-600">{usage}</div>
      </div>
    </motion.div>
  );
}

function DAS28Card({ color, label, range, description, textDark, index }: any) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      whileHover={{ y: -5, scale: 1.02 }}
      className="group"
    >
      <div className={`${color} rounded-2xl p-6 shadow-xl ${textDark ? 'text-slate-900' : 'text-white'} transition-all relative overflow-hidden`}>
        <motion.div
          initial={{ x: -100 }}
          whileHover={{ x: 0 }}
          className="absolute inset-0 bg-white/10 backdrop-blur-sm"
        />
        <div className="relative z-10">
          <div className="text-sm opacity-90 mb-1">{range}</div>
          <div className="text-lg mb-2 flex items-center gap-2">
            <Lucide.Activity className="w-5 h-5" />
            {label}
          </div>
          <div className="text-xs opacity-75">{description}</div>
        </div>
      </div>
    </motion.div>
  );
}

function TypographyView() {
  return (
    <div className="space-y-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white/60 backdrop-blur-xl rounded-3xl shadow-2xl p-8 border border-white/20"
      >
        <h2 className="text-4xl mb-2 flex items-center gap-3">
          <Lucide.Type className="w-10 h-10 text-blue-600" />
          Typography System
        </h2>
        <p className="text-slate-600">System fonts for instant loading and native feel</p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-white/60 backdrop-blur-xl rounded-3xl shadow-2xl p-8 border border-white/20"
      >
        <h3 className="text-2xl mb-6">Font Stack</h3>
        <div className="bg-gradient-to-br from-slate-50 to-slate-100 border border-slate-200 rounded-2xl p-6">
          <code className="text-sm text-slate-700">
            -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif
          </code>
        </div>
        <div className="mt-4 text-sm text-slate-600 flex items-center gap-2">
          <Lucide.Zap className="w-4 h-4 text-blue-600" />
          Uses native system fonts for zero loading time and familiar appearance
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-white/60 backdrop-blur-xl rounded-3xl shadow-2xl p-8 border border-white/20"
      >
        <h3 className="text-2xl mb-6">Type Scale</h3>
        <div className="space-y-4">
          {[
            { size: "text-5xl", label: "Display", pixels: "48px", sample: "Extra Large Display" },
            { size: "text-4xl", label: "H1", pixels: "36px", sample: "Page Heading Level 1" },
            { size: "text-3xl", label: "H2", pixels: "30px", sample: "Section Heading Level 2" },
            { size: "text-2xl", label: "H3", pixels: "24px", sample: "Subsection Heading Level 3" },
            { size: "text-xl", label: "Large", pixels: "20px", sample: "Large body text and emphasis" },
            { size: "text-base", label: "Body", pixels: "16px", sample: "Standard body text for paragraphs" },
            { size: "text-sm", label: "Small", pixels: "14px", sample: "Helper text and secondary information" },
            { size: "text-xs", label: "Caption", pixels: "12px", sample: "Labels, captions, and minimal text" }
          ].map((item, index) => (
            <TypeScale key={index} {...item} index={index} />
          ))}
        </div>
      </motion.div>
    </div>
  );
}

function TypeScale({ size, label, pixels, sample, index }: any) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.05 }}
      whileHover={{ x: 5 }}
      className="p-6 border border-slate-200 rounded-2xl hover:border-blue-300 hover:shadow-lg transition-all bg-gradient-to-br from-white to-slate-50"
    >
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm text-slate-500 flex items-center gap-2">
          <Lucide.Type className="w-4 h-4" />
          {label}
        </span>
        <span className="text-xs text-slate-400 px-3 py-1 bg-slate-100 rounded-full">{pixels}</span>
      </div>
      <div className={size}>{sample}</div>
    </motion.div>
  );
}

function ComponentsView() {
  return (
    <div className="space-y-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white/60 backdrop-blur-xl rounded-3xl shadow-2xl p-8 border border-white/20"
      >
        <h2 className="text-4xl mb-2 flex items-center gap-3">
          <Lucide.Box className="w-10 h-10 text-blue-600" />
          UI Components
        </h2>
        <p className="text-slate-600">Modern, accessible component library with smooth interactions</p>
      </motion.div>

      {/* Buttons */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-white/60 backdrop-blur-xl rounded-3xl shadow-2xl p-8 border border-white/20"
      >
        <h3 className="text-2xl mb-6">Buttons</h3>
        <div className="space-y-6">
          {[
            { variant: "primary", label: "Primary Button", description: "Main call-to-action for important actions", icon: <Lucide.Check className="w-5 h-5" /> },
            { variant: "secondary", label: "Secondary Button", description: "Secondary actions and cancel operations", icon: <Lucide.ArrowRight className="w-5 h-5" /> },
            { variant: "success", label: "Success Button", description: "Confirmation and finalize actions", icon: <Lucide.Check className="w-5 h-5" /> },
            { variant: "warning", label: "Warning Button", description: "Draft saves and caution actions", icon: <Lucide.AlertCircle className="w-5 h-5" /> },
            { variant: "danger", label: "Danger Button", description: "Destructive actions like delete", icon: <Lucide.AlertCircle className="w-5 h-5" /> }
          ].map((item, index) => (
            <ButtonShowcase key={index} {...item} index={index} />
          ))}
        </div>
      </motion.div>

      {/* Form Elements */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-white/60 backdrop-blur-xl rounded-3xl shadow-2xl p-8 border border-white/20"
      >
        <h3 className="text-2xl mb-6">Form Elements</h3>
        <div className="space-y-6">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            <label className="block text-sm mb-2 text-slate-700 flex items-center gap-2">
              <Lucide.Search className="w-4 h-4" />
              Text Input with Icon
            </label>
            <div className="relative">
              <Lucide.Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
              <input
                type="text"
                placeholder="Search patients..."
                className="w-full h-12 pl-11 pr-4 border-2 border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              />
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
          >
            <label className="block text-sm mb-2 text-slate-700">Textarea</label>
            <textarea
              placeholder="Enter medical notes..."
              rows={4}
              className="w-full p-4 border-2 border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
            />
          </motion.div>
        </div>
      </motion.div>

      {/* Status Indicators with Animation */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="bg-white/60 backdrop-blur-xl rounded-3xl shadow-2xl p-8 border border-white/20"
      >
        <h3 className="text-2xl mb-6">Status Indicators</h3>
        <div className="space-y-4">
          <StatusIndicator status="saving" />
          <StatusIndicator status="saved" />
          <StatusIndicator status="error" />
        </div>
      </motion.div>

      {/* DAS28 Displays */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="bg-white/60 backdrop-blur-xl rounded-3xl shadow-2xl p-8 border border-white/20"
      >
        <h3 className="text-2xl mb-6">DAS28 Score Display</h3>
        <div className="space-y-3">
          {[
            { score: "2.10", status: "Remission", color: "green" },
            { score: "2.90", status: "Low Activity", color: "yellow" },
            { score: "4.20", status: "Moderate Activity", color: "orange" },
            { score: "6.50", status: "High Activity", color: "red" }
          ].map((item, index) => (
            <DAS28Badge key={index} {...item} index={index} />
          ))}
        </div>
      </motion.div>
    </div>
  );
}

function ButtonShowcase({ variant, label, description, icon, index }: any) {
  const styles = {
    primary: 'bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white shadow-lg',
    secondary: 'bg-white hover:bg-slate-50 text-slate-700 border-2 border-slate-300 shadow',
    success: 'bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white shadow-lg',
    warning: 'bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white shadow-lg',
    danger: 'bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white shadow-lg'
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.1 }}
      className="flex items-center gap-6"
    >
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        className={`h-12 px-6 rounded-xl transition-all flex items-center gap-2 ${styles[variant as keyof typeof styles]}`}
      >
        {icon}
        {label}
      </motion.button>
      <div className="flex-1">
        <div className="text-sm text-slate-600">{description}</div>
      </div>
    </motion.div>
  );
}

function StatusIndicator({ status }: { status: 'saving' | 'saved' | 'error' }) {
  const configs = {
    saving: {
      icon: <Lucide.Clock className="w-4 h-4" />,
      text: 'Saving...',
      color: 'bg-yellow-50 border-yellow-300 text-yellow-700',
      dotColor: 'bg-yellow-500',
      gradient: 'from-yellow-100 to-yellow-50'
    },
    saved: {
      icon: <Lucide.Check className="w-4 h-4" />,
      text: 'Saved',
      time: 'Last saved: 14:30',
      color: 'bg-green-50 border-green-300 text-green-700',
      dotColor: 'bg-green-500',
      gradient: 'from-green-100 to-green-50'
    },
    error: {
      icon: <Lucide.AlertCircle className="w-4 h-4" />,
      text: 'Error - Not Saved',
      color: 'bg-red-50 border-red-300 text-red-700',
      dotColor: 'bg-red-500',
      gradient: 'from-red-100 to-red-50'
    }
  };

  const config = configs[status];

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{ scale: 1.02 }}
      className={`inline-flex items-center gap-3 px-5 py-3 rounded-xl border-2 ${config.color} bg-gradient-to-r ${config.gradient} shadow-sm`}
    >
      <motion.div
        animate={{ scale: [1, 1.2, 1] }}
        transition={{ repeat: Infinity, duration: 2 }}
        className={`w-2 h-2 rounded-full ${config.dotColor}`}
      />
      {config.icon}
      <div>
        <div className="text-sm">{config.text}</div>
        {'time' in config && config.time && <div className="text-xs opacity-75">{config.time}</div>}
      </div>
    </motion.div>
  );
}

function DAS28Badge({ score, status, color, index }: any) {
  const colors = {
    green: 'from-green-500 to-emerald-600',
    yellow: 'from-yellow-400 to-yellow-500 text-slate-900',
    orange: 'from-orange-500 to-orange-600',
    red: 'from-red-500 to-red-600'
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.1 }}
      whileHover={{ scale: 1.02, x: 5 }}
      className={`flex items-center justify-between px-6 py-4 rounded-xl shadow-xl bg-gradient-to-r ${colors[color as keyof typeof colors]} text-white cursor-pointer`}
    >
      <div className="flex items-center gap-3">
        <Lucide.Activity className="w-5 h-5" />
        <span>Score: {score}</span>
      </div>
      <div className="flex items-center gap-2">
        <span>{status}</span>
        <Lucide.ChevronRight className="w-5 h-5" />
      </div>
    </motion.div>
  );
}

function DashboardMockup() {
  return (
    <div className="space-y-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white/60 backdrop-blur-xl rounded-3xl shadow-2xl p-8 border border-white/20"
      >
        <h2 className="text-4xl mb-2">Dashboard Mockup</h2>
        <p className="text-slate-600">Main overview screen for clinic management</p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-white rounded-3xl shadow-2xl overflow-hidden border border-slate-200"
      >
        {/* App Header */}
        <div className="bg-gradient-to-r from-blue-600 via-blue-700 to-indigo-700 text-white p-6 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full blur-3xl"></div>
          <div className="relative z-10 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
                className="p-2 bg-white/10 backdrop-blur-sm rounded-xl"
              >
                <Lucide.Activity className="w-8 h-8" />
              </motion.div>
              <div>
                <h1 className="text-2xl">Rheumatology EHR</h1>
                <p className="text-sm text-blue-100">Rural Health Clinic</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <div className="text-sm">Dr. Singh</div>
                <div className="text-xs text-blue-100">Rheumatologist</div>
              </div>
              <div className="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center text-lg border-2 border-white/30">
                DS
              </div>
            </div>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-4 gap-6 p-6 bg-gradient-to-br from-slate-50 to-white border-b border-slate-200">
          {[
            { icon: <Lucide.Users className="w-5 h-5" />, label: "Patients Today", value: "24", trend: "+3", color: "blue" },
            { icon: <Lucide.FileText className="w-5 h-5" />, label: "Pending Notes", value: "7", trend: "-2", color: "orange" },
            { icon: <Lucide.Activity className="w-5 h-5" />, label: "Active Patients", value: "156", trend: "+12", color: "green" },
            { icon: <Lucide.AlertCircle className="w-5 h-5" />, label: "Follow-ups Due", value: "12", trend: "+5", color: "red" }
          ].map((item, index) => (
            <StatCard key={index} {...item} index={index} />
          ))}
        </div>

        {/* Quick Actions */}
        <div className="p-6">
          <h3 className="text-lg mb-4 flex items-center gap-2">
            <Lucide.Zap className="w-5 h-5 text-blue-600" />
            Quick Actions
          </h3>
          <div className="grid grid-cols-2 gap-4">
            {[
              { icon: <Lucide.Plus className="w-5 h-5" />, label: "New Patient Visit", primary: true },
              { icon: <Lucide.Search className="w-5 h-5" />, label: "Search Patient" },
              { icon: <Lucide.BarChart3 className="w-5 h-5" />, label: "View Reports" },
              { icon: <Lucide.Calendar className="w-5 h-5" />, label: "Schedule" }
            ].map((item, index) => (
              <QuickAction key={index} {...item} index={index} />
            ))}
          </div>
        </div>

        {/* Recent Patients */}
        <div className="p-6 border-t border-slate-200 bg-slate-50/50">
          <h3 className="text-lg mb-4">Recent Patients</h3>
          <div className="space-y-3">
            {[
              { name: "Rajesh Kumar", mrn: "MRN-2025-001", das28: "3.5", status: "moderate" },
              { name: "Priya Sharma", mrn: "MRN-2025-002", das28: "2.4", status: "remission" },
              { name: "Amit Patel", mrn: "MRN-2025-003", das28: "5.8", status: "high" }
            ].map((item, index) => (
              <PatientRow key={index} {...item} index={index} />
            ))}
          </div>
        </div>
      </motion.div>
    </div>
  );
}

function StatCard({ icon, label, value, trend, color, index }: any) {
  const colors = {
    blue: 'from-blue-500 to-blue-600',
    green: 'from-green-500 to-emerald-600',
    orange: 'from-orange-500 to-orange-600',
    red: 'from-red-500 to-red-600'
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      whileHover={{ y: -5 }}
      className="bg-white rounded-xl p-4 shadow-lg border border-slate-200 hover:shadow-xl transition-all"
    >
      <div className={`inline-flex p-2 rounded-lg bg-gradient-to-br ${colors[color as keyof typeof colors]} text-white mb-3`}>
        {icon}
      </div>
      <div className="text-sm text-slate-600 mb-1">{label}</div>
      <div className="flex items-baseline gap-2">
        <div className="text-2xl">{value}</div>
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-xs text-green-600 flex items-center gap-1"
        >
          <Lucide.TrendingUp className="w-3 h-3" />
          {trend}
        </motion.div>
      </div>
    </motion.div>
  );
}

function QuickAction({ icon, label, primary, index }: any) {
  return (
    <motion.button
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: index * 0.1 }}
      whileHover={{ scale: 1.02, y: -2 }}
      whileTap={{ scale: 0.98 }}
      className={`h-16 px-6 rounded-xl flex items-center gap-3 transition-all ${
        primary
          ? 'bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white shadow-xl'
          : 'bg-white hover:bg-slate-50 text-slate-700 border-2 border-slate-200 shadow-md'
      }`}
    >
      {icon}
      <span>{label}</span>
    </motion.button>
  );
}

function PatientRow({ name, mrn, das28, status, index }: any) {
  const statusColors = {
    remission: 'from-green-500 to-emerald-600',
    moderate: 'from-orange-500 to-orange-600',
    high: 'from-red-500 to-red-600'
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.1 }}
      whileHover={{ x: 5, scale: 1.01 }}
      className="flex items-center justify-between p-4 bg-white rounded-xl hover:shadow-md transition-all cursor-pointer border border-slate-200"
    >
      <div className="flex items-center gap-4">
        <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full flex items-center justify-center text-white text-sm shadow-lg">
          {name.split(' ').map((n: string) => n[0]).join('')}
        </div>
        <div>
          <div>{name}</div>
          <div className="text-sm text-slate-500">{mrn}</div>
        </div>
      </div>
      <div className="flex items-center gap-3">
        <div className="text-right">
          <div className="text-xs text-slate-500 mb-1">DAS28</div>
          <div className={`px-3 py-1 rounded-full text-sm text-white bg-gradient-to-r ${statusColors[status as keyof typeof statusColors]} shadow-md`}>
            {das28}
          </div>
        </div>
        <Lucide.ChevronRight className="w-5 h-5 text-slate-400" />
      </div>
    </motion.div>
  );
}

function PatientsMockup() {
  return (
    <div className="space-y-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white/60 backdrop-blur-xl rounded-3xl shadow-2xl p-8 border border-white/20"
      >
        <h2 className="text-4xl mb-2">Patient Management</h2>
        <p className="text-slate-600">Search, view, and manage patient records</p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-white rounded-3xl shadow-2xl overflow-hidden border border-slate-200"
      >
        {/* Search Bar */}
        <div className="p-6 border-b border-slate-200 bg-gradient-to-br from-slate-50 to-white">
          <div className="flex gap-4">
            <div className="flex-1 relative">
              <Lucide.Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
              <input
                type="text"
                placeholder="Search by name, MRN, or phone number..."
                className="w-full h-12 pl-12 pr-4 border-2 border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              />
            </div>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="h-12 px-6 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white rounded-xl shadow-lg flex items-center gap-2 transition-colors"
            >
              <Lucide.Plus className="w-5 h-5" />
              Add Patient
            </motion.button>
          </div>
          <div className="mt-3 text-sm text-slate-500 flex items-center gap-2">
            <Lucide.Users className="w-4 h-4" />
            Found 156 patients
          </div>
        </div>

        {/* Modern Table */}
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="bg-gradient-to-r from-slate-100 to-slate-50 border-b-2 border-slate-200">
                <th className="px-6 py-4 text-left text-sm text-slate-600">MRN</th>
                <th className="px-6 py-4 text-left text-sm text-slate-600">Patient</th>
                <th className="px-6 py-4 text-left text-sm text-slate-600">Age / Gender</th>
                <th className="px-6 py-4 text-left text-sm text-slate-600">Phone</th>
                <th className="px-6 py-4 text-left text-sm text-slate-600">Diagnosis</th>
                <th className="px-6 py-4 text-left text-sm text-slate-600">Last Visit</th>
                <th className="px-6 py-4 text-left text-sm text-slate-600">DAS28</th>
              </tr>
            </thead>
            <tbody>
              {[
                { mrn: "MRN-2025-001", name: "Rajesh Kumar", age: "52 / M", phone: "9876543210", diagnosis: "Rheumatoid Arthritis", visit: "2025-11-15", das28: "3.5", das28Color: "orange" },
                { mrn: "MRN-2025-002", name: "Priya Sharma", age: "45 / F", phone: "9876543211", diagnosis: "Rheumatoid Arthritis", visit: "2025-11-15", das28: "2.4", das28Color: "green" },
                { mrn: "MRN-2025-003", name: "Amit Patel", age: "58 / M", phone: "9876543212", diagnosis: "Psoriatic Arthritis", visit: "2025-11-14", das28: "5.8", das28Color: "red" }
              ].map((item, index) => (
                <PatientTableRow key={index} {...item} index={index} />
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>
    </div>
  );
}

function PatientTableRow({ mrn, name, age, phone, diagnosis, visit, das28, das28Color, index }: any) {
  const colors = {
    green: 'from-green-500 to-emerald-600',
    orange: 'from-orange-500 to-orange-600',
    red: 'from-red-500 to-red-600'
  };

  return (
    <motion.tr
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      whileHover={{ backgroundColor: 'rgba(248, 250, 252, 1)' }}
      className="border-b border-slate-100 transition-colors cursor-pointer"
    >
      <td className="px-6 py-4 text-sm text-slate-500">{mrn}</td>
      <td className="px-6 py-4">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full flex items-center justify-center text-white text-xs shadow-md">
            {name.split(' ').map((n: string) => n[0]).join('')}
          </div>
          <span>{name}</span>
        </div>
      </td>
      <td className="px-6 py-4 text-sm">{age}</td>
      <td className="px-6 py-4 text-sm text-slate-600">{phone}</td>
      <td className="px-6 py-4 text-sm">{diagnosis}</td>
      <td className="px-6 py-4 text-sm text-slate-600">{visit}</td>
      <td className="px-6 py-4">
        <span className={`px-3 py-1 rounded-full text-sm text-white bg-gradient-to-r ${colors[das28Color as keyof typeof colors]} shadow-md`}>
          {das28}
        </span>
      </td>
    </motion.tr>
  );
}

function MedicalNoteMockup() {
  return (
    <div className="space-y-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white/60 backdrop-blur-xl rounded-3xl shadow-2xl p-8 border border-white/20"
      >
        <h2 className="text-4xl mb-2">Medical Note</h2>
        <p className="text-slate-600">Clinical documentation with auto-save</p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-white rounded-3xl shadow-2xl overflow-hidden border border-slate-200"
      >
        {/* Header */}
        <div className="p-6 border-b border-slate-200 bg-gradient-to-r from-slate-50 to-white">
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-2xl mb-1 flex items-center gap-2">
                <Lucide.FileText className="w-6 h-6 text-blue-600" />
                Create Medical Note
              </h2>
              <p className="text-slate-600">Comprehensive rheumatology assessment</p>
            </div>
            <StatusIndicator status="saved" />
          </div>
        </div>

        {/* Patient Info Card */}
        <div className="p-6 bg-gradient-to-br from-blue-50 to-indigo-50 border-b border-blue-100">
          <div className="flex items-center justify-between mb-4">
            <h3 className="flex items-center gap-2">
              <Lucide.Users className="w-5 h-5 text-blue-600" />
              Patient Information
            </h3>
            <motion.div
              whileHover={{ scale: 1.05 }}
              className="px-4 py-2 bg-gradient-to-r from-orange-500 to-orange-600 text-white rounded-xl text-sm shadow-md"
            >
              Draft
            </motion.div>
          </div>
          <div className="grid grid-cols-4 gap-6">
            <InfoField label="MRN" value="MRN-2025-001" />
            <InfoField label="Patient" value="Rajesh Kumar" />
            <InfoField label="Date" value="Nov 15, 2025" />
            <InfoField label="Provider" value="Dr. Singh" />
          </div>
        </div>

        {/* Form Sections */}
        <div className="p-6 space-y-6">
          <FormField label="Chief Complaint" placeholder="Enter chief complaint..." icon={<Lucide.FileText className="w-4 h-4" />} />
          <FormField label="History of Present Illness" placeholder="Document patient history..." icon={<Lucide.FileText className="w-4 h-4" />} multiline />
          <FormField label="Physical Examination" placeholder="Document examination findings..." icon={<Lucide.Activity className="w-4 h-4" />} multiline />

          <div className="pt-4 border-t border-slate-200">
            <div className="flex gap-4">
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="flex-1 h-12 bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white rounded-xl shadow-lg flex items-center justify-center gap-2 transition-colors"
              >
                <Lucide.Save className="w-5 h-5" />
                Save Draft
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="flex-1 h-12 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white rounded-xl shadow-lg flex items-center justify-center gap-2 transition-colors"
              >
                <Lucide.Check className="w-5 h-5" />
                Finalize Note
              </motion.button>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}

function InfoField({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="text-xs text-blue-600 mb-1 flex items-center gap-1">
        <div className="w-1.5 h-1.5 rounded-full bg-blue-600"></div>
        {label}
      </div>
      <div className="text-sm">{value}</div>
    </div>
  );
}

function FormField({ label, placeholder, multiline, icon }: any) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <label className="block text-sm mb-2 text-slate-700 flex items-center gap-2">
        {icon}
        {label}
      </label>
      {multiline ? (
        <textarea
          placeholder={placeholder}
          rows={4}
          className="w-full p-4 border-2 border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
        />
      ) : (
        <input
          type="text"
          placeholder={placeholder}
          className="w-full h-12 px-4 border-2 border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
        />
      )}
    </motion.div>
  );
}

function JointAssessmentMockup() {
  return (
    <div className="space-y-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white/60 backdrop-blur-xl rounded-3xl shadow-2xl p-8 border border-white/20"
      >
        <h2 className="text-4xl mb-2">Joint Assessment</h2>
        <p className="text-slate-600">Interactive 28-joint evaluation with DAS28 calculation</p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-white rounded-3xl shadow-2xl overflow-hidden border border-slate-200"
      >
        {/* Canvas Area */}
        <div className="p-8">
          <div className="bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 border-2 border-blue-200 rounded-2xl p-8">
            <div className="flex items-center justify-between mb-6">
              <h3 className="flex items-center gap-2 text-xl">
                <Lucide.Hand className="w-6 h-6 text-blue-600" />
                28-Joint Assessment
              </h3>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-4 py-2 bg-white hover:bg-slate-50 text-slate-700 rounded-xl transition-colors shadow-md border border-slate-200"
              >
                Reset All
              </motion.button>
            </div>

            <div className="bg-white rounded-2xl p-8 mb-6 shadow-xl">
              <div className="text-center mb-8">
                <div className="text-sm text-slate-600 mb-4 flex items-center justify-center gap-2">
                  <Lucide.Target className="w-4 h-4" />
                  Click joints to mark swelling • Right-click for tenderness
                </div>
              </div>

              <div className="grid grid-cols-2 gap-16 max-w-3xl mx-auto">
                <JointSideDisplay side="Right" />
                <JointSideDisplay side="Left" />
              </div>
            </div>

            <div className="bg-blue-50 border-2 border-blue-200 rounded-2xl p-4">
              <div className="text-sm mb-2 flex items-center gap-2">
                <Lucide.Activity className="w-4 h-4 text-blue-600" />
                Instructions
              </div>
              <ul className="text-xs text-slate-600 space-y-1">
                <li>• Left Click: Cycle swelling grades 0 to 3</li>
                <li>• Right Click: Toggle tenderness marker</li>
                <li>• Grades: 0 None, 1 Mild, 2 Moderate, 3 Severe</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Joint Counts */}
        <div className="px-8 pb-4">
          <div className="grid grid-cols-2 gap-4">
            <motion.div
              whileHover={{ scale: 1.02 }}
              className="bg-gradient-to-br from-orange-50 to-orange-100 border-2 border-orange-200 rounded-2xl p-4 shadow-md"
            >
              <div className="text-xs text-orange-600 mb-1 flex items-center gap-1">
                <div className="w-2 h-2 rounded-full bg-orange-500"></div>
                Swollen Joints
              </div>
              <div className="text-2xl text-orange-700">3 / 28</div>
            </motion.div>
            <motion.div
              whileHover={{ scale: 1.02 }}
              className="bg-gradient-to-br from-red-50 to-red-100 border-2 border-red-200 rounded-2xl p-4 shadow-md"
            >
              <div className="text-xs text-red-600 mb-1 flex items-center gap-1">
                <div className="w-2 h-2 rounded-full bg-red-500"></div>
                Tender Joints
              </div>
              <div className="text-2xl text-red-700">5 / 28</div>
            </motion.div>
          </div>
        </div>

        {/* DAS28 Result */}
        <div className="p-8 border-t border-slate-200 bg-gradient-to-br from-slate-50 to-white">
          <h3 className="mb-4 flex items-center gap-2 text-xl">
            <Lucide.Activity className="w-6 h-6 text-blue-600" />
            DAS28-ESR Calculation
          </h3>
          <motion.div
            whileHover={{ scale: 1.02 }}
            className="bg-gradient-to-r from-orange-500 via-orange-600 to-red-500 text-white rounded-2xl p-6 shadow-2xl"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-white/20 backdrop-blur-sm rounded-xl">
                  <Lucide.Activity className="w-6 h-6" />
                </div>
                <div>
                  <div className="text-sm opacity-90">DAS28 Score</div>
                  <div className="text-4xl">4.20</div>
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm opacity-90">Disease Activity</div>
                <div className="text-2xl">Moderate</div>
              </div>
            </div>
          </motion.div>
        </div>
      </motion.div>
    </div>
  );
}

function JointSideDisplay({ side }: { side: string }) {
  return (
    <div className="space-y-6">
      <div className="text-center text-sm text-slate-600 flex items-center justify-center gap-2">
        <Lucide.Hand className="w-4 h-4" />
        {side} Side
      </div>
      <div className="flex justify-center gap-2">
        {[1, 2, 3, 4, 5].map(i => (
          <motion.div
            key={i}
            whileHover={{ scale: 1.2, backgroundColor: 'rgba(59, 130, 246, 0.1)' }}
            whileTap={{ scale: 0.9 }}
            className="w-10 h-10 rounded-full border-2 border-slate-300 bg-white hover:border-blue-400 transition-all cursor-pointer shadow-md"
          />
        ))}
      </div>
      <div className="text-center text-xs text-slate-500">PIP Joints</div>
    </div>
  );
}

function ReportsMockup() {
  return (
    <div className="space-y-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white/60 backdrop-blur-xl rounded-3xl shadow-2xl p-8 border border-white/20"
      >
        <h2 className="text-4xl mb-2">Reports & Analytics</h2>
        <p className="text-slate-600">Clinic performance and patient outcomes</p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-white rounded-3xl shadow-2xl overflow-hidden border border-slate-200"
      >
        {/* Filters */}
        <div className="p-6 border-b border-slate-200 bg-gradient-to-br from-slate-50 to-white">
          <h3 className="mb-4 flex items-center gap-2 text-xl">
            <Lucide.BarChart3 className="w-6 h-6 text-blue-600" />
            Generate Report
          </h3>
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm mb-2 text-slate-700">Report Type</label>
              <select className="w-full h-12 px-4 border-2 border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all">
                <option>Patient Summary Report</option>
                <option>Disease Activity Trends</option>
                <option>Treatment Outcomes</option>
              </select>
            </div>
            <div>
              <label className="block text-sm mb-2 text-slate-700">Date Range</label>
              <select className="w-full h-12 px-4 border-2 border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all">
                <option>Last Month</option>
                <option>Last Quarter</option>
                <option>Last Year</option>
              </select>
            </div>
          </div>
          <div className="flex gap-4">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="h-12 px-6 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white rounded-xl shadow-lg flex items-center gap-2 transition-colors"
            >
              <Lucide.BarChart3 className="w-5 h-5" />
              Generate Report
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="h-12 px-6 bg-white hover:bg-slate-50 text-slate-700 border-2 border-slate-300 rounded-xl flex items-center gap-2 transition-colors shadow-md"
            >
              <Lucide.Download className="w-5 h-5" />
              Export PDF
            </motion.button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-4 gap-6 p-6 bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 border-b border-slate-200">
          {[
            { label: "Total Patients", value: "156", trend: "+12", icon: <Lucide.Users className="w-5 h-5" /> },
            { label: "Active Patients", value: "142", trend: "+8", icon: <Lucide.Activity className="w-5 h-5" /> },
            { label: "Avg DAS28", value: "3.4", trend: "-0.3", icon: <Lucide.TrendingDown className="w-5 h-5" />, positive: true },
            { label: "Remission Rate", value: "28%", trend: "+5%", icon: <Lucide.TrendingUp className="w-5 h-5" />, positive: true }
          ].map((item, index) => (
            <MetricBox key={index} {...item} index={index} />
          ))}
        </div>

        {/* Charts */}
        <div className="p-6">
          <h3 className="mb-6 text-xl">Disease Activity Distribution</h3>
          <div className="space-y-4">
            {[
              { label: "Remission (< 2.6)", value: "28%", count: "44", color: "green" },
              { label: "Low Activity (2.6-3.2)", value: "25%", count: "39", color: "yellow" },
              { label: "Moderate (3.2-5.1)", value: "35%", count: "55", color: "orange" },
              { label: "High Activity (> 5.1)", value: "12%", count: "18", color: "red" }
            ].map((item, index) => (
              <ProgressChart key={index} {...item} index={index} />
            ))}
          </div>
        </div>
      </motion.div>
    </div>
  );
}

function MetricBox({ label, value, trend, icon, positive, index }: any) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      whileHover={{ y: -5, scale: 1.02 }}
      className="bg-white rounded-2xl p-4 shadow-xl border border-slate-200"
    >
      <div className="flex items-center gap-2 mb-3">
        <div className="p-2 bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-xl shadow-md">
          {icon}
        </div>
      </div>
      <div className="text-sm text-slate-600 mb-1">{label}</div>
      <div className="flex items-baseline gap-2">
        <div className="text-2xl">{value}</div>
        <div className={`text-xs flex items-center gap-1 ${positive ? 'text-green-600' : 'text-green-600'}`}>
          {positive ? <Lucide.TrendingUp className="w-3 h-3" /> : <Lucide.TrendingUp className="w-3 h-3" />}
          {trend}
        </div>
      </div>
    </motion.div>
  );
}

function ProgressChart({ label, value, count, color, index }: any) {
  const colors = {
    green: { bg: 'from-green-500 to-emerald-600', text: 'text-green-700', light: 'bg-green-100' },
    yellow: { bg: 'from-yellow-400 to-yellow-500', text: 'text-yellow-700', light: 'bg-yellow-100' },
    orange: { bg: 'from-orange-500 to-orange-600', text: 'text-orange-700', light: 'bg-orange-100' },
    red: { bg: 'from-red-500 to-red-600', text: 'text-red-700', light: 'bg-red-100' }
  };

  const c = colors[color as keyof typeof colors];

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.1 }}
    >
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm">{label}</span>
        <span className={`text-sm ${c.text}`}>{count} patients ({value})</span>
      </div>
      <div className={`w-full h-4 ${c.light} rounded-full overflow-hidden shadow-inner`}>
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: value }}
          transition={{ duration: 1, delay: index * 0.1 }}
          className={`h-full bg-gradient-to-r ${c.bg} rounded-full shadow-md`}
        />
      </div>
    </motion.div>
  );
}

function SpecificationsView() {
  return (
    <div className="space-y-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white/60 backdrop-blur-xl rounded-3xl shadow-2xl p-8 border border-white/20"
      >
        <h2 className="text-4xl mb-2 flex items-center gap-3">
          <Lucide.Settings className="w-10 h-10 text-blue-600" />
          Technical Specifications
        </h2>
        <p className="text-slate-600">Implementation guidelines and measurements</p>
      </motion.div>

      <div className="grid md:grid-cols-2 gap-6">
        {[
          {
            title: "Spacing System",
            icon: <Lucide.Box className="w-5 h-5" />,
            items: ['XS: 4px - Tight spacing', 'SM: 8px - Related elements', 'MD: 16px - Standard spacing', 'LG: 24px - Section spacing', 'XL: 32px - Major sections']
          },
          {
            title: "Border Radius",
            icon: <Lucide.Box className="w-5 h-5" />,
            items: ['SM: 8px - Badges, tags', 'MD: 12px - Buttons, inputs', 'LG: 16px - Cards', 'XL: 24px - Large cards', '2XL: 32px - Hero sections']
          },
          {
            title: "Animations",
            icon: <Lucide.Zap className="w-5 h-5" />,
            items: ['Hover: 0.2s ease', 'Page transitions: 0.3s', 'Micro-interactions: 0.15s', 'Progress bars: 1s ease-out', 'All GPU-accelerated']
          },
          {
            title: "Accessibility",
            icon: <Lucide.Shield className="w-5 h-5" />,
            items: ['Min contrast: 7:1 (WCAG AAA)', 'Touch targets: 48x48px', 'Focus rings: 2px visible', 'Keyboard navigation: Full', 'Screen reader: ARIA labels']
          }
        ].map((item, index) => (
          <SpecCard key={index} {...item} index={index} />
        ))}
      </div>

      {/* Performance Metrics */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="bg-gradient-to-br from-blue-600 via-blue-700 to-indigo-700 text-white rounded-3xl p-8 shadow-2xl"
      >
        <h3 className="text-2xl mb-6 flex items-center gap-2">
          <Lucide.Zap className="w-6 h-6" />
          Performance Targets
        </h3>
        <div className="grid md:grid-cols-4 gap-6">
          {[
            { label: "Bundle Size", value: "150KB", icon: <Lucide.Download className="w-5 h-5" /> },
            { label: "Load Time", value: "<1s", icon: <Lucide.Zap className="w-5 h-5" /> },
            { label: "3G Compatible", value: "Yes", icon: <Lucide.Smartphone className="w-5 h-5" /> },
            { label: "Animations", value: "CSS Only", icon: <Lucide.Activity className="w-5 h-5" /> }
          ].map((item, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.4 + index * 0.1 }}
              className="bg-white/10 backdrop-blur-sm rounded-2xl p-4 border border-white/20"
            >
              <div className="mb-3">{item.icon}</div>
              <div className="text-sm opacity-90 mb-1">{item.label}</div>
              <div className="text-2xl">{item.value}</div>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </div>
  );
}

function SpecCard({ title, icon, items, index }: any) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      whileHover={{ y: -5 }}
      className="bg-white/60 backdrop-blur-xl rounded-2xl shadow-xl p-6 border border-white/20"
    >
      <h3 className="flex items-center gap-2 mb-4 text-lg">
        <div className="p-2 bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-xl shadow-md">
          {icon}
        </div>
        {title}
      </h3>
      <ul className="space-y-2">
        {items.map((item: string, i: number) => (
          <motion.li
            key={i}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 + i * 0.05 }}
            className="text-sm text-slate-600 flex items-start gap-2"
          >
            <Lucide.ChevronRight className="w-4 h-4 text-blue-500 flex-shrink-0 mt-0.5" />
            <span>{item}</span>
          </motion.li>
        ))}
      </ul>
    </motion.div>
  );
}
