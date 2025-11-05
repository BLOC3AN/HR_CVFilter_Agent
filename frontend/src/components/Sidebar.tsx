import { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { apiClient } from '../services/apiClient';

interface SidebarProps {
  jobDescription: string;
  onJobDescriptionChange: (value: string) => void;
  customRules: string;
  onCustomRulesChange: (value: string) => void;
  llmModel: string;
  onLlmModelChange: (value: string) => void;
  collapsed: boolean;
  onToggleCollapse: () => void;
}

export default function Sidebar({
  jobDescription,
  onJobDescriptionChange,
  onCustomRulesChange,
  llmModel,
  onLlmModelChange,
  collapsed,
  onToggleCollapse,
}: SidebarProps) {
  const [ruleNames, setRuleNames] = useState<string[]>([]);
  const [selectedRuleName, setSelectedRuleName] = useState<string | null>(null);
  const [ruleName, setRuleName] = useState('');
  const [ruleDescription, setRuleDescription] = useState('');
  const [ruleContent, setRuleContent] = useState('');
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    loadRuleNames();
  }, []);

  const loadRuleNames = async () => {
    const response = await apiClient.getRuleNames();
    if (response.success && response.names) {
      setRuleNames(response.names);
    }
  };

  const handleRuleSelect = async (name: string) => {
    if (name === '-- Create New --') {
      setSelectedRuleName(null);
      setRuleName('');
      setRuleDescription('');
      setRuleContent('');
      onCustomRulesChange('');
      return;
    }

    const response = await apiClient.getRule(name);
    if (response.success && response.rule) {
      setSelectedRuleName(name);
      setRuleName(name);
      setRuleDescription(response.rule.description || '');
      setRuleContent(response.rule.rules);
      onCustomRulesChange(response.rule.rules);
    }
  };

  const handleCreateRule = async () => {
    if (!ruleName) {
      setMessage({ type: 'error', text: 'Please enter a rule name' });
      return;
    }
    if (!ruleContent) {
      setMessage({ type: 'error', text: 'Please enter rule content' });
      return;
    }
    if (ruleNames.includes(ruleName)) {
      setMessage({ type: 'error', text: `Rule '${ruleName}' already exists` });
      return;
    }

    const response = await apiClient.createRule(ruleName, ruleContent, ruleDescription);
    if (response.success) {
      setMessage({ type: 'success', text: `Created rule: ${ruleName}` });
      setSelectedRuleName(ruleName);
      await loadRuleNames();
      setTimeout(() => setMessage(null), 3000);
    } else {
      setMessage({ type: 'error', text: `Failed to create rule: ${response.error}` });
    }
  };

  const handleUpdateRule = async () => {
    if (!selectedRuleName) {
      setMessage({ type: 'error', text: 'Please select a rule to update' });
      return;
    }
    if (!ruleContent) {
      setMessage({ type: 'error', text: 'Please enter rule content' });
      return;
    }

    const response = await apiClient.updateRule(selectedRuleName, ruleContent, ruleDescription);
    if (response.success) {
      setMessage({ type: 'success', text: `Updated rule: ${selectedRuleName}` });
      setTimeout(() => setMessage(null), 3000);
    } else {
      setMessage({ type: 'error', text: `Failed to update rule: ${response.error}` });
    }
  };

  const handleDeleteRule = async () => {
    if (!selectedRuleName) {
      setMessage({ type: 'error', text: 'Please select a rule to delete' });
      return;
    }

    const response = await apiClient.deleteRule(selectedRuleName);
    if (response.success) {
      setMessage({ type: 'success', text: `Deleted rule: ${selectedRuleName}` });
      setSelectedRuleName(null);
      setRuleName('');
      setRuleDescription('');
      setRuleContent('');
      onCustomRulesChange('');
      await loadRuleNames();
      setTimeout(() => setMessage(null), 3000);
    } else {
      setMessage({ type: 'error', text: `Failed to delete rule: ${response.error}` });
    }
  };

  return (
    <div className="sidebar">
      <button className="sidebar-toggle" onClick={onToggleCollapse} title={collapsed ? "Expand" : "Collapse"}>
        {collapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
      </button>

      {!collapsed && (
        <>
          <div className="sidebar-section">
        <h3>Configuration</h3>
        <div className="form-group">
          <label>Select LLM Model</label>
          <select value={llmModel} onChange={(e) => onLlmModelChange(e.target.value)}>
            <option value="gemini-2.0-flash">gemini-2.0-flash</option>
            <option value="gemini-1.5-pro">gemini-1.5-pro</option>
            <option value="gemini-2.5-flash">gemini-2.5-flash</option>
          </select>
        </div>
      </div>

      <div className="sidebar-section">
        <h3>💼 Job Description</h3>
        <textarea
          className="job-description-textarea"
          value={jobDescription}
          onChange={(e) => onJobDescriptionChange(e.target.value)}
          placeholder="Paste the job description here..."
        />
      </div>

      <div className="sidebar-section">
        <h3>📋 Custom Evaluation Rules</h3>
        
        <div className="form-group">
          <label>Select a rule</label>
          <select
            value={selectedRuleName || '-- Create New --'}
            onChange={(e) => handleRuleSelect(e.target.value)}
          >
            <option value="-- Create New --">-- Create New --</option>
            {ruleNames.map((name) => (
              <option key={name} value={name}>
                {name}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label>Rule Name</label>
          <input
            type="text"
            value={ruleName}
            onChange={(e) => setRuleName(e.target.value)}
            placeholder="Enter rule name..."
            disabled={!!selectedRuleName}
          />
        </div>

        <div className="form-group">
          <label>Description (optional)</label>
          <input
            type="text"
            value={ruleDescription}
            onChange={(e) => setRuleDescription(e.target.value)}
            placeholder="Brief description of this rule..."
          />
        </div>

        <div className="form-group">
          <label>Rule Content</label>
          <textarea
            value={ruleContent}
            onChange={(e) => {
              setRuleContent(e.target.value);
              onCustomRulesChange(e.target.value);
            }}
            placeholder="Example:&#10;- Prioritize candidates with 5+ years experience&#10;- Must have Python skills&#10;- Prefer candidates with ML background"
            rows={6}
          />
        </div>

        <div className="button-group">
          <button onClick={handleCreateRule} className="btn-create">
            Create Rule
          </button>
          <button onClick={handleUpdateRule} className="btn-update">
            Update Rule
          </button>
          <button onClick={handleDeleteRule} className="btn-delete">
            Delete Rule
          </button>
        </div>

        {message && (
          <div className={`message ${message.type}`}>
            {message.text}
          </div>
        )}
      </div>
        </>
      )}
    </div>
  );
}

