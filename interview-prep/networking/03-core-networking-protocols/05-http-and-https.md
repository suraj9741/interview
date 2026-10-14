# 3.5 · HTTP and HTTPS

> **Level 3 · Core networking protocols** · Lesson 5 of 11 · ⏱️ about 90 minutes (estimate)
> ⬅️ [3.4 DNS](04-dns.md) · ➡️ [3.6 TLS and certificates](06-tls-and-certificates.md)

## What you'll learn

- The parts of a **URL**, and what an HTTP **request** and **response** look like as plain text on the wire.
- **Methods** (GET, POST …), which are **safe** and **idempotent**, and why that matters for retries.
- **Status codes**, especially the 5xx codes a load balancer generates (502, 503, 504).
- The **headers** that matter for operations: `Host`, `Content-Length`, `Cache-Control`, `X-Forwarded-For` …
- **HTTP/1.0 → 1.1 → 2 → 3**: connection reuse, multiplexing, and QUIC.
- How to time a request phase by phase with `curl -w`.

## Before you start

- [3.3](03-tcp-in-depth.md): HTTP/1.1 and HTTP/2 run inside a TCP connection.
- [3.4](04-dns.md): the name in the URL is resolved first.

---

## The idea in plain words

HTTP is a **conversation in plain text**: the client sends a **request** ("GET me `/index.html`, I'm curl, I accept anything"), the server sends back a **response** ("200 OK, here are 22 bytes of HTML"). Every web page, REST API, Kubernetes API call and container image pull is this conversation.

**HTTPS** is exactly the same conversation, sent **inside an encrypted TLS tunnel** ([3.6](06-tls-and-certificates.md)), normally on port 443 instead of 80.

## Why it matters

- Most production traffic you'll debug is HTTP. Reading a status code and two headers often tells you which layer failed.
- Load balancers, ingress controllers, API gateways and CDNs all **speak HTTP** and make decisions on its headers.
- Retries are only safe for **idempotent** methods; getting this wrong charges a customer twice.

---

## How it works

### Anatomy of a URL

```text
https://api.shop.com:8443/v1/orders?status=open#top
└─┬─┘   └─────┬────┘ └┬─┘└───┬───┘ └────┬────┘ └┬┘
scheme      host    port   path       query    fragment
```

| Part | Meaning |
|---|---|
| **Scheme** | `http` (default port 80) or `https` (default 443) |
| **Host** | Resolved by DNS; also sent in the `Host` header so one IP can serve many sites |
| **Port** | Optional when it's the default |
| **Path + query** | What to fetch, and parameters |
| **Fragment** | Used only by the browser; **never sent** to the server |

### A request and a response on the wire (tested)

HTTP/1.x is plain text, so you can type it by hand. Sending a request with `nc` to Python's `http.server` in [Lab 3.1](../13-hands-on-labs/lab-03.1-capture-a-tcp-handshake.md)'s namespaces **(tested in the lab container)**:

```console
$ printf 'GET /index.html HTTP/1.1\r\nHost: 10.10.0.2\r\nConnection: close\r\n\r\n' | nc -w 2 10.10.0.2 8080
HTTP/1.0 200 OK
Server: SimpleHTTP/0.6 Python/3.13.16
Date: Wed, 14 Oct 2026 19:45:27 GMT
Content-type: text/html
Content-Length: 22
Last-Modified: Wed, 14 Oct 2026 19:44:34 GMT

hello from the server
```

The same exchange through `curl -v` (`>` = sent, `<` = received) **(tested in the lab container; progress meter trimmed)**:

```text
*   Trying 10.10.0.2:8080...
* Connected to 10.10.0.2 (10.10.0.2) port 8080
> GET /index.html HTTP/1.1
> Host: 10.10.0.2:8080
> User-Agent: curl/8.5.0
> Accept: */*
>
* HTTP 1.0, assume close after body
< HTTP/1.0 200 OK
< Server: SimpleHTTP/0.6 Python/3.13.16
< Date: Wed, 14 Oct 2026 19:45:27 GMT
< Content-type: text/html
< Content-Length: 22
< Last-Modified: Wed, 14 Oct 2026 19:44:34 GMT
<
* Closing connection
hello from the server
```

| Piece | Request | Response |
|---|---|---|
| First line | **Method, path, version**: `GET /index.html HTTP/1.1` | **Version, status code, reason**: `HTTP/1.0 200 OK` |
| Headers | `Name: value` lines | Same format |
| Blank line | Ends the headers (`\r\n\r\n`) | Same |
| Body | Optional (e.g. a POST's JSON) | The content, `Content-Length` bytes long |

In the packet capture of [3.3](03-tcp-in-depth.md) this request was **87 bytes** (packet 4) and the response headers **186 bytes** (packet 6), followed by the 22-byte body.

### Methods

| Method | Purpose | Safe? (no change) | Idempotent? (repeat = same result) |
|---|---|---|---|
| **GET** | Read a resource | ✅ | ✅ |
| **HEAD** | Like GET, headers only | ✅ | ✅ |
| **OPTIONS** | Which methods are allowed (CORS preflight) | ✅ | ✅ |
| **POST** | Create / submit / "do something" | ❌ | ❌ |
| **PUT** | Replace a resource completely | ❌ | ✅ |
| **PATCH** | Change part of a resource | ❌ | Not necessarily |
| **DELETE** | Remove a resource | ❌ | ✅ |

**Why idempotency matters:** proxies, load balancers and client libraries may **retry** a request after a timeout. Retrying a GET or PUT is harmless; retrying a POST can create a second order. APIs use **idempotency keys** to make POST retries safe.

`HEAD` and two error cases against the lab server **(tested in the lab container)**:

```console
$ curl -sSI http://10.10.0.2:8080/index.html
HTTP/1.0 200 OK
Server: SimpleHTTP/0.6 Python/3.13.16
...
Content-Length: 22
$ curl -s -o /dev/null -w '%{http_code}\n' http://10.10.0.2:8080/nope
404
$ curl -s -X POST -d 'a=1' -o /dev/null -w '%{http_code}\n' http://10.10.0.2:8080/
501
```

(`501 Not Implemented`: Python's simple server doesn't support POST at all.)

### Status codes

| Class | Meaning | Ones to know |
|---|---|---|
| **1xx** | Informational | `101 Switching Protocols` (WebSocket upgrade) |
| **2xx** | Success | `200 OK`, `201 Created`, `204 No Content` |
| **3xx** | Redirect / use cache | `301`/`308` moved permanently, `302`/`307` temporary, `304 Not Modified` (your cached copy is fine) |
| **4xx** | **Client** error: fix the request | `400` bad request, **`401`** not authenticated, **`403`** authenticated but not allowed, `404` not found, `405` method not allowed, `408` request timeout, **`429`** too many requests (rate limited) |
| **5xx** | **Server** error | `500` app crashed, `501` not implemented, **`502`**, **`503`**, **`504`** (below) |

The three you'll debug most, usually **generated by a load balancer or reverse proxy**, not by your app:

| Code | Meaning at a proxy / load balancer | Typical cause |
|---|---|---|
| **502 Bad Gateway** | The backend **answered badly**: closed the connection, reset it, or sent garbage | App crashed mid-request; backend keepalive timeout **shorter** than the LB's; wrong protocol (HTTPS to an HTTP port) |
| **503 Service Unavailable** | **No healthy backend** to send to (or deliberately overloaded) | All targets failing health checks; Kubernetes Service with no ready endpoints |
| **504 Gateway Timeout** | The backend **didn't answer in time** | Slow app or database; security group blocking the LB → target path (the connect times out) |

### Headers worth knowing

| Header | Direction | Why it matters |
|---|---|---|
| `Host` | Request | **Required in HTTP/1.1.** Lets one IP host many sites; ingress controllers and ALBs route on it. (HTTP/2 uses `:authority`) |
| `Content-Type` / `Content-Length` | Both | What the body is, and how long. Mismatched length = truncated or hanging responses |
| `Connection: keep-alive` / `close` | Both | Reuse the TCP connection or not (HTTP/1.x) |
| `Cache-Control`, `ETag`, `Last-Modified` | Response | How long caches (browser, CDN) may keep it; `304` revalidation |
| `Location` | Response | Where a `3xx` redirect points |
| `Set-Cookie` / `Cookie` | Response / request | Sessions. HTTP itself is **stateless**; cookies or tokens add state |
| `Authorization` | Request | Credentials (e.g. `Bearer <token>`) |
| `X-Forwarded-For`, `X-Forwarded-Proto` | Request (added by proxies) | The **original client IP** and scheme, because the app only sees the proxy's IP. The standard form is `Forwarded` (RFC 7239) |

### HTTP versions

| Version | Transport | Key change |
|---|---|---|
| **HTTP/1.0** (1996) | TCP | One request per connection by default |
| **HTTP/1.1** (1997) | TCP | **Persistent connections** (keep-alive) by default; `Host` header required. Requests on one connection are answered **in order**, so a slow response blocks the ones behind it |
| **HTTP/2** (2015) | TCP (TLS in practice) | **Binary**, **multiplexes** many requests over **one** connection, compresses headers. Negotiated with **ALPN** during TLS (`h2`). Still suffers TCP head-of-line blocking when a packet is lost |
| **HTTP/3** (2022) | **QUIC over UDP** | Streams are independent, so one lost packet only stalls its own stream; TLS 1.3 is built in, so connection setup is faster. Falls back to HTTP/2 when UDP 443 is blocked |

Connection reuse, seen from the client. The lab server speaks HTTP/1.0, so `curl` closes after each request (`HTTP 1.0, assume close after body`, above). A second server configured for HTTP/1.1, asked for two URLs in one `curl` command **(tested in the lab container)**:

```text
* Connected to 10.10.0.2 (10.10.0.2) port 8081
> GET /index.html HTTP/1.1
< HTTP/1.1 200 OK
* Connection #0 to host 10.10.0.2 left intact
* Re-using existing connection with host 10.10.0.2
> GET /index.html HTTP/1.1
< HTTP/1.1 200 OK
* Connection #0 to host 10.10.0.2 left intact
```

One TCP handshake, two requests.

### Timing a request phase by phase

`curl -w` prints how long each phase took (cumulative seconds from the start) **(tested in the lab container, two namespaces on one machine, so everything is tiny)**:

```console
$ curl -s -o /dev/null -w 'dns=%{time_namelookup} connect=%{time_connect} ttfb=%{time_starttransfer} total=%{time_total}\n' http://10.10.0.2:8080/index.html
dns=0.000019 connect=0.000162 ttfb=0.001369 total=0.001414
```

| Phase | Large value means |
|---|---|
| `time_namelookup` | Slow DNS |
| `time_connect` − namelookup | Network RTT / SYN retries |
| `time_appconnect` (HTTPS only) | TLS handshake cost |
| `time_starttransfer` (TTFB) − connect | **Server think time**: the app or database is slow |
| `time_total` − starttransfer | Transfer: big body or slow link |

---

## Try it

**On your Mac or Linux:**

```bash
curl -v https://example.com/ -o /dev/null          # request and response headers, TLS info
curl -sSI https://example.com/                      # headers only (HEAD)
curl -sS -o /dev/null -w '%{http_code} %{time_total}\n' https://example.com/
curl -sS -L -o /dev/null -w '%{url_effective}\n' http://github.com   # follow redirects
curl -sS --http2 -o /dev/null -w '%{http_version}\n' https://example.com/
curl -H 'Host: other.site' http://<ip>/             # test name-based routing by IP
```

## In the real world

- **AWS ALB** is an HTTP-aware (L7) load balancer: it routes on host and path, terminates TLS, adds `X-Forwarded-For`, and generates 502/503/504 itself. **NLB** works at L4 and doesn't look at HTTP at all.
- **Kubernetes Ingress / Gateway API**: an ingress controller (NGINX, ALB controller, Envoy) routes by `Host` and path to Services.
- **Health checks** are usually an HTTP GET to a path like `/healthz`; a target is "healthy" only if it returns the expected status code.
- **Container registries** are HTTP APIs: `docker pull` is a series of GETs with `Authorization` headers.
- **Keepalive mismatch**: if a backend closes idle connections **sooner** than the load balancer does, the LB may send a request on a connection the backend just closed → sporadic **502s**. Keep the backend's keepalive timeout **longer** than the LB's idle timeout.

## Common mistakes

| Mistake | Fix |
|---|---|
| Treating every 5xx as an app bug | 502/503/504 are usually generated by the proxy; check its logs and target health first |
| Using the source IP for client identity behind a proxy | Read `X-Forwarded-For` (and trust it only from your own proxies) |
| Retrying POSTs automatically | Retry only idempotent methods, or use idempotency keys |
| Testing a virtual host by IP without a `Host` header | `curl -H 'Host: name' http://ip/` or `curl --resolve name:443:ip https://name/` |
| 401 vs 403 confusion | 401 = who are you? (log in); 403 = I know who you are, and no |

## Troubleshooting

| What you see | Likely cause | Check |
|---|---|---|
| `curl: (6) Could not resolve host` | DNS | [3.4](04-dns.md) |
| `curl: (7) … Couldn't connect` | Nothing listening, or REJECT | `ss -tlnp` on the server ([3.2](02-tcp-and-udp.md)) |
| `curl: (28) … Timeout` | SYNs dropped / slow server | Is it `time_connect` or TTFB that's slow? |
| `curl: (52) Empty reply from server` / `(56) Recv failure` | Connection closed or reset with no response: app crashed, wrong protocol, app listening only on `127.0.0.1` behind a port publish ([1.3](../01-networking-fundamentals/03-addresses-ports-and-protocols.md)) | App logs; `ss -tlnp` |
| 502 from the LB | Backend reset/closed or spoke the wrong protocol | LB access logs; backend keepalive; HTTP vs HTTPS to the target |
| 503 from the LB | No healthy targets | Target health; readiness probes; Service endpoints |
| 504 from the LB | Backend too slow or unreachable | App latency; security group from LB to target |
| Redirect loop | HTTP→HTTPS redirect behind a TLS-terminating LB that talks HTTP to the app | Make the app trust `X-Forwarded-Proto` |

## Hands-on lab

[Lab 3.1 · Capture a TCP handshake](../13-hands-on-labs/lab-03.1-capture-a-tcp-handshake.md), part F: send an HTTP request by hand with `nc`, compare HTTP/1.0 and HTTP/1.1 connection reuse, and time a request with `curl -w`. HTTPS is in [Lab 3.3](../13-hands-on-labs/lab-03.3-tls-certificates-and-handshake.md).

## Interview angle

- ⭐ **"What happens when you type a URL?"** → DNS → TCP handshake → TLS handshake → HTTP request with `Host` → response → rendering, with caching at every step ([3.10](10-packet-flow-end-to-end.md)).
- ⭐ **"502 vs 503 vs 504?"** → Bad answer from the backend / no healthy backend / backend too slow. Usually generated by the LB, not the app.
- **"401 vs 403?"** → Not authenticated vs not authorised.
- **"What did HTTP/2 and HTTP/3 change?"** → HTTP/2: binary multiplexing over one TCP connection. HTTP/3: the same over QUIC (UDP), removing TCP head-of-line blocking.
- **"How does the app learn the client's real IP behind a load balancer?"** → `X-Forwarded-For` (ALB), or the PROXY protocol / client IP preservation (NLB).
- **"Which methods are idempotent?"** → GET, HEAD, OPTIONS, PUT, DELETE. Not POST (or necessarily PATCH).

## Check yourself

1. Which part of `https://shop.com/cart?id=7#summary` is never sent to the server?
2. Why must an HTTP/1.1 request contain a `Host` header?
3. A Kubernetes Service has no ready pods. What status code does the ingress likely return?
4. TTFB is 2.8 s, `time_connect` is 0.02 s. Where's the problem?
5. Can a client safely retry a timed-out `PUT /users/42`? A `POST /orders`?

<details>
<summary><b>Answers</b> (try first)</summary>

1. The **fragment** `#summary`.
2. Many sites share one IP address; `Host` tells the server (or ingress) which site is wanted.
3. **503 Service Unavailable**.
4. On the **server side** (application or database): the network connected in 20 ms, but the first byte took 2.8 s.
5. `PUT` is idempotent, so **yes**. `POST` is not, so only with an idempotency key or after checking whether the first attempt succeeded.

</details>

## Summary

- HTTP = text request (**method, path, headers, body**) and response (**status, headers, body**). HTTPS = the same inside TLS.
- **GET/HEAD/PUT/DELETE are idempotent; POST isn't**: it matters for retries.
- 4xx = client's fault, 5xx = server side. **502/503/504** usually come from the load balancer.
- HTTP/1.1 reuses connections; HTTP/2 multiplexes over one TCP connection; HTTP/3 uses QUIC over UDP.
- `curl -v` and `curl -w` are your first tools.

## Next

➡️ [3.6 · TLS and certificates](06-tls-and-certificates.md): how the "S" in HTTPS works, and how to read every certificate error.
