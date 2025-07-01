#!/usr/bin/env python3


#
#
#
class StrikerException(Exception):
    def get_message(error):
        return f"${{goto 20}}${{color red}}${{font4}}${{alignc}}{error}\n"
