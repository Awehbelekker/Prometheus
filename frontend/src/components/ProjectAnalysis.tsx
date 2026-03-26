import React, { useState } from 'react';
import './ProjectAnalysis.css';
import SearchIcon from '@mui/icons-material/Search';
import RocketLaunchIcon from '@mui/icons-material/RocketLaunch';
import SyncIcon from '@mui/icons-material/Sync';
import ErrorIcon from '@mui/icons-material/Error';

import { apiCall } from '../config/api';

interface AnalysisResult {
  success: boolean;
  analysis_type: string;
  [key: string]: any;
}

const ProjectAnalysis: React.FC = () => {
  const [projectPath, setProjectPath] = useState('');
  const [analysisType, setAnalysisType] = useState('full_project_analysis');
  const [results, setResults] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const analysisTypes = [
    { value: 'full_project_analysis', label: 'Full Project Analysis', description: 'Comprehensive analysis of all project aspects' },
    { value: 'analyze_project_structure', label: 'Project Structure', description: 'Analyze project organization and structure' },
    { value: 'analyze_dependencies', label: 'Dependencies', description: 'Analyze project dependencies and security' },
    { value: 'assess_code_quality', label: 'Code Quality', description: 'Assess overall code quality and metrics' },
    { value: 'analyze_tech_stack', label: 'Technology Stack', description: 'Analyze technology choices and architecture' },
    { value: 'recommend_architecture', label: 'Architecture Recommendations', description: 'Get architectural improvement suggestions' }
  ];

  const analyzeProject = async () => {
    if (!projectPath.trim()) {
      setError('Please enter a project path');
      return;
    }

    setLoading(true);
    setError('');
    setResults(null);

    try {
      const endpoint = analysisType === 'full_project_analysis'
        ? '/api/ai/analyze-project'
        : `/api/ai/${analysisType.replace(/_/g, '-')}`;

      const data = await apiCall(endpoint, {
        method: 'POST',
        body: JSON.stringify({
          analysis_type: analysisType,
          project_path: projectPath,
          context: {}
        }),
      });

      setResults(data);
    } catch (err) {
      setError('Failed to analyze project');
      console.error('Analysis error:', err);
    } finally {
      setLoading(false);
    }
  };

  const renderAnalysisResults = () => {
    if (!results) return null;

    return (
      <div className="analysis-results">
        <div className="results-header">
          <h3>Analysis Results</h3>
          <div className="analysis-type-badge">
            {analysisTypes.find(t => t.value === analysisType)?.label}
          </div>
        </div>

        {!results.success && (
          <div className="error-message">
            <h4>❌ Analysis Failed</h4>
            <p>{results.error}</p>
          </div>
        )}

        {results.success && (
          <div className="results-content">
            {/* Full Project Analysis */}
            {results.analysis_type === 'comprehensive' && (
              <div className="comprehensive-results">
                {results.executive_summary && (
                  <div className="executive-summary">
                    <h4>📋 Executive Summary</h4>
                    <div className="summary-content">
                      <pre>{results.executive_summary}</pre>
                    </div>
                  </div>
                )}

                {results.overall_health_score && (
                  <div className="health-score">
                    <h4>🏥 Overall Health Score</h4>
                    <div className="score-display">
                      <div className="score-circle">
                        <span className="score-number">{results.overall_health_score}</span>
                        <span className="score-label">/ 100</span>
                      </div>
                    </div>
                  </div>
                )}

                {results.analyses && (
                  <div className="sub-analyses">
                    {Object.entries(results.analyses).map(([key, analysis]: [string, any]) => (
                      <div key={key} className="sub-analysis">
                        <h4>{key.replace(/_/g, ' ').toUpperCase()}</h4>
                        {analysis.success ? (
                          <div className="analysis-summary">
                            {analysis.ai_insights && (
                              <div className="ai-insights">
                                <h5>AI Insights</h5>
                                <pre>{analysis.ai_insights}</pre>
                              </div>
                            )}
                            {analysis.recommendations && (
                              <div className="recommendations">
                                <h5>Recommendations</h5>
                                <ul>
                                  {analysis.recommendations.map((rec: string, index: number) => (
                                    <li key={index}>{rec}</li>
                                  ))}
                                </ul>
                              </div>
                            )}
                          </div>
                        ) : (
                          <div className="analysis-error">
                            <p>❌ {analysis.error}</p>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Project Structure Analysis */}
            {results.analysis_type === 'project_structure' && (
              <div className="structure-results">
                {results.ai_insights && (
                  <div className="ai-insights">
                    <h4>🔍 AI Insights</h4>
                    <pre>{results.ai_insights}</pre>
                  </div>
                )}

                {results.file_stats && (
                  <div className="file-stats">
                    <h4>📊 File Statistics</h4>
                    <div className="stats-grid">
                      <div className="stat-item">
                        <span className="stat-label">Total Files</span>
                        <span className="stat-value">{results.file_stats.total_files}</span>
                      </div>
                      <div className="stat-item">
                        <span className="stat-label">Total Lines</span>
                        <span className="stat-value">{results.file_stats.total_lines}</span>
                      </div>
                      <div className="stat-item">
                        <span className="stat-label">Avg File Size</span>
                        <span className="stat-value">{Math.round(results.file_stats.avg_file_size)} bytes</span>
                      </div>
                    </div>

                    {results.file_stats.file_types && (
                      <div className="file-types">
                        <h5>File Types</h5>
                        <div className="file-type-list">
                          {Object.entries(results.file_stats.file_types).map(([ext, count]: [string, any]) => (
                            <div key={ext} className="file-type-item">
                              <span className="file-ext">{ext || 'no extension'}</span>
                              <span className="file-count">{count}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {results.recommendations && (
                  <div className="recommendations">
                    <h4>💡 Recommendations</h4>
                    <ul>
                      {results.recommendations.map((rec: string, index: number) => (
                        <li key={index}>{rec}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {/* Dependencies Analysis */}
            {results.analysis_type === 'dependencies' && (
              <div className="dependencies-results">
                {results.analysis && (
                  <div className="ai-insights">
                    <h4>🔍 Dependency Analysis</h4>
                    <pre>{results.analysis}</pre>
                  </div>
                )}

                {results.dependencies && (
                  <div className="dependencies-breakdown">
                    <h4>📦 Dependencies Breakdown</h4>
                    {Object.entries(results.dependencies).map(([lang, deps]: [string, any]) => (
                      <div key={lang} className="lang-dependencies">
                        <h5>{lang.toUpperCase()}</h5>
                        {Array.isArray(deps) && deps.length > 0 ? (
                          <div className="deps-list">
                            {deps.map((dep: any, index: number) => (
                              <div key={index} className="dep-item">
                                <span className="dep-name">{dep.name}</span>
                                <span className="dep-version">{dep.version}</span>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <p>No {lang} dependencies found</p>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Code Quality Analysis */}
            {results.analysis_type === 'code_quality' && (
              <div className="quality-results">
                {results.quality_score && (
                  <div className="quality-score">
                    <h4>📊 Quality Score</h4>
                    <div className="score-display">
                      <div className="score-circle">
                        <span className="score-number">{results.quality_score}</span>
                        <span className="score-label">/ 100</span>
                      </div>
                    </div>
                  </div>
                )}

                {results.ai_assessment && (
                  <div className="ai-insights">
                    <h4>🔍 AI Assessment</h4>
                    <pre>{results.ai_assessment}</pre>
                  </div>
                )}

                {results.metrics && (
                  <div className="code-metrics">
                    <h4>📈 Code Metrics</h4>
                    <div className="metrics-grid">
                      <div className="metric-item">
                        <span className="metric-label">Total Functions</span>
                        <span className="metric-value">{results.metrics.total_functions}</span>
                      </div>
                      <div className="metric-item">
                        <span className="metric-label">Total Classes</span>
                        <span className="metric-value">{results.metrics.total_classes}</span>
                      </div>
                      <div className="metric-item">
                        <span className="metric-label">Avg Function Length</span>
                        <span className="metric-value">{Math.round(results.metrics.avg_function_length)} lines</span>
                      </div>
                      <div className="metric-item">
                        <span className="metric-label">Complex Functions</span>
                        <span className="metric-value">{results.metrics.complex_functions}</span>
                      </div>
                    </div>
                  </div>
                )}

                {results.issues && results.issues.length > 0 && (
                  <div className="quality-issues">
                    <h4>⚠️ Quality Issues</h4>
                    <div className="issues-list">
                      {results.issues.map((issue: any, index: number) => (
                        <div key={index} className={`issue-item severity-${issue.severity}`}>
                          <div className="issue-header">
                            <span className="issue-type">{issue.type}</span>
                            <span className="issue-severity">{issue.severity}</span>
                          </div>
                          <p className="issue-message">{issue.message}</p>
                          <div className="issue-location">
                            {issue.file}:{issue.line}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Technology Stack Analysis */}
            {results.analysis_type === 'technology_stack' && (
              <div className="tech-stack-results">
                {results.ai_analysis && (
                  <div className="ai-insights">
                    <h4>🔍 Technology Stack Analysis</h4>
                    <pre>{results.ai_analysis}</pre>
                  </div>
                )}

                {results.tech_stack && (
                  <div className="tech-breakdown">
                    <h4>🛠️ Technology Breakdown</h4>
                    {Object.entries(results.tech_stack).map(([category, items]: [string, any]) => (
                      <div key={category} className="tech-category">
                        <h5>{category.replace(/_/g, ' ').toUpperCase()}</h5>
                        {Array.isArray(items) && items.length > 0 ? (
                          <div className="tech-items">
                            {items.map((item: string, index: number) => (
                              <span key={index} className="tech-item">{item}</span>
                            ))}
                          </div>
                        ) : (
                          <p>None identified</p>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Architecture Recommendations */}
            {results.analysis_type === 'architectural_recommendations' && (
              <div className="architecture-results">
                {results.recommendations && (
                  <div className="ai-insights">
                    <h4>🏗️ Architectural Recommendations</h4>
                    <pre>{results.recommendations}</pre>
                  </div>
                )}

                {results.priority_actions && (
                  <div className="priority-actions">
                    <h4>⚡ Priority Actions</h4>
                    <ul>
                      {results.priority_actions.map((action: string, index: number) => (
                        <li key={index}>{action}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {/* Generic Results */}
            {results.recommendations && (
              <div className="generic-recommendations">
                <h4>💡 Recommendations</h4>
                <ul>
                  {results.recommendations.map((rec: string, index: number) => (
                    <li key={index}>{rec}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="project-analysis">
      <div className="analysis-header">
        <h2><SearchIcon sx={{ fontSize: 24, color: 'primary.main', mr: 1 }} /> AI Project Analysis</h2>
        <p>Get comprehensive insights about your project using AI</p>
      </div>

      <div className="analysis-form">
        <div className="form-section">
          <h3>Project Information</h3>

          <div className="form-group">
            <label>Project Path</label>
            <input
              type="text"
              value={projectPath}
              onChange={(e) => setProjectPath(e.target.value)}
              placeholder="Enter the path to your project directory"
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="analysis-type">Analysis Type</label>
            <select
              id="analysis-type"
              name="analysis-type"
              value={analysisType}
              onChange={(e) => setAnalysisType(e.target.value)}
              disabled={loading}
              aria-label="Select analysis type"
              title="Choose the type of analysis to perform"
            >
              {analysisTypes.map(type => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
            <div className="analysis-description">
              {analysisTypes.find(t => t.value === analysisType)?.description}
            </div>
          </div>

          <button
            className="analyze-btn"
            onClick={analyzeProject}
            disabled={loading || !projectPath.trim()}
          >
            {loading ? <SyncIcon sx={{ fontSize: 16, mr: 1 }} /> : <RocketLaunchIcon sx={{ fontSize: 16, mr: 1 }} />}
            {loading ? 'Analyzing...' : 'Start Analysis'}
          </button>

          {error && (
            <div className="error-message">
              <p><ErrorIcon sx={{ fontSize: 16, color: 'error.main', mr: 1 }} /> {error}</p>
            </div>
          )}
        </div>
      </div>

      {renderAnalysisResults()}
    </div>
  );
};

export default ProjectAnalysis;
