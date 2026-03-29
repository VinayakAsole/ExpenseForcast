import React, { useState } from 'react';
import { 
  LayoutDashboard, 
  ArrowUpRight, 
  ArrowDownRight, 
  Target, 
  PieChart, 
  TrendingUp, 
  Sun, 
  Moon,
  ChevronDown,
  Briefcase
} from 'lucide-react';

const Sidebar = ({ darkMode, setDarkMode }) => {
  const [investmentsOpen, setInvestmentsOpen] = useState(false);

  const menuItems = [
    { icon: <LayoutDashboard size={20} />, label: 'Dashboard', path: '/' },
    { icon: <ArrowDownRight size={20} />, label: 'Expenses', path: '/expenses' },
    { icon: <ArrowUpRight size={20} />, label: 'Income', path: '/income' },
    { icon: <Target size={20} />, label: 'Goals', path: '/goals' },
    { icon: <PieChart size={20} />, label: 'Budgets', path: '/budgets' },
    { icon: <TrendingUp size={20} />, label: 'Analytics', path: '/analytics' },
  ];

  const investmentSubtypes = [
    { label: 'Stocks', path: '/investments/stocks' },
    { label: 'Bonds/FD', path: '/investments/bonds' },
    { label: 'Real Estate', path: '/investments/real-estate' },
    { label: 'Crypto', path: '/investments/crypto' }
  ];

  return (
    <div className={`h-screen w-64 border-r transition-colors duration-300 ${darkMode ? 'bg-slate-900 border-slate-800 text-white' : 'bg-white border-slate-200 text-slate-800'}`}>
      <div className="p-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold bg-gradient-to-r from-primary-600 to-indigo-600 bg-clip-text text-transparent">ExpenWise</h1>
        <button 
          onClick={() => setDarkMode(!darkMode)}
          className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
        >
          {darkMode ? <Sun size={20} className="text-yellow-400" /> : <Moon size={20} className="text-slate-600" />}
        </button>
      </div>

      <nav className="mt-4 px-4 space-y-2">
        {menuItems.map((item) => (
          <a key={item.label} href={item.path} className="flex items-center gap-3 px-4 py-2.5 rounded-xl hover:bg-primary-50 dark:hover:bg-slate-800 transition-all group">
            <span className="text-slate-400 group-hover:text-primary-600">{item.icon}</span>
            <span className="font-medium">{item.label}</span>
          </a>
        ))}

        {/* Investments Dropdown */}
        <div className="space-y-1">
          <button 
            onClick={() => setInvestmentsOpen(!investmentsOpen)}
            className="w-full flex items-center justify-between gap-3 px-4 py-2.5 rounded-xl hover:bg-primary-50 dark:hover:bg-slate-800 transition-all group"
          >
            <div className="flex items-center gap-3">
              <span className="text-slate-400 group-hover:text-primary-600"><Briefcase size={20} /></span>
              <span className="font-medium">Investments</span>
            </div>
            <ChevronDown size={16} className={`transition-transform duration-300 ${investmentsOpen ? 'rotate-180' : ''}`} />
          </button>
          
          {investmentsOpen && (
            <div className="pl-12 space-y-1 animate-fade-in">
              {investmentSubtypes.map((sub) => (
                <a key={sub.label} href={sub.path} className="block py-2 text-sm text-slate-500 hover:text-primary-600 dark:text-slate-400 transition-colors">
                  {sub.label}
                </a>
              ))}
            </div>
          )}
        </div>
      </nav>

      <div className="absolute bottom-8 left-0 w-full px-6">
        <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-800">
          <p className="text-xs text-slate-400 uppercase tracking-widest font-bold">Pro Account</p>
          <div className="mt-2 flex items-center gap-3">
            <div className="h-8 w-8 rounded-full bg-primary-600 flex items-center justify-center text-white text-xs font-bold">JD</div>
            <div>
              <p className="text-sm font-bold">John Doe</p>
              <p className="text-[10px] text-slate-400">Premium Health</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
