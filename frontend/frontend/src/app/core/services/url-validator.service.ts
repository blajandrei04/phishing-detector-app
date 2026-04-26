import { Injectable } from '@angular/core';

export interface ValidationResult {
  isValid: boolean;
  formattedUrl: string;
  errorMessage: string | null;
}

@Injectable({
  providedIn: 'root'
})
export class UrlValidatorService {
  constructor() {}

  /**
   * Validates and formats a raw URL string input by the user.
   * Prepends protocol if missing and checks for valid hostnames.
   */
  validate(rawUrl: string): ValidationResult {
    let url = rawUrl.trim();

    if (!url) {
      return { isValid: false, formattedUrl: '', errorMessage: 'Please enter a URL to analyze.' };
    }

    if (url.length > 2048) {
      return { isValid: false, formattedUrl: '', errorMessage: 'URL is too long (max 2048 characters).' };
    }

    // Auto-prepend https:// if no protocol
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      url = 'https://' + url;
    }

    // Basic URL format validation
    try {
      const parsed = new URL(url);
      if (!parsed.hostname || !parsed.hostname.includes('.')) {
        // Allow IP addresses too
        if (!/^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/.test(parsed.hostname)) {
          return { 
            isValid: false, 
            formattedUrl: '', 
            errorMessage: 'Please enter a valid URL (e.g. google.com or 192.168.1.1).' 
          };
        }
      }
    } catch {
      return { 
        isValid: false, 
        formattedUrl: '', 
        errorMessage: 'Invalid URL format. Please enter a valid web address.' 
      };
    }

    return { isValid: true, formattedUrl: url, errorMessage: null };
  }
}
