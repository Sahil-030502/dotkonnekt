from datetime import datetime


def create_trace(

    event_type,

    node,

    status,

    message=""

):

    return {

        "timestamp": datetime.utcnow().isoformat(),

        "event": event_type,

        "node": node,

        "status": status,

        "message": message

    }