export interface AnalyzeResponse {
  url: string;
  score: number;
  verdict: 'phishing' | 'suspicious' | 'legitimate';
  confidence: number;
  extracted_features: Record<string, any>;
  shap_explanation?: {
    shap_values: Array<{ label: string; shap_value: number }>;
  };
  timestamp: string;
}