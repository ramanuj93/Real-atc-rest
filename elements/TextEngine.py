from elements.Processors import CallObject, ControllerResponseCall, FLIGHT_STATE, ATC_RESPONSE


class TextEngine:

    @staticmethod
    def CallToText(call: CallObject):
        response = 'say what?'
        if isinstance(call, ControllerResponseCall):
            if call.grant_status == ATC_RESPONSE.GRANTED:
                if call.type_call == FLIGHT_STATE.TAXI:
                    response = '{0}, {1}, Taxi to and hold short of runway {2}'\
                        .format(call.recipient, call.caller, call.runway)
                elif call.type_call == FLIGHT_STATE.TAKE_RUNWAY:
                    response = '{0}, you are cleared to take the active'.format(call.recipient)
                elif call.type_call == FLIGHT_STATE.TAKEOFF:
                    response = '{0}, you are cleared for takeoff, fly runway heading to angels five'\
                        .format(call.recipient)
            elif call.grant_status == ATC_RESPONSE.STANDBY:
                response = '{0}, please standby'.format(call.recipient)
            elif call.grant_status == ATC_RESPONSE.ACKNOWLEDGE:
                if call.type_call == FLIGHT_STATE.HOLD_SHORT_RUNWAY:
                    response = 'Copy {0}'.format(call.recipient)
            elif call.grant_status == ATC_RESPONSE.DENIED:
                response = 'negative {0}'.format(call.recipient)
        return response


