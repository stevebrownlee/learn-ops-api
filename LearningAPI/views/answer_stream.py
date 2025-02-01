"""Stream responses from Lore service to clients"""
import json
import time
from typing import Generator
import structlog
from django.conf import settings
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from valkey import Valkey

# Initialize logging
log = structlog.get_logger()

# Initialize Valkey client
valkey = Valkey(
    host=settings.VALKEY_CONFIG['HOST'],
    port=settings.VALKEY_CONFIG['PORT'],
    db=settings.VALKEY_CONFIG['DB']
)

def event_stream(request_id: int) -> Generator[str, None, None]:
    """Generate stream of events from Valkey"""
    timeout = getattr(settings, 'STREAM_TIMEOUT', 300)  # 5 minutes default
    start_time = time.time()
    pubsub = None

    try:
        log.info("connecting_to_valkey",
            request_id=request_id,
            timeout=timeout
        )

        pubsub = valkey.pubsub()
        channel = f'lore_response_{request_id}'
        pubsub.subscribe(channel)

        while time.time() - start_time < timeout:
            message = pubsub.get_message(timeout=1.0)

            if message is None:
                continue

            if message['type'] == 'message':
                try:
                    data = json.loads(message['data'])
                    sequence_number = data.get('sequence_number')
                    is_final = data.get('is_final', False)

                    log.info("chunk_received",
                        request_id=request_id,
                        sequence_number=sequence_number,
                        is_final=is_final
                    )

                    yield f"data: {json.dumps(data)}\n\n"

                    if is_final:
                        log.info("stream_complete",
                            request_id=request_id,
                            duration=time.time() - start_time
                        )
                        break

                except json.JSONDecodeError as e:
                    log.error("chunk_decode_error",
                        request_id=request_id,
                        error=str(e)
                    )

        else:
            # Timeout occurred
            log.warning("stream_timeout",
                request_id=request_id,
                timeout=timeout
            )
            yield f"data: {json.dumps({'error': 'Stream timeout', 'is_final': True})}\n\n"

    except Exception as e:
        log.error("stream_error",
            request_id=request_id,
            error=str(e)
        )
        yield f"data: {json.dumps({'error': str(e), 'is_final': True})}\n\n"

    finally:
        if pubsub:
            try:
                pubsub.unsubscribe(channel)
                pubsub.close()
            except Exception as e:
                log.error("pubsub_cleanup_error",
                    request_id=request_id,
                    error=str(e)
                )

def stream_response(request, request_id: int) -> StreamingHttpResponse:
    """Stream response from Lore"""
    log.info("initializing_streaming", request_id=request_id)

    response = StreamingHttpResponse(
        event_stream(request_id),
        content_type='text/event-stream'
    )

    # Headers for SSE
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'  # Important for Nginx

    return response

@csrf_exempt  # Required for cross-origin requests
@require_http_methods(["POST"])
def acknowledge_chunk(request, request_id: int) -> JsonResponse:
    """Handle chunk acknowledgment"""
    start_time = time.time()

    try:
        data = json.loads(request.body)
        sequence_number = data.get('sequence_number')

        if sequence_number is None:
            raise ValueError("sequence_number is required")

        log.info("processing_ack",
            request_id=request_id,
            sequence_number=sequence_number
        )

        # Send acknowledgment to Lore
        ack_data = {
            'type': 'ack',
            'request_id': request_id,
            'sequence_number': sequence_number,
            'timestamp': time.time()
        }
        valkey.publish('lore_ack', json.dumps(ack_data))

        processing_time = time.time() - start_time
        log.info("ack_processed",
            request_id=request_id,
            sequence_number=sequence_number,
            processing_time=processing_time
        )

        return JsonResponse({
            'status': 'acknowledged',
            'processing_time': processing_time
        })

    except json.JSONDecodeError as e:
        log.error("ack_json_error",
            request_id=request_id,
            error=str(e)
        )
        return JsonResponse({
            'error': 'Invalid JSON in request body'
        }, status=400)

    except Exception as e:
        log.error("ack_error",
            request_id=request_id,
            error=str(e)
        )
        return JsonResponse({
            'error': str(e)
        }, status=400)
