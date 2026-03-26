import React, { useEffect, useState } from "react";
import './AuditLogViewer.css';
import { apiCall } from '../config/api';


const AuditLogViewer: React.FC = () => {
  const [logs, setLogs] = useState<any[]>([]);
  const [tenantId, setTenantId] = useState("");

  useEffect(() => {
    (async () => {
      const data = await apiCall(`/audit/logs${tenantId ? `?tenant_id=${tenantId}` : ""}`);
      setLogs(data);
    })();
  }, [tenantId]);

  return (
    <div className="audit-container">
      <h2>Audit Log Viewer</h2>
      <input
        placeholder="Filter by Tenant ID"
        value={tenantId}
        onChange={e => setTenantId(e.target.value)}
        className="audit-section"
      />
      <pre className="audit-code">
        {JSON.stringify(logs, null, 2)}
      </pre>
    </div>
  );
};

export default AuditLogViewer;
