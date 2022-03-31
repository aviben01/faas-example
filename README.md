# FaaS - Simple implementation of a Function as a Service

Example application for demonstrating simple functions that get executed asynchronously in a separate process.

In event where no process is available, a new is created.

Install:
```bash
pip install requirements.txt
```

Run Server:
```bash
python ./faas-example.py
```

Send a single message:

```bash
curl -H 'Content-Type: application/json' -X POST --data '{"message": "xyz"}' http://localhost:8000/messages
```

Run multiple concurrent requests:

```bash
for i in {1..100}; do curl -H 'Content-Type: application/json' -X POST --data '{"message": "xyz-'$i'"}' http://localhost:8000/messages & done
```

To read function invocation statistics:

```bash
$ curl http://localhost:8000/statistics
{"active_instances": 12, "total_invocations": 150, "max_workers": 14}
```

Logs can be read from file: `faas-example.log`