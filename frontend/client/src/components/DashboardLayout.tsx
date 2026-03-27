import { useState } from "react";
import { Menu, X, LogOut, Settings, BarChart3 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Link } from "wouter";

interface DashboardLayoutProps {
  children: React.ReactNode;
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const navItems = [
    { label: "Dashboard", href: "/dashboard", icon: BarChart3 },
    { label: "Integrações", href: "/integrations", icon: Settings },
  ];

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <aside
        className={`${
          sidebarOpen ? "w-64" : "w-20"
        } bg-sidebar border-r border-sidebar-border transition-all duration-300 flex flex-col`}
      >
        {/* Logo */}
        <div className="h-16 border-b border-sidebar-border flex items-center justify-between px-4">
          {sidebarOpen && (
            <h1 className="text-lg font-bold text-sidebar-foreground">
              Kora Vision
            </h1>
          )}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="text-sidebar-foreground"
          >
            {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </Button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-2 py-4 space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <Link key={item.href} href={item.href} className="flex items-center gap-3 px-3 py-2 rounded-lg text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground transition-colors">
                <Icon size={20} />
                {sidebarOpen && <span className="text-sm font-medium">{item.label}</span>}
              </Link>
            );
          })}
        </nav>

        {/* User Menu */}
        <div className="border-t border-sidebar-border p-2">
          <button
            className="w-full flex items-center justify-start px-3 py-2 rounded-lg text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground transition-colors text-sm"
          >
            <LogOut size={20} />
            {sidebarOpen && <span className="ml-3">Sair</span>}
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        {/* Header */}
        <div className="h-16 border-b border-border bg-card px-6 flex items-center">
          <h2 className="text-xl font-semibold text-foreground">
            Kora Vision
          </h2>
        </div>

        {/* Content */}
        <div className="p-6">{children}</div>
      </main>
    </div>
  );
}
