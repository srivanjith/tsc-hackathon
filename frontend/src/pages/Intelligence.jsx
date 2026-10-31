import React from "react";
import EvidencePanel from "../components/EvidencePanel";

export default function Intelligence({ incidents = [], onEvidenceSubmitted }) {
  return (
    <div className="space-y-6">
      <EvidencePanel
        incidents={incidents}
        onEvidenceSubmitted={onEvidenceSubmitted}
      />
    </div>
  );
}
