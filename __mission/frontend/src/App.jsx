import React, { useState } from 'react';

const Card = ({ title, children, accent = "blue" }) => (
  <div className={`group relative overflow-hidden rounded-xl bg-white/5 p-6 shadow-2xl backdrop-blur-xl border border-white/10 hover:border-${accent}-500/50 transition-all duration-300 hover:-translate-y-1`}>
    <div className={`absolute inset-0 bg-gradient-to-br from-${accent}-500/10 to-purple-500/10 opacity-0 group-hover:opacity-100 transition-opacity`} />
    <div className="relative">
      <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
        <span className={`h-2 w-2 rounded-full bg-${accent}-500`} />
        {title}
      </h3>
      <div className="text-gray-300">
        {children}
      </div>
    </div>
  </div>
);

export default function App() {
  const [active, setActive] = useState(true);

  return (
    <div className="min-h-screen bg-[#0A0A0B] text-white p-8 font-sans selection:bg-purple-500/30">
      <div className="max-w-7xl mx-auto">
        <header className="flex justify-between items-center mb-12">
          <div className="flex items-center gap-4">
            <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-purple-600 to-blue-600 animate-pulse" />
            <h1 className="text-4xl font-black tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-500">
              #_MISSION
            </h1>
          </div>
          <button className="px-6 py-2 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition-colors backdrop-blur-md">
            + System Action
          </button>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <Card title="Analytics" accent="purple">
            <div className="text-4xl font-mono font-bold">98.5%</div>
            <div className="text-sm text-green-400 mt-2">System Optimal</div>
          </Card>
          
          <Card title="Active Protocols" accent="blue">
            <div className="space-y-2 mt-2">
              <div className="h-2 w-full bg-gray-800 rounded-full overflow-hidden">
                <div className="h-full bg-blue-500 w-3/4 animate-pulse" />
              </div>
              <div className="flex justify-between text-xs text-gray-500">
                <span>Processing...</span>
                <span>75%</span>
              </div>
            </div>
          </Card>

           <Card title="AI Insight" accent="green">
             <p className="italic text-sm">"The architecture suggests a scalar approach to complexity management."</p>
           </Card>
        </div>
      </div>
    </div>
  );
}
