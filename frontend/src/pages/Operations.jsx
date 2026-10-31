import React from "react";
import ResourcePanel from "../components/ResourcePanel";

export default function Operations({
  resources = [],
  shelters = [],
  assignments = [],
  onPlanGenerated,
}) {
  return (
    <div className="space-y-6">
      <ResourcePanel
        resources={resources}
        shelters={shelters}
        assignments={assignments}
        onPlanGenerated={onPlanGenerated}
      />
    </div>
  );
}
