export interface AnalyzeResponse {
  url: string;
  score: number;
  verdict: 'phishing' | 'suspicious' | 'legitimate';
  confidence: number;
  extracted_features: Record<string, any>;
  shap_explanation?: {
    shap_values: Array<{ label: string; shap_value: number }>;
  };
  dynamic_checks?: {
    dns: { resolved: boolean; ip: string | null; error: string | null };
    ssl: {
      valid: boolean;
      is_expired: boolean;
      days_until_expiry: number;
      issuer_common_name: string;
      issuer_organization: string;
      error: string | null;
    };
    domain_age: {
      domain_age_days: number | null;
      creation_date: string | null;
      error: string | null;
    };
  };
  timestamp: string;
}