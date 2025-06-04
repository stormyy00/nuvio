"use client";

import { useState } from "react";
import { Input } from "./ui/input";
import { Button } from "./ui/button";
import Form from "./form";
import Content from "./content";

const Landing = () => {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<Clone | null>(null);
  const [previewMode, setPreviewMode] = useState<"preview" | "code">("preview");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!url.trim()) {
      alert("Please enter a valid URL");
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const response = await fetch("http://127.0.0.1:8000/clone", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ url: url.trim() }),
      });

      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error("Error cloning website:", error);
      setResult({
        success: false,
        error:
          "Failed to connect to the cloning service. Make sure the backend is running.",
      });
    } finally {
      setLoading(false);
    }
  };

  const downloadHtml = () => {
    if (!result?.html) return;

    const blob = new Blob([result.html], { type: "text/html" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "cloned-website.html";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };
  return (
    <div>
      <div className="flex flex-col items-center justify-center min-h-screen bg-gray-950  p-4">
        <h1 className="text-3xl font-bold mb-6 text-white">
          What would you like to scrape today?
        </h1>
        <Form
          url={url}
          setUrl={setUrl}
          handleSubmit={handleSubmit}
          loading={loading}
        />
        <Content
          result={result}
          previewMode={previewMode}
          setPreviewMode={setPreviewMode}
          downloadHtml={downloadHtml}
        />
      </div>
    </div>
  );
};

export default Landing;
