from elements.Processors import CallObject, ControllerResponseCall, FLIGHT_STATE, ATC_RESPONSE


class TextEngine:

    @staticmethod
    def CallToText(call: CallObject):
        response = 'say what?'
        if isinstance(call, ControllerResponseCall):
            if call.grant_status == ATC_RESPONSE.GRANTED:
                if call.type_call == FLIGHT_STATE.TAXI_HOLD:
                    response = '{0}, {1}, Taxi to and hold short of runway {2}'\
                        .format(call.recipient, call.caller, call.runway)
                elif call.type_call == FLIGHT_STATE.TAXI:
                    response = '{0}, {1}, Cleared to Taxi to runway {2}, line up and hold'\
                        .format(call.recipient, call.caller, call.runway)
                elif call.type_call == FLIGHT_STATE.TAKE_RUNWAY:
                    response = '{0}, you are cleared to take the active, contact tower at {1}'\
                        .format(call.recipient, call.forward_freq)
                elif call.type_call == FLIGHT_STATE.TAKEOFF:
                    response = '{0}, you are cleared for takeoff, fly runway heading to angels five'\
                        .format(call.recipient)
            elif call.grant_status == ATC_RESPONSE.STANDBY:
                if call.type_call == FLIGHT_STATE.TAKEOFF:
                    if call.request.type_call == FLIGHT_STATE.TAKE_RUNWAY:
                        response = 'Copy that, {0}, standby for takeoff clearance '.format(call.recipient)
                    else:
                        response = '{0}, cannot clear take off at this time, please standby'.format(call.recipient)
                else:
                    response = '{0}, please standby'.format(call.recipient)
            elif call.grant_status == ATC_RESPONSE.ACKNOWLEDGE:
                if call.type_call == FLIGHT_STATE.HOLD_SHORT_RUNWAY:
                    response = 'Copy {0}'.format(call.recipient)
                elif call.type_call == FLIGHT_STATE.TAKE_RUNWAY:
                    if call.forward_freq and call.forward_freq > 0:
                        response = 'Copy that {0}, contact tower at {1} for takeoff clearance'\
                            .format(call.recipient, call.forward_freq)
                    else:
                        response = 'Copy that {0}'.format(call.recipient)
                elif call.type_call == FLIGHT_STATE.TAKEOFF:
                    response = 'Copy that {0}, and you are cleared for takeoff, fly runway heading to angels five'\
                        .format(call.recipient)
                elif call.type_call == FLIGHT_STATE.DEPART_RUNWAY:
                    response = 'copy {0}, have a safe flight'.format(call.recipient)

            elif call.grant_status == ATC_RESPONSE.DENIED:
                response = 'negative {0}'.format(call.recipient)
        return response


