/**
 * Daily AI Digest — Newsletter Worker
 * 
 * Endpoints:
 *   POST /api/subscribe          — { email } → adds subscriber
 *   GET  /api/unsubscribe?token=xxx — unsubscribes via token
 *   GET  /api/subscribers?secret=xxx — lists all active subscribers (admin)
 *   POST /api/send               — { post_slug, post_title, post_url, secret } → sends newsletter
 *   GET  /api/health             — health check
 */

import { Resend } from 'resend';

// ─── CORS helper ───
function corsHeaders() {
  return {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
  };
}

function jsonResponse(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json', ...corsHeaders() },
  });
}

// ─── Generate unsubscribe token ───
function generateToken() {
  const array = new Uint8Array(32);
  crypto.getRandomValues(array);
  return Array.from(array, b => b.toString(16).padStart(2, '0')).join('');
}

// ─── Send email via Resend ───
async function sendEmail(resend, to, subject, html, unsubscribeToken, workerUrl) {
  const unsubscribeUrl = `${workerUrl}/api/unsubscribe?token=${unsubscribeToken}`;
  
  const fullHtml = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0;padding:0;background:#020205;font-family:'Inter',system-ui,sans-serif;color:#f0f0f8;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:600px;margin:0 auto;">
    <tr>
      <td style="padding:40px 24px;">
        <!-- Header -->
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0">
          <tr>
            <td style="text-align:center;padding-bottom:32px;">
              <div style="display:inline-block;background:linear-gradient(135deg,#7c6cf0,#b46eff,#00d4f0);border-radius:12px;padding:12px 24px;">
                <span style="color:#fff;font-size:18px;font-weight:700;letter-spacing:-0.5px;">Daily AI Digest</span>
              </div>
            </td>
          </tr>
        </table>
        
        <!-- Content -->
        <div style="background:rgba(10,10,20,0.7);border:1px solid rgba(255,255,255,0.05);border-radius:24px;padding:40px 32px;">
          ${html}
        </div>
        
        <!-- Footer -->
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0">
          <tr>
            <td style="text-align:center;padding-top:32px;">
              <p style="color:#5a5a78;font-size:12px;line-height:1.6;">
                You're receiving this because you subscribed to Daily AI Digest.<br>
                <a href="${unsubscribeUrl}" style="color:#7c6cf0;text-decoration:none;">Unsubscribe</a> · 
                <a href="https://daily-ai-digest.freelancerloki.workers.dev" style="color:#7c6cf0;text-decoration:none;">Visit Site</a>
              </p>
              <p style="color:#3a3a58;font-size:11px;margin-top:12px;">
                © ${new Date().getFullYear()} LancerLoki. All rights reserved.
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>`;

  try {
    await resend.emails.send({
      from: 'Daily AI Digest <newsletter@daily-ai-digest.freelancerloki.workers.dev>',
      to: [to],
      subject: subject,
      html: fullHtml,
    });
    return true;
  } catch (err) {
    console.error(`Failed to send to ${to}:`, err);
    return false;
  }
}

// ─── Main Worker ───
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;
    const workerUrl = `${url.protocol}//${url.host}`;

    // CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders() });
    }

    // ─── Health check ───
    if (path === '/api/health') {
      return jsonResponse({ status: 'ok', service: 'daily-ai-digest-newsletter' });
    }

    // ─── Subscribe ───
    if (path === '/api/subscribe' && request.method === 'POST') {
      try {
        const body = await request.json();
        const email = (body.email || '').trim().toLowerCase();

        if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
          return jsonResponse({ error: 'Invalid email address' }, 400);
        }

        const token = generateToken();

        // Try to insert, if already exists and inactive, reactivate
        const existing = await env.DB.prepare(
          'SELECT id, is_active, unsubscribe_token FROM subscribers WHERE email = ?'
        ).bind(email).first();

        if (existing) {
          if (existing.is_active) {
            return jsonResponse({ message: 'Already subscribed!', alreadySubscribed: true });
          } else {
            // Reactivate
            await env.DB.prepare(
              'UPDATE subscribers SET is_active = 1, subscribed_at = datetime("now"), unsubscribe_token = ? WHERE email = ?'
            ).bind(token, email).run();
            return jsonResponse({ message: 'Welcome back! Re-subscribed successfully.', success: true });
          }
        }

        await env.DB.prepare(
          'INSERT INTO subscribers (email, unsubscribe_token) VALUES (?, ?)'
        ).bind(email, token).run();

        return jsonResponse({ 
          message: 'Subscribed successfully! Check your inbox.', 
          success: true 
        });
      } catch (err) {
        console.error('Subscribe error:', err);
        return jsonResponse({ error: 'Server error. Try again.' }, 500);
      }
    }

    // ─── Unsubscribe ───
    if (path === '/api/unsubscribe' && request.method === 'GET') {
      const token = url.searchParams.get('token');
      if (!token) {
        return jsonResponse({ error: 'Missing token' }, 400);
      }

      const result = await env.DB.prepare(
        'UPDATE subscribers SET is_active = 0 WHERE unsubscribe_token = ? AND is_active = 1'
      ).bind(token).run();

      if (result.meta.changes > 0) {
        return new Response(`
<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Unsubscribed</title>
<style>body{background:#020205;color:#f0f0f8;font-family:system-ui;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0}
.card{background:rgba(10,10,20,.7);border:1px solid rgba(255,255,255,.05);border-radius:24px;padding:48px;text-align:center;max-width:420px}
h1{font-size:24px;margin-bottom:12px}p{color:#a0a0c0}a{color:#7c6cf0}</style>
</head><body><div class="card"><h1>Unsubscribed</h1><p>You've been removed from the newsletter.</p><p>Changed your mind? <a href="https://daily-ai-digest.freelancerloki.workers.dev">Subscribe again</a></p></div></body></html>
        `, { headers: { 'Content-Type': 'text/html' } });
      }

      return jsonResponse({ error: 'Invalid or expired token' }, 404);
    }

    // ─── List subscribers (admin only) ───
    if (path === '/api/subscribers' && request.method === 'GET') {
      const secret = url.searchParams.get('secret');
      if (secret !== env.ADMIN_SECRET) {
        return jsonResponse({ error: 'Unauthorized' }, 401);
      }

      const { results } = await env.DB.prepare(
        'SELECT email, subscribed_at, is_active FROM subscribers ORDER BY subscribed_at DESC'
      ).all();

      return jsonResponse({ subscribers: results, count: results.length });
    }

    // ─── Send newsletter (admin only) ───
    if (path === '/api/send' && request.method === 'POST') {
      const body = await request.json();
      
      if (body.secret !== env.ADMIN_SECRET) {
        return jsonResponse({ error: 'Unauthorized' }, 401);
      }

      const { post_slug, post_title, post_url } = body;
      if (!post_slug || !post_title || !post_url) {
        return jsonResponse({ error: 'Missing post_slug, post_title, or post_url' }, 400);
      }

      const resend = new Resend(env.RESEND_API_KEY);

      // Get all active subscribers
      const { results: subscribers } = await env.DB.prepare(
        'SELECT email, unsubscribe_token FROM subscribers WHERE is_active = 1'
      ).all();

      if (subscribers.length === 0) {
        return jsonResponse({ message: 'No active subscribers', sent: 0 });
      }

      // Build email content
      const emailHtml = `
        <h1 style="font-size:28px;font-weight:700;margin-bottom:8px;background:linear-gradient(135deg,#7c6cf0,#b46eff,#00d4f0);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">${post_title}</h1>
        <p style="color:#a0a0c0;font-size:14px;margin-bottom:24px;">Fresh from Daily AI Digest</p>
        <a href="https://daily-ai-digest.freelancerloki.workers.dev/posts/${post_slug}.html" 
           style="display:inline-block;background:linear-gradient(135deg,#7c6cf0,#b46eff);color:#fff;padding:14px 32px;border-radius:12px;text-decoration:none;font-weight:600;font-size:15px;">
          Read Full Article →
        </a>
        <p style="color:#5a5a78;font-size:13px;margin-top:32px;">New post published at <a href="https://daily-ai-digest.freelancerloki.workers.dev" style="color:#7c6cf0;">daily-ai-digest.freelancerloki.workers.dev</a></p>
      `;

      // Send to all subscribers
      let sent = 0;
      let failed = 0;
      
      for (const sub of subscribers) {
        const ok = await sendEmail(resend, sub.email, `📡 ${post_title}`, emailHtml, sub.unsubscribeToken, workerUrl);
        if (ok) sent++;
        else failed++;
        
        // Small delay to avoid rate limits
        await new Promise(r => setTimeout(r, 100));
      }

      // Log the send
      await env.DB.prepare(
        'INSERT INTO newsletter_sends (post_slug, post_title, post_url, recipient_count, status) VALUES (?, ?, ?, ?, ?)'
      ).bind(post_slug, post_title, post_url, sent, failed > 0 ? 'partial' : 'sent').run();

      return jsonResponse({ 
        message: `Newsletter sent to ${sent} subscribers${failed > 0 ? ` (${failed} failed)` : ''}`,
        sent, 
        failed,
        total: subscribers.length 
      });
    }

    // ─── 404 ───
    return jsonResponse({ error: 'Not found' }, 404);
  },
};
