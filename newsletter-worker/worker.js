/**
 * Daily AI Digest — Newsletter Subscription Worker
 * Endpoints:
 *   POST /api/subscribe   { email: "user@example.com" }
 *   GET  /api/subscribers  (requires Bearer API key)
 *   POST /api/send        { subject, html } (requires Bearer API key)
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

    // Send newsletter (protected)
    if (path === '/api/send' && request.method === 'POST') {
      const auth = request.headers.get('Authorization');
      if (!auth || !auth.startsWith('Bearer ') || auth.slice(7) !== (env.ADMIN_API_KEY || '')) {
        return jsonResponse({ success: false, error: 'Unauthorized' }, 401);
      }

      try {
        const body = await request.json();
        const { subject, html } = body;

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

    return jsonResponse({ success: false, error: 'Not found' }, 404);
  },
};
