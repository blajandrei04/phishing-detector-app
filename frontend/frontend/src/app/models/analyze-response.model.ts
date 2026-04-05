export interface AnalyzeResponse {
  score: number;
  verdict: 'phishing' | 'suspicious' | 'safe';
  confidence: number;
}