from rest_framework.throttling import AnonRateThrottle


class GeneralAnonRateThrottle(AnonRateThrottle):
    THROTTLE_RATES = {
        'user': None,
        'anon': '100/day',
    }


class SignUpRateThrottle(GeneralAnonRateThrottle):
    pass


class VarifyMailThrottle(GeneralAnonRateThrottle):
    THROTTLE_RATES = {
        'user': None,
        'anon': '200/day',
    }
