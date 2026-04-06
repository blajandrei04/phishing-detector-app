export interface AnalyzeResponse {
  url: string;
  score: number;
  verdict: 'phishing' | 'suspicious' | 'legitimate';
  confidence: number;
  extracted_features: Record<string, number>;
  timestamp: string;
}