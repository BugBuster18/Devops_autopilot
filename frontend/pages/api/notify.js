import { NextApiRequest, NextApiResponse } from 'next';

const logger = {
  info: (message) => console.log(`[INFO] ${message}`),
  error: (message) => console.error(`[ERROR] ${message}`)
};

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  try {
    const { status, preview_url, review_summary } = req.body;

    // Placeholder: Call Oumi API
    logger.info(`Sending notification via Oumi: ${status}`);

    // In a real implementation, you would call the Oumi API here
    const notifyResult = {
      status: "notification_sent"
    };

    res.status(200).json(notifyResult);
  } catch (error) {
    logger.error(`Notify error: ${error.message}`);
    res.status(500).json({ message: 'Internal server error', error: error.message });
  }
}
