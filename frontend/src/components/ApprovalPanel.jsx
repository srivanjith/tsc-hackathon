import React, { useEffect, useState } from "react";
import { History, CheckCircle, Clock, ShieldCheck, UserCheck } from "lucide-react";
import { getDecisionLogs, approveDecision } from "../services/api";

export default function ApprovalPanel() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchLogs = () => {
    setLoading(true);
    getDecisionLogs()
      .then((res) => {
        setLogs(res.data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to fetch decision logs", err);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  const handleApprove = async (logId) => {
    try {
      await approveDecision(logId);
      fetchLogs();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
        <div className="flex items-center gap-2 mb-1">
          <History className="w-5 h-5 text-[#1677D2]" />
          <h2 className="text-base font-bold text-slate-800">
            Decision Audit Trail & Human Approval Register
          </h2>
        </div>
        <p className="text-xs text-slate-500">
          Permanent, timestamped record of algorithmic recommendations, road closures, replanning events, and commander authorizations.
        </p>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-3">
        <h3 className="font-bold text-xs uppercase tracking-wide text-slate-700">
          Decision Audit Log Entries ({logs.length})
        </h3>

        {loading ? (
          <div className="text-center py-10 text-xs text-slate-400">
            Loading decision logs...
          </div>
        ) : logs.length === 0 ? (
          <div className="text-center py-10 text-xs text-slate-400">
            No decision events logged yet.
          </div>
        ) : (
          <div className="space-y-3">
            {logs.map((log) => (
              <div
                key={log.id}
                className="p-4 rounded-xl bg-[#F5F8FC] border border-slate-200 text-xs space-y-2"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-slate-900 font-mono text-[11px] px-2 py-0.5 rounded bg-slate-200">
                      #{log.id} {log.decision_type}
                    </span>
                    <span className="text-slate-400 text-[11px]">
                      {new Date(log.timestamp).toLocaleTimeString()}
                    </span>
                  </div>

                  <span
                    className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                      log.approval_status === "APPROVED" || log.approval_status === "CONFIRMED"
                        ? "bg-emerald-100 text-[#16A36A]"
                        : "bg-amber-100 text-[#F59E0B]"
                    }`}
                  >
                    {log.approval_status}
                  </span>
                </div>

                <p className="text-slate-700 font-medium">
                  {log.explanation}
                </p>

                {log.proposed_value && (
                  <div className="p-2 rounded bg-white border border-slate-200 text-[11px] font-mono text-slate-600 truncate">
                    Proposed: {log.proposed_value}
                  </div>
                )}

                {log.approval_status === "PENDING" && (
                  <div className="pt-2 flex justify-end">
                    <button
                      onClick={() => handleApprove(log.id)}
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#16A36A] text-white font-semibold hover:bg-emerald-600 transition"
                    >
                      <UserCheck className="w-3.5 h-3.5" />
                      <span>Approve Decision</span>
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
