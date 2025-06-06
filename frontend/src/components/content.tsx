import React from "react";
import { Button } from "./ui/button";
import { Download, Loader2 } from "lucide-react";
import { Tabs, TabsList, TabsTrigger } from "./ui/tabs";

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
  loading: boolean;
  previewMode: "preview" | "code";
  setPreviewMode: (mode: "preview" | "code") => void;
  downloadHtml: () => void;
}

const Content = ({
  result,
  loading,
  previewMode,
  setPreviewMode,
  downloadHtml,
}: ContentProps) => {
  return (
    <>
      {loading && (
        <div className="w-full max-w-6xl mt-8 bg-gray-900/50 backdrop-blur-sm border border-gray-800 rounded-xl shadow-2xl p-6">
          <div className="flex  flex-col items-center justify-center h-96">
            <Loader2 className="animate-spin text-cyan-500 w-12 h-12" />
          <div className="text-center text-gray-400 mt-4">
            Cloning the website, please wait...
          </div>
          </div>
        </div>
      )}
      {result && (
        <div className="w-full max-w-6xl mt-8 bg-gray-900/50 backdrop-blur-sm border border-gray-800 rounded-xl shadow-2xl p-6">
          {result.success ? (
            <>
              <div className="mb-6">
                <div className="text-2xl font-bold text-white mb-4">
                  Clone Generated Successfully!
                </div>
                {result.metadata && (
                  <div className="flex gap-6 text-sm text-gray-400">
                    <span className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-cyan-400 rounded-full"></div>
                      Elements: {result.metadata.elements_extracted}
                    </span>
                    <span className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-cyan-400 rounded-full"></div>
                      Stylesheets: {result.metadata.stylesheets_found}
                    </span>
                    <span className="flex items-center gap-2">
                      <div
                        className={`w-2 h-2 rounded-full ${result.metadata.has_screenshot ? "bg-green-400" : "bg-gray-600"}`}
                      ></div>
                      Screenshot:{" "}
                      {result.metadata.has_screenshot
                        ? "Available"
                        : "Not Available"}
                    </span>
                  </div>
                )}
              </div>

              <Tabs
                defaultValue="preview"
                value={previewMode}
                onValueChange={(value) =>
                  setPreviewMode(value as "preview" | "code")
                }
                className="w-full"
              >
                <div className="flex justify-between items-center mb-6">
                  <TabsList className="bg-gray-800/50 border border-gray-700 p-1 rounded-lg">
                    <TabsTrigger
                      value="preview"
                      className="text-gray-300 font-medium px-6 py-2 rounded-md transition-all duration-300 data-[state=active]:bg-cyan-500 data-[state=active]:text-white data-[state=active]:shadow-lg hover:text-white"
                    >
                      Preview
                    </TabsTrigger>
                    <TabsTrigger
                      value="code"
                      className="text-gray-300 font-medium px-6 py-2 rounded-md transition-all duration-300 data-[state=active]:bg-cyan-500 data-[state=active]:text-white data-[state=active]:shadow-lg hover:text-white"
                    >
                      HTML Code
                    </TabsTrigger>
                  </TabsList>

                  <Button
                    onClick={downloadHtml}
                    className="bg-cyan-500 hover:bg-cyan-400 text-white px-6 py-2 rounded-lg font-medium transition-all duration-300 hover:shadow-lg hover:scale-105 flex items-center gap-2"
                  >
                    <Download size={18} />
                    Download
                  </Button>
                </div>

                <div className="border border-gray-700 rounded-xl overflow-hidden bg-gray-800/30">
                  {previewMode === "preview" ? (
                    <div className="bg-white rounded-xl overflow-hidden">
                      <iframe
                        srcDoc={result.html}
                        className="w-full h-96 border-none"
                        title="Website Clone Preview"
                      />
                    </div>
                  ) : (
                    <div className="relative">
                      <div className="absolute top-4 right-4 z-10">
                        <div className="flex gap-2">
                          <div className="w-3 h-3 bg-red-500 rounded-full" />
                          <div className="w-3 h-3 bg-yellow-500 rounded-full" />
                          <div className="w-3 h-3 bg-green-500 rounded-full" />
                        </div>
                      </div>
                      <pre className="bg-gray-900 text-gray-300 p-6 overflow-auto h-96 text-sm font-mono leading-relaxed">
                        <code className="text-cyan-300">{result.html}</code>
                      </pre>
                    </div>
                  )}
                </div>
              </Tabs>
            </>
          ) : (
            <div className="text-center py-12">
              <div className="mb-6">
                <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                  <div className="w-8 h-8 bg-red-500 rounded-full flex items-center justify-center">
                    <span className="text-white font-bold text-lg">!</span>
                  </div>
                </div>
                <div className="text-2xl font-bold text-red-400 mb-4">
                  Clone Failed
                </div>
                <p className="text-gray-400 max-w-md mx-auto leading-relaxed">
                  {result.error ||
                    "An unexpected error occurred while cloning the website. Please try again."}
                </p>
              </div>

              {/* <Button
                onClick={() => window.location.reload()}
                className="bg-gray-700 hover:bg-gray-600 text-white px-6 py-2 rounded-lg font-medium transition-all duration-300 hover:shadow-lg"
              >
                Try Again
              </Button> */}
            </div>
          )}
        </div>
      )}
    </>
  );
};

export default Content;
