type Clone  = {
  success: boolean;
  html?: string;
  error?: string;
  metadata?: {
    original_url: string;
    elements_extracted: number;
    stylesheets_found: number;
    has_screenshot: boolean;
  };
}