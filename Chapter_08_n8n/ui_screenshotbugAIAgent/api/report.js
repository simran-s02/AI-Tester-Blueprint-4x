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
    res.statusCode = 405;
    res.setHeader('Content-Type', 'application/json');

    return res.end(
      JSON.stringify({
        error: 'Method not allowed'
      })
    );
  }

  const target = process.env.N8N_WEBHOOK_URL;

  if (!target) {
    res.statusCode = 500;
    res.setHeader('Content-Type', 'application/json');

    return res.end(
      JSON.stringify({
        error: 'N8N_WEBHOOK_URL is not configured.'
      })
    );
  }

  let body;

  try {
    body = await readRaw(req);
  } catch (error) {
    res.statusCode = 400;
    res.setHeader('Content-Type', 'application/json');

    return res.end(
      JSON.stringify({
        error: 'Could not read the upload: ' + error.message
      })
    );
  }

  if (!body.length) {
    res.statusCode = 400;
    res.setHeader('Content-Type', 'application/json');

    return res.end(
      JSON.stringify({
        error: 'Empty request body. Attach a screenshot and try again.'
      })
    );
  }

  let upstream;

  try {
    upstream = await fetch(target, {
      method: 'POST',
      headers: {
        'content-type': req.headers['content-type'] || 'application/octet-stream'
      },
      body
    });
  } catch (error) {
    res.statusCode = 502;
    res.setHeader('Content-Type', 'application/json');

    return res.end(
      JSON.stringify({
        error: 'Could not reach the n8n webhook: ' + error.message
      })
    );
  }

  const responseText = await upstream.text();

  let n8nData;

  try {
    n8nData = JSON.parse(responseText);
  } catch {
    n8nData = {
      raw: responseText
    };
  }

  const result =
    n8nData?.body ||
    n8nData?.data ||
    n8nData;

  const issueKey =
    result?.issue_key ||
    result?.issueKey ||
    result?.key ||
    '';

  const issueUrl =
    result?.issue_url ||
    result?.issueUrl ||
    '';

  res.statusCode = upstream.status;
  res.setHeader('Content-Type', 'application/json');

  return res.end(
    JSON.stringify({
      issue_key: issueKey,
      issue_url: issueUrl
    })
  );
}
