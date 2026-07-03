/**
 * Daily AI Digest — Newsletter Subscription Worker
 * Stores subscriber emails in Cloudflare KV.
 * Endpoints:
 *   POST /api/subscribe   { email: "user@example.com" }
 *   GET  /api/subscribers  (requires API key via Bearer token)
 *   DELETE /api/unsubscribe?email=user@example.com
 *   GET  /api/health
 */

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, DELETE, OPTIONS',
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

    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: CORS_HEADERS });
    }

    // Health check
    if (path === '/api/health') {
      return jsonResponse({ status: 'ok', timestamp: Date.now() });
    }

    // ── SUBSCRIBE ──
    if (path === '/api/subscribe' && request.method === 'POST') {
      try {
        const body = await request.json();
        const email = (body.email || '').trim().toLowerCase();

        if (!email || !isValidEmail(email)) {
          return jsonResponse({ success: false, error: 'Please enter a valid email address.' }, 400);
        }

        // Check if already subscribed
        const existing = await env.SUBSCRIBERS.get(`sub:${email}`);
        if (existing) {
          return jsonResponse({ success: false, alreadySubscribed: true, message: 'You are already subscribed!' });
        }

        // Store the subscriber
        const subscriber = {
          email,
          subscribedAt: new Date().toISOString(),
          source: 'website',
        };

        await env.SUBSCRIBERS.put(`sub:${email}`, JSON.stringify(subscriber));

        // Also maintain a simple index of all emails for easy export
        let indexRaw = await env.SUBSCRIBERS.get('index:all');
        let index = indexRaw ? JSON.parse(indexRaw) : [];
        if (!index.includes(email)) {
          index.push(email);
          await env.SUBSCRIBERS.put('index:all', JSON.stringify(index));
        }

        const count = index.length;

        // Optional: send notification email if configured
        if (env.NOTIFY_EMAIL && env.SENDGRID_API_KEY) {
          try {
            await fetch('https://api.sendgrid.com/v3/mail/send', {
              method: 'POST',
              headers: {
                'Authorization': `Bearer ${env.SENDGRID_API_KEY}`,
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                personalizations: [{ to: [{ email: env.NOTIFY_EMAIL }] }],
                from: { email: 'newsletter@daily-ai-digest.com' },
                subject: `New Newsletter Subscriber: ${email}`,
                content: [{ type: 'text/plain', value: `New subscriber: ${email}\nTotal subscribers: ${count}` }],
              }),
            });
          } catch (e) {
            // Notification failure should not block the subscription
            console.error('Notify error:', e);
          }
        }

        return jsonResponse({ success: true, message: 'Subscribed successfully!', totalSubscribers: count });
      } catch (err) {
        console.error('Subscribe error:', err);
        return jsonResponse({ success: false, error: 'Something went wrong. Please try again.' }, 500);
      }
    }

    // ── UNSUBSCRIBE ──
    if (path === '/api/unsubscribe' && request.method === 'DELETE') {
      const email = url.searchParams.get('email');
      if (!email || !isValidEmail(email)) {
        return jsonResponse({ success: false, error: 'Valid email required.' }, 400);
      }
      const normalized = email.trim().toLowerCase();
      await env.SUBSCRIBERS.delete(`sub:${normalized}`);

      let indexRaw = await env.SUBSCRIBERS.get('index:all');
      if (indexRaw) {
        let index = JSON.parse(indexRaw).filter(e => e !== normalized);
        await env.SUBSCRIBERS.put('index:all', JSON.stringify(index));
      }

      return jsonResponse({ success: true, message: 'Unsubscribed successfully.' });
    }

    // ── LIST SUBSCRIBERS (protected) ──
    if (path === '/api/subscribers' && request.method === 'GET') {
      const auth = request.headers.get('Authorization');
      if (!auth || !auth.startsWith('Bearer ') || auth.slice(7) !== (env.ADMIN_API_KEY || '')) {
        return jsonResponse({ success: false, error: 'Unauthorized' }, 401);
      }

      let indexRaw = await env.SUBSCRIBERS.get('index:all');
      let emails = indexRaw ? JSON.parse(indexRaw) : [];
      return jsonResponse({ success: true, count: emails.length, subscribers: emails });
    }

    return jsonResponse({ success: false, error: 'Not found' }, 404);
  },
};
