### SYSTEM ERROR DETECTED FOR FIXING

Context: Hybrid Loader - Orders Refresh
Error Type: ConnectionError
Error: ('Connection aborted.', ConnectionResetError(10054, 'An existing connection was forcibly closed by the remote host', None, 10054, None))
Timestamp: 2026-04-05 16:01:38

Environment:
```json
{
  "python": "3.14.3",
  "platform": "Windows-11-10.0.26200-SP0",
  "cwd": "H:\\Analysis\\Automation-Pivot"
}
```

Additional Details:
```json
{
  "days": 36500,
  "start_date": null,
  "end_date": "2026-04-05",
  "full_sync": true
}
```

Traceback:
```python
Traceback (most recent call last):
  File "C:\Users\deenb\AppData\Roaming\Python\Python314\site-packages\urllib3\connectionpool.py", line 787, in urlopen
    response = self._make_request(
        conn,
    ...<10 lines>...
        **response_kw,
    )
  File "C:\Users\deenb\AppData\Roaming\Python\Python314\site-packages\urllib3\connectionpool.py", line 488, in _make_request
    raise new_e
  File "C:\Users\deenb\AppData\Roaming\Python\Python314\site-packages\urllib3\connectionpool.py", line 464, in _make_request
    self._validate_conn(conn)
    ~~~~~~~~~~~~~~~~~~~^^^^^^
  File "C:\Users\deenb\AppData\Roaming\Python\Python314\site-packages\urllib3\connectionpool.py", line 1093, in _validate_conn
    conn.connect()
    ~~~~~~~~~~~~^^
  File "C:\Users\deenb\AppData\Roaming\Python\Python314\site-packages\urllib3\connection.py", line 796, in connect
    sock_and_verified = _ssl_wrap_socket_and_match_hostname(
        sock=sock,
    ...<14 lines>...
        assert_fingerprint=self.assert_fingerprint,
    )
  File "C:\Users\deenb\AppData\Roaming\Python\Python314\site-packages\urllib3\connection.py", line 975, in _ssl_wrap_socket_and_match_hostname
    ssl_sock = ssl_wrap_socket(
        sock=sock,
    ...<8 lines>...
        tls_in_tls=tls_in_tls,
    )
  File "C:\Users\deenb\AppData\Roaming\Python\Python314\site-packages\urllib3\util\ssl_.py", line 483, in ssl_wrap_socket
    ssl_sock = _ssl_wrap_socket_impl(sock, context, tls_in_tls, server_hostname)
  File "C:\Users\deenb\AppData\Roaming\Python\Python314\site-packages\urllib3\util\ssl_.py", line 527, in _ssl_wrap_socket_impl
    return ssl_context.wrap_socket(sock, server_hostname=server_hostname)
           ~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Program Files\Python314\Lib\ssl.py", line 455, in wrap_socket
    return self.sslsocket_class._create(
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~^
        sock=sock,
        ^^^^^^^^^^
    ...<5 lines>...
        session=session
        ^^^^^^^^^^^^^^^
    )
    ^
  File "C:\Program Files\Python314\Lib\ssl.py", line 1076, in _create
    self.do_handshake()
    ~~~~~~~~~~~~~~~~~^^
  File "C:\Program Files\Python314\Lib\ssl.py", line 1372, in do_handshake
    self._sslobj.do_handshake()
    ~~~~~~~~~~~~~~~~~~~~~~~~~^^
ConnectionResetError: [WinError 10054] An existing connection was forcibly closed by the remote host

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "C:\Users\deenb\AppData\Roaming\Python\Python314\site-packages\requests\adapters.py", line 644, in send
    resp = conn.urlopen(
        method=request.method,
    ...<9 lines>...
        chunked=chunked,
    )
  File "C:\Users\deenb\AppData\Roaming\Python\Python314\site-packages\urllib3\connectionpool.py", line 841, in urlopen
    retries = retries.increment(
        method, url, error=new_e, _pool=self, _stacktrace=sys.exc_info()[2]
    )
  File "C:\Users\deenb\AppData\Roaming\Python\Python314\site-packages\urllib3\util\retry.py", line 490, in increment
    raise reraise(type(error), error, _stacktrace)
          ~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\deenb\AppData\Roaming\Python\Python314\site-packages\urllib3\util\util.py", line 38, in reraise
    raise value.with_traceback(tb)
  File "C:\Users\deenb\AppData\Roaming\Python\Python314\site-packages\urllib3\connectionpool.py", line 787, in urlopen
    response = self._make_request(
        conn,
    ...<10 lines>...
        **response_kw,
    )
  File "C:\Users\deenb\AppData\Roaming\Python\Python314\site-packages\urllib3\connectionpool.py", line 488, in _make_request
    raise new_e
  File "C:\Users\deenb\AppData\Roaming\Python\Python314\site-packages\urllib3\connectionpool.py", line 464, in _make_request
    self._validate_conn(conn)
    ~~~~~~~~~~~~~~~~~~~^^^^^^
  File "C:\Users\deenb\AppData\Roaming\Python\Python314\site-packages\urllib3\connectionpool.py", line 1093, in _validate_conn
    conn.connect()
    ~~~~~~~~~~~~^^
  File "C:\Users\deenb\AppData\Roaming\Python\Python314\site-packages\urllib3\connection.py", line 796, in connect
    sock_and_verified = _ssl_wrap_socket_and_match_hostname(
        sock=sock,
    ...<14 lines>...
        assert_fingerprint=self.assert_fingerprint,
    )
  File "C:\Users\deenb\AppData\Roaming\Python\Python314\site-packages\urllib3\connection.py", line 975, in _ssl_wrap_socket_and_match_hostname
    ssl_sock = ssl_wrap_socket(
        sock=sock,
    ...<8 lines>...
        tls_in_tls=tls_in_tls,
    )
  File "C:\Users\deenb\AppData\Roaming\Python\Python314\site-packages\urllib3\util\ssl_.py", line 483, in ssl_wrap_socket
    ssl_sock = _ssl_wrap_socket_impl(sock, context, tls_in_tls, server_hostname)
  File "C:\Users\deenb\AppData\Roaming\Python\Python314\site-packages\urllib3\util\ssl_.py", line 527, in _ssl_wrap_socket_impl
    return ssl_context.wrap_socket(sock, server_hostname=server_hostname)
           ~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Program Files\Python314\Lib\ssl.py", line 455, in wrap_socket
    return self.sslsocket_class._create(
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~^
        sock=sock,
        ^^^^^^^^^^
    ...<5 lines>...
        session=session
        ^^^^^^^^^^^^^^^
    )
    ^
  File "C:\Program Files\Python314\Lib\ssl.py", line 1076, in _create
    self.do_handshake()
    ~~~~~~~~~~~~~~~~~^^
  File "C:\Program Files\Python314\Lib\ssl.py", line 1372, in do_handshake
    self._sslobj.do_handshake()
    ~~~~~~~~~~~~~~~~~~~~~~~~~^^
urllib3.exceptions.ProtocolError: ('Connection aborted.', ConnectionResetError(10054, 'An existing connection was forcibly closed by the remote host', None, 10054, None))

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "H:\Analysis\Automation-Pivot\BackEnd\services\hybrid_data_loader.py", line 483, in refresh_woocommerce_orders_cache
    fetched_df = wc_service.fetch_all_historical_orders(
        after=after,
    ...<3 lines>...
        show_errors=False,
    )
  File "H:\Analysis\Automation-Pivot\BackEnd\services\woocommerce_service.py", line 112, in fetch_all_historical_orders
    orders = self.fetch_orders(
        page=page,
    ...<3 lines>...
        show_errors=show_errors,
    )
  File "H:\Analysis\Automation-Pivot\BackEnd\services\woocommerce_service.py", line 87, in fetch_orders
    response = self.wcapi.get("orders", params=params)
  File "C:\Users\deenb\AppData\Roaming\Python\Python314\site-packages\woocommerce\api.py", line 106, in get
    return self.__request("GET", endpoint, None, **kwargs)
           ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\deenb\AppData\Roaming\Python\Python314\site-packages\woocommerce\api.py", line 92, in __request
    return request(
        method=method,
    ...<7 lines>...
        **kwargs
    )
  File "C:\Users\deenb\AppData\Roaming\Python\Python314\site-packages\requests\api.py", line 59, in request
    return session.request(method=method, url=url, **kwargs)
           ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\deenb\AppData\Roaming\Python\Python314\site-packages\requests\sessions.py", line 589, in request
    resp = self.send(prep, **send_kwargs)
  File "C:\Users\deenb\AppData\Roaming\Python\Python314\site-packages\requests\sessions.py", line 703, in send
    r = adapter.send(request, **kwargs)
  File "C:\Users\deenb\AppData\Roaming\Python\Python314\site-packages\requests\adapters.py", line 659, in send
    raise ConnectionError(err, request=request)
requests.exceptions.ConnectionError: ('Connection aborted.', ConnectionResetError(10054, 'An existing connection was forcibly closed by the remote host', None, 10054, None))

```

Task:
1. Explain the likely root cause.
2. Identify the safest code change.
3. Suggest tests to prevent regression.
4. Mention any schema mismatch, missing secret, or data-quality issue involved.
