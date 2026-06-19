export default {
  fetch(request, env) {
    var url = new URL(request.url);
    var path = url.pathname;
    var workerUrl = url.protocol + '//' + url.host;
    var DB = env.DB;
    var ADMIN_SECRET = env.ADMIN_SECRET;
    var RESEND_API_KEY = env.RESEND_API_KEY;

    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders() });
    }

    function corsHeaders() {
      return {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
      };
    }

    function jsonResponse(data, status) {
      if (status === undefined) status = 200;
      var h = corsHeaders();
      h['Content-Type'] = 'application/json';
      return new Response(JSON.stringify(data), { status: status, headers: h });
    }

    // Health check
    if (path === '/api/health') return jsonResponse({ status: 'ok' });

    // Debug
    if (path === '/api/debug') {
      var keys = [];
      for (var k in env) keys.push(k);
      return jsonResponse({ keys: keys, hasDB: !!DB, hasAdmin: !!ADMIN_SECRET, hasResend: !!RESEND_API_KEY });
    }

    // Subscribe
    if (path === '/api/subscribe' && request.method === 'POST') {
      return request.json().then(function(body) {
        var email = (body.email || '').trim().toLowerCase();
        if (!email || email.indexOf('@') === -1) return jsonResponse({ error: 'Invalid email' }, 400);
        if (!DB) return jsonResponse({ error: 'D1 not configured' }, 500);
        var token = generateToken();
        return DB.prepare('SELECT id, is_active, unsubscribe_token FROM subscribers WHERE email = ?').bind(email).first().then(function(existing) {
          if (existing) {
            if (existing.is_active) return jsonResponse({ message: 'Already subscribed!' });
            return DB.prepare('UPDATE subscribers SET is_active = 1, subscribed_at = datetime("now"), unsubscribe_token = ? WHERE email = ?').bind(token, email).run().then(function() {
              return jsonResponse({ message: 'Re-subscribed!', success: true });
            });
          }
          return DB.prepare('INSERT INTO subscribers (email, unsubscribe_token) VALUES (?, ?)').bind(email, token).run().then(function() {
            return jsonResponse({ message: 'Subscribed!', success: true });
          });
        });
      }).catch(function(e) { return jsonResponse({ error: 'Server error: ' + e.message }, 500); });
    }

    // Unsubscribe
    if (path === '/api/unsubscribe' && request.method === 'GET') {
      var token = url.searchParams.get('token');
      if (!token) return jsonResponse({ error: 'Missing token' }, 400);
      if (!DB) return jsonResponse({ error: 'D1 not configured' }, 500);
      return DB.prepare('UPDATE subscribers SET is_active = 0 WHERE unsubscribe_token = ? AND is_active = 1').bind(token).run().then(function(result) {
        if (result.meta.changes > 0) {
          return new Response('<!DOCTYPE html><html><head><meta charset="utf-8"><title>Unsubscribed</title>'
            + '<style>body{background:#020205;color:#f0f0f8;font-family:system-ui;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0}'
            + '.card{background:rgba(10,10,20,.7);border:1px solid rgba(255,255,255,.05);border-radius:24px;padding:48px;text-align:center;max-width:420px}'
            + 'h1{font-size:24px;margin-bottom:12px}p{color:#a0a0c0}a{color:#7c6cf0}</style>'
            + '</head><body><div class="card"><h1>Unsubscribed</h1><p>You have been removed.</p>'
            + '<p><a href="https://daily-ai-digest.freelancerloki.workers.dev">Subscribe again</a></p></div></body></html>',
            { headers: { 'Content-Type': 'text/html' } });
        }
        return jsonResponse({ error: 'Invalid token' }, 404);
      });
    }

    // List subscribers (admin)
    if (path === '/api/subscribers' && request.method === 'GET') {
      var secret = url.searchParams.get('secret');
      if (secret !== ADMIN_SECRET) return jsonResponse({ error: 'Unauthorized' }, 401);
      if (!DB) return jsonResponse({ error: 'D1 not configured' }, 500);
      return DB.prepare('SELECT email, subscribed_at, is_active FROM subscribers ORDER BY subscribed_at DESC').all().then(function(r) {
        return jsonResponse({ subscribers: r.results, count: r.results.length });
      });
    }

    // Send newsletter (admin)
    if (path === '/api/send' && request.method === 'POST') {
      return request.json().then(function(body) {
        if (body.secret !== ADMIN_SECRET) return jsonResponse({ error: 'Unauthorized' }, 401);
        var slug = body.post_slug, title = body.post_title, purl = body.post_url;
        if (!slug || !title || !purl) return jsonResponse({ error: 'Missing fields' }, 400);
        if (!DB) return jsonResponse({ error: 'D1 not configured' }, 500);
        if (!RESEND_API_KEY) return jsonResponse({ error: 'Resend not configured' }, 500);
        return DB.prepare('SELECT email, unsubscribe_token FROM subscribers WHERE is_active = 1').all().then(function(r) {
          var subs = r.results;
          if (subs.length === 0) return jsonResponse({ message: 'No subscribers', sent: 0 });
          var subject = '[Daily AI Digest] ' + title;
          var sent = 0, failed = 0;
          var chain = Promise.resolve();
          subs.forEach(function(sub) {
            chain = chain.then(function() {
              return sendEmail(RESEND_API_KEY, sub.email, subject, '<h1>' + title + '</h1><p>New post: <a href="' + purl + '">Read here</a></p>', sub.unsubscribe_token, workerUrl);
            }).then(function(ok) { if (ok) sent++; else failed++; })
              .then(function() { return new Promise(function(r) { setTimeout(r, 100); }); });
          });
          return chain.then(function() {
            return DB.prepare('INSERT INTO newsletter_sends (post_slug, post_title, post_url, recipient_count, status) VALUES (?, ?, ?, ?, ?)')
              .bind(slug, title, purl, sent, failed > 0 ? 'partial' : 'sent').run();
          }).then(function() {
            var msg = 'Sent to ' + sent + ' subscribers';
            if (failed > 0) msg += ' (' + failed + ' failed)';
            return jsonResponse({ message: msg, sent: sent, failed: failed, total: subs.length });
          });
        });
      });
    }

    return jsonResponse({ error: 'Not found' }, 404);
  }
};

function generateToken() {
  var array = new Uint8Array(32);
  crypto.getRandomValues(array);
  var hex = '';
  for (var i = 0; i < array.length; i++) {
    hex += array[i].toString(16).padStart(2, '0');
  }
  return hex;
}

function sendEmail(resendApiKey, to, subject, html, unsubscribeToken, workerUrl) {
  var unsubscribeUrl = workerUrl + '/api/unsubscribe?token=' + unsubscribeToken;
  var fullHtml = '<!DOCTYPE html><html><head><meta charset="utf-8"></head>'
    + '<body style="margin:0;padding:0;background:#020205;font-family:system-ui,sans-serif;color:#f0f0f8;">'
    + '<table width="100%" cellspacing="0" cellpadding="0" style="max-width:600px;margin:0 auto;"><tr><td style="padding:40px 24px;">'
    + '<div style="text-align:center;padding-bottom:32px;"><span style="color:#fff;font-size:18px;font-weight:700;">Daily AI Digest</span></div>'
    + '<div style="background:rgba(10,10,20,0.7);border:1px solid rgba(255,255,255,0.05);border-radius:24px;padding:40px 32px;">'
    + html + '</div>'
    + '<div style="text-align:center;padding-top:32px;">'
    + '<p style="color:#5a5a78;font-size:12px;"><a href="' + unsubscribeUrl + '" style="color:#7c6cf0;">Unsubscribe</a></p>'
    + '</div></td></tr></table></body></html>';
  return fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: { 'Authorization': 'Bearer ' + resendApiKey, 'Content-Type': 'application/json' },
    body: JSON.stringify({ from: 'Daily AI Digest <newsletter@daily-ai-digest.freelancerloki.workers.dev>', to: [to], subject: subject, html: fullHtml }),
  }).then(function(resp) {
    if (!resp.ok) { console.error('Resend error for ' + to + ': ' + resp.status); return false; }
    return true;
  }).catch(function(err) { console.error('Failed to send to ' + to + ': ' + err); return false; });
}
