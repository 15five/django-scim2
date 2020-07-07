import json

from fluent.handler import FluentHandler


class SCIMFluentHandler(FluentHandler):
    """
    And example of a custom log handler that ships data recovered
    from CustomSCIMAuthCheckMiddleware to Fluentd.
    """
    def emit(self, record):
        self.parse_message(record)
        self.obfuscate_record(record)
        data = self.format(record)
        return self.sender.emit(None, data)

    def parse_message(self, record):
        """
        Parse message on record for data set in overridden middleware.
        See CustomSCIMAuthCheckMiddleware.get_loggable_request_message.
        """
        # If record is a dict, lets assume we should set all items on
        # that dict as attributes on the record. The logging logic in Python
        # uses .__dict__ on the record to populate the outgoing message in
        # logging.Handler.format().
        if isinstance(record.msg, dict):
            for key, value in record.msg.items():
                setattr(record, key, value)

            # Reset the message to be the body of the SCIM call.
            record.msg = record.msg['body']

    def obfuscate_record(self, record):
        """
        Strip sensitive info from record.
        """
        try:
            obj = json.loads(record.msg)
        except:
            return

        obj = recursive_obfuscate(obj)

        record.msg = json.dumps(obj)


def recursive_obfuscate(obj, keys_to_obfuscate=('password',)):
    """
    Recursively obfuscate the values of keys with names specified in ``keys_to_obfuscate``.

    return: The same object passed in but hopefully obfuscated.
    """
    if isinstance(obj, dict):
        keys = obj.keys()
        for key in keys:
            if key.lower() in keys_to_obfuscate:
                obj[key] = '*' * 10
            else:
                obj[key] = recursive_obfuscate(obj[key], keys_to_obfuscate)

    return obj
