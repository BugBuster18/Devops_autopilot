import { NextApiRequest, NextApiResponse } from 'next';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  try {
    const { repo_url, execution_id, user_email } = req.body;

    if (!repo_url || !execution_id) {
      return res.status(400).json({ message: 'Missing required fields: repo_url, execution_id' });
    }

    // Call backend to generate Together AI report
    const response = await fetch(`${BACKEND_URL}/api/together-ai/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        repo_url,
        execution_id,
        user_email,
      }),
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Backend error: ${error}`);
    }

    const data = await response.json();
    res.status(200).json(data);
  } catch (error) {
    console.error('Together AI API error:', error);
    res.status(500).json({ 
      message: 'Failed to generate Together AI report', 
      error: error.message 
    });
  }
}


