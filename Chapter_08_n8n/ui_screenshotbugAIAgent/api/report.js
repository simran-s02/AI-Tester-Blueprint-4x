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

  try {
    const body = req.body || {};

    const {
      logs = '',
      steps = '',
      severity = 'S3',
      environment = '',
      screenshotBase64 = '',
      screenshotName = 'screenshot.png',
      screenshotType = 'image/png'
    } = body;

    if (!screenshotBase64) {
      res.statusCode = 400;
      res.setHeader('Content-Type', 'application/json');

      return res.end(
        JSON.stringify({
          error: 'No screenshot was uploaded.'
        })
      );
    }

    const n8nUrl = process.env.N8N_WEBHOOK_URL;

    if (!n8nUrl) {
      res.statusCode = 500;
      res.setHeader('Content-Type', 'application/json');

      return res.end(
        JSON.stringify({
          error: 'N8N_WEBHOOK_URL is not configured.'
        })
      );
    }

    const payload = {
      logs,
      steps,
      severity,
      environment,
      screenshotBase64,
      screenshotName,
      screenshotType
    };

    const n8nResponse = await fetch(n8nUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });

    const responseText = await n8nResponse.text();

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

    res.statusCode = n8nResponse.status;
    res.setHeader('Content-Type', 'application/json');

    return res.end(
      JSON.stringify({
        issue_key: issueKey,
        issue_url: issueUrl
      })
    );

  } catch (error) {
    console.error('API error:', error);

    res.statusCode = 500;
    res.setHeader('Content-Type', 'application/json');

    return res.end(
      JSON.stringify({
        error:
          error.message ||
          'Failed to contact n8n.'
      })
    );
  }
}