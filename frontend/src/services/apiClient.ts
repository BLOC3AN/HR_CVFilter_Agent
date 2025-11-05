import axios from 'axios';
import type { AxiosInstance } from 'axios';

export interface EvaluateCVRequest {
  cv_content: string;
  job_description: string;
  custom_rules?: string;
  llm_model?: string;
}

export interface EvaluateCVResponse {
  success: boolean;
  evaluation?: string;
  error?: string;
}

export interface ChatRequest {
  message: string;
  job_description: string;
  custom_rules?: string;
  cv_evaluations?: Array<{ filename: string; evaluation: string }>;
  chat_history?: Array<{ role: string; content: string }>;
  llm_model?: string;
}

export interface ChatResponse {
  success: boolean;
  response?: string;
  error?: string;
}

export interface Rule {
  name: string;
  rules: string;
  description?: string;
  created_at?: string;
  updated_at?: string;
}

export interface RulesResponse {
  success: boolean;
  rules?: Rule[];
  names?: string[];
  rule?: Rule;
  error?: string;
}

export interface HealthResponse {
  status: string;
  error?: string;
}

class APIClient {
  private client: AxiosInstance;
  private baseURL: string;

  constructor(baseURL?: string) {
    // Use relative URL for production (nginx will proxy to backend)
    // For local development, set VITE_BACKEND_API_URL=http://localhost:8000 in .env
    // Empty string means same origin (relative URLs)
    this.baseURL = baseURL !== undefined ? baseURL : (import.meta.env.VITE_BACKEND_API_URL || '');
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: 60000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  async healthCheck(): Promise<HealthResponse> {
    try {
      const response = await this.client.get<HealthResponse>('/health', { timeout: 5000 });
      return response.data;
    } catch (error) {
      return {
        status: 'unhealthy',
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  async evaluateCV(request: EvaluateCVRequest): Promise<EvaluateCVResponse> {
    try {
      const response = await this.client.post<EvaluateCVResponse>('/api/evaluate-cv', {
        cv_content: request.cv_content,
        job_description: request.job_description,
        custom_rules: request.custom_rules || '',
        llm_model: request.llm_model || 'gemini-2.0-flash',
      });
      return response.data;
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  async chat(request: ChatRequest): Promise<ChatResponse> {
    try {
      const response = await this.client.post<ChatResponse>('/api/chat', {
        message: request.message,
        job_description: request.job_description,
        custom_rules: request.custom_rules || '',
        cv_evaluations: request.cv_evaluations || [],
        chat_history: request.chat_history || [],
        llm_model: request.llm_model || 'gemini-2.0-flash',
      });
      return response.data;
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  async getAllRules(): Promise<RulesResponse> {
    try {
      const response = await this.client.get<RulesResponse>('/api/rules', { timeout: 10000 });
      return response.data;
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  async getRuleNames(): Promise<RulesResponse> {
    try {
      const response = await this.client.get<RulesResponse>('/api/rules/names', { timeout: 10000 });
      return response.data;
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  async getRule(name: string): Promise<RulesResponse> {
    try {
      const response = await this.client.get<RulesResponse>(`/api/rules/${name}`, { timeout: 10000 });
      return response.data;
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  async createRule(name: string, rules: string, description?: string): Promise<RulesResponse> {
    try {
      const response = await this.client.post<RulesResponse>('/api/rules', {
        name,
        rules,
        description: description || '',
      });
      return response.data;
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  async updateRule(name: string, rules: string, description?: string): Promise<RulesResponse> {
    try {
      const response = await this.client.put<RulesResponse>(`/api/rules/${name}`, {
        rules,
        description: description || '',
      });
      return response.data;
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  async deleteRule(name: string): Promise<RulesResponse> {
    try {
      const response = await this.client.delete<RulesResponse>(`/api/rules/${name}`);
      return response.data;
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }
}

export const apiClient = new APIClient();
export default APIClient;

