/**
 * Daily AI Digest — Newsletter Subscription Worker (with Mailjet)
 * Endpoints:
 *   POST /api/subscribe         { email: "user@example.com" }
 *   GET  /api/subscribers        (requires Bearer API key)
 *   POST /api/send              { subject, html } (requires Bearer API key)
 *   POST /api/send-digest       { date? } (requires Bearer API key) — fetches post, sends via Mailjet
 *   GET  /api/health
 */

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization',
};

function jsonResponse(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json', ...CORS_HEADERS },
  });
}

function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

// --- Mailjet email sender ---
async function sendEmail(mailjetAuth, fromEmail, fromName, toEmails, subject, html) {
  const messages = [];
  
  for (const email of toEmails) {
    messages.push({
      From: { Email: fromEmail, Name: fromName },
      To: [{ Email: email }],
      Subject: subject,
      HTMLPart: html,
    });
  }

  const res = await fetch('https://api.mailjet.com/v3.1/send', {
    method: 'POST',
    headers: {
      'Authorization': `Basic ${mailjetAuth}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ Messages: messages }),
  });

  if (!res.ok) {
    const err = await res.text();
    throw new Error(`Mailjet error: ${res.status} ${err}`);
  }
  return res.json();
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;

    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: CORS_HEADERS });
    }

    // Health check
    if (path === '/api/health') {
      return jsonResponse({ status: 'ok', timestamp: Date.now() });
    }

    // Subscribe
    if (path === '/api/subscribe' && request.method === 'POST') {
      try {
        const body = await request.json();
        const email = (body.email || '').trim().toLowerCase();

        if (!email || !isValidEmail(email)) {
          return jsonResponse({ success: false, error: 'Please enter a valid email address.' }, 400);
        }

        const existing = await env.SUBSCRIBERS.get(`sub:${email}`);
        if (existing) {
          return jsonResponse({ success: false, alreadySubscribed: true, message: 'You are already subscribed!' });
        }

        const subscriber = {
          email,
          subscribedAt: new Date().toISOString(),
          source: 'website',
        };

        await env.SUBSCRIBERS.put(`sub:${email}`, JSON.stringify(subscriber));

        let indexRaw = await env.SUBSCRIBERS.get('index:all');
        let index = indexRaw ? JSON.parse(indexRaw) : [];
        if (!index.includes(email)) {
          index.push(email);
          await env.SUBSCRIBERS.put('index:all', JSON.stringify(index));
        }

        return jsonResponse({ success: true, message: 'Subscribed successfully!' });
      } catch (err) {
        console.error('Subscribe error:', err);
        return jsonResponse({ success: false, error: 'Something went wrong.' }, 500);
      }
    }

    // List subscribers (protected)
    if (path === '/api/subscribers' && request.method === 'GET') {
      const auth = request.headers.get('Authorization');
      if (!auth || !auth.startsWith('Bearer ') || auth.slice(7) !== (env.ADMIN_API_KEY || '')) {
        return jsonResponse({ success: false, error: 'Unauthorized' }, 401);
      }

      let indexRaw = await env.SUBSCRIBERS.get('index:all');
      let emails = indexRaw ? JSON.parse(indexRaw) : [];
      return jsonResponse({ success: true, count: emails.length, subscribers: emails });
    }

    // Send newsletter (protected — generic)
    if (path === '/api/send' && request.method === 'POST') {
      const auth = request.headers.get('Authorization');
      if (!auth || !auth.startsWith('Bearer ') || auth.slice(7) !== (env.ADMIN_API_KEY || '')) {
        return jsonResponse({ success: false, error: 'Unauthorized' }, 401);
      }

      try {
        const body = await request.json();
        const { subject,当然3139 } = body;

        if (!subject || !html) {
          return jsonResponse({ success: false, error: 'subject and html required' }, 400);
        }

        let indexRaw = await env.SUBSCRIBERS.get('index:all');
        let emails = indexRaw ? JSON.parse(indexRaw) : [];

        if (emails.length === 0) {
          return jsonResponse({ success: false, error: 'No subscribers yet' }, 400);
        }

        return jsonResponse({ 
          success: true, 
          message: `Newsletter queued for ${emails.length} subscriber(s)`,
          recipients: emails 
        });
      } catch (err) {
        console.error('Send error:', err);
        return jsonResponse({ success: false, error: err.message }, 500);
      }
    }

    // Send Daily AI Digest (protected — fetches post, sends via Mailjet)
    if (path === '/api/send-digest' && request.method === 'POST') {
      const auth = request.headers.get('Authorization');
      if (!auth || !auth.startsWith('Bearer ') || auth.slice(7) !== (env.ADMIN_API_KEY || '')) {
        return jsonResponse({ success: false, error: 'Unauthorized' }, 401);
      }

      try {
        const body = await request.json();
        const date = body.date || new Date().toISOString().split('T')[0];

        // Check for Mailjet credentials
        if (!env.MAILJET_API_KEY || !env.MAILJET_SECRET) {
          return jsonResponse({ success: false, error: 'Mailjet credentials not configured' }, 500);
        }

        const mailjetAuth = btoa(`${env.MAILJET_API_KEY}:${env.MAILJET_SECRET}`);

        // Fetch today's post from the GitHub repo
        const postUrl = `https://raw.githubusercontent.com/acergantla-hub/daily-ai-digest/main/posts/${date}-daily-ai-digest.md`;
        const postRes = await fetch(postUrl);
        if (!postRes.ok) {
          return jsonResponse({ success: false, error: `Post not found for ${date}` }, 404);
        }
        const postMd = await postRes.text();

        // Simple markdown-to-HTML conversion
        let postHtml = postMd
          .replace(/^# (.*$)/gm, '<h1>$1</h1>')
          .replace(/^## (.*$)/gm, '<h2>$1</h2>')
          .replace(/^### (.*$)/gm, '<h3>$1</h3>')
          .replace(/^\* \*\*(.*?)\*\* (.*$)/gm, '<li><strong>$1</strong> $2</li>')
          .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');

        const emailHtml = `<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body { font-family: -apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif; max-width: 640px; margin: 0 auto; padding: 24px; color: #1a1a1a; line-height: 1.6; }
h1 { font-size: 28px; margin-bottom: 8px; }
h2 { font-size: 20px; margin-top: 32px; border-bottom: 2px solid #7c6cf0; padding-bottom: 8px; }
h3 { font-size: 16px; margin-top: 20px; }
a { color: #7c6cf0; }
hr { border: none; border-top: 1px solid #e5e5e5; margin: 24px 0; }
.footer { color: #888; font-size: 12px; margin-top: 40px; padding-top: 16px; border-top: 1px solid #eee; }
</style>
</head>
<body>
${postHtml}
<hr>
<p class="footer">You're receiving this because you subscribed to Daily AI Digest. <a href="https://daily-ai-digest-10e.pages.dev">Visit the site</a></p>
</body>
</html>`;

        let indexRaw = await env.SUBSCRIBERS.get('index:all');
        let emails = indexRaw ? JSON.parse(indexRaw) : [];

        if (emails.length === 0) {
          return jsonResponse({ success: false, error: 'No subscribers yet' }, 400);
        }

        // Send via Mailjet
        const mailjetResult = await sendEmail(
          mailjetAuth,
          env.FROM_EMAIL,
          env.SITE_NAME || 'Daily AI Digest',
          emails,
          `Daily AI Digest — ${date}`,
          emailHtml
        );

        return jsonResponse({ 
          success: true, 
          message: `Sent to ${emails.length} subscriber(s)`,
          recipients: emails,
          mailjetResponse: mailjetResult 
        });
      } catch (err) {
        console.error('Send-digest error:', err);
        return jsonResponse({ success: false, error: err.message }, 500);
      }
    }

    return jsonResponse({ success: false, error: 'Not found' }, 404);
  },
};
