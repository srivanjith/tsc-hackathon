import React from "react";

export default function StatCard({
  label,
  value,
  subtext,
  icon: Icon,
  variant = "blue",
  badge,
  onClick,
}) {
  const variantStyles = {
    blue: {
      border: "border-blue-100",
      iconBg: "bg-blue-50 text-[#1677D2]",
      valueColor: "text-slate-900",
    },
    red: {
      border: "border-red-100",
      iconBg: "bg-red-50 text-[#DC3545]",
      valueColor: "text-[#DC3545]",
    },
    amber: {
      border: "border-amber-100",
      iconBg: "bg-amber-50 text-[#F59E0B]",
      valueColor: "text-[#F59E0B]",
    },
    green: {
      border: "border-emerald-100",
      iconBg: "bg-emerald-50 text-[#16A36A]",
      valueColor: "text-[#16A36A]",
    },
    slate: {
      border: "border-slate-200",
      iconBg: "bg-slate-100 text-slate-700",
      valueColor: "text-slate-800",
    },
  };

  const current = variantStyles[variant] || variantStyles.blue;

  return (
    <div
      onClick={onClick}
      className={`bg-white rounded-xl border ${current.border} p-4 shadow-sm hover:shadow-md transition-all ${
        onClick ? "cursor-pointer hover:border-blue-300" : ""
      }`}
    >
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-semibold text-slate-500 tracking-wide uppercase">
          {label}
        </span>
        {Icon && (
          <div className={`p-2 rounded-lg ${current.iconBg}`}>
            <Icon className="w-4 h-4" />
          </div>
        )}
      </div>

      <div className="flex items-baseline justify-between">
        <div className={`text-2xl font-bold font-mono ${current.valueColor}`}>
          {value}
        </div>
        {badge && (
          <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 border border-slate-200">
            {badge}
          </span>
        )}
      </div>

      {subtext && (
        <div className="mt-1 text-[11px] text-slate-400 truncate font-medium">
          {subtext}
        </div>
      )}
    </div>
  );
}
