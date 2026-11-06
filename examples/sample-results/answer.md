# How do Cache-Control and ETag work together in HTTP caching?

## Answer

`Cache-Control` and `ETag` work together to control **when a cached HTTP response can be reused and how the client checks whether it is still up to date**\.

They have different but complementary responsibilities\:

- **`Cache-Control`** defines caching behavior, including how long a response remains fresh and whether it must be revalidated before reuse. [S1][S2]
- **`ETag`** identifies a specific version of a resource, allowing the client and server to determine whether the cached version is still current. [S1][S3]

Together, they reduce unnecessary data transfers while ensuring clients receive updated content when necessary.

The typical workflow is\:

1. The server responds with `Cache-Control` and `ETag`\.
2. The client stores the response according to the caching directives.
3. While the response is fresh, the client can reuse it without contacting the server.
4. Once the response becomes stale, the client sends its stored ETag using `If-None-Match`\.
5. The server compares the supplied ETag with the current resource version\:

   - If they match, it returns `304 Not Modified`, without a response body.
   - If they differ, it returns `200 OK` with the updated resource. [S1][S2][S3]

## Comparison

| Aspect | Cache-Control | ETag |
|--------|--------|--------|
| Purpose | Controls caching behavior. [S2] | Identifies a resource version. [S3] |
| Main responsibility | Determines freshness and revalidation requirements. [S1][S2] | Determines whether content has changed. [S1][S3] |
| Header type | Request and response header. [S2] | Response header. [S3] |
| Example | `max-age=3600` | `"abc123"` |
| When used | Throughout the caching lifecycle. [S2] | Particularly during cache validation. [S1][S3] |
| Result | Allows reuse or requires validation. [S2] | Enables `304 Not Modified` or an updated `200 OK`\. [S3] |

Important `Cache-Control` directives include\:

- `max-age=3600`\: The response remains fresh for 3600 seconds after generation. [S2]
- `no-cache`\: Allows storage but requires validation with the origin server before reuse. [S2]
- `no-store`\: Prevents storing the response. [S2]

## Example

Consider a server providing an HTML page.

**Illustrative example, not an observed server response\:**

Initial server response\:

```http
HTTP/1.1 200 OK
Cache-Control: max-age=60
ETag: "version1"

<html>Welcome!</html>
```

The browser stores the response and can reuse it for 60 seconds without contacting the server.

After 60 seconds, the cached response becomes stale. The browser can revalidate it\:

```http
GET /index.html HTTP/1.1
If-None-Match: "version1"
```

If the content has not changed, the server responds\:

```http
HTTP/1.1 304 Not Modified
```

The browser reuses its previously stored response without downloading the HTML again. [S1][S2][S3]

If the content has changed, the server instead returns `200 OK` with the new content and a new ETag. [S1][S3]

## Limitations

- `Cache-Control` does not identify whether two resource versions are identical; that is the role of validators such as ETag. [S1][S3]
- `ETag` alone does not define how long a response can remain fresh. [S2][S3]
- `no-cache` does not mean that a response cannot be stored; it means that validation is required before reuse. [S2]
- Weak ETags (`W/`\) can identify semantically equivalent representations that are not byte-for-byte identical. They are less suitable for certain comparisons, particularly byte-range requests. [S3]
- A `304 Not Modified` response does not contain the resource body, so the client needs its previously stored representation. [S3]

**In summary\:** `Cache-Control` determines the caching policy, while `ETag` provides the mechanism for checking whether cached content has changed. Using both enables efficient HTTP caching without unnecessarily downloading unchanged resources. [S1][S2][S3]

## Sources

- [S1] HTTP caching - HTTP | MDN - <https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching>
- [S2] Cache-Control header - HTTP | MDN - <https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cache-Control>
- [S3] ETag header - HTTP | MDN - <https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/ETag>
