import logging
import logging.handlers
from multiprocessing import Manager, Process, Queue
from queue import Empty as QEmpty
import uuid
from aiohttp import web

manager = Manager()
total_invocations = 0
max_workers = 0
q = Queue(-1)
workers = manager.dict()


# Configure logging to write to file
def configure_logging():
    root_logger = logging.getLogger()
    file_handler = logging.handlers.RotatingFileHandler('faas-example.log', mode='a', maxBytes=300000, backupCount=3)
    formatter = logging.Formatter('%(asctime)s %(processName)-10s %(name)s %(levelname)-8s %(message)s')
    file_handler.setFormatter(formatter)
    root_logger.propagate = False
    root_logger.addHandler(file_handler)
    root_logger.setLevel(logging.DEBUG)


# Handle messages in q - this is the 'FaaS' handler
def faas_message_handler(id):
    configure_logging()
    logger = logging.getLogger()
    while True:
        try:
            message = q.get(timeout=10)
            logger.info(message)
        except QEmpty:
            logger.debug("No message recieved, existing")
            # If no message recieved within 10 seconds, exit
            break
    global workers
    workers.pop(id, None)


# GET /statistics 
async def get_statistics(request):
    global total_invocations
    global max_workers
    return web.json_response({
        'active_instances': len(workers), 
        'total_invocations': total_invocations, 
        'max_workers': max_workers
    })


# POST /messages
async def write_message(request):
    request_body = await request.json()

    global total_invocations
    total_invocations = total_invocations + 1

    # TODO: Validate 'message' field exists
    q.put(request_body.get('message'))

    if len(workers) < q.qsize():
        global max_workers
        worker_id = str(uuid.uuid4())
        worker = Process(target=faas_message_handler, args=(worker_id,))
        worker.start()
        workers[worker_id] = worker.pid
        max_workers = max(max_workers, len(workers))

    return web.json_response({'status': 'OK'})


# Main application

app = web.Application()
app.router.add_get('/statistics', get_statistics)
app.router.add_post('/messages', write_message)
web.run_app(app, port=8000)
