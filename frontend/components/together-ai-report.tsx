"use client";

import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { FileCode, Loader2, CheckCircle, AlertCircle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { getTogetherAIReport, TogetherAIReport } from "../lib/ai-api";

interface TogetherAIReportProps {
  executionId: string;
  repoUrl?: string;
}

export default function TogetherAIReportComponent({ executionId, repoUrl }: TogetherAIReportProps) {
  const [report, setReport] = useState<TogetherAIReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchReport = async () => {
      try {
        setLoading(true);
        const data = await getTogetherAIReport(executionId);
        if (data) {
          setReport(data);
        } else {
          setError("Report not found. It may still be generating.");
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load report");
      } finally {
        setLoading(false);
      }
    };

    if (executionId) {
      fetchReport();
      // Poll for report if not found initially
      if (!report) {
        const interval = setInterval(fetchReport, 5000);
        return () => clearInterval(interval);
      }
    }
  }, [executionId]);

  if (loading) {
    return (
      <Card className="bg-black/50 backdrop-blur-sm border-purple-500/30 rounded-3xl">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Loader2 className="h-5 w-5 animate-spin text-purple-400" />
            Generating Together AI Report...
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-400">Doctor Strange is analyzing the outcomes...</p>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="bg-black/50 backdrop-blur-sm border-red-500/30 rounded-3xl">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <AlertCircle className="h-5 w-5 text-red-400" />
            Report Error
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-red-400">{error}</p>
        </CardContent>
      </Card>
    );
  }

  if (!report) {
    return null;
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Card className="bg-black/50 backdrop-blur-sm border-purple-500/30 rounded-3xl">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <FileCode className="h-5 w-5 text-purple-400" />
            Together AI Report
            <Badge className="ml-auto bg-purple-500/20 text-purple-400 border-purple-500/30">
              Doctor Strange
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {repoUrl && (
            <div className="text-sm text-gray-400">
              <span className="font-semibold">Repository:</span> {repoUrl}
            </div>
          )}
          <div className="bg-white/5 rounded-lg p-4 border border-white/10">
            <div className="prose prose-invert max-w-none">
              <p className="text-gray-300 whitespace-pre-wrap leading-relaxed">
                {report.report}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2 text-xs text-gray-500">
            <CheckCircle className="h-4 w-4 text-green-400" />
            <span>Report generated at {new Date(report.created_at).toLocaleString()}</span>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}


