import json
from django.conf import settings
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from valkey import Valkey

def stream_response(request, request_id):
    def event_stream():
        valkey = Valkey(
            host=settings.VALKEY_CONFIG['HOST'],
            port=settings.VALKEY_CONFIG['PORT'],
            db=settings.VALKEY_CONFIG['DB']
        )
        pubsub = valkey.pubsub()
        channel = f'lore_response_{request_id}'
        pubsub.subscribe(channel)

        for message in pubsub.listen():
            if message['type'] == 'message':
                data = json.loads(message['data'])
                yield f"data: {json.dumps(data)}\n\n"

    response = StreamingHttpResponse(
        event_stream(),
        content_type='text/event-stream'
    )
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'  # Important for Nginx
    return response

@require_http_methods(["POST"])
def acknowledge_chunk(request, request_id):
    """Handle chunk acknowledgment"""
    try:
        data = json.loads(request.body)
        sequence_number = data.get('sequence_number')

        valkey = Valkey(
            host=settings.VALKEY_CONFIG['HOST'],
            port=settings.VALKEY_CONFIG['PORT'],
            db=settings.VALKEY_CONFIG['DB']
        )

        # Send acknowledgment to Lore
        ack_data = {
            'type': 'ack',
            'request_id': request_id,
            'sequence_number': sequence_number
        }
        valkey.publish('lore_ack', json.dumps(ack_data))

        return JsonResponse({'status': 'acknowledged'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)