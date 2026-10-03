export const config = {
  api: { bodyParser: false },
  maxDuration: 60
};

function readRaw(req) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    req.on('data', (chunk) => chunks.push(chunk));
    req.on('end', () => resolve(Buffer.concat(chunks)));
    req.on('error', reject);
  });
}

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method Not Allowed' });
    return;
  }

  const target = process.env.N8N_WEBHOOK_URL;
  if (!target) {
    res.status(500).json({ error: 'N8N_WEBHOOK_URL is not set on this deployment.' });
    return;
  }

  let body;
  try {
    body = await readRaw(req);
  } catch (error) {
    res.status(400).json({ error: 'Could not read the upload: ' + error.message });
    return;
  }

  if (!body.length) {
    res.status(400).json({ error: 'Empty request body. Attach a screenshot and try again.' });
    return;
  }

  let upstream;
  try {
    upstream = await fetch(target, {
      method: 'POST',
      headers: { 'content-type': req.headers['content-type'] || 'application/octet-stream' },
      body
    });
  } catch (error) {
    res.status(502).json({ error: 'Could not reach the n8n webhook: ' + error.message });
    return;
  }

  const text = await upstream.text();
  res.status(upstream.status);
  res.setHeader('content-type', upstream.headers.get('content-type') || 'application/json');
  res.send(text);
}
