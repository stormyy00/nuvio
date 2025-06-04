import React from "react";

interface ContentProps {
  result: {
    success: boolean;
    html?: string;
    error?: string;
    metadata?: {
      elements_extracted: number;
      stylesheets_found: number;
      has_screenshot: boolean;
    };
  } | null;
  previewMode: "preview" | "code";
  setPreviewMode: (mode: "preview" | "code") => void;
  downloadHtml: () => void;
}

const Content = ({
  result,
  previewMode,
  setPreviewMode,
  downloadHtml,
}: ContentProps) => {
  return (
    <>
      {result && (
        <div className="w-full max-w-6xl mt-8 bg-white rounded-lg shadow-lg p-6">
          {result.success ? (
            <>
              <div className="mb-6">
                <h2 className="text-2xl font-bold text-cyan-400 mb-4">
                  Clone Generated Successfully!
                </h2>
                {result.metadata && (
                  <div className="flex gap-4 text-sm text-gray-600">
                    <span>Elements: {result.metadata.elements_extracted}</span>
                    <span>
                      Stylesheets: {result.metadata.stylesheets_found}
                    </span>
                    <span>
                      Screenshot: {result.metadata.has_screenshot ? "✓" : "✗"}
                    </span>
                  </div>
                )}
              </div>

              <div className="flex justify-between items-center mb-6">
                <div className="flex border-b border-gray-200">
                  <button
                    className={`px-4 py-2 font-medium ${
                      previewMode === "preview"
                        ? "text-blue-600 border-b-2 border-blue-600"
                        : "text-gray-500 hover:text-gray-700"
                    }`}
                    onClick={() => setPreviewMode("preview")}
                  >
                    Preview
                  </button>
                  <button
                    className={`px-4 py-2 font-medium ${
                      previewMode === "code"
                        ? "text-blue-600 border-b-2 border-blue-600"
                        : "text-gray-500 hover:text-gray-700"
                    }`}
                    onClick={() => setPreviewMode("code")}
                  >
                    Tailwind HTML
                  </button>
                </div>
                <button
                  onClick={downloadHtml}
                  className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded font-medium"
                >
                  Download HTML
                </button>
              </div>

              <div className="border border-gray-300 rounded-lg overflow-hidden">
                {previewMode === "preview" ? (
                  <iframe
                    srcDoc={result.html}
                    className="w-full h-96 border-none"
                    title="Website Clone Preview"
                  />
                ) : (
                  <pre className="bg-gray-900 text-green-400 p-4 overflow-auto h-96 text-sm">
                    <code>{result.html}</code>
                  </pre>
                )}
              </div>
            </>
          ) : (
            <div className="text-center py-8 bg-gray-950">
              <h2 className="text-2xl font-bold text-red-600 mb-4">
                Clone Failed
              </h2>
              <p className="text-gray-600">{result.error}</p>
            </div>
          )}
        </div>
      )}
    </>
  );
};

export default Content;
