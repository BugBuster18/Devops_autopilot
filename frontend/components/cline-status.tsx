"use client";

import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Code, Loader2, CheckCircle, AlertCircle, GitBranch, XCircle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { getClineStatus, ClineExecution } from "../lib/ai-api";

interface ClineStatusProps {
  executionId: string;
  repoUrl?: string;
}

export default function ClineStatusComponent({ executionId, repoUrl }: ClineStatusProps) {
  const [execution, setExecution] = useState<ClineExecution | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        setLoading(true);
        const data = await getClineStatus(executionId);
        setExecution(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load Cline status");
      } finally {
        setLoading(false);
      }
    };

    if (executionId) {
      fetchStatus();
      // Poll for status updates if still running
      const interval = setInterval(() => {
        if (execution?.status === "running" || execution?.status === "pending") {
          fetchStatus();
        }
      }, 3000);
      return () => clearInterval(interval);
    }
  }, [executionId, execution?.status]);

  if (loading && !execution) {
    return (
      <Card className="bg-black/50 backdrop-blur-sm border-red-500/30 rounded-3xl">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Loader2 className="h-5 w-5 animate-spin text-red-400" />
            Loading Cline Status...
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-400">Iron Man is preparing...</p>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="bg-black/50 backdrop-blur-sm border-red-500/30 rounded-3xl">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <XCircle className="h-5 w-5 text-red-400" />
            Cline Error
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-red-400">{error}</p>
        </CardContent>
      </Card>
    );
  }

  if (!execution) {
    return null;
  }

  const getStatusIcon = () => {
    switch (execution.status) {
      case "completed":
        return <CheckCircle className="h-5 w-5 text-green-400" />;
      case "failed":
        return <XCircle className="h-5 w-5 text-red-400" />;
      case "running":
        return <Loader2 className="h-5 w-5 animate-spin text-blue-400" />;
      default:
        return <AlertCircle className="h-5 w-5 text-yellow-400" />;
    }
  };

  const getStatusColor = () => {
    switch (execution.status) {
      case "completed":
        return "bg-green-500/20 text-green-400 border-green-500/30";
      case "failed":
        return "bg-red-500/20 text-red-400 border-red-500/30";
      case "running":
        return "bg-blue-500/20 text-blue-400 border-blue-500/30";
      default:
        return "bg-yellow-500/20 text-yellow-400 border-yellow-500/30";
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Card className="bg-black/50 backdrop-blur-sm border-red-500/30 rounded-3xl">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Code className="h-5 w-5 text-red-400" />
            Cline AI Agent
            <Badge className={`ml-auto ${getStatusColor()}`}>
              {execution.status}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-4 text-sm">
            {repoUrl && (
              <div className="text-gray-400">
                <span className="font-semibold">Repo:</span> {repoUrl}
              </div>
            )}
            {execution.branch && (
              <div className="flex items-center gap-1 text-gray-400">
                <GitBranch className="h-4 w-4" />
                <span>{execution.branch}</span>
              </div>
            )}
          </div>

          {execution.status === "running" && (
            <div className="bg-blue-500/10 rounded-lg p-4 border border-blue-500/30">
              <p className="text-blue-400 flex items-center gap-2">
                <Loader2 className="h-4 w-4 animate-spin" />
                Cline is analyzing and fixing code...
              </p>
            </div>
          )}

          {execution.status === "completed" && execution.output && (
            <div className="bg-green-500/10 rounded-lg p-4 border border-green-500/30">
              <p className="text-green-400 mb-2 flex items-center gap-2">
                <CheckCircle className="h-4 w-4" />
                Fixes Applied Successfully
              </p>
              {execution.branch_name && (
                <p className="text-sm text-gray-400">
                  Branch: <span className="text-gray-300">{execution.branch_name}</span>
                </p>
              )}
              <div className="mt-2 bg-black/30 rounded p-2 text-xs text-gray-300 font-mono">
                {execution.output.split('\n').slice(0, 5).join('\n')}
                {execution.output.split('\n').length > 5 && '...'}
              </div>
            </div>
          )}

          {execution.status === "failed" && execution.error && (
            <div className="bg-red-500/10 rounded-lg p-4 border border-red-500/30">
              <p className="text-red-400 mb-2 flex items-center gap-2">
                <XCircle className="h-4 w-4" />
                Execution Failed
              </p>
              <p className="text-sm text-red-300">{execution.error}</p>
            </div>
          )}

          <div className="flex items-center gap-2 text-xs text-gray-500">
            {getStatusIcon()}
            <span>Execution ID: {execution.execution_id}</span>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}


