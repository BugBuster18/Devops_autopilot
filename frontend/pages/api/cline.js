import { NextApiRequest, NextApiResponse } from 'next';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export default async function handler(req, res) {
  if (req.method === 'POST') {
    // Trigger Cline agent
    try {
      const { repo_url, branch, bug_report, github_token } = req.body;

      if (!repo_url) {
        return res.status(400).json({ message: 'Missing required field: repo_url' });
      }

      // Call backend to trigger Cline agent
      const response = await fetch(`${BACKEND_URL}/api/cline/trigger`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          repo_url,
          branch: branch || 'main',
          bug_report: bug_report || '',
          github_token,
        }),
      });

      if (!response.ok) {
        const error = await response.text();
        throw new Error(`Backend error: ${error}`);
      }

      const data = await response.json();
      res.status(200).json(data);
    } catch (error) {
      console.error('Cline API error:', error);
      res.status(500).json({ 
        message: 'Failed to trigger Cline agent', 
        error: error.message 
      });
    }
  } else if (req.method === 'GET') {
    // Get Cline agent status
    try {
      const { execution_id } = req.query;

      if (!execution_id) {
        return res.status(400).json({ message: 'Missing required query: execution_id' });
      }

      const response = await fetch(`${BACKEND_URL}/api/cline/status/${execution_id}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const error = await response.text();
        throw new Error(`Backend error: ${error}`);
      }

      const data = await response.json();
      res.status(200).json(data);
    } catch (error) {
      console.error('Cline status API error:', error);
      res.status(500).json({ 
        message: 'Failed to get Cline status', 
        error: error.message 
      });
    }
  } else {
    return res.status(405).json({ message: 'Method not allowed' });
  }
}


